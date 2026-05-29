"""
Stage 3: Customer segmentation using RFM analysis.

Run from the project root:
    python scripts/04_customer_segmentation.py
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "retail_analytics.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "customer_segments"

RFM_OUTPUT_PATH = OUTPUT_DIR / "rfm_customer_segments.csv"
SEGMENT_SUMMARY_PATH = OUTPUT_DIR / "rfm_segment_summary.csv"
COUNTRY_SUMMARY_PATH = OUTPUT_DIR / "rfm_country_summary.csv"
HIGH_VALUE_PATH = OUTPUT_DIR / "high_value_customers.csv"
AT_RISK_PATH = OUTPUT_DIR / "at_risk_customers.csv"
RECOMMENDATIONS_PATH = OUTPUT_DIR / "segment_recommendations.csv"

SEGMENT_ORDER = [
    "Champions",
    "Cannot Lose Them",
    "At Risk",
    "Loyal Customers",
    "Potential Loyalists",
    "New Customers",
    "Promising Customers",
    "Need Attention",
    "Hibernating",
    "Lost Customers",
    "Low Value Customers",
]


def require_database() -> None:
    """Stop with a clear error if the Stage 2 database is missing."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Required database is missing. Run "
            "python scripts/02_build_sql_database.py first."
        )


def validate_sales_transactions_table(connection: sqlite3.Connection) -> None:
    """Check that the source table needed for RFM exists."""
    table_exists = connection.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'sales_transactions'
        """
    ).fetchone()[0]

    if table_exists == 0:
        raise ValueError("Required table is missing from the database: sales_transactions")


def load_customer_sales(connection: sqlite3.Connection) -> pd.DataFrame:
    """Load only known-customer sales records from the sales_transactions table."""
    query = """
    SELECT
        customer_id,
        invoice_no,
        invoice_date,
        country,
        quantity,
        revenue
    FROM sales_transactions
    WHERE customer_id IS NOT NULL
    """
    sales = pd.read_sql_query(query, connection)

    if sales.empty:
        raise ValueError("No known-customer sales records found for RFM segmentation.")

    sales["customer_id"] = sales["customer_id"].astype("string")
    sales["invoice_no"] = sales["invoice_no"].astype("string")
    sales["invoice_date"] = pd.to_datetime(sales["invoice_date"], errors="coerce")
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales["revenue"] = pd.to_numeric(sales["revenue"], errors="coerce")
    sales = sales.dropna(subset=["customer_id", "invoice_no", "invoice_date", "revenue"])

    if sales.empty:
        raise ValueError("Known-customer sales records became empty after type validation.")

    return sales


def safe_qcut_score(series: pd.Series, higher_is_better: bool) -> pd.Series:
    """
    Create 1 to 5 scores with qcut.

    If repeated values force qcut to drop bins, scale the remaining bins back into
    the familiar 1 to 5 scoring range.
    """
    numeric_series = pd.to_numeric(series, errors="coerce")
    unique_values = numeric_series.dropna().nunique()

    if unique_values <= 1:
        return pd.Series([3] * len(numeric_series), index=numeric_series.index, dtype="int64")

    bin_count = min(5, unique_values)

    try:
        raw_bins = pd.qcut(
            numeric_series,
            q=bin_count,
            labels=False,
            duplicates="drop",
        )
    except ValueError:
        raw_bins = pd.qcut(
            numeric_series.rank(method="first"),
            q=bin_count,
            labels=False,
            duplicates="drop",
        )

    if raw_bins.dropna().empty:
        return pd.Series([3] * len(numeric_series), index=numeric_series.index, dtype="int64")

    max_bin = int(raw_bins.max())
    if max_bin == 0:
        return pd.Series([3] * len(numeric_series), index=numeric_series.index, dtype="int64")

    if higher_is_better:
        scores = 1 + (raw_bins * 4 / max_bin)
    else:
        scores = 5 - (raw_bins * 4 / max_bin)

    return scores.round().clip(1, 5).fillna(3).astype(int)


def assign_customer_segment(row: pd.Series) -> str:
    """Assign exactly one business-friendly segment using ordered rules."""
    recency_score = int(row["recency_score"])
    frequency_score = int(row["frequency_score"])
    monetary_score = int(row["monetary_score"])
    rfm_score = int(row["rfm_score"])

    if recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4:
        return "Champions"

    if recency_score <= 2 and frequency_score >= 4 and monetary_score >= 4:
        return "Cannot Lose Them"

    if recency_score <= 2 and (frequency_score >= 4 or monetary_score >= 4):
        return "At Risk"

    if frequency_score >= 4 and monetary_score >= 3:
        return "Loyal Customers"

    if recency_score >= 4 and frequency_score >= 2:
        return "Potential Loyalists"

    if recency_score == 5 and frequency_score == 1:
        return "New Customers"

    if recency_score >= 4 and monetary_score <= 3:
        return "Promising Customers"

    if recency_score == 3 and (frequency_score >= 3 or monetary_score >= 3):
        return "Need Attention"

    if recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2:
        return "Hibernating"

    if recency_score <= 1 and rfm_score <= 7:
        return "Lost Customers"

    if frequency_score <= 2 and monetary_score <= 2:
        return "Low Value Customers"

    return "Need Attention"


def calculate_rfm(sales: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Calculate customer-level RFM metrics, scores, codes, and segments."""
    snapshot_date = sales["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = (
        sales.groupby("customer_id", as_index=False)
        .agg(
            first_purchase_date=("invoice_date", "min"),
            last_purchase_date=("invoice_date", "max"),
            frequency=("invoice_no", "nunique"),
            monetary=("revenue", "sum"),
            total_quantity=("quantity", "sum"),
        )
    )

    rfm["recency_days"] = (snapshot_date - rfm["last_purchase_date"]).dt.days.astype(int)
    rfm["average_order_value"] = rfm["monetary"] / rfm["frequency"]
    rfm["active_days"] = (
        rfm["last_purchase_date"] - rfm["first_purchase_date"]
    ).dt.days.astype(int)

    country_rank = (
        sales.groupby(["customer_id", "country"], as_index=False)
        .agg(country_revenue=("revenue", "sum"), country_orders=("invoice_no", "nunique"))
        .sort_values(
            ["customer_id", "country_revenue", "country_orders", "country"],
            ascending=[True, False, False, True],
        )
    )
    main_country = country_rank.drop_duplicates("customer_id")[["customer_id", "country"]]
    main_country = main_country.rename(columns={"country": "main_country"})
    rfm = rfm.merge(main_country, on="customer_id", how="left")

    rfm["recency_score"] = safe_qcut_score(rfm["recency_days"], higher_is_better=False)
    rfm["frequency_score"] = safe_qcut_score(rfm["frequency"], higher_is_better=True)
    rfm["monetary_score"] = safe_qcut_score(rfm["monetary"], higher_is_better=True)
    rfm["rfm_score"] = (
        rfm["recency_score"] + rfm["frequency_score"] + rfm["monetary_score"]
    ).astype(int)
    rfm["rfm_code"] = (
        rfm["recency_score"].astype(str)
        + rfm["frequency_score"].astype(str)
        + rfm["monetary_score"].astype(str)
    )
    rfm["customer_segment"] = rfm.apply(assign_customer_segment, axis=1)

    if rfm["customer_segment"].isna().any():
        raise ValueError("Some customers did not receive a customer segment.")

    rfm["first_purchase_date"] = rfm["first_purchase_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    rfm["last_purchase_date"] = rfm["last_purchase_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    output_columns = [
        "customer_id",
        "first_purchase_date",
        "last_purchase_date",
        "recency_days",
        "frequency",
        "monetary",
        "total_quantity",
        "average_order_value",
        "active_days",
        "main_country",
        "recency_score",
        "frequency_score",
        "monetary_score",
        "rfm_score",
        "rfm_code",
        "customer_segment",
    ]

    return rfm[output_columns].sort_values("monetary", ascending=False), snapshot_date


def build_segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Summarize customer and revenue performance by segment."""
    summary = (
        rfm.groupby("customer_segment", as_index=False)
        .agg(
            customer_count=("customer_id", "count"),
            total_revenue=("monetary", "sum"),
            average_recency_days=("recency_days", "mean"),
            average_frequency=("frequency", "mean"),
            average_monetary=("monetary", "mean"),
            average_order_value=("average_order_value", "mean"),
            total_quantity=("total_quantity", "sum"),
        )
    )

    summary["customer_percentage"] = summary["customer_count"] / len(rfm) * 100
    summary["revenue_percentage"] = summary["total_revenue"] / rfm["monetary"].sum() * 100
    summary["segment_order"] = summary["customer_segment"].map(
        {segment: index for index, segment in enumerate(SEGMENT_ORDER)}
    )
    summary = summary.sort_values("segment_order").drop(columns="segment_order")

    numeric_columns = [
        "customer_percentage",
        "total_revenue",
        "revenue_percentage",
        "average_recency_days",
        "average_frequency",
        "average_monetary",
        "average_order_value",
        "total_quantity",
    ]
    summary[numeric_columns] = summary[numeric_columns].round(2)

    return summary[
        [
            "customer_segment",
            "customer_count",
            "customer_percentage",
            "total_revenue",
            "revenue_percentage",
            "average_recency_days",
            "average_frequency",
            "average_monetary",
            "average_order_value",
            "total_quantity",
        ]
    ]


def build_country_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Summarize segment performance by main customer country."""
    country_summary = (
        rfm.groupby(["customer_segment", "main_country"], as_index=False)
        .agg(
            customer_count=("customer_id", "count"),
            total_revenue=("monetary", "sum"),
            average_monetary=("monetary", "mean"),
        )
        .sort_values(["customer_segment", "total_revenue"], ascending=[True, False])
    )
    country_summary["total_revenue"] = country_summary["total_revenue"].round(2)
    country_summary["average_monetary"] = country_summary["average_monetary"].round(2)
    return country_summary


def build_segment_recommendations() -> pd.DataFrame:
    """Create simple business actions for each segment."""
    recommendations = [
        (
            "Champions",
            "Best customers with recent, frequent, high-value purchases.",
            "Reward with loyalty offers, early access, and premium retention campaigns.",
        ),
        (
            "Cannot Lose Them",
            "Historically strong customers who have not purchased recently.",
            "Prioritize personal win-back outreach and high-value incentives.",
        ),
        (
            "At Risk",
            "Previously valuable customers showing signs of inactivity.",
            "Send targeted win-back campaigns and reminders based on prior preferences.",
        ),
        (
            "Loyal Customers",
            "Frequent buyers with strong monetary value.",
            "Encourage bundles, cross-selling, and loyalty program upgrades.",
        ),
        (
            "Potential Loyalists",
            "Recent customers starting to show repeat behavior.",
            "Nurture with personalized product recommendations and second-purchase offers.",
        ),
        (
            "New Customers",
            "Very recent customers with limited purchase history.",
            "Create onboarding journeys and first-repeat purchase incentives.",
        ),
        (
            "Promising Customers",
            "Recent customers with room to increase value.",
            "Promote relevant categories and low-friction upsell offers.",
        ),
        (
            "Need Attention",
            "Mid-tier customers who need stronger engagement.",
            "Use targeted campaigns, product education, and limited-time offers.",
        ),
        (
            "Hibernating",
            "Inactive customers with low historical activity.",
            "Use low-cost reactivation campaigns and monitor response carefully.",
        ),
        (
            "Lost Customers",
            "Very inactive customers with weak overall activity.",
            "Use low-cost reactivation only or suppress from expensive campaigns.",
        ),
        (
            "Low Value Customers",
            "Customers with weak frequency and monetary contribution.",
            "Use automated, low-cost campaigns and avoid heavy discounting.",
        ),
    ]

    return pd.DataFrame(
        recommendations,
        columns=["customer_segment", "business_meaning", "recommended_action"],
    )


def create_customer_segments_table(connection: sqlite3.Connection, rfm: pd.DataFrame) -> None:
    """Replace only the customer_segments table in SQLite."""
    connection.execute("DROP TABLE IF EXISTS customer_segments;")
    connection.execute(
        """
        CREATE TABLE customer_segments (
            customer_id TEXT PRIMARY KEY,
            first_purchase_date TEXT,
            last_purchase_date TEXT,
            recency_days INTEGER,
            frequency INTEGER,
            monetary REAL,
            total_quantity REAL,
            average_order_value REAL,
            active_days INTEGER,
            main_country TEXT,
            recency_score INTEGER,
            frequency_score INTEGER,
            monetary_score INTEGER,
            rfm_score INTEGER,
            rfm_code TEXT,
            customer_segment TEXT
        );
        """
    )
    rfm.to_sql("customer_segments", connection, if_exists="append", index=False)
    connection.commit()


def main() -> None:
    print("Starting Stage 3 RFM customer segmentation...")
    require_database()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        validate_sales_transactions_table(connection)

        print("Loading known-customer sales records from sales_transactions...")
        sales = load_customer_sales(connection)
        known_customer_revenue = round(float(sales["revenue"].sum()), 2)

        print("Calculating customer RFM metrics, scores, and segments...")
        rfm, snapshot_date = calculate_rfm(sales)

        print(f"Snapshot date used for recency: {snapshot_date}")
        print("Building segment summaries and recommendation table...")
        segment_summary = build_segment_summary(rfm)
        country_summary = build_country_summary(rfm)
        high_value_customers = rfm.sort_values("monetary", ascending=False).head(100)
        at_risk_customers = rfm[
            rfm["customer_segment"].isin(["At Risk", "Cannot Lose Them"])
        ].sort_values("monetary", ascending=False)
        segment_recommendations = build_segment_recommendations()

        print("Saving customer segmentation CSV outputs...")
        rfm.to_csv(RFM_OUTPUT_PATH, index=False)
        segment_summary.to_csv(SEGMENT_SUMMARY_PATH, index=False)
        country_summary.to_csv(COUNTRY_SUMMARY_PATH, index=False)
        high_value_customers[
            [
                "customer_id",
                "main_country",
                "frequency",
                "monetary",
                "average_order_value",
                "recency_days",
                "customer_segment",
            ]
        ].to_csv(HIGH_VALUE_PATH, index=False)
        at_risk_customers[
            [
                "customer_id",
                "main_country",
                "frequency",
                "monetary",
                "average_order_value",
                "recency_days",
                "customer_segment",
            ]
        ].to_csv(AT_RISK_PATH, index=False)
        segment_recommendations.to_csv(RECOMMENDATIONS_PATH, index=False)

        print("Creating or replacing customer_segments table in SQLite...")
        create_customer_segments_table(connection, rfm)

        table_row_count = connection.execute(
            "SELECT COUNT(*) FROM customer_segments"
        ).fetchone()[0]

    output_files = [
        RFM_OUTPUT_PATH,
        SEGMENT_SUMMARY_PATH,
        COUNTRY_SUMMARY_PATH,
        HIGH_VALUE_PATH,
        AT_RISK_PATH,
        RECOMMENDATIONS_PATH,
    ]
    rfm_monetary_total = round(float(rfm["monetary"].sum()), 2)
    revenue_difference = round(rfm_monetary_total - known_customer_revenue, 2)
    top_segment_by_revenue = segment_summary.sort_values(
        "total_revenue", ascending=False
    ).iloc[0]
    largest_segment = segment_summary.sort_values(
        "customer_count", ascending=False
    ).iloc[0]

    if rfm["customer_id"].duplicated().any():
        raise ValueError("A customer appears more than once in the final RFM output.")
    if rfm["customer_segment"].isna().any():
        raise ValueError("Some customers are missing customer_segment values.")

    print("\nFinal RFM validation")
    print(f"Number of customers segmented: {len(rfm):,}")
    print(f"Number of unique segments: {rfm['customer_segment'].nunique():,}")
    print(f"Total monetary value in RFM: {rfm_monetary_total:,.2f}")
    print(f"Known-customer sales revenue from sales_transactions: {known_customer_revenue:,.2f}")
    print(f"Difference between RFM monetary and known-customer sales revenue: {revenue_difference:,.2f}")
    print(f"Top segment by revenue: {top_segment_by_revenue['customer_segment']}")
    print(f"Largest segment by customer count: {largest_segment['customer_segment']}")
    print(f"Number of files created: {sum(path.exists() for path in output_files)}")
    print(f"customer_segments table row count: {table_row_count:,}")
    print("Stage 3 RFM customer segmentation completed.")


if __name__ == "__main__":
    main()
