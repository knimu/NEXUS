"""
IP Rotation Attack Simulator for NEXUS Member 3.

Simulates an adversary rotating shared IP identifiers
to weaken IP-based relationship detection.

Only ip_id is modified.
All other event attributes remain unchanged.
"""

import pandas as pd


def rotate_shared_ips(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rotate IP IDs for accounts that share an IP.

    Returns a new DataFrame; the original DataFrame is not modified.
    """

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a valid pandas DataFrame.")

    if "account_id" not in df.columns or "ip_id" not in df.columns:
        raise ValueError(
            "DataFrame must contain 'account_id' and 'ip_id' columns."
        )

    mutated_df = df.copy()

    # Find IPs shared by two or more distinct accounts.
    shared_ips = (
        mutated_df.groupby("ip_id")["account_id"]
        .nunique()
    )

    shared_ips = shared_ips[shared_ips >= 2].index.tolist()

    # Generate unique replacement IP IDs.
    counter = 1

    for ip_id in shared_ips:
        mask = mutated_df["ip_id"] == ip_id

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

            mutated_df.loc[account_mask, "ip_id"] = (
                f"ADV_IP_{counter:03d}"
            )
            counter += 1

    return mutated_df