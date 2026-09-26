"""
Device Rotation Attack Simulator for NEXUS Member 3.

Simulates an adversary rotating shared device identifiers
to weaken device-based relationship detection.

Only device_id is modified.
All other event attributes remain unchanged.
"""

import pandas as pd


def rotate_shared_devices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rotate device IDs for accounts that share a device.

    Returns a new DataFrame; the original DataFrame is not modified.
    """

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a valid pandas DataFrame.")

    if "account_id" not in df.columns or "device_id" not in df.columns:
        raise ValueError(
            "DataFrame must contain 'account_id' and 'device_id' columns."
        )

    mutated_df = df.copy()

    # Find devices shared by two or more distinct accounts.
    shared_devices = (
        mutated_df.groupby("device_id")["account_id"]
        .nunique()
    )

    shared_devices = shared_devices[shared_devices >= 2].index.tolist()

    # Generate unique replacement device IDs.
    counter = 1

    for device_id in shared_devices:
        mask = mutated_df["device_id"] == device_id
        accounts = (
            mutated_df.loc[mask, "account_id"]
            .astype(str)
            .str.strip()
            .unique()
        )

        for account_id in sorted(accounts):
            account_mask = mask & (
                mutated_df["account_id"].astype(str).str.strip()
                == account_id
            )

            mutated_df.loc[account_mask, "device_id"] = (
                f"ADV_DEVICE_{counter:03d}"
            )
            counter += 1

    return mutated_df