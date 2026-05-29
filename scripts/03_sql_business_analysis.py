"""
Stage 2: Run SQL business analysis queries and export dashboard-ready CSVs.

Run from the project root:
    python scripts/03_sql_business_analysis.py
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "retail_analytics.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "sql_outputs"


def require_database() -> None:
    """Stop with a clear error if the Stage 2 database does not exist."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Required database is missing. Run "
            "python scripts/02_build_sql_database.py first."
        )


def read_single_value(connection: sqlite3.Connection, query: str):
    """Run a one-value SQL query and return the scalar result."""
    return connection.execute(query).fetchone()[0]


def export_query(
    connection: sqlite3.Connection,
    file_name: str,
    query: str,
) -> pd.DataFrame:
    """Run a SQL query and save the result as a CSV file."""
    output_path = OUTPUT_DIR / file_name
    result = pd.read_sql_query(query, connection)
    result.to_csv(output_path, index=False)
    print(f"Created {output_path.relative_to(PROJECT_ROOT)}")
    return result


def main() -> None:
    print("Starting Stage 2 SQL business analysis...")
    require_database()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    existing_outputs = list(OUTPUT_DIR.glob("*.csv"))
    if existing_outputs:
        print("Warning: existing SQL output CSV files will be replaced.")
        for output_file in existing_outputs:
            output_file.unlink()

    with sqlite3.connect(DATABASE_PATH) as connection:
        total_revenue = round(
            float(read_single_value(connection, "SELECT SUM(revenue) FROM sales_transactions")),
            2,
        )
        total_orders = int(
            read_single_value(
                connection, "SELECT COUNT(DISTINCT invoice_no) FROM sales_transactions"
            )
        )
        total_customers = int(
            read_single_value(
                connection,
                "SELECT COUNT(DISTINCT customer_id) "
                "FROM sales_transactions WHERE customer_id IS NOT NULL",
            )
        )
        average_order_value = round(total_revenue / total_orders, 2)
        repeat_customer_rate = round(
            float(
                read_single_value(
                    connection,
                    """
                    SELECT
                        1.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END)
                        / NULLIF(COUNT(*), 0)
                    FROM customers
                    """,
                )
            ),
            4,
        )
        cancellation_count = int(
            read_single_value(
                connection, "SELECT COUNT(*) FROM transactions WHERE is_cancelled = 1"
            )
        )
        cancellation_rate = round(
            float(
                read_single_value(
                    connection,
                    """
                    SELECT
                        1.0 * SUM(CASE WHEN is_cancelled = 1 THEN 1 ELSE 0 END)
                        / NULLIF(COUNT(*), 0)
                    FROM transactions
                    """,
                )
            ),
            4,
        )
        estimated_revenue_lost = round(
            float(
                read_single_value(
                    connection,
                    """
                    SELECT ABS(SUM(revenue))
                    FROM transactions
                    WHERE is_cancelled = 1
                    """,
                )
            ),
            2,
        )
        best_revenue_month = pd.read_sql_query(
            """
            SELECT invoice_year_month, total_revenue
            FROM monthly_sales
            ORDER BY total_revenue DESC
            LIMIT 1
            """,
            connection,
        )
        worst_revenue_month = pd.read_sql_query(
            """
            SELECT invoice_year_month, total_revenue
            FROM monthly_sales
            ORDER BY total_revenue ASC
            LIMIT 1
            """,
            connection,
        )

        kpi_summary = pd.DataFrame(
            [
                ("total_revenue", total_revenue),
                ("total_orders", total_orders),
                ("total_customers", total_customers),
                ("average_order_value", average_order_value),
                ("repeat_customer_rate", repeat_customer_rate),
                ("best_revenue_month", best_revenue_month.loc[0, "invoice_year_month"]),
                (
                    "best_revenue_month_revenue",
                    round(float(best_revenue_month.loc[0, "total_revenue"]), 2),
                ),
                ("worst_revenue_month", worst_revenue_month.loc[0, "invoice_year_month"]),
                (
                    "worst_revenue_month_revenue",
                    round(float(worst_revenue_month.loc[0, "total_revenue"]), 2),
                ),
                ("cancellation_count", cancellation_count),
                ("cancellation_rate", cancellation_rate),
                ("estimated_revenue_lost_from_cancellations_returns", estimated_revenue_lost),
            ],
            columns=["metric", "value"],
        )
        kpi_summary.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)
        print(f"Created {(OUTPUT_DIR / 'kpi_summary.csv').relative_to(PROJECT_ROOT)}")

        export_query(
            connection,
            "monthly_revenue.csv",
            """
            SELECT
                invoice_year_month,
                ROUND(total_revenue, 2) AS total_revenue,
                total_orders,
                total_quantity_sold,
                total_customers,
                ROUND(average_order_value, 2) AS average_order_value
            FROM vw_monthly_revenue
            ORDER BY invoice_year_month
            """,
        )
        export_query(
            connection,
            "country_performance.csv",
            """
            SELECT
                country,
                ROUND(total_revenue, 2) AS total_revenue,
                total_orders,
                total_customers,
                total_quantity_sold,
                ROUND(average_order_value, 2) AS average_order_value
            FROM vw_country_performance
            ORDER BY total_revenue DESC
            """,
        )
        export_query(
            connection,
            "product_performance.csv",
            """
            SELECT
                stock_code,
                description,
                total_quantity_sold,
                ROUND(total_revenue, 2) AS total_revenue,
                number_of_orders,
                number_of_customers,
                ROUND(average_unit_price, 2) AS average_unit_price
            FROM vw_product_performance
            ORDER BY total_revenue DESC
            """,
        )
        export_query(
            connection,
            "customer_performance.csv",
            """
            SELECT
                customer_id,
                first_purchase_date,
                last_purchase_date,
                total_orders,
                total_quantity,
                ROUND(total_revenue, 2) AS total_revenue,
                ROUND(average_order_value, 2) AS average_order_value,
                country_count,
                main_country
            FROM vw_customer_performance
            ORDER BY total_revenue DESC
            """,
        )
        export_query(
            connection,
            "cancellation_analysis.csv",
            """
            SELECT
                invoice_year_month,
                country,
                cancellation_return_count,
                ROUND(estimated_revenue_lost, 2) AS estimated_revenue_lost
            FROM vw_cancellation_analysis
            ORDER BY invoice_year_month, estimated_revenue_lost DESC
            """,
        )
        export_query(
            connection,
            "top_10_products.csv",
            """
            SELECT
                stock_code,
                description,
                total_quantity_sold,
                ROUND(total_revenue, 2) AS total_revenue,
                number_of_orders,
                number_of_customers,
                ROUND(average_unit_price, 2) AS average_unit_price
            FROM products
            ORDER BY total_revenue DESC
            LIMIT 10
            """,
        )
        export_query(
            connection,
            "top_10_customers.csv",
            """
            SELECT
                customer_id,
                first_purchase_date,
                last_purchase_date,
                total_orders,
                total_quantity,
                ROUND(total_revenue, 2) AS total_revenue,
                ROUND(average_order_value, 2) AS average_order_value,
                main_country
            FROM customers
            ORDER BY total_revenue DESC
            LIMIT 10
            """,
        )
        export_query(
            connection,
            "top_10_countries.csv",
            """
            SELECT
                country,
                ROUND(total_revenue, 2) AS total_revenue,
                total_orders,
                total_customers,
                total_quantity_sold,
                ROUND(average_order_value, 2) AS average_order_value
            FROM countries
            ORDER BY total_revenue DESC
            LIMIT 10
            """,
        )

    created_csv_count = len(list(OUTPUT_DIR.glob("*.csv")))

    print("\nFinal SQL analysis validation")
    print(f"Number of SQL output CSV files created: {created_csv_count}")
    print(f"Total revenue: {total_revenue:,.2f}")
    print(f"Total orders: {total_orders:,}")
    print(f"Total customers: {total_customers:,}")
    print(f"Average order value: {average_order_value:,.2f}")
    print(f"Cancellation count: {cancellation_count:,}")
    print(f"Cancellation rate: {cancellation_rate:.4f}")
    print("Stage 2 SQL business analysis completed.")


if __name__ == "__main__":
    main()
