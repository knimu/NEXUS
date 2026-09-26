"""
Service Layer for NEXUS Member 4 Dashboard.
Handles data consumption, dynamic metric calculations, graph topology generation,
adversarial resilience comparisons, and persistent audit log management.

Note: ground_truth_cluster and scenario_id are intentionally excluded from runtime decisions.
"""

import json
import os
from datetime import datetime, timezone
import pandas as pd

from graph_engine.relationships import extract_shared_relationships
from graph_engine.graph_builder import build_account_graph
from graph_engine.cluster_detector import detect_candidate_clusters
from evidence.evidence_engine import extract_cluster_evidence
from evidence.scoring import calculate_cluster_score

SYNTHETIC_DATA_PATH = os.path.join("data", "generated", "synthetic_data.csv")
RISK_RESULTS_PATH = os.path.join("data", "generated", "risk_results.csv")
CLUSTER_RESULTS_PATH = os.path.join("data", "generated", "cluster_results.json")
AUDIT_LOG_PATH = os.path.join("data", "generated", "audit_log.json")
ADVERSARIAL_DIR = os.path.join("data", "generated", "adversarial")


def load_synthetic_df() -> pd.DataFrame:
    """Load synthetic_data.csv safely."""
    if os.path.exists(SYNTHETIC_DATA_PATH):
        return pd.read_csv(SYNTHETIC_DATA_PATH)
    return pd.DataFrame()


def load_risk_df() -> pd.DataFrame:
    """Load risk_results.csv safely."""
    if os.path.exists(RISK_RESULTS_PATH):
        return pd.read_csv(RISK_RESULTS_PATH)
    return pd.DataFrame()


def load_cluster_results() -> list[dict]:
    """Load cluster_results.json safely."""
    if os.path.exists(CLUSTER_RESULTS_PATH):
        try:
            with open(CLUSTER_RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def get_overview_metrics() -> dict:
    """Calculate dynamic overview metrics from actual pipeline outputs."""
    syn_df = load_synthetic_df()
    clusters = load_cluster_results()

    total_accounts = int(syn_df["account_id"].nunique()) if not syn_df.empty and "account_id" in syn_df.columns else 0
    cluster_count = len(clusters)

    clustered_acc_set = set()
    for c in clusters:
        for acc in c.get("account_ids", []):
            clustered_acc_set.add(str(acc).strip())
    clustered_account_count = len(clustered_acc_set)

    high_severity_count = sum(1 for c in clusters if c.get("severity") == "HIGH")
    medium_severity_count = sum(1 for c in clusters if c.get("severity") == "MEDIUM")
    low_severity_count = sum(1 for c in clusters if c.get("severity") == "LOW")

    total_evidence_count = sum(len(c.get("evidence", [])) for c in clusters)

    risks = [c.get("cluster_risk", 0.0) for c in clusters]
    avg_risk = round(sum(risks) / len(risks), 2) if risks else 0.0

    confs = [c.get("confidence", 0.0) for c in clusters]
    avg_conf = round(sum(confs) / len(confs), 4) if confs else 0.0

    return {
        "total_accounts": total_accounts,
        "cluster_count": cluster_count,
        "clustered_account_count": clustered_account_count,
        "high_severity_count": high_severity_count,
        "medium_severity_count": medium_severity_count,
        "low_severity_count": low_severity_count,
        "total_evidence_count": total_evidence_count,
        "average_cluster_risk": avg_risk,
        "average_confidence": avg_conf,
    }


def get_all_clusters() -> list[dict]:
    """Get all candidate clusters."""
    return load_cluster_results()


def get_cluster_detail(cluster_id: str) -> dict | None:
    """Get full details for a specific cluster including account details and graph topology."""
    clusters = load_cluster_results()
    target = None
    for c in clusters:
        if c.get("cluster_id") == cluster_id:
            target = c
            break

    if target is None:
        return None

    syn_df = load_synthetic_df()
    risk_df = load_risk_df()

    acc_ids = [str(a).strip() for a in target.get("account_ids", [])]

    # Map individual account information
    accounts_detail = []
    risk_map = {}
    if not risk_df.empty and "account_id" in risk_df.columns:
        for _, row in risk_df.iterrows():
            risk_map[str(row["account_id"]).strip()] = {
                "risk_score": float(row.get("risk_score", 0)),
                "risk_level": str(row.get("risk_level", "LOW")),
                "risk_features": str(row.get("risk_features", "")),
            }

    if not syn_df.empty and "account_id" in syn_df.columns:
        sub_syn = syn_df[syn_df["account_id"].astype(str).str.strip().isin(set(acc_ids))]
        for _, row in sub_syn.iterrows():
            acc_id = str(row["account_id"]).strip()
            r_info = risk_map.get(acc_id, {"risk_score": 0.0, "risk_level": "LOW", "risk_features": ""})
            accounts_detail.append({
                "account_id": acc_id,
                "device_id": str(row.get("device_id", "")),
                "ip_id": str(row.get("ip_id", "")),
                "beneficiary_id": str(row.get("beneficiary_id", "")),
                "timestamp": str(row.get("timestamp", "")),
                "amount": float(row.get("amount", 0)),
                "behavior_features": str(row.get("behavior_features", "")),
                "risk_score": r_info["risk_score"],
                "risk_level": r_info["risk_level"],
            })

    # Sort accounts by ID
    accounts_detail.sort(key=lambda x: x["account_id"])

    # Build Cytoscape graph nodes and edges for visual rendering
    nodes = []
    edges = []

    # Account nodes
    for acc in accounts_detail:
        nodes.append({
            "data": {
                "id": acc["account_id"],
                "label": acc["account_id"],
                "type": "account",
                "risk_score": acc["risk_score"],
                "risk_level": acc["risk_level"],
            }
        })

    # Shared Attribute Nodes & Edges
    for dev in target.get("shared_devices", []):
        dev_node_id = f"DEV_{dev}"
        nodes.append({"data": {"id": dev_node_id, "label": f"Device: {dev}", "type": "device"}})
        for acc in accounts_detail:
            if acc["device_id"] == dev:
                edges.append({
                    "data": {
                        "id": f"e_{acc['account_id']}_{dev_node_id}",
                        "source": acc["account_id"],
                        "target": dev_node_id,
                        "label": "shared_device",
                        "type": "shared_device"
                    }
                })

    for ip in target.get("shared_ips", []):
        ip_node_id = f"IP_{ip}"
        nodes.append({"data": {"id": ip_node_id, "label": f"IP: {ip}", "type": "ip"}})
        for acc in accounts_detail:
            if acc["ip_id"] == ip:
                edges.append({
                    "data": {
                        "id": f"e_{acc['account_id']}_{ip_node_id}",
                        "source": acc["account_id"],
                        "target": ip_node_id,
                        "label": "shared_ip",
                        "type": "shared_ip"
                    }
                })

    for ben in target.get("shared_beneficiaries", []):
        ben_node_id = f"BEN_{ben}"
        nodes.append({"data": {"id": ben_node_id, "label": f"Beneficiary: {ben}", "type": "beneficiary"}})
        for acc in accounts_detail:
            if acc["beneficiary_id"] == ben:
                edges.append({
                    "data": {
                        "id": f"e_{acc['account_id']}_{ben_node_id}",
                        "source": acc["account_id"],
                        "target": ben_node_id,
                        "label": "shared_beneficiary",
                        "type": "shared_beneficiary"
                    }
                })

    result = dict(target)
    result["accounts_detail"] = accounts_detail
    result["graph_topology"] = {"nodes": nodes, "edges": edges}

    return result


def get_audit_log() -> list[dict]:
    """Retrieve recorded human decisions, newest first."""
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
                logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return logs
        except Exception:
            return []
    return []


def record_decision(cluster_id: str, decision: str, reason: str) -> bool:
    """
    Validate and record a human analyst decision to audit_log.json.

    Parameters:
        cluster_id (str): Existing candidate cluster ID.
        decision (str): Must be 'REVIEW', 'ALLOW', or 'ESCALATE'.
        reason (str): Mandatory non-empty reason string.

    Returns:
        bool: True if recorded successfully.
    """
    # 1. Validate decision value
    valid_decisions = {"REVIEW", "ALLOW", "ESCALATE"}
    if not decision or str(decision).upper() not in valid_decisions:
        raise ValueError(f"Invalid decision. Must be one of: {sorted(list(valid_decisions))}")

    # 2. Validate reason string
    if not reason or not isinstance(reason, str) or not reason.strip():
        raise ValueError("Reason is mandatory and cannot be empty.")

    # 3. Validate cluster_id exists
    clusters = load_cluster_results()
    cluster_exists = any(c.get("cluster_id") == cluster_id for c in clusters)
    if not cluster_exists:
        raise ValueError(f"Cluster ID '{cluster_id}' does not exist.")

    # 4. Construct audit entry
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cluster_id": cluster_id,
        "decision": str(decision).upper(),
        "reason": reason.strip(),
    }

    # 5. Persist atomically to audit_log.json
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    logs.append(entry)

    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    return True


def simulate_adversarial_attack(attack_type: str) -> list[dict]:
    """
    Helper function: execute infrastructure rotation on synthetic data and recalculate Member 2 pipeline
    to evaluate resilience under attack scenarios.
    """
    syn_df = load_synthetic_df()
    risk_df = load_risk_df()

    if syn_df.empty:
        return []

    mod_df = syn_df.copy()

    if attack_type == "device_rotation":
        # Each account gets a unique device ID
        mod_df["device_id"] = mod_df["account_id"].apply(lambda acc: f"D_ROT_{acc}")
    elif attack_type == "ip_rotation":
        # Each account gets a unique IP ID
        mod_df["ip_id"] = mod_df["account_id"].apply(lambda acc: f"IP_ROT_{acc}")
    elif attack_type == "combined":
        # Both device and IP rotated
        mod_df["device_id"] = mod_df["account_id"].apply(lambda acc: f"D_ROT_{acc}")
        mod_df["ip_id"] = mod_df["account_id"].apply(lambda acc: f"IP_ROT_{acc}")
    else:
        raise ValueError(f"Unknown attack_type: '{attack_type}'")

    rels = extract_shared_relationships(mod_df)
    G = build_account_graph(mod_df, rels)
    candidate_clusters = detect_candidate_clusters(G)

    results = []
    for cluster in candidate_clusters:
        c_id = cluster["cluster_id"]
        c_accs = cluster["account_ids"]
        ev = extract_cluster_evidence(c_accs, mod_df, G)
        sc = calculate_cluster_score(c_accs, ev, risk_df)
        results.append({
            "cluster_id": c_id,
            "account_ids": c_accs,
            "shared_devices": ev["shared_devices"],
            "shared_ips": ev["shared_ips"],
            "shared_beneficiaries": ev["shared_beneficiaries"],
            "Ndev": sc["Ndev"],
            "Nben": sc["Nben"],
            "Nip": sc["Nip"],
            "Ntemp": sc["Ntemp"],
            "Nbeh": sc["Nbeh"],
            "Trel": sc["Trel"],
            "cluster_risk": sc["cluster_risk"],
            "severity": sc["severity"],
            "confidence": sc["confidence"],
            "evidence": ev["evidence"],
        })

    return results


def summarize_cluster_list(clusters: list[dict]) -> dict:
    """Summarize cluster metrics for adversarial comparison."""
    if not clusters:
        return {
            "cluster_count": 0,
            "clustered_account_count": 0,
            "shared_device_count": 0,
            "shared_ip_count": 0,
            "shared_beneficiary_count": 0,
            "total_evidence_count": 0,
            "average_cluster_risk": 0.0,
            "average_confidence": 0.0,
        }

    acc_set = set()
    dev_set = set()
    ip_set = set()
    ben_set = set()
    total_ev = 0
    risks = []
    confs = []

    for c in clusters:
        for acc in c.get("account_ids", []):
            acc_set.add(acc)
        for dev in c.get("shared_devices", []):
            dev_set.add(dev)
        for ip in c.get("shared_ips", []):
            ip_set.add(ip)
        for ben in c.get("shared_beneficiaries", []):
            ben_set.add(ben)
        total_ev += len(c.get("evidence", []))
        risks.append(c.get("cluster_risk", 0.0))
        confs.append(c.get("confidence", 0.0))

    return {
        "cluster_count": len(clusters),
        "clustered_account_count": len(acc_set),
        "shared_device_count": len(dev_set),
        "shared_ip_count": len(ip_set),
        "shared_beneficiary_count": len(ben_set),
        "total_evidence_count": total_ev,
        "average_cluster_risk": round(sum(risks) / len(risks), 2) if risks else 0.0,
        "average_confidence": round(sum(confs) / len(confs), 4) if confs else 0.0,
    }


def get_adversarial_comparison(attack_type: str | None = None) -> dict:
    """
    Retrieve or compute adversarial resilience comparison results.

    Supports:
    - baseline
    - device_rotation
    - ip_rotation
    - combined
    """
    valid_attacks = {"baseline", "device_rotation", "ip_rotation", "combined"}

    if attack_type and attack_type not in valid_attacks:
        raise ValueError(f"Invalid attack type '{attack_type}'. Must be one of: {sorted(list(valid_attacks))}")

    # Baseline metrics
    baseline_clusters = load_cluster_results()
    baseline_summary = summarize_cluster_list(baseline_clusters)

    # Check if Member 3 output files exist in data/generated/adversarial/
    attack_data = {}

    for at in ["device_rotation", "ip_rotation", "combined"]:
        file_path = os.path.join(ADVERSARIAL_DIR, f"{at}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    at_clusters = json.load(f)
            except Exception:
                at_clusters = simulate_adversarial_attack(at)
        else:
            at_clusters = simulate_adversarial_attack(at)

        at_summary = summarize_cluster_list(at_clusters)

        # Calculate delta comparison against baseline
        evidence_survival = (
            round((at_summary["total_evidence_count"] / baseline_summary["total_evidence_count"]) * 100.0, 2)
            if baseline_summary["total_evidence_count"] > 0 else 100.0
        )

        attack_data[at] = {
            "attack_type": at,
            "clusters": at_clusters,
            "summary": at_summary,
            "comparison": {
                "cluster_count": {
                    "baseline": baseline_summary["cluster_count"],
                    "attack": at_summary["cluster_count"],
                    "change": at_summary["cluster_count"] - baseline_summary["cluster_count"],
                },
                "clustered_account_count": {
                    "baseline": baseline_summary["clustered_account_count"],
                    "attack": at_summary["clustered_account_count"],
                    "change": at_summary["clustered_account_count"] - baseline_summary["clustered_account_count"],
                },
                "shared_device_count": {
                    "baseline": baseline_summary["shared_device_count"],
                    "attack": at_summary["shared_device_count"],
                    "change": at_summary["shared_device_count"] - baseline_summary["shared_device_count"],
                },
                "shared_ip_count": {
                    "baseline": baseline_summary["shared_ip_count"],
                    "attack": at_summary["shared_ip_count"],
                    "change": at_summary["shared_ip_count"] - baseline_summary["shared_ip_count"],
                },
                "shared_beneficiary_count": {
                    "baseline": baseline_summary["shared_beneficiary_count"],
                    "attack": at_summary["shared_beneficiary_count"],
                    "change": at_summary["shared_beneficiary_count"] - baseline_summary["shared_beneficiary_count"],
                },
                "total_evidence_count": {
                    "baseline": baseline_summary["total_evidence_count"],
                    "attack": at_summary["total_evidence_count"],
                    "change": at_summary["total_evidence_count"] - baseline_summary["total_evidence_count"],
                },
                "average_cluster_risk": {
                    "baseline": baseline_summary["average_cluster_risk"],
                    "attack": at_summary["average_cluster_risk"],
                    "change": round(at_summary["average_cluster_risk"] - baseline_summary["average_cluster_risk"], 2),
                },
                "average_confidence": {
                    "baseline": baseline_summary["average_confidence"],
                    "attack": at_summary["average_confidence"],
                    "change": round(at_summary["average_confidence"] - baseline_summary["average_confidence"], 4),
                },
                "evidence_survival_percentage": evidence_survival,
            }
        }

    if attack_type and attack_type != "baseline":
        return attack_data.get(attack_type, {})

    return {
        "baseline_summary": baseline_summary,
        "available_attacks": list(attack_data.keys()),
        "attack_comparisons": attack_data,
    }
