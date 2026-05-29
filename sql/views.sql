-- Stage 2 dashboard-ready SQL views.

CREATE VIEW IF NOT EXISTS vw_sales_overview AS
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT invoice_no), 0), 2) AS average_order_value,
    SUM(quantity) AS total_quantity_sold
FROM sales_transactions;

CREATE VIEW IF NOT EXISTS vw_monthly_revenue AS
SELECT
    invoice_year_month,
    total_revenue,
    total_orders,
    total_quantity_sold,
    total_customers,
    average_order_value
FROM monthly_sales;

CREATE VIEW IF NOT EXISTS vw_country_performance AS
SELECT
    country,
    total_revenue,
    total_orders,
    total_customers,
    total_quantity_sold,
    average_order_value
FROM countries;

CREATE VIEW IF NOT EXISTS vw_product_performance AS
SELECT
    stock_code,
    description,
    total_quantity_sold,
    total_revenue,
    number_of_orders,
    number_of_customers,
    average_unit_price
FROM products;

CREATE VIEW IF NOT EXISTS vw_customer_performance AS
SELECT
    customer_id,
    first_purchase_date,
    last_purchase_date,
    total_orders,
    total_quantity,
    total_revenue,
    average_order_value,
    country_count,
    main_country
FROM customers;

CREATE VIEW IF NOT EXISTS vw_cancellation_analysis AS
SELECT
    invoice_year_month,
    country,
    COUNT(*) AS cancellation_return_count,
    ROUND(ABS(SUM(revenue)), 2) AS estimated_revenue_lost
FROM transactions
WHERE is_cancelled = 1
GROUP BY invoice_year_month, country;
