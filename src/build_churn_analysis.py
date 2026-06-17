from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw/customer_monthly_features.csv")
PROCESSED_DIR = Path("data/processed")
CHART_DIR = Path("dashboard/screenshots")


def score_band(score):
    if score >= 45:
        return "High churn risk"
    if score >= 20:
        return "Medium churn risk"
    return "Low churn risk"


def retention_action(row):
    if row["complaint_count_90d"] > 0:
        return "Service recovery call"
    if row["salary_inflow"] == 0 or row["salary_inflow_change_pct"] < -0.20:
        return "Salary switch or current account offer"
    if row["product_count"] <= 1:
        return "Product deepening offer"
    if row["digital_logins_30d"] <= 2 or row["app_sessions_change_pct"] < -0.25:
        return "Digital engagement campaign"
    if row["overdraft_usage_rate"] > 0.65:
        return "Financial wellbeing support"
    return "Monitor"


def svg_bar_chart(df, label_col, value_col, title, output_path, value_format="{:.1%}"):
    width = 940
    height = 500
    margin_left = 245
    margin_right = 85
    margin_top = 72
    bar_gap = 18
    bar_height = 42
    plot_width = width - margin_left - margin_right
    max_value = max(df[value_col].max(), 0.01)

    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="42" font-family="Arial" font-size="24" font-weight="700" fill="#172033">{title}</text>',
    ]

    for idx, row in df.reset_index(drop=True).iterrows():
        y = margin_top + idx * (bar_height + bar_gap)
        bar_width = int((row[value_col] / max_value) * plot_width)
        rows.extend(
            [
                f'<text x="32" y="{y + 28}" font-family="Arial" font-size="15" fill="#172033">{row[label_col]}</text>',
                f'<rect x="{margin_left}" y="{y}" width="{bar_width}" height="{bar_height}" rx="4" fill="#0f766e"/>',
                f'<text x="{margin_left + bar_width + 12}" y="{y + 28}" font-family="Arial" font-size="15" fill="#172033">{value_format.format(row[value_col])}</text>',
            ]
        )

    rows.append("</svg>")
    output_path.write_text("\n".join(rows), encoding="utf-8")


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH)

    score = pd.Series(0, index=df.index)
    score += (df["product_count"] == 1).astype(int) * 15
    score += (df["digital_logins_30d"] <= 2).astype(int) * 18
    score += (df["app_sessions_change_pct"] < -0.25).astype(int) * 14
    score += (df["salary_inflow"] == 0).astype(int) * 16
    score += (df["salary_inflow_change_pct"] < -0.20).astype(int) * 16
    score += (df["balance_change_pct"] < -0.30).astype(int) * 14
    score += df["complaint_count_90d"].clip(upper=3) * 12
    score += (df["overdraft_usage_rate"] > 0.65).astype(int) * 10
    score -= (df["tenure_months"] > 36).astype(int) * 6
    score -= (df["product_count"] >= 4).astype(int) * 8

    df["churn_risk_score"] = score.clip(0, 100).astype(int)
    df["churn_risk_band"] = df["churn_risk_score"].apply(score_band)
    df["retention_action"] = df.apply(retention_action, axis=1)
    df["value_at_risk"] = (df["avg_balance"] * df["churn_flag"]).round(2)

    segment_summary = (
        df.groupby("customer_segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            churn_rate=("churn_flag", "mean"),
            avg_churn_score=("churn_risk_score", "mean"),
            avg_balance=("avg_balance", "mean"),
            value_at_risk=("value_at_risk", "sum"),
        )
        .sort_values("churn_rate", ascending=False)
    )
    risk_summary = (
        df.groupby("churn_risk_band", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            churn_rate=("churn_flag", "mean"),
            avg_balance=("avg_balance", "mean"),
            value_at_risk=("value_at_risk", "sum"),
        )
        .sort_values("churn_rate", ascending=False)
    )
    action_summary = (
        df.groupby("retention_action", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            churn_rate=("churn_flag", "mean"),
            avg_churn_score=("churn_risk_score", "mean"),
            value_at_risk=("value_at_risk", "sum"),
        )
        .sort_values(["churn_rate", "customers"], ascending=[False, False])
    )
    priority_customers = (
        df[df["churn_risk_band"] != "Low churn risk"]
        .sort_values(["churn_risk_score", "avg_balance"], ascending=[False, False])
        .head(300)
    )

    df.to_csv(PROCESSED_DIR / "customers_churn_scored.csv", index=False)
    segment_summary.to_csv(PROCESSED_DIR / "segment_churn_summary.csv", index=False)
    risk_summary.to_csv(PROCESSED_DIR / "risk_band_summary.csv", index=False)
    action_summary.to_csv(PROCESSED_DIR / "retention_action_summary.csv", index=False)
    priority_customers.to_csv(PROCESSED_DIR / "priority_retention_queue.csv", index=False)

    svg_bar_chart(
        segment_summary,
        "customer_segment",
        "churn_rate",
        "Churn Rate by Customer Segment",
        CHART_DIR / "churn_rate_by_segment.svg",
    )
    svg_bar_chart(
        action_summary.head(6),
        "retention_action",
        "churn_rate",
        "Churn Rate by Recommended Retention Action",
        CHART_DIR / "churn_rate_by_action.svg",
    )

    print("Created churn-scored customers, summaries, retention queue, and SVG charts.")


if __name__ == "__main__":
    main()
