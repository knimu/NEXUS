"""
Unit Tests for evidence_engine and scoring modules.
"""

import pytest
import pandas as pd
import networkx as nx

from evidence.evidence_engine import extract_cluster_evidence
from evidence.scoring import calculate_cluster_score


def test_extract_cluster_evidence_basic():
    df = pd.DataFrame({
        "account_id": ["A101", "A102"],
        "device_id": ["D20", "D20"],
        "ip_id": ["IP20", "IP20"],
        "beneficiary_id": ["B900", "B900"],
        "timestamp": ["2026-09-24T13:05:00", "2026-09-24T13:12:00"],
        "behavior_features": [
            "high_amount;high_frequency;shared_device;shared_ip",
            "high_amount;high_frequency;shared_device;shared_ip"
        ]
    })
    G = nx.Graph()
    G.add_edge("A101", "A102")

    evidence = extract_cluster_evidence(["A101", "A102"], df, G)

    assert evidence["Ndev"] == 1
    assert evidence["Nip"] == 1
    assert evidence["Nben"] == 1
    assert evidence["shared_devices"] == ["D20"]
    assert evidence["shared_ips"] == ["IP20"]
    assert evidence["shared_beneficiaries"] == ["B900"]

    # 7 minutes delta <= 30 mins -> Ntemp = 1
    assert evidence["Ntemp"] == 1

    # Suspicious tags present in both: high_amount, high_frequency -> Nbeh = 2
    assert evidence["Nbeh"] == 2
    assert "high_amount" in evidence["behavioral_overlap"]
    assert "high_frequency" in evidence["behavioral_overlap"]
    # Contextual tags shared_device/shared_ip should NOT be in behavioral_overlap
    assert "shared_device" not in evidence["behavioral_overlap"]
    assert "shared_ip" not in evidence["behavioral_overlap"]


def test_temporal_boundary():
    # Exactly 30 minutes (1800 seconds) vs 31 minutes (1860 seconds)
    df = pd.DataFrame({
        "account_id": ["A01", "A02", "A03"],
        "device_id": ["D1", "D1", "D1"],
        "ip_id": ["IP1", "IP1", "IP1"],
        "beneficiary_id": ["B1", "B1", "B1"],
        "timestamp": [
            "2026-09-24T10:00:00",
            "2026-09-24T10:30:00",  # Exactly 30m after A01
            "2026-09-24T10:31:00"   # 31m after A01
        ],
        "behavior_features": ["normal_amount", "normal_amount", "normal_amount"]
    })
    G = nx.Graph()
    G.add_edge("A01", "A02")
    G.add_edge("A01", "A03")

    ev = extract_cluster_evidence(["A01", "A02", "A03"], df, G)

    # Pair (A01, A02) = 30m -> qualifies. Pair (A01, A03) = 31m -> does not qualify.
    assert ev["Ntemp"] == 1
    assert ev["temporal_pairs"][0]["account_a"] == "A01"
    assert ev["temporal_pairs"][0]["account_b"] == "A02"


def test_behavioral_parsing_suspicious_only():
    df = pd.DataFrame({
        "account_id": ["A01", "A02"],
        "device_id": ["D1", "D2"],
        "ip_id": ["IP1", "IP2"],
        "beneficiary_id": ["B1", "B2"],
        "timestamp": ["2026-09-24T10:00:00", "2026-09-24T11:00:00"],
        "behavior_features": [
            "normal_amount;normal_frequency;shared_office_network;rapid_transactions;rapid_transactions",
            "high_amount;normal_frequency;shared_office_network;rapid_transactions"
        ]
    })
    G = nx.Graph()
    G.add_node("A01")
    G.add_node("A02")

    ev = extract_cluster_evidence(["A01", "A02"], df, G)

    # rapid_transactions is the only suspicious tag present in both accounts.
    # Duplicate 'rapid_transactions' in A01's string should not inflate Nbeh.
    assert ev["Nbeh"] == 1
    assert ev["behavioral_overlap"] == ["rapid_transactions"]


def test_scoring_legit_shared_cap():
    # Only shared IP (Ndev=0, Nben=0, Nip=1)
    ev_meta = {
        "Ndev": 0, "Nben": 0, "Nip": 1, "Ntemp": 0, "Nbeh": 0,
        "shared_devices": [], "shared_ips": ["IP01"], "shared_beneficiaries": [],
        "temporal_pairs": [], "behavioral_overlap": []
    }
    risk_df = pd.DataFrame({
        "account_id": ["A01", "A02"],
        "risk_score": [0, 0]
    })

    score = calculate_cluster_score(["A01", "A02"], ev_meta, risk_df)

    assert score["base_risk"] == 0.0
    assert score["network_contribution"] <= 15.0
    assert score["cluster_risk"] <= 15.0
    assert score["severity"] == "LOW"
    # Shared IP alone confidence is low
    assert score["confidence"] < 0.30


def test_scoring_diversity_bonus_and_severity():
    risk_df = pd.DataFrame({
        "account_id": ["A101", "A102"],
        "risk_score": [105, 105]
    })

    # Trel = 3 (Ndev=1, Nben=1, Nip=1)
    ev_meta_t3 = {
        "Ndev": 1, "Nben": 1, "Nip": 1, "Ntemp": 1, "Nbeh": 2,
        "shared_devices": ["D20"], "shared_ips": ["IP20"], "shared_beneficiaries": ["B900"],
        "temporal_pairs": [{"account_a": "A101", "account_b": "A102", "time_diff_minutes": 7.0}],
        "behavioral_overlap": ["high_amount", "high_frequency"]
    }

    score_t3 = calculate_cluster_score(["A101", "A102"], ev_meta_t3, risk_df)

    assert score_t3["Trel"] == 3
    assert score_t3["diversity_bonus"] == 30.0
    assert score_t3["temporal_bonus"] == 10.0
    assert score_t3["behavioral_bonus"] == 10.0
    assert score_t3["cluster_risk"] == 100.0  # Bounded at 100
    assert score_t3["severity"] == "HIGH"
    assert score_t3["confidence"] >= 0.80
