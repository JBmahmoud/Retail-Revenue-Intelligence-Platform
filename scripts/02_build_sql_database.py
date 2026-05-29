"""
Stage 2: Build the SQLite analytics database.

Run from the project root:
    python scripts/02_build_sql_database.py
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
SQL_DIR = PROJECT_ROOT / "sql"

CLEAN_TRANSACTIONS_PATH = DATA_DIR / "clean_retail_transactions.csv"
SALES_TRANSACTIONS_PATH = DATA_DIR / "sales_transactions_only.csv"
DATABASE_PATH = DATABASE_DIR / "retail_analytics.db"
CREATE_TABLES_SQL_PATH = SQL_DIR / "create_tables.sql"
VIEWS_SQL_PATH = SQL_DIR / "views.sql"

BASE_TRANSACTION_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "invoice_date_only",
    "invoice_year",
    "invoice_month",
    "invoice_month_name",
    "invoice_day_name",
    "invoice_hour",
    "invoice_year_month",
    "revenue",
    "is_cancelled",
    "has_customer_id",
    "is_invalid_transaction",
]


def require_file(path: Path) -> None:
    """Stop with a clear error if a required file is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required file is missing: {path.relative_to(PROJECT_ROOT)}")


def read_transactions_csv(path: Path) -> pd.DataFrame:
    """Read transaction CSVs while preserving ID columns as strings."""
    df = pd.read_csv(
        path,
        dtype={
            "invoice_no": "string",
            "stock_code": "string",
            "customer_id": "string",
        },
        low_memory=False,
    )

    missing_columns = [column for column in BASE_TRANSACTION_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"{path.name} is missing required columns: {missing_columns}")

    return df[BASE_TRANSACTION_COLUMNS].copy()


def prepare_transaction_table(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Add a primary key column and convert booleans to SQLite-friendly integers."""
    prepared = df.copy()
    prepared.insert(0, id_column, range(1, len(prepared) + 1))

    for flag_column in ["is_cancelled", "has_customer_id", "is_invalid_transaction"]:
        prepared[flag_column] = (
            prepared[flag_column]
            .astype("string")
            .str.lower()
            .map({"true": 1, "false": 0, "1": 1, "0": 0})
            .fillna(0)
            .astype(int)
        )

    return prepared


def build_customers_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per known customer using valid sales transactions only."""
    known_sales = sales_df[sales_df["customer_id"].notna()].copy()
    known_sales["invoice_date"] = pd.to_datetime(known_sales["invoice_date"], errors="coerce")

    customer_summary = (
        known_sales.groupby("customer_id", as_index=False)
        .agg(
            first_purchase_date=("invoice_date", "min"),
            last_purchase_date=("invoice_date", "max"),
            total_orders=("invoice_no", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            country_count=("country", "nunique"),
        )
    )

    customer_summary["average_order_value"] = (
        customer_summary["total_revenue"] / customer_summary["total_orders"]
    ).round(2)

    country_rank = (
        known_sales.groupby(["customer_id", "country"], as_index=False)
        .agg(country_revenue=("revenue", "sum"), country_orders=("invoice_no", "nunique"))
        .sort_values(
            ["customer_id", "country_revenue", "country_orders", "country"],
            ascending=[True, False, False, True],
        )
    )
    main_country = country_rank.drop_duplicates("customer_id")[["customer_id", "country"]]
    main_country = main_country.rename(columns={"country": "main_country"})

    customer_summary = customer_summary.merge(main_country, on="customer_id", how="left")
    customer_summary["first_purchase_date"] = customer_summary["first_purchase_date"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    customer_summary["last_purchase_date"] = customer_summary["last_purchase_date"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return customer_summary[
        [
            "customer_id",
            "first_purchase_date",
            "last_purchase_date",
            "total_orders",
            "total_quantity",
            "total_revenue",
            "average_order_value",
            "country_count",
            "main_country",
        ]
    ].sort_values("total_revenue", ascending=False)


def build_products_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per product using valid sales transactions only."""
    description_mode = (
        sales_df.dropna(subset=["description"])
        .groupby("stock_code")["description"]
        .agg(lambda values: values.mode().iloc[0] if not values.mode().empty else values.iloc[0])
        .reset_index()
    )

    products = (
        sales_df.groupby("stock_code", as_index=False)
        .agg(
            total_quantity_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            number_of_orders=("invoice_no", "nunique"),
            number_of_customers=("customer_id", "nunique"),
        )
        .merge(description_mode, on="stock_code", how="left")
    )
    products["average_unit_price"] = (
        products["total_revenue"] / products["total_quantity_sold"]
    ).round(2)

    return products[
        [
            "stock_code",
            "description",
            "total_quantity_sold",
            "total_revenue",
            "number_of_orders",
            "number_of_customers",
            "average_unit_price",
        ]
    ].sort_values("total_revenue", ascending=False)


def build_countries_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create country-level revenue and order metrics."""
    countries = (
        sales_df.groupby("country", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("invoice_no", "nunique"),
            total_customers=("customer_id", "nunique"),
            total_quantity_sold=("quantity", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    countries["average_order_value"] = (
        countries["total_revenue"] / countries["total_orders"]
    ).round(2)

    return countries[
        [
            "country",
            "total_revenue",
            "total_orders",
            "total_customers",
            "total_quantity_sold",
            "average_order_value",
        ]
    ]


def build_monthly_sales_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Create monthly sales trends for dashboarding and forecasting preparation."""
    monthly_sales = (
        sales_df.groupby("invoice_year_month", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("invoice_no", "nunique"),
            total_quantity_sold=("quantity", "sum"),
            total_customers=("customer_id", "nunique"),
        )
        .sort_values("invoice_year_month")
    )
    monthly_sales["average_order_value"] = (
        monthly_sales["total_revenue"] / monthly_sales["total_orders"]
    ).round(2)

    return monthly_sales[
        [
            "invoice_year_month",
            "total_revenue",
            "total_orders",
            "total_quantity_sold",
            "total_customers",
            "average_order_value",
        ]
    ]


def table_row_count(connection: sqlite3.Connection, table_name: str) -> int:
    """Return the row count for a SQLite table."""
    result = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return int(result[0])


def main() -> None:
    print("Starting Stage 2 SQLite database build...")

    for path in [
        CLEAN_TRANSACTIONS_PATH,
        SALES_TRANSACTIONS_PATH,
        CREATE_TABLES_SQL_PATH,
        VIEWS_SQL_PATH,
    ]:
        require_file(path)

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists():
        print(
            "Warning: existing database will be replaced: "
            f"{DATABASE_PATH.relative_to(PROJECT_ROOT)}"
        )
        DATABASE_PATH.unlink()

    print("Loading Stage 1 processed CSV files...")
    clean_df = read_transactions_csv(CLEAN_TRANSACTIONS_PATH)
    sales_df = read_transactions_csv(SALES_TRANSACTIONS_PATH)

    transactions = prepare_transaction_table(clean_df, "transaction_id")
    sales_transactions = prepare_transaction_table(sales_df, "sales_transaction_id")

    print("Building aggregate analytics tables...")
    customers = build_customers_table(sales_df)
    products = build_products_table(sales_df)
    countries = build_countries_table(sales_df)
    monthly_sales = build_monthly_sales_table(sales_df)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        print("Executing SQL table creation script...")
        connection.executescript(CREATE_TABLES_SQL_PATH.read_text(encoding="utf-8"))

        print("Inserting tables into SQLite using append mode...")
        transactions.to_sql("transactions", connection, if_exists="append", index=False)
        sales_transactions.to_sql(
            "sales_transactions", connection, if_exists="append", index=False
        )
        customers.to_sql("customers", connection, if_exists="append", index=False)
        products.to_sql("products", connection, if_exists="append", index=False)
        countries.to_sql("countries", connection, if_exists="append", index=False)
        monthly_sales.to_sql("monthly_sales", connection, if_exists="append", index=False)

        print("Executing SQL views script...")
        connection.executescript(VIEWS_SQL_PATH.read_text(encoding="utf-8"))
        connection.commit()

        table_names = [
            "transactions",
            "sales_transactions",
            "customers",
            "products",
            "countries",
            "monthly_sales",
        ]

        print("\nFinal database validation")
        for table_name in table_names:
            print(f"{table_name} row count: {table_row_count(connection, table_name):,}")

        total_sales_revenue = connection.execute(
            "SELECT ROUND(SUM(revenue), 2) FROM sales_transactions"
        ).fetchone()[0]
        print(f"Total revenue from sales_transactions: {total_sales_revenue:,.2f}")
        print(f"Database file path: {DATABASE_PATH.relative_to(PROJECT_ROOT)}")

    print("Stage 2 database build completed.")


if __name__ == "__main__":
    main()
