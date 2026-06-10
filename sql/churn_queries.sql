-- Monthly churn rate by customer segment

SELECT
  customer_segment,
  month,
  COUNT(*) AS customers,
  AVG(churn_flag) AS churn_rate
FROM customer_monthly_features
GROUP BY customer_segment, month
ORDER BY month, churn_rate DESC;

-- Customers with high value and low engagement
SELECT
  customer_id,
  avg_balance,
  salary_inflow,
  digital_logins_30d,
  product_count
FROM customer_monthly_features
WHERE avg_balance >= 5000
  AND digital_logins_30d <= 2
  AND churn_probability >= 0.60;

