-- Stage 4 revenue forecasting queries.
-- Forecasting uses sales_transactions only because that table contains valid positive sales.

-- Weekly revenue trend used for model evaluation
SELECT
    week_start_date,
    total_revenue,
    total_orders,
    total_quantity,
    average_order_value
FROM weekly_revenue
ORDER BY week_start_date;

-- Monthly revenue trend for executive reporting
SELECT
    strftime('%Y-%m', invoice_date) AS invoice_year_month,
    date(invoice_date, 'start of month') AS month_start_date,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT invoice_no), 0), 2) AS average_order_value
FROM sales_transactions
GROUP BY invoice_year_month, month_start_date
ORDER BY month_start_date;

-- Best revenue week
SELECT
    week_start_date,
    total_revenue
FROM weekly_revenue
ORDER BY total_revenue DESC
LIMIT 1;

-- Worst revenue week
SELECT
    week_start_date,
    total_revenue
FROM weekly_revenue
ORDER BY total_revenue ASC
LIMIT 1;

-- Revenue by weekday
SELECT
    CASE strftime('%w', invoice_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS weekday_name,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders
FROM sales_transactions
GROUP BY weekday_name
ORDER BY total_revenue DESC;

-- Revenue by month
SELECT
    strftime('%Y-%m', invoice_date) AS invoice_year_month,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders
FROM sales_transactions
GROUP BY invoice_year_month
ORDER BY invoice_year_month;

-- Forecast model comparison
SELECT
    model_name,
    mae,
    rmse,
    mape,
    notes
FROM forecast_model_comparison
ORDER BY mae;

-- Future forecast output
SELECT
    forecast_type,
    forecast_period,
    forecast_period_start,
    forecast_revenue,
    model_used
FROM revenue_forecasts
ORDER BY forecast_type, forecast_period_start;
