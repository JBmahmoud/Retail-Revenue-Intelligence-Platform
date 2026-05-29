-- Stage 3 RFM customer segmentation queries.
-- These queries use the customer_segments table created by scripts/04_customer_segmentation.py.

-- Segment distribution
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customer_segments), 2) AS customer_percentage
FROM customer_segments
GROUP BY customer_segment
ORDER BY customer_count DESC;

-- Revenue by segment
SELECT
    customer_segment,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(100.0 * SUM(monetary) / (SELECT SUM(monetary) FROM customer_segments), 2) AS revenue_percentage
FROM customer_segments
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- Average RFM values by segment
SELECT
    customer_segment,
    ROUND(AVG(recency_days), 2) AS average_recency_days,
    ROUND(AVG(frequency), 2) AS average_frequency,
    ROUND(AVG(monetary), 2) AS average_monetary,
    ROUND(AVG(rfm_score), 2) AS average_rfm_score
FROM customer_segments
GROUP BY customer_segment
ORDER BY average_rfm_score DESC;

-- Top customers by monetary value
SELECT
    customer_id,
    main_country,
    frequency,
    ROUND(monetary, 2) AS monetary,
    ROUND(average_order_value, 2) AS average_order_value,
    recency_days,
    customer_segment
FROM customer_segments
ORDER BY monetary DESC
LIMIT 100;

-- At-risk high-value customers
SELECT
    customer_id,
    main_country,
    frequency,
    ROUND(monetary, 2) AS monetary,
    ROUND(average_order_value, 2) AS average_order_value,
    recency_days,
    customer_segment
FROM customer_segments
WHERE customer_segment IN ('At Risk', 'Cannot Lose Them')
ORDER BY monetary DESC;

-- Segment distribution by country
SELECT
    customer_segment,
    main_country,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(AVG(monetary), 2) AS average_monetary
FROM customer_segments
GROUP BY customer_segment, main_country
ORDER BY customer_segment, total_revenue DESC;
