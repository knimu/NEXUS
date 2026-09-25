"""
Deterministic Cluster Risk Scoring & Confidence Module for NEXUS Member 2.

Calculates explainable cluster-level risk scores, severity classifications, and
evidence-strength confidence metrics using Member 1's individual risk scores
and network evidence.

Note: ground_truth_cluster and scenario_id are intentionally NOT used.
"""

import pandas as pd


def calculate_cluster_score(
    cluster_accounts: list[str],
    evidence_meta: dict,
    risk_results_df: pd.DataFrame
) -> dict:
    """
    Calculate deterministic cluster risk, severity classification, and confidence.

    Parameters:
        cluster_accounts (list[str]): Account IDs in candidate cluster.
        evidence_meta (dict): Output dictionary from extract_cluster_evidence.
        risk_results_df (pd.DataFrame): Member 1 risk results DataFrame.

    Returns:
        dict: Complete scoring metrics including cluster_risk, severity, and confidence.
    """
    if not cluster_accounts:
        raise ValueError("cluster_accounts list cannot be empty.")

    # 1. Base Individual Risk Calculation
    risk_scores = []
    if risk_results_df is not None and not risk_results_df.empty and "account_id" in risk_results_df.columns:
        # Create lookup dictionary for risk_score
        risk_map = dict(
            zip(
                risk_results_df["account_id"].astype(str).str.strip(),
                pd.to_numeric(risk_results_df["risk_score"], errors="coerce").fillna(0.0)
            )
        )
        for acc in cluster_accounts:
            acc_str = str(acc).strip()
            score = risk_map.get(acc_str, 0.0)
            risk_scores.append(float(score))
    else:
        risk_scores = [0.0] * len(cluster_accounts)

    max_risk = max(risk_scores) if risk_scores else 0.0
    mean_risk = (sum(risk_scores) / len(risk_scores)) if risk_scores else 0.0
    base_risk = 0.60 * max_risk + 0.40 * mean_risk

    # 2. Extract Evidence Quantities
    Ndev = int(evidence_meta.get("Ndev", 0))
    Nben = int(evidence_meta.get("Nben", 0))
    Nip = int(evidence_meta.get("Nip", 0))
    Ntemp = int(evidence_meta.get("Ntemp", 0))
    Nbeh = int(evidence_meta.get("Nbeh", 0))

    # 3. Relationship Type Diversity (Trel)
    relationship_types = []
    if Ndev >= 1:
        relationship_types.append("shared_device")
    if Nip >= 1:
        relationship_types.append("shared_ip")
    if Nben >= 1:
        relationship_types.append("shared_beneficiary")
    
    Trel = len(relationship_types)

    # Diversity Bonus
    if Trel >= 3:
        diversity_bonus = 30.0
    elif Trel == 2:
        diversity_bonus = 15.0
    else:
        diversity_bonus = 0.0

    # Temporal Bonus
    temporal_bonus = 10.0 if Ntemp >= 1 else 0.0

    # Behavioral Bonus
    behavioral_bonus = min(15.0, 5.0 * float(Nbeh))

    # 4. Network Raw Score
    network_raw = (
        20.0 * float(Ndev)
        + 25.0 * float(Nben)
        + 5.0 * float(Nip)
        + diversity_bonus
        + temporal_bonus
        + behavioral_bonus
    )

    # 5. Network Contribution Cap Rule
    # If cluster contains ONLY shared_ip relationships (no shared_device and no shared_beneficiary)
    if Ndev == 0 and Nben == 0:
        network_contribution = min(network_raw, 15.0)
    else:
        network_contribution = min(network_raw, 50.0)

    # 6. Final Bounded Cluster Risk Score [0, 100]
    cluster_risk = min(100.0, max(0.0, base_risk + network_contribution))

    # 7. Severity Classification
    if cluster_risk < 30.0:
        severity = "LOW"
    elif cluster_risk < 60.0:
        severity = "MEDIUM"
    else:
        severity = "HIGH"

    # 8. Evidence-Strength Confidence Metric
    temporal_indicator = 1 if Ntemp > 0 else 0
    Nitems = Ndev + Nben + Nip + temporal_indicator + Nbeh

    if Ntemp > 0 and Nbeh > 0:
        support_factor = 1.0
    elif (Ntemp > 0 and Nbeh == 0) or (Ntemp == 0 and Nbeh > 0):
        support_factor = 0.5
    else:
        support_factor = 0.0

    raw_conf = (
        0.40 * (float(Trel) / 3.0)
        + 0.35 * min(1.0, float(Nitems) / 5.0)
        + 0.25 * support_factor
    )
    confidence = min(1.0, max(0.10, raw_conf))

    return {
        "relationship_types": relationship_types,
        "Trel": Trel,
        "Ndev": Ndev,
        "Nben": Nben,
        "Nip": Nip,
        "Ntemp": Ntemp,
        "Nbeh": Nbeh,
        "Nitems": Nitems,
        "support_factor": support_factor,
        "base_risk": round(base_risk, 2),
        "diversity_bonus": round(diversity_bonus, 2),
        "temporal_bonus": round(temporal_bonus, 2),
        "behavioral_bonus": round(behavioral_bonus, 2),
        "network_raw": round(network_raw, 2),
        "network_contribution": round(network_contribution, 2),
        "cluster_risk": round(cluster_risk, 2),
        "severity": severity,
        "confidence": round(confidence, 4),
    }
