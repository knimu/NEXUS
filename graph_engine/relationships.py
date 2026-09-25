"""
Relationship Extraction Module for NEXUS Member 2.

Extracts pairwise account relationships based on observable shared attributes:
- shared_device
- shared_ip
- shared_beneficiary

Note: ground_truth_cluster and scenario_id are intentionally NOT used.
"""

from itertools import combinations
import pandas as pd


REQUIRED_COLUMNS = ["account_id"]
ATTRIBUTE_MAPPING = {
    "device_id": "shared_device",
    "ip_id": "shared_ip",
    "beneficiary_id": "shared_beneficiary",
}


def is_valid_value(value) -> bool:
    """Return True if an attribute value is valid and non-empty."""
    if pd.isna(value) or value is None:
        return False
    val_str = str(value).strip()
    return val_str not in {"", "nan", "None", "NONE", "null", "NULL"}


def extract_shared_relationships(df: pd.DataFrame) -> list[dict]:
    """
    Extract account-to-account relationships based on observable shared attributes.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing synthetic event data.

    Returns:
        list[dict]: Deterministic list of relationship dictionaries:
            {
                "account_a": str,
                "account_b": str,
                "relationship_type": str,
                "shared_value": str
            }
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a valid pandas DataFrame.")

    if "account_id" not in df.columns:
        raise ValueError("DataFrame missing required column: 'account_id'")

    # Verify at least one attribute column exists
    available_attrs = [col for col in ATTRIBUTE_MAPPING if col in df.columns]
    if not available_attrs:
        raise ValueError(
            f"DataFrame missing attribute columns. Required at least one of: {list(ATTRIBUTE_MAPPING.keys())}"
        )

    relationships = []

    for attr_col, rel_type in ATTRIBUTE_MAPPING.items():
        if attr_col not in df.columns:
            continue

        # Filter rows with valid non-null values
        valid_rows = df[df[attr_col].apply(is_valid_value)].copy()
        if valid_rows.empty:
            continue

        # Group accounts by shared attribute value
        grouped = valid_rows.groupby(attr_col)
        for shared_val, group in grouped:
            accounts = sorted(
                group["account_id"].astype(str).str.strip().unique().tolist()
            )

            # Generate all canonical pairs (account_a < account_b)
            for acc_a, acc_b in combinations(accounts, 2):
                if acc_a == acc_b:
                    continue  # Avoid self-links

                relationships.append(
                    {
                        "account_a": acc_a,
                        "account_b": acc_b,
                        "relationship_type": rel_type,
                        "shared_value": str(shared_val).strip(),
                    }
                )

    # Sort deterministically
    relationships.sort(
        key=lambda r: (
            r["account_a"],
            r["account_b"],
            r["relationship_type"],
            r["shared_value"],
        )
    )

    return relationships