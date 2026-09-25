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


SYNTHETIC_DATA_PATH = os.path.join(
    "data", "generated", "synthetic_data.csv"
)

RISK_RESULTS_PATH = os.path.join(
    "data", "generated", "risk_results.csv"
)

OUTPUT_JSON_PATH = os.path.join(
    "data", "generated", "cluster_results.json"
)

OUTPUT_CSV_PATH = os.path.join(
    "data", "generated", "cluster_results.csv"
)


def run_pipeline(
    synthetic_data_path=SYNTHETIC_DATA_PATH,
    risk_results_path=RISK_RESULTS_PATH,
    output_json_path=OUTPUT_JSON_PATH,
    output_csv_path=OUTPUT_CSV_PATH,
) -> list[dict]:
    """
    Execute the full Member 2 graph + evidence pipeline.

    Input paths and output paths can be customized so that
    adversarial experiments can run without overwriting
    baseline results.
    """

    print("=" * 60)
    print(" NEXUS MEMBER 2 — GRAPH + EVIDENCE PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load Inputs
    # ---------------------------------------------------------

    if not os.path.exists(synthetic_data_path):
        raise FileNotFoundError(
            f"Input file missing: {synthetic_data_path}"
        )

    if not os.path.exists(risk_results_path):
        raise FileNotFoundError(
            f"Input file missing: {risk_results_path}"
        )

    print(
        f"[1/7] Loading data from "
        f"{synthetic_data_path} & {risk_results_path}..."
    )

    synthetic_df = pd.read_csv(synthetic_data_path)
    risk_results_df = pd.read_csv(risk_results_path)

    print(
        f"      Synthetic events loaded: "
        f"{len(synthetic_df)} rows."
    )

    print(
        f"      Individual risk results loaded: "
        f"{len(risk_results_df)} rows."
    )

    # ---------------------------------------------------------
    # 2. Extract Relationships
    # ---------------------------------------------------------

    print(
        "[2/7] Extracting shared attribute relationships..."
    )

    relationships = extract_shared_relationships(
        synthetic_df
    )

    print(
        f"      Extracted "
        f"{len(relationships)} pairwise relationship records."
    )

    # ---------------------------------------------------------
    # 3. Build Graph
    # ---------------------------------------------------------

    print(
        "[3/7] Building NetworkX account graph..."
    )

    G = build_account_graph(
        synthetic_df,
        relationships
    )

    print(
        f"      Graph constructed: "
        f"{G.number_of_nodes()} nodes, "
        f"{G.number_of_edges()} edges."
    )

    # ---------------------------------------------------------
    # 4. Detect Candidate Clusters
    # ---------------------------------------------------------

    print(
        "[4/7] Detecting candidate clusters via "
        "connected components..."
    )

    candidate_clusters = detect_candidate_clusters(G)

    print(
        f"      Detected "
        f"{len(candidate_clusters)} candidate clusters "
        f"(size >= 2)."
    )

    # ---------------------------------------------------------
    # 5. Extract Evidence & Compute Scores
    # ---------------------------------------------------------

    print(
        "[5/7] Extracting post-detection evidence "
        "& calculating cluster risk..."
    )

    cluster_results = []

    for cluster in candidate_clusters:

        c_id = cluster["cluster_id"]
        c_accounts = cluster["account_ids"]

        # Extract post-detection evidence.
        evidence_meta = extract_cluster_evidence(
            c_accounts,
            synthetic_df,
            G
        )

        # Compute cluster risk and confidence.
        scores = calculate_cluster_score(
            c_accounts,
            evidence_meta,
            risk_results_df
        )

        # Merge into the output contract record.
        record = {
            "cluster_id": c_id,
            "account_ids": c_accounts,

            "shared_devices": (
                evidence_meta["shared_devices"]
            ),

            "shared_ips": (
                evidence_meta["shared_ips"]
            ),

            "shared_beneficiaries": (
                evidence_meta["shared_beneficiaries"]
            ),

            "relationship_types": (
                scores["relationship_types"]
            ),

            "temporal_pairs": (
                evidence_meta["temporal_pairs"]
            ),

            "behavioral_overlap": (
                evidence_meta["behavioral_overlap"]
            ),

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
            "network_contribution": (
                scores["network_contribution"]
            ),

            "cluster_risk": scores["cluster_risk"],
            "severity": scores["severity"],
            "confidence": scores["confidence"],

            "evidence": evidence_meta["evidence"],
        }

        cluster_results.append(record)

    # ---------------------------------------------------------
    # 6. Save Outputs
    # ---------------------------------------------------------

    print(
        "[6/7] Saving structured outputs..."
    )

    # Create output directories if required.
    json_directory = os.path.dirname(output_json_path)

    if json_directory:
        os.makedirs(
            json_directory,
            exist_ok=True
        )

    csv_directory = os.path.dirname(output_csv_path)

    if csv_directory:
        os.makedirs(
            csv_directory,
            exist_ok=True
        )

    # Save JSON output.
    with open(
        output_json_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            cluster_results,
            f,
            indent=2
        )

    print(
        f"      Saved JSON: "
        f"{output_json_path}"
    )

    # ---------------------------------------------------------
    # Build CSV representation
    # ---------------------------------------------------------

    csv_rows = []

    for r in cluster_results:

        csv_rows.append({
            "cluster_id": r["cluster_id"],
            "account_count": len(
                r["account_ids"]
            ),

            "account_ids": ";".join(
                r["account_ids"]
            ),

            "shared_devices": ";".join(
                r["shared_devices"]
            ),

            "shared_ips": ";".join(
                r["shared_ips"]
            ),

            "shared_beneficiaries": ";".join(
                r["shared_beneficiaries"]
            ),

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

    csv_df.to_csv(
        output_csv_path,
        index=False
    )

    print(
        f"      Saved CSV: "
        f"{output_csv_path}"
    )

    # ---------------------------------------------------------
    # 7. Console Summary
    # ---------------------------------------------------------

    print(
        "[7/7] Pipeline completed successfully!"
    )

    print("=" * 60)
    print(
        " CLUSTER DETECTION & RISK SUMMARY"
    )
    print("=" * 60)

    print(
        f"{'Cluster ID':<12} | "
        f"{'Accounts':<10} | "
        f"{'Risk':<6} | "
        f"{'Severity':<8} | "
        f"{'Conf':<6} | "
        f"{'Ndev/Nben/Nip/Ntemp/Nbeh'}"
    )

    print("-" * 60)

    for r in cluster_results:

        acc_str = (
            f"{len(r['account_ids'])} accs"
        )

        counts_str = (
            f"{r['Ndev']}/"
            f"{r['Nben']}/"
            f"{r['Nip']}/"
            f"{r['Ntemp']}/"
            f"{r['Nbeh']}"
        )

        print(
            f"{r['cluster_id']:<12} | "
            f"{acc_str:<10} | "
            f"{r['cluster_risk']:<6.2f} | "
            f"{r['severity']:<8} | "
            f"{r['confidence']:<6.4f} | "
            f"{counts_str}"
        )

    print("=" * 60)

    return cluster_results


if __name__ == "__main__":

    try:
        run_pipeline()

    except Exception as e:

        print(
            f"Error running pipeline: {e}",
            file=sys.stderr
        )

        sys.exit(1)

