-- Stage 2 business analysis queries.
-- These are kept as a readable SQL reference. The Python analysis script executes
-- equivalent named queries and exports dashboard-ready CSV files.

-- Total revenue
SELECT ROUND(SUM(revenue), 2) AS total_revenue
FROM sales_transactions;

-- Total orders
SELECT COUNT(DISTINCT invoice_no) AS total_orders
FROM sales_transactions;

-- Total customers
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM sales_transactions
WHERE customer_id IS NOT NULL;

-- Average order value
SELECT ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT invoice_no), 0), 2) AS average_order_value
FROM sales_transactions;

-- Monthly revenue trend
SELECT *
FROM monthly_sales
ORDER BY invoice_year_month;

-- Best revenue month
SELECT invoice_year_month, total_revenue
FROM monthly_sales
ORDER BY total_revenue DESC
LIMIT 1;

-- Worst revenue month
SELECT invoice_year_month, total_revenue
FROM monthly_sales
ORDER BY total_revenue ASC
LIMIT 1;

-- Top 10 countries by revenue
SELECT *
FROM countries
ORDER BY total_revenue DESC
LIMIT 10;

-- Top 10 products by revenue
SELECT *
FROM products
ORDER BY total_revenue DESC
LIMIT 10;

-- Top 10 customers by revenue
SELECT *
FROM customers
ORDER BY total_revenue DESC
LIMIT 10;

-- Repeat customer rate
SELECT
    ROUND(
        1.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        4
    ) AS repeat_customer_rate
FROM customers;

-- Cancellation count
SELECT COUNT(*) AS cancellation_count
FROM transactions
WHERE is_cancelled = 1;

-- Cancellation rate
SELECT
    ROUND(
        1.0 * SUM(CASE WHEN is_cancelled = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        4
    ) AS cancellation_rate
FROM transactions;

-- Estimated revenue lost from cancellations and returns
SELECT ROUND(ABS(SUM(revenue)), 2) AS estimated_revenue_lost
FROM transactions
WHERE is_cancelled = 1;

-- Products with highest cancellation or return count
SELECT
    stock_code,
    description,
    COUNT(*) AS cancellation_return_count,
    ROUND(ABS(SUM(revenue)), 2) AS estimated_revenue_lost
FROM transactions
WHERE is_cancelled = 1
GROUP BY stock_code, description
ORDER BY cancellation_return_count DESC, estimated_revenue_lost DESC
LIMIT 10;

-- Countries with highest revenue
SELECT *
FROM countries
ORDER BY total_revenue DESC;

-- Countries with highest average order value
SELECT *
FROM countries
ORDER BY average_order_value DESC;
