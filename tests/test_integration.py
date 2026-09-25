"""
Integration Tests for NEXUS Member 2 Pipeline.
Runs end-to-end validation on real dataset files without using ground_truth_cluster or scenario_id during detection.
"""

import os
import pytest
import pandas as pd

from graph_engine.relationships import extract_shared_relationships
from graph_engine.graph_builder import build_account_graph
from graph_engine.cluster_detector import detect_candidate_clusters
from evidence.evidence_engine import extract_cluster_evidence
from evidence.scoring import calculate_cluster_score
from run_graph_evidence import run_pipeline


SYNTHETIC_DATA_PATH = os.path.join("data", "generated", "synthetic_data.csv")
RISK_RESULTS_PATH = os.path.join("data", "generated", "risk_results.csv")


def test_integration_full_pipeline_run():
    """Verify that run_pipeline executes successfully and writes output files."""
    results = run_pipeline()
    assert isinstance(results, list)
    assert len(results) > 0

    assert os.path.exists("data/generated/cluster_results.json")
    assert os.path.exists("data/generated/cluster_results.csv")


def test_scenario_fraud_obvious():
    """Test FRAUD_OBVIOUS accounts (A101-A110)."""
    df = pd.read_csv(SYNTHETIC_DATA_PATH)
    risk_df = pd.read_csv(RISK_RESULTS_PATH)

    rels = extract_shared_relationships(df)
    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    # Find cluster containing A101
    fraud_cluster = None
    for c in clusters:
        if "A101" in c["account_ids"]:
            fraud_cluster = c
            break

    assert fraud_cluster is not None
    # All A101-A110 should be in this single connected component
    for acc in ["A101", "A102", "A103", "A104", "A105", "A106", "A107", "A108", "A109", "A110"]:
        assert acc in fraud_cluster["account_ids"]

    ev = extract_cluster_evidence(fraud_cluster["account_ids"], df, G)
    scores = calculate_cluster_score(fraud_cluster["account_ids"], ev, risk_df)

    assert scores["severity"] == "HIGH"
    assert scores["cluster_risk"] >= 60.0
    assert scores["confidence"] >= 0.75
    assert scores["Trel"] == 3  # shared_device, shared_ip, shared_beneficiary


def test_scenario_legit_shared():
    """Test LEGIT_SHARED accounts (A001-A010)."""
    df = pd.read_csv(SYNTHETIC_DATA_PATH)
    risk_df = pd.read_csv(RISK_RESULTS_PATH)

    rels = extract_shared_relationships(df)
    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    # Find clusters containing A001-A010
    legit_clusters = [c for c in clusters if any(acc in c["account_ids"] for acc in ["A001", "A002"])]
    assert len(legit_clusters) > 0

    for lc in legit_clusters:
        ev = extract_cluster_evidence(lc["account_ids"], df, G)
        scores = calculate_cluster_score(lc["account_ids"], ev, risk_df)

        # LEGIT_SHARED only shares IP -> network contribution capped at 15.0
        assert scores["Ndev"] == 0
        assert scores["Nben"] == 0
        assert scores["Nip"] >= 1
        assert scores["network_contribution"] <= 15.0
        assert scores["severity"] == "LOW"
        assert scores["cluster_risk"] < 30.0


def test_scenario_fraud_mixed():
    """Test FRAUD_MIXED accounts (A401-A410)."""
    df = pd.read_csv(SYNTHETIC_DATA_PATH)
    risk_df = pd.read_csv(RISK_RESULTS_PATH)

    rels = extract_shared_relationships(df)
    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    mixed_cluster = None
    for c in clusters:
        if "A401" in c["account_ids"]:
            mixed_cluster = c
            break

    assert mixed_cluster is not None
    ev = extract_cluster_evidence(mixed_cluster["account_ids"], df, G)
    scores = calculate_cluster_score(mixed_cluster["account_ids"], ev, risk_df)

    # FRAUD_MIXED has unique devices (Ndev=0) but shared beneficiary (Nben >= 1) and shared IP (Nip >= 1)
    assert scores["Ndev"] == 0
    assert scores["Nben"] >= 1
    assert scores["Nip"] >= 1
    assert scores["Trel"] == 2
    assert scores["severity"] in ["MEDIUM", "HIGH"]


def test_isolated_accounts_no_candidate_cluster():
    """Verify that isolated accounts do not form candidate clusters."""
    df = pd.DataFrame({
        "account_id": ["ISO_01", "ISO_02"],
        "device_id": ["D999", "D998"],
        "ip_id": ["IP999", "IP998"],
        "beneficiary_id": ["B999", "B998"],
    })
    rels = extract_shared_relationships(df)
    assert len(rels) == 0

    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    # 0 candidate clusters because size >= 2 required
    assert len(clusters) == 0


def test_ground_truth_and_scenario_id_isolation():
    """Verify ground_truth_cluster and scenario_id are not accessed in core logic."""
    df = pd.DataFrame({
        "account_id": ["A1", "A2"],
        "device_id": ["D1", "D1"],
        "ip_id": ["IP1", "IP1"],
        "beneficiary_id": ["B1", "B1"],
        # Intentionally omit ground_truth_cluster and scenario_id columns
    })
    risk_df = pd.DataFrame({
        "account_id": ["A1", "A2"],
        "risk_score": [50, 50]
    })

    rels = extract_shared_relationships(df)
    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    assert len(clusters) == 1
    ev = extract_cluster_evidence(clusters[0]["account_ids"], df, G)
    scores = calculate_cluster_score(clusters[0]["account_ids"], ev, risk_df)

    assert scores["cluster_risk"] > 0
    assert scores["severity"] in ["MEDIUM", "HIGH"]
