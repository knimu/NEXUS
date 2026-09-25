"""
Evidence Engine Module for NEXUS Member 2.

Extracts post-detection structured evidence for a candidate cluster:
- Shared attributes (devices, beneficiaries, IPs)
- Temporal proximity (connected account pairs with timestamps <= 30 minutes apart)
- Behavioral feature overlap (suspicious tags shared across >= 2 accounts)

Note: ground_truth_cluster and scenario_id are intentionally NOT used.
"""

from itertools import combinations
import pandas as pd
import networkx as nx


SUSPICIOUS_BEHAVIOR_TAGS = [
    "high_amount",
    "high_frequency",
    "rapid_transactions",
    "suspicious_beneficiary",
]

TEMPORAL_WINDOW_SECONDS = 30 * 60  # 30 minutes


def is_valid_val(val) -> bool:
    """Return True if an attribute value is valid and non-empty."""
    if pd.isna(val) or val is None:
        return False
    s = str(val).strip()
    return s not in {"", "nan", "None", "NONE", "null", "NULL"}


def extract_cluster_evidence(
    cluster_accounts: list[str], df: pd.DataFrame, G: nx.Graph
) -> dict:
    """
    Extract deterministic, machine-readable evidence for a candidate cluster.

    Parameters:
        cluster_accounts (list[str]): Account IDs in the candidate cluster.
        df (pd.DataFrame): Input event DataFrame.
        G (nx.Graph): Candidate account graph.

    Returns:
        dict: Complete structured evidence metadata for the cluster.
    """
    if df is None or "account_id" not in df.columns:
        raise ValueError("DataFrame missing required column: 'account_id'")

    cluster_set = set(cluster_accounts)
    sub_df = df[df["account_id"].astype(str).str.strip().isin(cluster_set)].copy()

    # 1. Attribute Sharing (Devices, Beneficiaries, IPs)
    shared_devices = []
    if "device_id" in sub_df.columns:
        valid_devs = sub_df[sub_df["device_id"].apply(is_valid_val)]
        for dev_id, grp in valid_devs.groupby("device_id"):
            accs = grp["account_id"].astype(str).str.strip().unique()
            if len(accs) >= 2:
                shared_devices.append(str(dev_id).strip())
    shared_devices = sorted(shared_devices)

    shared_beneficiaries = []
    if "beneficiary_id" in sub_df.columns:
        valid_bens = sub_df[sub_df["beneficiary_id"].apply(is_valid_val)]
        for ben_id, grp in valid_bens.groupby("beneficiary_id"):
            accs = grp["account_id"].astype(str).str.strip().unique()
            if len(accs) >= 2:
                shared_beneficiaries.append(str(ben_id).strip())
    shared_beneficiaries = sorted(shared_beneficiaries)

    shared_ips = []
    if "ip_id" in sub_df.columns:
        valid_ips = sub_df[sub_df["ip_id"].apply(is_valid_val)]
        for ip_id, grp in valid_ips.groupby("ip_id"):
            accs = grp["account_id"].astype(str).str.strip().unique()
            if len(accs) >= 2:
                shared_ips.append(str(ip_id).strip())
    shared_ips = sorted(shared_ips)

    Ndev = len(shared_devices)
    Nben = len(shared_beneficiaries)
    Nip = len(shared_ips)

    # 2. Temporal Evidence
    # Parse timestamps per account
    account_timestamps = {}
    if "timestamp" in sub_df.columns:
        for _, row in sub_df.iterrows():
            acc_id = str(row["account_id"]).strip()
            ts_val = row["timestamp"]
            try:
                ts_dt = pd.to_datetime(ts_val)
                account_timestamps[acc_id] = ts_dt
            except Exception:
                pass

    temporal_pairs = []
    seen_pairs = set()

    # Iterate over distinct connected pairs in G that belong to cluster_accounts
    for u, v in G.edges():
        u_str, v_str = str(u).strip(), str(v).strip()
        if u_str in cluster_set and v_str in cluster_set:
            pair_key = tuple(sorted([u_str, v_str]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            if u_str in account_timestamps and v_str in account_timestamps:
                ts_u = account_timestamps[u_str]
                ts_v = account_timestamps[v_str]
                delta_sec = abs((ts_u - ts_v).total_seconds())

                if delta_sec <= TEMPORAL_WINDOW_SECONDS:
                    temporal_pairs.append(
                        {
                            "account_a": pair_key[0],
                            "account_b": pair_key[1],
                            "time_diff_minutes": round(delta_sec / 60.0, 2),
                        }
                    )

    temporal_pairs.sort(key=lambda x: (x["account_a"], x["account_b"]))
    Ntemp = len(temporal_pairs)

    # 3. Behavioral Evidence
    account_behavior_tags = {}
    if "behavior_features" in sub_df.columns:
        for _, row in sub_df.iterrows():
            acc_id = str(row["account_id"]).strip()
            feat_str = str(row["behavior_features"]) if pd.notna(row["behavior_features"]) else ""
            tags = [t.strip() for t in feat_str.split(";") if t.strip()]
            account_behavior_tags[acc_id] = tags

    tag_account_counts = {tag: set() for tag in SUSPICIOUS_BEHAVIOR_TAGS}
    for acc_id, tags in account_behavior_tags.items():
        for tag in tags:
            if tag in tag_account_counts:
                tag_account_counts[tag].add(acc_id)

    Sbehavior = sorted(
        [tag for tag, accs in tag_account_counts.items() if len(accs) >= 2]
    )
    Nbeh = len(Sbehavior)

    # 4. Construct Granular Machine-Readable Evidence List
    evidence_items = []

    # Shared devices evidence
    for dev in shared_devices:
        accs_with_dev = sorted(
            sub_df[sub_df["device_id"].astype(str).str.strip() == dev]["account_id"]
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
        evidence_items.append(
            {
                "type": "shared_device",
                "accounts": accs_with_dev,
                "shared_values": [dev],
                "description": f"Accounts {', '.join(accs_with_dev)} share device {dev}.",
            }
        )

    # Shared beneficiaries evidence
    for ben in shared_beneficiaries:
        accs_with_ben = sorted(
            sub_df[sub_df["beneficiary_id"].astype(str).str.strip() == ben]["account_id"]
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
        evidence_items.append(
            {
                "type": "shared_beneficiary",
                "accounts": accs_with_ben,
                "shared_values": [ben],
                "description": f"Accounts {', '.join(accs_with_ben)} share beneficiary {ben}.",
            }
        )

    # Shared IPs evidence
    for ip in shared_ips:
        accs_with_ip = sorted(
            sub_df[sub_df["ip_id"].astype(str).str.strip() == ip]["account_id"]
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
        evidence_items.append(
            {
                "type": "shared_ip",
                "accounts": accs_with_ip,
                "shared_values": [ip],
                "description": f"Accounts {', '.join(accs_with_ip)} share IP address {ip}.",
            }
        )

    # Temporal evidence
    if Ntemp > 0:
        involved_temporal_accs = sorted(
            list({p["account_a"] for p in temporal_pairs} | {p["account_b"] for p in temporal_pairs})
        )
        evidence_items.append(
            {
                "type": "temporal_proximity",
                "accounts": involved_temporal_accs,
                "shared_values": ["<= 30 minutes"],
                "description": f"Detected {Ntemp} connected account pair(s) transacting within 30 minutes.",
            }
        )

    # Behavioral evidence
    for tag in Sbehavior:
        accs_with_tag = sorted(list(tag_account_counts[tag]))
        evidence_items.append(
            {
                "type": "behavioral_overlap",
                "accounts": accs_with_tag,
                "shared_values": [tag],
                "description": f"Suspicious behavior tag '{tag}' shared across {len(accs_with_tag)} accounts.",
            }
        )

    return {
        "shared_devices": shared_devices,
        "shared_ips": shared_ips,
        "shared_beneficiaries": shared_beneficiaries,
        "temporal_pairs": temporal_pairs,
        "behavioral_overlap": Sbehavior,
        "Ndev": Ndev,
        "Nben": Nben,
        "Nip": Nip,
        "Ntemp": Ntemp,
        "Nbeh": Nbeh,
        "evidence": evidence_items,
    }
