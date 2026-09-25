"""
Adversarial Attack Simulator for NEXUS.

Provides controlled attack modes that mutate only the
infrastructure identifiers used by the graph detector.
"""

import pandas as pd

from adversarial.device_rotation import rotate_shared_devices
from adversarial.ip_rotation import rotate_shared_ips


def apply_attack(df: pd.DataFrame, attack_type: str) -> pd.DataFrame:
    """
    Apply a selected adversarial attack.

    Supported attack types:
        - device_rotation
        - ip_rotation
        - combined

    Returns a new DataFrame.
    """

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a valid pandas DataFrame.")

    if attack_type == "device_rotation":
        return rotate_shared_devices(df)

    if attack_type == "ip_rotation":
        return rotate_shared_ips(df)

    if attack_type == "combined":
        mutated_df = rotate_shared_devices(df)
        mutated_df = rotate_shared_ips(mutated_df)
        return mutated_df

    raise ValueError(
        "Unknown attack type. "
        "Use 'device_rotation', 'ip_rotation', or 'combined'."
    )