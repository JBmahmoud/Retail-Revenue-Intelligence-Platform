# Retail Revenue Intelligence Platform: SQL, BI Dashboard, Customer Segmentation & Sales Forecasting

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
