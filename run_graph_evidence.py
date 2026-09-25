"""
Main Integration Entry Point for NEXUS Member 2 Pipeline.

Workflow:
Synthetic Events + Individual Risk
  -> Relationship Extraction
  -> NetworkX Graph Construction
  -> Candidate Cluster Detection
  -> Post-Detection Evidence Generation
  -> Deterministic Cluster Risk Scoring, Severity & Confidence
  -> Save cluster_results.json and cluster_results.csv
"""

import json
import os
import sys
import pandas as pd

from graph_engine.relationships import extract_shared_relationships
from graph_engine.graph_builder import build_account_graph
from graph_engine.cluster_detector import detect_candidate_clusters
from evidence.evidence_engine import extract_cluster_evidence
from evidence.scoring import calculate_cluster_score


SYNTHETIC_DATA_PATH = os.path.join("data", "generated", "synthetic_data.csv")
RISK_RESULTS_PATH = os.path.join("data", "generated", "risk_results.csv")
OUTPUT_JSON_PATH = os.path.join("data", "generated", "cluster_results.json")
OUTPUT_CSV_PATH = os.path.join("data", "generated", "cluster_results.csv")


def run_pipeline() -> list[dict]:
    """Execute full Member 2 pipeline and return structured cluster results."""
    print("=" * 60)
    print(" NEXUS MEMBER 2 — GRAPH + EVIDENCE PIPELINE")
    print("=" * 60)

    # 1. Load Inputs
    if not os.path.exists(SYNTHETIC_DATA_PATH):
        raise FileNotFoundError(f"Input file missing: {SYNTHETIC_DATA_PATH}")

    if not os.path.exists(RISK_RESULTS_PATH):
        raise FileNotFoundError(f"Input file missing: {RISK_RESULTS_PATH}")

    print(f"[1/7] Loading data from {SYNTHETIC_DATA_PATH} & {RISK_RESULTS_PATH}...")
    synthetic_df = pd.read_csv(SYNTHETIC_DATA_PATH)
    risk_results_df = pd.read_csv(RISK_RESULTS_PATH)

    print(f"      Synthetic events loaded: {len(synthetic_df)} rows.")
    print(f"      Individual risk results loaded: {len(risk_results_df)} rows.")

    # 2. Extract Relationships
    print("[2/7] Extracting shared attribute relationships...")
    relationships = extract_shared_relationships(synthetic_df)
    print(f"      Extracted {len(relationships)} pairwise relationship records.")

    # 3. Build Graph
    print("[3/7] Building NetworkX account graph...")
    G = build_account_graph(synthetic_df, relationships)
    print(f"      Graph constructed: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

    # 4. Detect Candidate Clusters
    print("[4/7] Detecting candidate clusters via connected components...")
    candidate_clusters = detect_candidate_clusters(G)
    print(f"      Detected {len(candidate_clusters)} candidate clusters (size >= 2).")

    # 5. Extract Evidence & Compute Scores for each Cluster
    print("[5/7] Extracting post-detection evidence & calculating cluster risk...")
    cluster_results = []

    for cluster in candidate_clusters:
        c_id = cluster["cluster_id"]
        c_accounts = cluster["account_ids"]

        # Extract Evidence
        evidence_meta = extract_cluster_evidence(c_accounts, synthetic_df, G)

        # Compute Risk & Confidence Scores
        scores = calculate_cluster_score(c_accounts, evidence_meta, risk_results_df)

        # Merge into output contract record
        record = {
            "cluster_id": c_id,
            "account_ids": c_accounts,
            "shared_devices": evidence_meta["shared_devices"],
            "shared_ips": evidence_meta["shared_ips"],
            "shared_beneficiaries": evidence_meta["shared_beneficiaries"],
            "relationship_types": scores["relationship_types"],
            "temporal_pairs": evidence_meta["temporal_pairs"],
            "behavioral_overlap": evidence_meta["behavioral_overlap"],
            "Ndev": scores["Ndev"],
            "Nben": scores["Nben"],
            "Nip": scores["Nip"],
            "Ntemp": scores["Ntemp"],
            "Nbeh": scores["Nbeh"],
            "Trel": scores["Trel"],
            "Nitems": scores["Nitems"],
            "support_factor": scores["support_factor"],
            "base_risk": scores["base_risk"],
            "diversity_bonus": scores["diversity_bonus"],
            "temporal_bonus": scores["temporal_bonus"],
            "behavioral_bonus": scores["behavioral_bonus"],
            "network_raw": scores["network_raw"],
            "network_contribution": scores["network_contribution"],
            "cluster_risk": scores["cluster_risk"],
            "severity": scores["severity"],
            "confidence": scores["confidence"],
            "evidence": evidence_meta["evidence"],
        }
        cluster_results.append(record)

    # 6. Save Outputs
    print("[6/7] Saving structured outputs...")
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cluster_results, f, indent=2)
    print(f"      Saved JSON: {OUTPUT_JSON_PATH}")

    # Build CSV representation for dashboard/tabular use
    csv_rows = []
    for r in cluster_results:
        csv_rows.append({
            "cluster_id": r["cluster_id"],
            "account_count": len(r["account_ids"]),
            "account_ids": ";".join(r["account_ids"]),
            "shared_devices": ";".join(r["shared_devices"]),
            "shared_ips": ";".join(r["shared_ips"]),
            "shared_beneficiaries": ";".join(r["shared_beneficiaries"]),
            "Ndev": r["Ndev"],
            "Nben": r["Nben"],
            "Nip": r["Nip"],
            "Ntemp": r["Ntemp"],
            "Nbeh": r["Nbeh"],
            "Trel": r["Trel"],
            "cluster_risk": r["cluster_risk"],
            "severity": r["severity"],
            "confidence": r["confidence"],
        })

    csv_df = pd.DataFrame(csv_rows)
    csv_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"      Saved CSV:  {OUTPUT_CSV_PATH}")

    # 7. Console Summary
    print("[7/7] Pipeline completed successfully!")
    print("=" * 60)
    print(" CLUSTER DETECTION & RISK SUMMARY")
    print("=" * 60)
    print(f"{'Cluster ID':<12} | {'Accounts':<10} | {'Risk':<6} | {'Severity':<8} | {'Conf':<6} | {'Ndev/Nben/Nip/Ntemp/Nbeh'}")
    print("-" * 60)
    for r in cluster_results:
        acc_str = f"{len(r['account_ids'])} accs"
        counts_str = f"{r['Ndev']}/{r['Nben']}/{r['Nip']}/{r['Ntemp']}/{r['Nbeh']}"
        print(f"{r['cluster_id']:<12} | {acc_str:<10} | {r['cluster_risk']:<6.2f} | {r['severity']:<8} | {r['confidence']:<6.4f} | {counts_str}")
    print("=" * 60)

    return cluster_results


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"Error running pipeline: {e}", file=sys.stderr)
        sys.exit(1)
