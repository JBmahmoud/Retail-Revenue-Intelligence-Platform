# Dashboard Page Specification

# Retail Revenue Intelligence Dashboard

Use a premium business analytics style with a light background, navy accents, blue/cyan/purple highlights, clean cards, and strong spacing. Avoid clutter and keep each page focused on business decisions.

## Page 1: Executive Overview

Purpose: Give management a quick understanding of total business performance.

Datasets needed:

- `dashboard_kpi_summary`
- `dashboard_monthly_sales`
- `dashboard_country_performance`
- `dashboard_product_performance`

Recommended visuals:

- KPI cards: Total Revenue, Total Orders, Total Customers, Average Order Value, Repeat Customer Rate, Cancellation Rate
- Monthly revenue line chart
- Revenue by country bar chart or map
- Top 10 products by revenue
- Short insight text box

Layout guidance:

- Top row: six KPI cards
- Middle: monthly revenue trend across the page
- Bottom: country revenue and top products side by side
- Keep the insight text compact and executive-focused

Filters/slicers:

- Month
- Country

Insight text suggestion:

Revenue is concentrated in key markets and product categories. Repeat purchasing and cancellation rate should be monitored alongside top-line revenue.

Business questions answered:

- What is total revenue?
- How many orders and customers were generated?
- Which countries and products are driving performance?

## Page 2: Sales Performance

Purpose: Analyze revenue trends and commercial performance.

Datasets needed:

- `dashboard_monthly_sales`
- `dashboard_weekly_revenue`
- `dashboard_country_performance`
- `dashboard_product_performance`

Recommended visuals:

- Monthly revenue trend
- Weekly revenue trend
- Best vs worst revenue month cards
- Average order value over time
- Revenue by country
- Orders by country

Layout guidance:

- Use trend visuals at the top and ranking visuals below
- Place slicers in a thin left panel or top filter row

Filters/slicers:

- Country
- Month
- Product

Insight text suggestion:

Revenue shows clear monthly variation, so weekly views are useful for spotting short-term demand shifts.

Business questions answered:

- When did revenue peak?
- Which markets have the strongest sales?
- How is average order value changing over time?

## Page 3: Customer Segmentation

Purpose: Show customer value and behavior using RFM segmentation.

Datasets needed:

- `dashboard_customer_segments`
- `dashboard_segment_summary`

Recommended visuals:

- Customer count by segment
- Revenue by segment
- Revenue percentage by segment
- Segment summary table
- Top high-value customers table using monetary sort
- At-risk customers table filtered to `At Risk` and `Cannot Lose Them`
- Business recommendation cards from `recommended_action`

Layout guidance:

- Top row: segment count and revenue share charts
- Middle: segment summary table
- Bottom: customer detail tables and recommendation cards

Filters/slicers:

- Customer segment
- Main country
- RFM score

Insight text suggestion:

Champions generate the highest revenue concentration, while at-risk valuable customers should be prioritized for win-back actions.

Business questions answered:

- Which customer segments are most valuable?
- Which customers need retention action?
- What actions should management take by segment?

## Page 4: Product & Country Performance

Purpose: Identify best products and best markets.

Datasets needed:

- `dashboard_product_performance`
- `dashboard_country_performance`

Recommended visuals:

- Top products by revenue
- Top products by quantity
- Country revenue ranking
- Average order value by country
- Product performance table
- Country performance table

Layout guidance:

- Use product visuals on the left and country visuals on the right
- Keep tables below charts for detail inspection

Filters/slicers:

- Country
- Product

Insight text suggestion:

Product and market concentration should guide inventory planning, commercial prioritization, and dashboard drill-downs.

Business questions answered:

- Which products drive the most revenue?
- Which countries have the highest revenue and AOV?
- Which products sell high quantities but may have lower value?

## Page 5: Forecasting & Business Recommendations

Purpose: Show expected future revenue and management actions.

Datasets needed:

- `dashboard_weekly_revenue`
- `dashboard_weekly_actual_vs_forecast`
- `dashboard_forecast_model_comparison`
- `dashboard_future_weekly_forecast`
- `dashboard_future_monthly_forecast`
- `dashboard_forecast_summary`

Recommended visuals:

- Actual vs forecast weekly revenue line chart
- Future weekly forecast chart
- Future monthly forecast chart
- Forecast model comparison table
- Forecast direction card
- Forecast model summary cards
- Forecast recommendation cards
- Forecast limitation text

Layout guidance:

- Top: forecast KPI cards and direction signal
- Middle: actual vs forecast weekly revenue and future weekly forecast
- Bottom: model comparison table, future monthly forecast, and recommendation text

Filters/slicers:

- Forecast model
- Forecast month

Insight text suggestion:

Forecasts are directional estimates because the available monthly history is limited.

Business questions answered:

- What is the expected revenue direction?
- What is the next 8-week forecast?
- Which forecasting model performed best?
- What management action should follow from the forecast signal?
