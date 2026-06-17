from pathlib import Path

import numpy as np
import pandas as pd


np.random.seed(42)
out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)

segments = ["Mass", "Affluent", "Student", "Young professional", "SME owner"]
regions = ["London", "South East", "North West", "West Midlands", "Scotland", "Wales", "Yorkshire"]

rows = []
for i in range(1, 3501):
    segment = str(np.random.choice(segments, p=[0.48, 0.16, 0.12, 0.16, 0.08]))
    tenure_months = int(np.random.randint(2, 121))
    product_count = int(np.random.choice([1, 2, 3, 4, 5], p=[0.28, 0.33, 0.22, 0.12, 0.05]))
    digital_logins_30d = int(np.random.poisson(9 if segment != "Student" else 14))
    app_sessions_change_pct = round(float(np.random.normal(-0.04, 0.22)), 3)
    salary_inflow = int(np.random.choice([0, 1], p=[0.28, 0.72]))
    salary_inflow_change_pct = round(float(np.random.normal(-0.03 if salary_inflow else -0.18, 0.18)), 3)
    avg_balance = round(float(np.random.lognormal(mean=7.6 if segment == "Affluent" else 6.5, sigma=0.85)), 2)
    balance_change_pct = round(float(np.random.normal(-0.02, 0.25)), 3)
    direct_debits = int(np.random.poisson(5 if salary_inflow else 2))
    complaint_count_90d = int(np.random.poisson(0.12))
    overdraft_usage_rate = round(float(np.clip(np.random.beta(1.4, 5.5), 0, 1)), 3)
    card_spend_30d = round(float(np.random.lognormal(mean=5.6, sigma=0.8)), 2)
    open_banking_connected = int(np.random.random() < 0.34)

    churn_signal = (
        -2.1
        + (product_count == 1) * 0.55
        + (digital_logins_30d <= 2) * 0.8
        + (app_sessions_change_pct < -0.25) * 0.6
        + (salary_inflow == 0) * 0.65
        + (salary_inflow_change_pct < -0.20) * 0.75
        + (balance_change_pct < -0.30) * 0.65
        + complaint_count_90d * 0.65
        + (overdraft_usage_rate > 0.65) * 0.45
        - (tenure_months > 36) * 0.25
        - (product_count >= 4) * 0.35
    )
    churn_probability = 1 / (1 + np.exp(-churn_signal))
    churn_flag = int(np.random.random() < churn_probability)

    rows.append(
        {
            "customer_id": f"C{i:06d}",
            "customer_segment": segment,
            "region": str(np.random.choice(regions)),
            "tenure_months": tenure_months,
            "product_count": product_count,
            "digital_logins_30d": digital_logins_30d,
            "app_sessions_change_pct": app_sessions_change_pct,
            "salary_inflow": salary_inflow,
            "salary_inflow_change_pct": salary_inflow_change_pct,
            "avg_balance": avg_balance,
            "balance_change_pct": balance_change_pct,
            "direct_debits": direct_debits,
            "complaint_count_90d": complaint_count_90d,
            "overdraft_usage_rate": overdraft_usage_rate,
            "card_spend_30d": card_spend_30d,
            "open_banking_connected": open_banking_connected,
            "churn_probability_simulated": round(float(churn_probability), 4),
            "churn_flag": churn_flag,
        }
    )

pd.DataFrame(rows).to_csv(out / "customer_monthly_features.csv", index=False)
print("Created data/raw/customer_monthly_features.csv")
