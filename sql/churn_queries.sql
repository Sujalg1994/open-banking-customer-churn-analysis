-- Churn rate by customer segment

SELECT
  customer_segment,
  COUNT(*) AS customers,
  AVG(churn_flag) AS churn_rate,
  AVG(churn_risk_score) AS avg_churn_score,
  SUM(value_at_risk) AS value_at_risk
FROM customers_churn_scored
GROUP BY customer_segment
ORDER BY churn_rate DESC;

-- Customers with high value and low engagement
SELECT
  customer_id,
  customer_segment,
  avg_balance,
  salary_inflow,
  digital_logins_30d,
  product_count,
  churn_risk_score,
  churn_risk_band,
  retention_action
FROM customers_churn_scored
WHERE avg_balance >= 5000
  AND digital_logins_30d <= 2
  AND churn_risk_band IN ('Medium churn risk', 'High churn risk')
ORDER BY churn_risk_score DESC, avg_balance DESC;

-- Recommended retention action MI
SELECT
  retention_action,
  COUNT(*) AS customers,
  AVG(churn_flag) AS churn_rate,
  AVG(churn_risk_score) AS avg_churn_score,
  SUM(value_at_risk) AS value_at_risk
FROM customers_churn_scored
GROUP BY retention_action
ORDER BY churn_rate DESC, customers DESC;

-- Priority retention queue
SELECT
  customer_id,
  customer_segment,
  region,
  avg_balance,
  product_count,
  digital_logins_30d,
  salary_inflow,
  complaint_count_90d,
  churn_risk_score,
  churn_risk_band,
  retention_action
FROM customers_churn_scored
WHERE churn_risk_band <> 'Low churn risk'
ORDER BY churn_risk_score DESC, avg_balance DESC;
