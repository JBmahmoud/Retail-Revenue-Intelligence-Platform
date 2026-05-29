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
