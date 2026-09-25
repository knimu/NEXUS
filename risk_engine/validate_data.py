import pandas as pd


REQUIRED_COLUMNS = {
    "account_id",
    "device_id",
    "ip_id",
    "beneficiary_id",
    "timestamp",
    "amount",
    "behavior_features",
    "scenario_id",
    "ground_truth_cluster",
}


VALID_FEATURES = {
    "normal_amount",
    "normal_frequency",
    "high_amount",
    "high_frequency",
    "rapid_transactions",
    "shared_device",
    "shared_ip",
    "shared_beneficiary",
    "suspicious_beneficiary",
    "shared_office_network",
}


VALID_SCENARIOS = {
    "LEGIT_SHARED",
    "FRAUD_OBVIOUS",
    "FRAUD_EVASIVE",
    "LEGIT_BORDERLINE",
    "FRAUD_MIXED",
}


def validate_dataset(file_path):
    errors = []

    # Read dataset
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [f"Could not read dataset: {e}"]

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        errors.append(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Stop here if required columns are missing
    if errors:
        return errors

    # Check required fields for missing values
    required_fields = [
        "account_id",
        "device_id",
        "ip_id",
        "beneficiary_id",
        "timestamp",
        "behavior_features",
        "scenario_id",
    ]

    for column in required_fields:
        if df[column].isna().any():
            errors.append(
                f"Missing values found in column: {column}"
            )

    # Validate transaction amount
    numeric_amount = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    if numeric_amount.isna().any():
        errors.append(
            "Invalid or non-numeric amount found."
        )

    if (numeric_amount < 0).any():
        errors.append(
            "Negative transaction amount found."
        )

    # Validate timestamps
    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    if timestamps.isna().any():
        errors.append(
            "Invalid timestamp found."
        )

    # Validate behavior features
    if (
        df["behavior_features"]
        .astype(str)
        .str.strip()
        .eq("")
        .any()
    ):
        errors.append(
            "Empty behavior_features found."
        )

    # Check that every behavior feature is recognized
    for index, value in df["behavior_features"].items():

        features = str(value).split(";")

        invalid_features = [
            feature.strip()
            for feature in features
            if feature.strip() not in VALID_FEATURES
        ]

        if invalid_features:
            errors.append(
                f"Unknown behavior feature at row {index + 1}: "
                f"{invalid_features}"
            )

    # Validate scenario IDs
    invalid_scenarios = (
        set(df["scenario_id"].dropna())
        - VALID_SCENARIOS
    )

    if invalid_scenarios:
        errors.append(
            f"Unknown scenario IDs found: "
            f"{sorted(invalid_scenarios)}"
        )

    return errors


if __name__ == "__main__":

    # Temporary test dataset
    DATASET = "data/generated/synthetic_data.csv"

    errors = validate_dataset(DATASET)

    if errors:

        print("DATASET VALIDATION FAILED")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("DATASET VALIDATION PASSED")
    print("All required fields and values are valid.")