"""
Stage 5: Prepare dashboard-ready CSV files for Power BI.

Run from the project root:
    python scripts/06_prepare_dashboard_data.py
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SQL_OUTPUTS_DIR = PROJECT_ROOT / "data" / "processed" / "sql_outputs"
CUSTOMER_SEGMENTS_DIR = PROJECT_ROOT / "data" / "processed" / "customer_segments"
FORECASTING_DIR = PROJECT_ROOT / "data" / "processed" / "forecasting"

DASHBOARD_DATA_DIR = PROJECT_ROOT / "dashboard" / "data"
POWERBI_DIR = PROJECT_ROOT / "dashboard" / "powerbi"
DASHBOARD_READY_DIR = PROJECT_ROOT / "data" / "processed" / "dashboard_ready"
DATA_DICTIONARY_PATH = DASHBOARD_READY_DIR / "dashboard_data_dictionary.csv"


REQUIRED_INPUTS = {
    "Stage 2": [
        SQL_OUTPUTS_DIR / "kpi_summary.csv",
        SQL_OUTPUTS_DIR / "monthly_revenue.csv",
        SQL_OUTPUTS_DIR / "country_performance.csv",
        SQL_OUTPUTS_DIR / "product_performance.csv",
        SQL_OUTPUTS_DIR / "customer_performance.csv",
        SQL_OUTPUTS_DIR / "top_10_products.csv",
        SQL_OUTPUTS_DIR / "top_10_customers.csv",
        SQL_OUTPUTS_DIR / "top_10_countries.csv",
        SQL_OUTPUTS_DIR / "cancellation_analysis.csv",
    ],
    "Stage 3": [
        CUSTOMER_SEGMENTS_DIR / "rfm_customer_segments.csv",
        CUSTOMER_SEGMENTS_DIR / "rfm_segment_summary.csv",
        CUSTOMER_SEGMENTS_DIR / "rfm_country_summary.csv",
        CUSTOMER_SEGMENTS_DIR / "high_value_customers.csv",
        CUSTOMER_SEGMENTS_DIR / "at_risk_customers.csv",
        CUSTOMER_SEGMENTS_DIR / "segment_recommendations.csv",
    ],
    "Stage 4": [
        FORECASTING_DIR / "weekly_revenue.csv",
        FORECASTING_DIR / "monthly_revenue_for_forecasting.csv",
        FORECASTING_DIR / "forecast_model_comparison.csv",
        FORECASTING_DIR / "weekly_actual_vs_forecast.csv",
        FORECASTING_DIR / "future_weekly_forecast.csv",
        FORECASTING_DIR / "future_monthly_forecast.csv",
        FORECASTING_DIR / "forecast_business_summary.csv",
        FORECASTING_DIR / "forecast_recommendations.csv",
    ],
}


DATA_DICTIONARY_ROWS = [
    {
        "file_name": "dashboard_kpi_summary.csv",
        "source_stage": "Stage 2 SQL Business Analysis",
        "business_purpose": "Executive KPI cards for revenue, orders, customers, AOV, repeat rate, and cancellation rate.",
        "key_columns": "metric, value",
        "recommended_visuals": "KPI cards, compact executive summary table",
    },
    {
        "file_name": "dashboard_monthly_sales.csv",
        "source_stage": "Stage 2 SQL Business Analysis",
        "business_purpose": "Monthly sales trend for executive revenue performance tracking.",
        "key_columns": "invoice_year_month, total_revenue, total_orders, total_quantity_sold, total_customers, average_order_value",
        "recommended_visuals": "Line chart, column chart, AOV trend, monthly slicer",
    },
    {
        "file_name": "dashboard_weekly_revenue.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Weekly historical revenue used for trend and forecast context.",
        "key_columns": "week_start_date, total_revenue, total_orders, total_quantity, average_order_value",
        "recommended_visuals": "Weekly line chart, trend card, forecast comparison context",
    },
    {
        "file_name": "dashboard_country_performance.csv",
        "source_stage": "Stage 2 SQL Business Analysis",
        "business_purpose": "Country-level revenue, order, customer, quantity, and AOV performance.",
        "key_columns": "country, total_revenue, total_orders, total_customers, total_quantity_sold, average_order_value",
        "recommended_visuals": "Bar chart, map, ranking table, country slicer",
    },
    {
        "file_name": "dashboard_product_performance.csv",
        "source_stage": "Stage 2 SQL Business Analysis",
        "business_purpose": "Product-level revenue, quantity, customer, and unit price performance.",
        "key_columns": "stock_code, description, total_quantity_sold, total_revenue, number_of_orders, number_of_customers, average_unit_price",
        "recommended_visuals": "Top products bar chart, product performance table, quantity ranking",
    },
    {
        "file_name": "dashboard_customer_segments.csv",
        "source_stage": "Stage 3 RFM Customer Segmentation",
        "business_purpose": "Customer-level RFM metrics and segment assignment for customer behavior analysis.",
        "key_columns": "customer_id, recency_days, frequency, monetary, rfm_score, rfm_code, customer_segment, main_country",
        "recommended_visuals": "Segment slicer, customer table, high-value customer table, at-risk customer table",
    },
    {
        "file_name": "dashboard_segment_summary.csv",
        "source_stage": "Stage 3 RFM Customer Segmentation",
        "business_purpose": "Segment-level customer count, revenue share, behavior metrics, and business recommendations.",
        "key_columns": "customer_segment, customer_count, customer_percentage, total_revenue, revenue_percentage, business_meaning, recommended_action",
        "recommended_visuals": "Segment bar charts, recommendation cards, segment summary table",
    },
    {
        "file_name": "dashboard_forecast_summary.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Forecast KPI summary including best model, forecast totals, and direction signal.",
        "key_columns": "metric, value",
        "recommended_visuals": "Forecast KPI cards, model summary card, direction signal card",
    },
    {
        "file_name": "dashboard_weekly_actual_vs_forecast.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Actual vs forecast weekly revenue comparison for model evaluation and Page 5 trend visuals.",
        "key_columns": "week_start_date, actual_revenue, naive_forecast, moving_average_forecast, linear_trend_forecast",
        "recommended_visuals": "Actual vs forecast line chart, forecast accuracy review table",
    },
    {
        "file_name": "dashboard_forecast_model_comparison.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Forecast model performance comparison using MAE, RMSE, MAPE, and model notes.",
        "key_columns": "model_name, mae, rmse, mape, notes",
        "recommended_visuals": "Model comparison table, best model highlight card",
    },
    {
        "file_name": "dashboard_future_weekly_forecast.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Next 8 weeks of directional revenue forecasts.",
        "key_columns": "week_start_date, forecast_revenue, model_used",
        "recommended_visuals": "Future weekly forecast line chart, forecast table",
    },
    {
        "file_name": "dashboard_future_monthly_forecast.csv",
        "source_stage": "Stage 4 Revenue Forecasting",
        "business_purpose": "Next 3 months of directional executive revenue forecasts.",
        "key_columns": "forecast_month, forecast_revenue, model_used",
        "recommended_visuals": "Monthly forecast column chart, forecast KPI card",
    },
]


def validate_inputs() -> list[Path]:
    """Return missing required input files. The caller decides whether to stop."""
    missing_files = []
    for file_paths in REQUIRED_INPUTS.values():
        for file_path in file_paths:
            if not file_path.exists():
                missing_files.append(file_path)
    return missing_files


def read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file and keep the code easy to follow."""
    return pd.read_csv(path)


def save_dashboard_csv(df: pd.DataFrame, file_name: str) -> Path:
    """Save a dashboard-ready CSV file."""
    output_path = DASHBOARD_DATA_DIR / file_name
    df.to_csv(output_path, index=False)
    return output_path


def build_dashboard_outputs() -> list[Path]:
    """Create the 12 dashboard-ready CSV files from prior stage outputs."""
    created_files = []

    kpi_summary = read_csv(SQL_OUTPUTS_DIR / "kpi_summary.csv")
    created_files.append(save_dashboard_csv(kpi_summary[["metric", "value"]], "dashboard_kpi_summary.csv"))

    monthly_sales = read_csv(SQL_OUTPUTS_DIR / "monthly_revenue.csv")
    monthly_columns = [
        "invoice_year_month",
        "total_revenue",
        "total_orders",
        "total_quantity_sold",
        "total_customers",
        "average_order_value",
    ]
    created_files.append(save_dashboard_csv(monthly_sales[monthly_columns], "dashboard_monthly_sales.csv"))

    weekly_revenue = read_csv(FORECASTING_DIR / "weekly_revenue.csv")
    weekly_columns = [
        "week_start_date",
        "total_revenue",
        "total_orders",
        "total_quantity",
        "average_order_value",
    ]
    created_files.append(save_dashboard_csv(weekly_revenue[weekly_columns], "dashboard_weekly_revenue.csv"))

    country_performance = read_csv(SQL_OUTPUTS_DIR / "country_performance.csv")
    created_files.append(save_dashboard_csv(country_performance, "dashboard_country_performance.csv"))

    product_performance = read_csv(SQL_OUTPUTS_DIR / "product_performance.csv")
    created_files.append(save_dashboard_csv(product_performance, "dashboard_product_performance.csv"))

    customer_segments = read_csv(CUSTOMER_SEGMENTS_DIR / "rfm_customer_segments.csv")
    created_files.append(save_dashboard_csv(customer_segments, "dashboard_customer_segments.csv"))

    segment_summary = read_csv(CUSTOMER_SEGMENTS_DIR / "rfm_segment_summary.csv")
    segment_recommendations = read_csv(CUSTOMER_SEGMENTS_DIR / "segment_recommendations.csv")
    enriched_segment_summary = segment_summary.merge(
        segment_recommendations,
        on="customer_segment",
        how="left",
    )
    created_files.append(save_dashboard_csv(enriched_segment_summary, "dashboard_segment_summary.csv"))

    forecast_summary = read_csv(FORECASTING_DIR / "forecast_business_summary.csv")
    created_files.append(save_dashboard_csv(forecast_summary[["metric", "value"]], "dashboard_forecast_summary.csv"))

    weekly_actual_vs_forecast = read_csv(FORECASTING_DIR / "weekly_actual_vs_forecast.csv")
    created_files.append(
        save_dashboard_csv(
            weekly_actual_vs_forecast,
            "dashboard_weekly_actual_vs_forecast.csv",
        )
    )

    forecast_model_comparison = read_csv(FORECASTING_DIR / "forecast_model_comparison.csv")
    created_files.append(
        save_dashboard_csv(
            forecast_model_comparison,
            "dashboard_forecast_model_comparison.csv",
        )
    )

    future_weekly = read_csv(FORECASTING_DIR / "future_weekly_forecast.csv")
    created_files.append(save_dashboard_csv(future_weekly, "dashboard_future_weekly_forecast.csv"))

    future_monthly = read_csv(FORECASTING_DIR / "future_monthly_forecast.csv")
    created_files.append(save_dashboard_csv(future_monthly, "dashboard_future_monthly_forecast.csv"))

    return created_files


def build_data_dictionary() -> pd.DataFrame:
    """Create the dashboard data dictionary."""
    data_dictionary = pd.DataFrame(DATA_DICTIONARY_ROWS)
    data_dictionary.to_csv(DATA_DICTIONARY_PATH, index=False)
    return data_dictionary


def main() -> None:
    print("Starting Stage 5 Power BI dashboard data preparation...")

    missing_files = validate_inputs()
    if missing_files:
        print("Missing required input files:")
        for file_path in missing_files:
            print(f"- {file_path.relative_to(PROJECT_ROOT)}")
        raise FileNotFoundError("Stage 5 cannot continue until all required inputs exist.")

    print("All required Stage 2, Stage 3, and Stage 4 input files were found.")

    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_READY_DIR.mkdir(parents=True, exist_ok=True)

    for existing_dashboard_file in DASHBOARD_DATA_DIR.glob("dashboard_*.csv"):
        existing_dashboard_file.unlink()

    print("Creating dashboard-ready CSV files...")
    created_files = build_dashboard_outputs()

    print("Creating dashboard data dictionary...")
    data_dictionary = build_data_dictionary()

    print("\nFinal dashboard data validation")
    print(f"Number of dashboard CSV files created: {len(created_files)}")
    print("Files created:")
    for file_path in created_files:
        print(f"- {file_path.relative_to(PROJECT_ROOT)}")
    print(f"Data dictionary rows: {len(data_dictionary)}")
    print(f"Missing inputs: {len(missing_files)}")
    print("Next manual step: open Power BI Desktop and build dashboard/Retail_Revenue_Intelligence_Dashboard.pbix")
    print("Stage 5 dashboard data preparation completed.")


if __name__ == "__main__":
    main()
