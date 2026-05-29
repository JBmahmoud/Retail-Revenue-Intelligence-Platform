"""
Stage 6: Generate final portfolio report markdown files.

Run from the project root:
    python scripts/07_generate_final_reports.py
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = PROJECT_ROOT / "dashboard" / "dashboard_screenshots"

PROJECT_TITLE = (
    "Retail Revenue Intelligence Platform: SQL, BI Dashboard, "
    "Customer Segmentation & Sales Forecasting"
)


def write_report(file_name: str, content: str) -> Path:
    """Write one markdown report file."""
    path = REPORTS_DIR / file_name
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def screenshot_lines() -> str:
    """Create a markdown list of existing dashboard screenshots."""
    screenshot_files = sorted(SCREENSHOTS_DIR.glob("*.png"))
    if not screenshot_files:
        return (
            "Dashboard screenshots should be added to "
            "`dashboard/dashboard_screenshots/` after exporting from Power BI."
        )

    lines = []
    for screenshot in screenshot_files:
        lines.append(f"- `{screenshot.relative_to(PROJECT_ROOT)}`")
    return "\n".join(lines)


def build_reports() -> dict[str, str]:
    """Return report file names and their markdown content."""
    return {
        "executive_case_study.md": f"""
# {PROJECT_TITLE}

## Overview

This project analyzes online retail transaction data to understand revenue performance, customer behavior, product performance, country-level performance, cancellations and returns, customer segments, and future revenue direction. The work was built as a professional portfolio project for Data Analyst, BI Analyst, and Business Analyst internship roles.

## Business Problem

Retail leaders need a clear view of what drives revenue, which customers are most valuable, where risk exists, and what revenue direction to expect in the near term. Raw transaction data alone does not answer those questions without cleaning, SQL analysis, segmentation, forecasting, and dashboard reporting.

## Solution Approach

The project turns raw retail data into a complete analytics pipeline:

1. Clean and standardize transaction data.
2. Build a SQLite database and SQL business analysis layer.
3. Segment customers using RFM analysis.
4. Forecast short-term revenue using weekly revenue data.
5. Build a Power BI dashboard for management reporting.
6. Create executive documentation and business recommendations.

## Tools Used

- Python
- Pandas
- NumPy
- SQLite
- SQL
- Power BI Desktop
- DAX
- Markdown

## Pipeline Summary

| Stage | Output |
|---|---|
| Data Cleaning | Clean transaction and sales-only datasets |
| SQL Analysis | SQLite database and dashboard-ready SQL outputs |
| Customer Segmentation | RFM customer segments and segment recommendations |
| Forecasting | Weekly model comparison and future revenue estimates |
| Power BI Dashboard | Manual dashboard file and screenshots |
| Final Documentation | Executive case study, final report, recommendations, CV and interview assets |

## Key Results

| Metric | Value |
|---|---:|
| Cleaned transactions | 536,641 |
| Sales transactions | 524,878 |
| Total sales revenue | 10,642,110.80 |
| Total orders | 19,960 |
| Total customers | 4,338 |
| Average order value | 533.17 |
| Repeat customer rate | 0.6558 |
| Cancellation rate | 0.0197 |
| Estimated revenue lost from cancellations/returns | 893,979.73 |
| Best revenue month | 2011-11 |
| Worst revenue month | 2011-02 |

## Customer Segmentation Highlights

RFM segmentation identified 4,338 known customers across 11 segments. The Champions segment generated 5,713,136.80 in revenue from 918 customers, making it the highest-value segment. The largest segment by customer count was Hibernating, with 997 customers.

## Forecasting Highlights

The forecasting layer used 53 weekly periods for model evaluation. The 4-Week Moving Average model performed best, with MAE of 51,235.53, RMSE of 73,758.57, and MAPE of 12.78. The next 8 weeks forecast total was 3,172,808.88, and the forecast direction was Increasing.

## Dashboard Summary

The Power BI dashboard includes 15 completed visuals covering revenue trends, KPIs, country performance, product performance, customer segmentation, high-value customers, at-risk customers, actual vs forecast revenue, and future forecast views.

## Business Recommendations

- Retain and reward Champions with loyalty offers and early access.
- Prioritize At Risk and Cannot Lose Them customers for win-back campaigns.
- Monitor cancellations and returns because estimated revenue lost was 893,979.73.
- Prioritize high-revenue countries and best-selling products in commercial planning.
- Treat forecasts as directional and monitor weekly performance continuously.

## Limitations

- Monthly forecasting is limited because there are only 13 monthly observations.
- Forecasts are directional estimates, not guaranteed predictions.
- Missing customer IDs are retained for revenue analysis but excluded from RFM segmentation.
- The dashboard is based on available transactional history and does not include external market data.

## Future Improvements

- Add margin and cost data if available.
- Add marketing campaign and channel data.
- Build a more advanced forecast after collecting more history.
- Improve the Power BI dashboard layout into a polished five-page executive format.
- Add automated dashboard refresh and scheduled reporting.

## Conclusion

This project demonstrates an end-to-end analytics workflow from raw retail transactions to business-ready insights. It shows practical skills in Python, SQL, Power BI, customer analytics, forecasting, and executive communication.
""",
        "final_project_report.md": f"""
# Final Project Report

# {PROJECT_TITLE}

## Executive Summary

This project built a complete retail revenue intelligence platform using online retail transaction data. The final solution includes cleaned datasets, a SQLite analytics database, SQL business analysis outputs, RFM customer segmentation, revenue forecasting, dashboard-ready data, a Power BI dashboard, and executive documentation.

The project found total sales revenue of 10,642,110.80 across 19,960 orders and 4,338 known customers. The Champions customer segment was the top revenue segment, generating 5,713,136.80. The best forecasting model was a 4-Week Moving Average, and the near-term forecast direction was Increasing.

## Business Objective

The objective was to analyze retail transaction data to understand revenue performance, customer behavior, product performance, country-level performance, customer segments, cancellations and returns, and future revenue direction.

## Dataset Overview

The project uses an Online Retail transactional dataset with invoice, product, quantity, date, price, customer, and country fields. The cleaned transaction dataset contains 536,641 rows. The sales-only dataset contains 524,878 valid positive sales rows.

## Project Architecture / Pipeline

```text
Raw Retail Dataset
        |
        v
Data Cleaning
        |
        v
SQLite Database and SQL Analysis
        |
        v
RFM Customer Segmentation
        |
        v
Revenue Forecasting
        |
        v
Power BI Dashboard
        |
        v
Executive Case Study and Final Report
```

## Stage 1: Data Cleaning

Stage 1 cleaned and standardized the raw retail dataset.

Key outputs:

- Cleaned transactions: 536,641 rows
- Sales transactions: 524,878 rows
- Cancellations/returns kept in main dataset: 10,587
- Missing customer IDs kept in main dataset: 135,037
- Sales-only cancelled rows: 0
- Sales-only invalid rows: 0
- Sales-only revenue: 10,642,110.80

Business reasoning:

- Cancelled and returned transactions were retained in the main dataset because they are useful for cancellation and return analysis.
- Missing customer IDs were retained in the main dataset because they are still useful for revenue, product, and country analysis.
- A separate sales-only dataset was created for clean revenue analysis.

## Stage 2: SQL Database and Business Analysis

Stage 2 created a SQLite database at `database/retail_analytics.db`.

Database tables:

| Table | Rows |
|---|---:|
| transactions | 536,641 |
| sales_transactions | 524,878 |
| customers | 4,338 |
| products | 3,922 |
| countries | 38 |
| monthly_sales | 13 |

Main KPIs:

| Metric | Value |
|---|---:|
| Total sales revenue | 10,642,110.80 |
| Total orders | 19,960 |
| Total customers | 4,338 |
| Average order value | 533.17 |
| Repeat customer rate | 0.6558 |
| Cancellation count | 10,587 |
| Cancellation rate | 0.0197 |
| Estimated revenue lost from cancellations/returns | 893,979.73 |
| Best revenue month | 2011-11 |
| Worst revenue month | 2011-02 |

## Stage 3: RFM Customer Segmentation

Stage 3 segmented known customers using RFM analysis.

RFM results:

- Customers segmented: 4,338
- Unique segments: 11
- Total RFM monetary value: 8,887,208.89
- Known-customer SQL revenue: 8,887,208.89
- Difference: 0.00
- Top segment by revenue: Champions
- Largest segment by customer count: Hibernating

Customer count by segment:

| Segment | Customers |
|---|---:|
| Champions | 918 |
| Cannot Lose Them | 142 |
| At Risk | 256 |
| Loyal Customers | 363 |
| Potential Loyalists | 222 |
| New Customers | 187 |
| Promising Customers | 306 |
| Need Attention | 498 |
| Hibernating | 997 |
| Lost Customers | 121 |
| Low Value Customers | 328 |

Revenue by segment:

| Segment | Revenue |
|---|---:|
| Champions | 5,713,136.80 |
| Loyal Customers | 796,683.37 |
| At Risk | 531,580.22 |
| Need Attention | 479,561.14 |
| Cannot Lose Them | 333,942.08 |
| New Customers | 265,852.26 |
| Potential Loyalists | 247,184.81 |
| Hibernating | 241,799.35 |
| Promising Customers | 108,830.21 |
| Low Value Customers | 88,372.44 |
| Lost Customers | 80,266.21 |

## Stage 4: Revenue Forecasting

Stage 4 created a weekly revenue forecasting layer.

Forecasting setup:

- Weekly periods: 53
- Monthly periods: 13
- Train weeks: 45
- Test weeks: 8
- Best model: 4-Week Moving Average
- Next 8 weeks forecast total: 3,172,808.88
- Next 3 months forecast total: 5,212,432.39
- Forecast direction: Increasing

Model comparison:

| Model | MAE | RMSE | MAPE |
|---|---:|---:|---:|
| Naive Forecast | 56,618.44 | 76,697.82 | 15.24 |
| 4-Week Moving Average | 51,235.53 | 73,758.57 | 12.78 |
| Linear Trend Regression | 130,113.31 | 148,213.06 | 35.71 |
| Exponential Smoothing | skipped | skipped | skipped |

Important limitation:

Monthly forecasts are directional business estimates because the dataset has only 13 monthly observations.

## Stage 5: Power BI Dashboard

The final Power BI file is saved at:

```text
dashboard/Retail_Revenue_Intelligence_Dashboard.pbix
```

Screenshot folder:

```text
dashboard/dashboard_screenshots/
```

Completed visuals:

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

## Key Business Insights

- Revenue reached 10,642,110.80 across 19,960 orders.
- Champions are the most valuable segment and generated 5,713,136.80 in revenue.
- Hibernating is the largest segment by customer count, with 997 customers.
- Estimated revenue lost from cancellations and returns was 893,979.73.
- The 4-Week Moving Average produced the best forecast performance.
- Forecast direction was Increasing, but forecasts should be treated as directional estimates.

## Business Recommendations

- Retain Champions with loyalty offers and early access.
- Win back At Risk and Cannot Lose Them customers.
- Investigate products and countries linked to cancellations and returns.
- Prioritize high-revenue countries and best-selling products.
- Monitor weekly revenue forecasts and update plans as new data arrives.

## Limitations

- Monthly forecasting is limited by only 13 monthly observations.
- Forecasting does not include external market, seasonality, or promotion data.
- RFM excludes missing customer IDs because segmentation requires customer identity.
- The dataset does not include cost or margin data.

## Future Improvements

- Add gross margin and profitability analysis.
- Add marketing campaign data and acquisition channels.
- Improve dashboard layout into a polished five-page executive structure.
- Automate refresh and reporting.
- Rebuild forecasting after collecting more time history.

## Conclusion

The project demonstrates a complete analytics workflow from raw data to executive reporting. It is suitable for a Data Analyst, BI Analyst, or Business Analyst internship portfolio because it combines data cleaning, SQL, business KPIs, customer analytics, forecasting, dashboarding, and business communication.
""",
        "business_recommendations.md": """
# Business Recommendations

## 1. Retain And Reward Champions

Business issue:

Champions are the most valuable customer segment and should be protected from churn.

Evidence from analysis:

- Champions generated 5,713,136.80 in revenue.
- Champions included 918 customers.
- Champions were the top segment by revenue.

Recommended action:

Create loyalty offers, early product access, and premium customer communications for Champions.

Expected business value:

Protecting Champions supports revenue retention and strengthens long-term customer value.

## 2. Win Back At Risk And Cannot Lose Them Customers

Business issue:

Some valuable customers have not purchased recently and may be moving toward inactivity.

Evidence from analysis:

- At Risk customers generated 531,580.22 in revenue.
- Cannot Lose Them customers generated 333,942.08 in revenue.

Recommended action:

Run targeted win-back campaigns using personalized offers, reminders, and product recommendations.

Expected business value:

Winning back valuable inactive customers can recover revenue faster than acquiring entirely new customers.

## 3. Investigate Cancellations And Returns

Business issue:

Cancellations and returns reduce realized revenue and may signal product, fulfillment, or customer expectation issues.

Evidence from analysis:

- Cancellation count: 10,587.
- Cancellation rate: 0.0197.
- Estimated revenue lost from cancellations/returns: 893,979.73.

Recommended action:

Analyze cancellations and returns by product, country, and month to identify recurring problem areas.

Expected business value:

Reducing cancellations and returns can protect revenue and improve customer experience.

## 4. Prioritize High-Revenue Countries

Business issue:

Country-level performance varies, so commercial focus should be aligned with market value.

Evidence from analysis:

- The project identified 38 countries in the sales analysis.
- Country-level performance tables show revenue, orders, customers, quantity, and average order value.

Recommended action:

Prioritize marketing, inventory, and operational support for high-revenue and high-AOV countries.

Expected business value:

Focused market investment can improve revenue efficiency and operational planning.

## 5. Focus On Best-Selling Products

Business issue:

Product performance affects revenue, inventory planning, and merchandising decisions.

Evidence from analysis:

- Product analysis covers 3,922 products.
- Dashboard visuals show top products by revenue and quantity sold.

Recommended action:

Use top product rankings to support inventory planning, product bundling, and promotional strategy.

Expected business value:

Prioritizing proven products can improve sales performance and reduce inventory risk.

## 6. Monitor Future Revenue Growth Carefully

Business issue:

Forecasting suggests revenue may increase, but forecasts are directional and should be monitored.

Evidence from analysis:

- Best model: 4-Week Moving Average.
- Next 8 weeks forecast total: 3,172,808.88.
- Next 3 months forecast total: 5,212,432.39.
- Forecast direction: Increasing.

Recommended action:

Use the forecast as an early planning signal, but update it as new weekly data becomes available.

Expected business value:

Regular monitoring helps management prepare inventory, staffing, and campaigns without overcommitting.

## 7. Use Dashboard Tracking For Management Decisions

Business issue:

Management needs a repeatable way to monitor KPIs, customer segments, products, countries, and forecasts.

Evidence from analysis:

- The Power BI dashboard includes KPI cards, revenue trends, segmentation views, product and country performance, and forecast visuals.

Recommended action:

Use the dashboard as the central monitoring tool for weekly performance reviews.

Expected business value:

A single dashboard improves visibility, decision speed, and communication across business stakeholders.
""",
        "project_summary_for_cv.md": """
# Project Summary For CV

## Strong CV Bullet

- Built an end-to-end retail revenue intelligence platform using Python, SQL, SQLite, Power BI, RFM customer segmentation, and time-series forecasting; cleaned 536,641 transactions, analyzed 10.64M in sales revenue, segmented 4,338 customers, and created a dashboard-ready business reporting layer.

## Short Portfolio Description

Retail Revenue Intelligence Platform is an end-to-end analytics project that transforms online retail transaction data into business-ready insights. The project includes data cleaning, SQL database design, business KPI analysis, customer segmentation, revenue forecasting, and a Power BI dashboard.

## GitHub Project Summary

This project demonstrates a complete data analyst workflow using Python, SQL, SQLite, Power BI, RFM analysis, and forecasting. It cleans and structures online retail transaction data, creates a SQL analytics layer, identifies customer segments, compares forecasting models, and prepares executive dashboard outputs and business recommendations.

## LinkedIn Headline-Style Summary

Built a Retail Revenue Intelligence Platform using Python, SQL, Power BI, RFM segmentation, and forecasting to analyze 10.64M in retail sales revenue.

## Skills Demonstrated

- Data cleaning and preprocessing
- Business KPI analysis
- SQL database design
- SQL business queries
- Customer segmentation using RFM
- Revenue forecasting and model comparison
- Dashboard data preparation
- Power BI dashboard design
- Business recommendations
- Executive communication

## Tools Used

- Python
- Pandas
- NumPy
- SQLite
- SQL
- Power BI Desktop
- DAX
- Markdown
""",
        "linkedin_project_post.md": f"""
# LinkedIn Project Post

I recently completed a portfolio project: **{PROJECT_TITLE}**.

The goal was to turn online retail transaction data into a professional business intelligence project suitable for Data Analyst, BI Analyst, and Business Analyst internship roles.

What I built:

- Cleaned and prepared 536,641 retail transaction rows using Python and pandas
- Built a SQLite database and SQL analysis layer
- Created business KPI outputs for revenue, orders, customers, cancellations, products, and countries
- Segmented 4,338 customers using RFM analysis
- Compared simple revenue forecasting models using weekly revenue data
- Built a Power BI dashboard covering revenue trends, customer segments, product performance, country performance, and forecasts
- Created executive recommendations and final portfolio documentation

Key results:

- Total sales revenue: 10,642,110.80
- Total orders: 19,960
- Top revenue segment: Champions
- Best forecast model: 4-Week Moving Average
- Forecast direction: Increasing

This was a valuable project for practicing the full analytics workflow: Python, SQL, Power BI, customer analytics, forecasting, and business storytelling.

I built this as a portfolio project, not for a real company, and the focus was on demonstrating practical analytics thinking and clear communication.
""",
        "interview_talking_points.md": """
# Interview Talking Points

## Explain The Project In 30 Seconds

I built a retail revenue intelligence platform using online retail transaction data. I cleaned the data in Python, built a SQLite database and SQL analysis layer, segmented customers with RFM analysis, created a simple weekly revenue forecasting layer, and built a Power BI dashboard. The project turns raw transactions into business insights about revenue, customers, products, countries, cancellations, and future revenue direction.

## Explain The Project In 2 Minutes

This project simulates an end-to-end business analytics workflow. I started with raw online retail transaction data and cleaned it using Python and pandas. I preserved business-useful rows such as cancellations, returns, and missing customer IDs in the main dataset, but created a separate sales-only dataset for revenue analysis.

Then I built a SQLite database with transaction, sales, customer, product, country, and monthly sales tables. I used SQL outputs to answer business questions about revenue, orders, customers, product performance, country performance, cancellations, and average order value.

Next, I used RFM analysis to segment 4,338 known customers into 11 business-friendly segments. Champions were the top revenue segment, generating 5,713,136.80. I also identified At Risk and Cannot Lose Them customers for retention actions.

For forecasting, I used weekly revenue instead of monthly revenue because there were only 13 monthly observations. I compared a naive forecast, 4-week moving average, and linear trend regression. The 4-week moving average performed best, and the forecast direction was Increasing.

Finally, I prepared dashboard-ready CSV files and built a Power BI dashboard with KPIs, trends, segmentation, product and country performance, and forecasting visuals.

## Why The Project Matters

The project matters because it connects technical analytics work to business decisions. It does not stop at cleaning or modelling; it produces KPIs, customer segments, dashboard views, and recommendations that management could use.

## Why RFM Was Used

RFM is useful because it is simple, explainable, and business-friendly. It helps identify customers based on how recently they purchased, how often they purchased, and how much revenue they generated. This makes it easier to design retention, loyalty, and win-back actions.

## Why Weekly Forecasting Was Used Instead Of Monthly Forecasting

The dataset has only about 13 monthly observations, which is not enough for strong monthly modelling. Weekly data gave 53 observations, which is better for model evaluation. Monthly forecasts were still provided, but clearly treated as directional business estimates.

## Why The 4-Week Moving Average Performed Best

The 4-week moving average performed best because it captured recent short-term revenue behavior without overfitting a limited dataset. The linear trend model performed worse because retail revenue was not purely linear over time.

## Business Insights Found

- Total sales revenue was 10,642,110.80.
- The business had 19,960 orders and 4,338 known customers.
- Champions were the top revenue segment with 5,713,136.80 in revenue.
- Hibernating was the largest segment by customer count.
- Estimated revenue lost from cancellations and returns was 893,979.73.
- The forecast direction was Increasing, but forecasts should be treated as directional.

## Limitations

- Monthly forecasting is limited by only 13 monthly observations.
- The dataset does not include cost or margin data.
- The dataset does not include marketing channels or campaign data.
- Missing customer IDs could not be used for RFM segmentation.
- Forecasts do not include external factors such as seasonality, promotions, or market conditions.

## What I Would Improve Next

- Add margin and profitability analysis.
- Add marketing or acquisition channel data.
- Improve the dashboard into a polished five-page executive layout.
- Add automated refresh.
- Rebuild forecasting after collecting more historical data.
- Add cohort analysis and retention curves.
""",
        "report_assets.md": f"""
# Report Assets

## Power BI File

- `dashboard/Retail_Revenue_Intelligence_Dashboard.pbix`

## Dashboard Screenshots

{screenshot_lines()}

## How To Use These Assets

Use these screenshots in the README, final report, portfolio page, or presentation. If more polished screenshots are exported later, replace the files in `dashboard/dashboard_screenshots/` and update references if file names change.
""",
    }


def main() -> None:
    print("Starting Stage 6 final report generation...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    reports = build_reports()
    created_paths = []
    for file_name, content in reports.items():
        created_paths.append(write_report(file_name, content))

    print("Created report files:")
    for path in created_paths:
        print(f"- {path.relative_to(PROJECT_ROOT)}")

    print(f"Total report files created: {len(created_paths)}")
    print("Stage 6 final report generation completed.")


if __name__ == "__main__":
    main()
