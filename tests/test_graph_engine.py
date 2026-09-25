"""
Unit Tests for graph_engine (relationships, graph_builder, cluster_detector).
"""

import pytest
import pandas as pd
import networkx as nx

from graph_engine.relationships import extract_shared_relationships
from graph_engine.graph_builder import build_account_graph
from graph_engine.cluster_detector import detect_candidate_clusters


def test_extract_shared_relationships_basic():
    data = {
        "account_id": ["A01", "A02", "A03"],
        "device_id": ["D1", "D1", "D2"],
        "ip_id": ["IP1", "IP1", "IP1"],
        "beneficiary_id": ["B1", "B2", "B1"],
    }
    df = pd.DataFrame(data)

    rels = extract_shared_relationships(df)
    assert isinstance(rels, list)
    assert len(rels) > 0

    # Verify canonical pair ordering (account_a < account_b)
    for r in rels:
        assert r["account_a"] < r["account_b"]
        assert r["relationship_type"] in ["shared_device", "shared_ip", "shared_beneficiary"]

    # Verify D1 produces pair (A01, A02)
    dev_rels = [r for r in rels if r["relationship_type"] == "shared_device"]
    assert len(dev_rels) == 1
    assert dev_rels[0]["account_a"] == "A01"
    assert dev_rels[0]["account_b"] == "A02"
    assert dev_rels[0]["shared_value"] == "D1"

    # Verify IP1 produces 3 pairs: (A01, A02), (A01, A03), (A02, A03)
    ip_rels = [r for r in rels if r["relationship_type"] == "shared_ip"]
    assert len(ip_rels) == 3


def test_extract_shared_relationships_invalid_values():
    data = {
        "account_id": ["A01", "A02", "A03"],
        "device_id": ["D1", None, "nan"],
        "ip_id": ["", "NONE", "IP01"],
        "beneficiary_id": ["B01", "B01", None],
    }
    df = pd.DataFrame(data)

    rels = extract_shared_relationships(df)
    # Only B01 should produce a relationship between A01 and A02
    assert len(rels) == 1
    assert rels[0]["relationship_type"] == "shared_beneficiary"
    assert rels[0]["account_a"] == "A01"
    assert rels[0]["account_b"] == "A02"


def test_extract_shared_relationships_missing_columns():
    df = pd.DataFrame({"other_col": [1, 2]})
    with pytest.raises(ValueError):
        extract_shared_relationships(df)


def test_build_account_graph():
    df = pd.DataFrame({
        "account_id": ["A01", "A02", "A03", "A04"]
    })
    rels = [
        {"account_a": "A01", "account_b": "A02", "relationship_type": "shared_device", "shared_value": "D1"},
        {"account_a": "A01", "account_b": "A02", "relationship_type": "shared_ip", "shared_value": "IP1"},
    ]

    G = build_account_graph(df, rels)
    assert isinstance(G, nx.Graph)
    assert len(G.nodes()) == 4
    assert "A04" in G.nodes()  # Isolated node is present
    assert G.degree("A04") == 0

    assert G.has_edge("A01", "A02")
    edge_data = G["A01"]["A02"]
    assert "shared_device" in edge_data["relationship_types"]
    assert "shared_ip" in edge_data["relationship_types"]
    assert edge_data["shared_values_map"]["shared_device"] == ["D1"]


def test_detect_candidate_clusters():
    G = nx.Graph()
    G.add_nodes_from(["A01", "A02", "A03", "A04", "A05", "A06"])
    G.add_edge("A01", "A02")
    G.add_edge("A02", "A03")
    G.add_edge("A04", "A05")
    # A06 is isolated

    clusters = detect_candidate_clusters(G)
    assert len(clusters) == 2

    # Verify deterministic cluster formatting
    assert clusters[0]["cluster_id"] == "CLUSTER_001"
    assert clusters[0]["account_ids"] == ["A01", "A02", "A03"]

    assert clusters[1]["cluster_id"] == "CLUSTER_002"
    assert clusters[1]["account_ids"] == ["A04", "A05"]

    # Verify A06 (isolated) is not a candidate cluster
    all_clustered_accs = {acc for c in clusters for acc in c["account_ids"]}
    assert "A06" not in all_clustered_accs


def test_ground_truth_isolation():
    # Verify relationships and clustering operate without ground_truth_cluster or scenario_id
    df = pd.DataFrame({
        "account_id": ["A101", "A102"],
        "device_id": ["D1", "D1"],
        "ip_id": ["IP1", "IP1"],
        "beneficiary_id": ["B1", "B1"],
    })
    rels = extract_shared_relationships(df)
    G = build_account_graph(df, rels)
    clusters = detect_candidate_clusters(G)

    assert len(clusters) == 1
    assert clusters[0]["account_ids"] == ["A101", "A102"]
