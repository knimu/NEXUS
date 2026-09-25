import pandas as pd

from risk_engine.risk_rules import calculate_risk_score, classify_risk
from risk_engine.validate_data import validate_dataset
from data_integrity.verify_dataset import verify_dataset_integrity

DATASET = "data/generated/synthetic_data.csv"


# Step 1: Verify dataset integrity
print("Checking dataset integrity...\n")

if not verify_dataset_integrity():
    print("\nRisk analysis stopped because dataset integrity verification failed.")
    raise SystemExit(1)

print("\nDataset integrity verified.")


# Step 2: Validate dataset
validation_errors = validate_dataset(DATASET)

if validation_errors:
    print("\nDATASET VALIDATION FAILED")
    for error in validation_errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Dataset validation passed.")
print("Starting individual risk analysis...\n")


# Step 3: Individual risk analysis
df = pd.read_csv(DATASET)
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


# Step 4: Save results
results_df = pd.DataFrame(results)

print(results_df)

results_df.to_csv(
    "data/generated/risk_results.csv",
    index=False
)

print("\nRisk results saved successfully.")