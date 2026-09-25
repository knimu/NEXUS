import pandas as pd

from risk_rules import calculate_risk_score, classify_risk
df = pd.read_csv("data/generated/synthetic_data.csv")

results = []

for _, row in df.iterrows():
    features = row["behavior_features"].split(";")

    score = calculate_risk_score(features)
    risk_level = classify_risk(score)

    results.append({
    "account_id": row["account_id"],
    "risk_score": score,
    "risk_level": risk_level,
    "risk_features": row["behavior_features"],
    "scenario_id": row["scenario_id"],
    "ground_truth_cluster": row["ground_truth_cluster"]
})

results_df = pd.DataFrame(results)

print(results_df)
results_df.to_csv("data/generated/risk_results.csv", index=False)

print("\nRisk results saved successfully.")