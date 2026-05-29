# Final Project Report

# Retail Revenue Intelligence Platform: SQL, BI Dashboard, Customer Segmentation & Sales Forecasting

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
