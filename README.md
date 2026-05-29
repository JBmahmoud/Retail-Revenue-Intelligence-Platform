# Retail Revenue Intelligence Platform

## Business Objective

This project is a professional business analytics portfolio project built around the Online Retail transactional dataset. The goal is to transform raw retail transaction data into a complete business intelligence pipeline for data cleaning, SQL analysis, customer segmentation, revenue forecasting, Power BI dashboarding, and executive business recommendations.

The project is designed for Data Analyst, BI Analyst, Business Analyst, and entry-level Data Science portfolio use.

## Project Status

Completed stages:

1. Stage 1: Data Cleaning
2. Stage 2: SQL Database and Business Analysis
3. Stage 3: RFM Customer Segmentation
4. Stage 4: Revenue Forecasting
5. Stage 5: Power BI Dashboard
6. Stage 6: Executive Case Study / Final Report

Final project status:

```text
Complete
```

## Key Results Snapshot

| Metric | Value |
|---|---:|
| Total revenue | 10,642,110.80 |
| Total orders | 19,960 |
| Customers segmented | 4,338 |
| Top segment by revenue | Champions |
| Best forecast model | 4-Week Moving Average |
| Forecast direction | Increasing |

## Dataset

The project uses the Online Retail transactional dataset stored in:

```text
data/raw/
```

The cleaning workflow supports one raw file in `.xlsx`, `.xls`, or `.csv` format. Expected fields include invoice, product, quantity, date, price, customer, and country information.

## Key Business Results

| Metric | Value |
|---|---:|
| Total sales revenue | 10,642,110.80 |
| Total orders | 19,960 |
| Total customers | 4,338 |
| Average order value | 533.17 |
| Repeat customer rate | 65.58% |
| Cancellation count | 10,587 |
| Cancellation rate | 1.97% |
| Estimated revenue lost from cancellations/returns | 893,979.73 |
| Best revenue month | 2011-11 |
| Worst revenue month | 2011-02 |

## Key Customer Segmentation Results

| Segment Insight | Value |
|---|---:|
| Customers segmented | 4,338 |
| Unique customer segments | 11 |
| Known-customer RFM monetary value | 8,887,208.89 |
| Top revenue segment | Champions |
| Champion segment revenue | 5,713,136.80 |
| Largest segment by customer count | Hibernating |
| Hibernating customers | 997 |

## Key Forecasting Results

| Forecasting Metric | Value |
|---|---:|
| Weekly periods used | 53 |
| Monthly periods used | 13 |
| Best forecasting model | 4-Week Moving Average |
| Next 8 weeks forecast total | 3,172,808.88 |
| Next 3 months forecast total | 5,212,432.39 |
| Forecast direction | Increasing |

Monthly forecasts are treated as directional business estimates because the dataset contains only about 13 monthly observations.

## Project Pipeline

```text
Raw Retail Dataset
        |
        v
Stage 1: Data Cleaning
        |
        v
Stage 2: SQLite Database + SQL Business Analysis
        |
        v
Stage 3: RFM Customer Segmentation
        |
        v
Stage 4: Revenue Forecasting
        |
        v
Stage 5: Power BI Dashboard
        |
        v
Stage 6: Executive Case Study / Final Report
```

## Folder Structure

```text
Retail-Revenue-Intelligence-Platform/
|-- data/
|   |-- raw/
|   |-- processed/
|   |   |-- sql_outputs/
|   |   |-- customer_segments/
|   |   |-- forecasting/
|   |   |-- dashboard_ready/
|-- database/
|-- notebooks/
|-- scripts/
|-- sql/
|-- dashboard/
|   |-- data/
|   |-- powerbi/
|   |-- dashboard_screenshots/
|   |-- Retail_Revenue_Intelligence_Dashboard.pbix
|-- reports/
|-- visuals/
|-- README.md
|-- requirements.txt
```

## How To Run The Project

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the stages from the project root in this order:

```bash
python scripts/01_data_cleaning.py
python scripts/02_build_sql_database.py
python scripts/03_sql_business_analysis.py
python scripts/04_customer_segmentation.py
python scripts/05_revenue_forecasting.py
python scripts/06_prepare_dashboard_data.py
python scripts/07_generate_final_reports.py
```

The Power BI dashboard is built manually in Power BI Desktop after the dashboard-ready CSV files are prepared.

## Stage 1: Data Cleaning

Stage 1 prepares the raw retail dataset for analysis.

This stage focuses on:

- loading the raw retail dataset
- inspecting file structure, shape, columns, and data types
- standardizing column names
- preserving identifiers correctly
- flagging cancelled, returned, invalid, and missing-customer transactions
- creating date and revenue features
- saving cleaned datasets for later analysis

Cancelled, returned, and missing-customer rows are kept in the main cleaned dataset because they are useful for business analysis.

Run Stage 1:

```bash
python scripts/01_data_cleaning.py
```

Stage 1 generated files:

```text
data/processed/clean_retail_transactions.csv
data/processed/sales_transactions_only.csv
data/processed/data_cleaning_summary.csv
```

### `clean_retail_transactions.csv`

Contains standardized retail transactions. It keeps cancelled invoices, return rows, and missing customer IDs, while clearly flagging them for later business analysis.

### `sales_transactions_only.csv`

Contains only valid positive sales transactions suitable for clean revenue analysis. It excludes cancelled invoices, non-positive quantities, non-positive prices, and transactions missing required business fields.

### `data_cleaning_summary.csv`

Contains key cleaning metrics, including row counts, duplicate removal, cancellation counts, missing customer IDs, total sales-only revenue, unique countries, unique customers, unique products, and invoice date range.

## Stage 2: SQL Database And Business Analysis

Stage 2 builds a SQLite analytics layer from the cleaned Stage 1 datasets.

The database contains:

- `transactions`: full cleaned transaction data, including cancelled, returned, and missing-customer rows
- `sales_transactions`: valid positive sales transactions only
- `customers`: known customer-level sales performance
- `products`: product-level sales performance
- `countries`: country-level sales performance
- `monthly_sales`: monthly revenue trends for dashboarding and forecasting preparation

Database location:

```text
database/retail_analytics.db
```

Run Stage 2:

```bash
python scripts/02_build_sql_database.py
python scripts/03_sql_business_analysis.py
```

SQL files created:

```text
sql/create_tables.sql
sql/views.sql
sql/business_queries.sql
```

Stage 2 SQL analysis outputs:

```text
data/processed/sql_outputs/kpi_summary.csv
data/processed/sql_outputs/monthly_revenue.csv
data/processed/sql_outputs/country_performance.csv
data/processed/sql_outputs/product_performance.csv
data/processed/sql_outputs/customer_performance.csv
data/processed/sql_outputs/cancellation_analysis.csv
data/processed/sql_outputs/top_10_products.csv
data/processed/sql_outputs/top_10_customers.csv
data/processed/sql_outputs/top_10_countries.csv
```

Business questions answered include total revenue, total orders, total customers, average order value, monthly revenue trend, best and worst revenue months, top countries, top products, top customers, repeat customer rate, cancellation count, cancellation rate, estimated revenue lost from cancellations and returns, products with the highest cancellation or return count, and countries with the highest average order value.

## Stage 3: RFM Customer Segmentation

Stage 3 builds a customer segmentation layer using RFM analysis.

RFM means:

- `Recency`: how recently a customer purchased
- `Frequency`: how often a customer purchased
- `Monetary`: how much revenue a customer generated

The RFM workflow uses only `sales_transactions` from the SQLite database and excludes rows with missing `customer_id`, because customer segmentation requires a known customer identity. This means the total RFM monetary value reconciles to known-customer sales revenue, not total sales revenue across all rows.

Run Stage 3:

```bash
python scripts/04_customer_segmentation.py
```

Stage 3 SQL reference file:

```text
sql/rfm_queries.sql
```

Stage 3 customer segmentation outputs:

```text
data/processed/customer_segments/rfm_customer_segments.csv
data/processed/customer_segments/rfm_segment_summary.csv
data/processed/customer_segments/rfm_country_summary.csv
data/processed/customer_segments/high_value_customers.csv
data/processed/customer_segments/at_risk_customers.csv
data/processed/customer_segments/segment_recommendations.csv
```

The database is also updated with:

```text
customer_segments
```

This table contains one row per known customer, including RFM metrics, RFM scores, RFM code, and a business-friendly customer segment.

Business questions answered include which customers are champions, which customers are at risk, which segments generate the most revenue, which segments are largest by customer count, which countries contain each segment, which customers are highest value, and which valuable customers need win-back campaigns.

## Stage 4: Revenue Forecasting

Stage 4 builds a revenue forecasting layer using valid positive sales from `sales_transactions`.

The goal is to compare simple, explainable forecasting models and create dashboard-ready forecast outputs. Forecasting uses weekly revenue for model evaluation because the dataset has 53 weekly observations. Monthly revenue is still included for executive trend reporting, but the project has only about 13 monthly observations, so monthly forecasts should be treated as directional business estimates rather than strong statistical predictions.

Run Stage 4:

```bash
python scripts/05_revenue_forecasting.py
```

Stage 4 SQL reference file:

```text
sql/forecasting_queries.sql
```

Stage 4 forecasting outputs:

```text
data/processed/forecasting/weekly_revenue.csv
data/processed/forecasting/monthly_revenue_for_forecasting.csv
data/processed/forecasting/forecast_model_comparison.csv
data/processed/forecasting/weekly_actual_vs_forecast.csv
data/processed/forecasting/future_weekly_forecast.csv
data/processed/forecasting/future_monthly_forecast.csv
data/processed/forecasting/forecast_business_summary.csv
data/processed/forecasting/forecast_recommendations.csv
```

The database is also updated with these forecasting tables:

```text
weekly_revenue
revenue_forecasts
forecast_model_comparison
```

Business questions answered include weekly revenue trends, monthly revenue trends, best and worst revenue weeks, model performance comparison, expected revenue for the next 8 weeks, directional revenue estimate for the next 3 months, and whether the near-term revenue signal is increasing, decreasing, or stable.

## Stage 5: Power BI Dashboard

Stage 5 prepares and builds the Power BI dashboard layer.

The dashboard-ready data package is created by running:

```bash
python scripts/06_prepare_dashboard_data.py
```

Stage 5 creates these dashboard-ready CSV files:

```text
dashboard/data/dashboard_kpi_summary.csv
dashboard/data/dashboard_monthly_sales.csv
dashboard/data/dashboard_weekly_revenue.csv
dashboard/data/dashboard_country_performance.csv
dashboard/data/dashboard_product_performance.csv
dashboard/data/dashboard_customer_segments.csv
dashboard/data/dashboard_segment_summary.csv
dashboard/data/dashboard_forecast_summary.csv
dashboard/data/dashboard_weekly_actual_vs_forecast.csv
dashboard/data/dashboard_forecast_model_comparison.csv
dashboard/data/dashboard_future_weekly_forecast.csv
dashboard/data/dashboard_future_monthly_forecast.csv
```

Stage 5 also creates this data dictionary:

```text
data/processed/dashboard_ready/dashboard_data_dictionary.csv
```

Power BI documentation files:

```text
dashboard/powerbi/powerbi_dashboard_build_guide.md
dashboard/powerbi/powerbi_dax_measures.md
dashboard/powerbi/powerbi_data_model.md
dashboard/powerbi/powerbi_theme.json
dashboard/powerbi/dashboard_page_specification.md
```

The final Power BI file was built manually in Power BI Desktop and saved as:

```text
dashboard/Retail_Revenue_Intelligence_Dashboard.pbix
```

Dashboard screenshots are saved in:

```text
dashboard/dashboard_screenshots/
```

### Completed Power BI Visuals

The current Power BI dashboard includes these visuals:

1. Monthly Revenue Trend
2. Top Countries by Revenue
3. Top Products by Revenue
4. KPI Summary Cards
5. Weekly Revenue Trend
6. Customer Count by Segment
7. Revenue by Segment
8. Average Order Value by Country
9. Top Products by Quantity Sold
10. High-Value Customers Table
11. At-Risk Customers Table
12. Actual vs Forecast Weekly Revenue
13. Future Weekly Forecast
14. Future Monthly Forecast
15. Forecast Model Comparison Table

### Power BI Dashboard Screenshots

Dashboard screenshots are available in `dashboard/dashboard_screenshots/`:

- `1. Sum of total revenue by Month.png`
- `2. Top Countries by Revenue.png`
- `3. Top Products.png`
- `4. KPI Summary.png`
- `5. Weekly Revenue.png`
- `6. Customer Segments.png`
- `7. Revenue by segment.png`
- `8. Average Order By Country.png`
- `9. Product Quantity.png`
- `10. High Value Customers.png`
- `11. At Risk Customers.png`
- `12. Actual vs Forecast.png`
- `13. Future Weekly Forecast.png`
- `14. Future Monthly Forecast.png`
- `15. Forecast Models.png`

### Future Dashboard Improvement

The current dashboard was built with separate visual pages to make validation easier while learning Power BI. A future improvement is to reorganize these visuals into a polished five-page executive dashboard:

1. Executive Overview
2. Sales Performance
3. Customer Segmentation
4. Product & Country Performance
5. Forecasting & Business Recommendations

## Stage 6: Executive Case Study / Final Report

Stage 6 creates the final recruiter-ready portfolio documentation for the project.

Run Stage 6:

```bash
python scripts/07_generate_final_reports.py
```

Stage 6 report outputs:

```text
reports/executive_case_study.md
reports/final_project_report.md
reports/business_recommendations.md
reports/project_summary_for_cv.md
reports/linkedin_project_post.md
reports/interview_talking_points.md
reports/report_assets.md
```

These files make the project easier to review in a portfolio, discuss in interviews, summarize on a CV, and share professionally on LinkedIn.

## Business Questions Answered

This project answers the following business questions:

- How much revenue did the business generate?
- Which months and weeks performed best?
- Which countries generate the most revenue?
- Which products generate the most revenue and quantity sold?
- Which customers are most valuable?
- Which customers are at risk?
- Which customer segments drive the most revenue?
- What revenue should management expect in the short term?
- Which forecasting model performed best?
- What actions should management take based on customer and revenue behavior?

## Tools Used

- Python
- Pandas
- NumPy
- SQLite
- SQL
- Power BI Desktop
- Power BI DAX
- Markdown

## Final Project Status

This portfolio project is complete. It includes data cleaning, SQL analysis, customer segmentation, revenue forecasting, a Power BI dashboard, and executive documentation.
