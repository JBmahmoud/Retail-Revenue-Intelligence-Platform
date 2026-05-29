# Power BI Data Model Guide

## Tables To Import

Import every CSV from `dashboard/data/`:

- `dashboard_kpi_summary.csv`
- `dashboard_monthly_sales.csv`
- `dashboard_weekly_revenue.csv`
- `dashboard_country_performance.csv`
- `dashboard_product_performance.csv`
- `dashboard_customer_segments.csv`
- `dashboard_segment_summary.csv`
- `dashboard_forecast_summary.csv`
- `dashboard_weekly_actual_vs_forecast.csv`
- `dashboard_forecast_model_comparison.csv`
- `dashboard_future_weekly_forecast.csv`
- `dashboard_future_monthly_forecast.csv`

## Recommended Table Roles

Fact-like tables:

- `dashboard_monthly_sales`
- `dashboard_weekly_revenue`
- `dashboard_weekly_actual_vs_forecast`
- `dashboard_future_weekly_forecast`
- `dashboard_future_monthly_forecast`
- `dashboard_customer_segments`

Dimension-like or summary tables:

- `dashboard_kpi_summary`
- `dashboard_country_performance`
- `dashboard_product_performance`
- `dashboard_segment_summary`
- `dashboard_forecast_summary`
- `dashboard_forecast_model_comparison`

## Date Fields

Use these date fields for sorting and chart axes:

- `dashboard_monthly_sales[invoice_year_month]`
- `dashboard_weekly_revenue[week_start_date]`
- `dashboard_weekly_actual_vs_forecast[week_start_date]`
- `dashboard_future_weekly_forecast[week_start_date]`
- `dashboard_future_monthly_forecast[forecast_month]`

In Power BI, set `week_start_date` to Date type. Keep `invoice_year_month` and `forecast_month` as text if you want simple month labels, or create date columns manually for more advanced time intelligence.

## Recommended Relationships

Keep the model simple because most dashboard tables are already aggregated.

Recommended relationships:

- `dashboard_segment_summary[customer_segment]` one-to-many to `dashboard_customer_segments[customer_segment]`
- `dashboard_country_performance[country]` one-to-many to `dashboard_customer_segments[main_country]`

Use single-direction filtering from summary tables to detail tables. Avoid connecting every summary table together, because that can create ambiguous filters and misleading totals.

## Recommended Slicers

- Country: `dashboard_country_performance[country]`
- Customer segment: `dashboard_segment_summary[customer_segment]`
- Month: `dashboard_monthly_sales[invoice_year_month]`
- Product: `dashboard_product_performance[description]` or `dashboard_product_performance[stock_code]`
- Forecast model: `dashboard_future_weekly_forecast[model_used]`
- Forecast comparison model: use `dashboard_forecast_model_comparison[model_name]` in tables or filters when needed

## Cross-Filtering Guidance

- Executive Overview should use KPI summary cards and broad trend visuals.
- Sales Performance should use country, month, and product slicers.
- Customer Segmentation should focus on segment filters and customer tables.
- Product & Country Performance should keep product and country visuals mostly independent.
- Forecasting should avoid over-filtering; it should explain future direction and limitations clearly.
