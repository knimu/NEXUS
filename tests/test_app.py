"""
Unit & Integration Tests for Member 4 Flask Application & REST APIs.
"""

import json
import os
import pytest
from app import create_app
from app.services import AUDIT_LOG_PATH


@pytest.fixture
def client():
    """Flask test client fixture."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_1_flask_starts(client):
    """Test 1: Flask starts successfully and renders dashboard UI."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"NEXUS" in response.data
    assert b"AI DEFENSE LAB 2026" in response.data


def test_2_api_overview(client):
    """Test 2: GET /api/overview returns 200 and dynamic metrics."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert "total_accounts" in data
    assert "cluster_count" in data
    assert "clustered_account_count" in data
    assert "high_severity_count" in data
    assert "total_evidence_count" in data
    assert "average_cluster_risk" in data
    assert "average_confidence" in data


def test_3_api_clusters(client):
    """Test 3: GET /api/clusters returns 200 and list of clusters."""
    response = client.get("/api/clusters")
    assert response.status_code == 200
    clusters = response.get_json()
    assert isinstance(clusters, list)
    assert len(clusters) > 0
    assert "cluster_id" in clusters[0]


def test_4_api_cluster_valid(client):
    """Test 4: GET /api/clusters/<valid_cluster> returns 200 and full details."""
    response = client.get("/api/clusters/CLUSTER_001")
    assert response.status_code == 200
    data = response.get_json()
    assert data["cluster_id"] == "CLUSTER_001"
    assert "accounts_detail" in data
    assert "graph_topology" in data


def test_5_api_cluster_invalid(client):
    """Test 5: GET /api/clusters/<invalid_cluster> returns 404."""
    response = client.get("/api/clusters/INVALID_CLUSTER_999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_6_api_adversarial_summary(client):
    """Test 6: GET /api/adversarial returns 200 and summary."""
    response = client.get("/api/adversarial")
    assert response.status_code == 200
    data = response.get_json()
    assert "baseline_summary" in data
    assert "attack_comparisons" in data


def test_7_api_adversarial_device_rotation(client):
    """Test 7: GET /api/adversarial/device_rotation returns 200."""
    response = client.get("/api/adversarial/device_rotation")
    assert response.status_code == 200
    data = response.get_json()
    assert data["attack_type"] == "device_rotation"
    assert "comparison" in data


def test_8_api_adversarial_ip_rotation(client):
    """Test 8: GET /api/adversarial/ip_rotation returns 200."""
    response = client.get("/api/adversarial/ip_rotation")
    assert response.status_code == 200
    data = response.get_json()
    assert data["attack_type"] == "ip_rotation"
    assert "comparison" in data


def test_9_api_adversarial_combined(client):
    """Test 9: GET /api/adversarial/combined returns 200."""
    response = client.get("/api/adversarial/combined")
    assert response.status_code == 200
    data = response.get_json()
    assert data["attack_type"] == "combined"
    assert "comparison" in data


def test_10_decision_valid_review(client):
    """Test 10: Valid REVIEW decision recorded."""
    payload = {
        "cluster_id": "CLUSTER_001",
        "decision": "REVIEW",
        "reason": "Initial review required for IP sharing."
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_11_decision_valid_allow(client):
    """Test 11: Valid ALLOW decision recorded."""
    payload = {
        "cluster_id": "CLUSTER_001",
        "decision": "ALLOW",
        "reason": "Legitimate shared office network verified."
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_12_decision_valid_escalate(client):
    """Test 12: Valid ESCALATE decision recorded."""
    payload = {
        "cluster_id": "CLUSTER_006",
        "decision": "ESCALATE",
        "reason": "Multiple independent relationship and behavioral signals require review."
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_13_decision_invalid_decision_rejected(client):
    """Test 13: Invalid decision value rejected with 400."""
    payload = {
        "cluster_id": "CLUSTER_001",
        "decision": "INVALID_DECISION",
        "reason": "Some reason"
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_14_decision_missing_reason_rejected(client):
    """Test 14: Missing or empty reason rejected with 400."""
    payload = {
        "cluster_id": "CLUSTER_001",
        "decision": "REVIEW",
        "reason": "   "
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_15_decision_invalid_cluster_rejected(client):
    """Test 15: Invalid cluster_id rejected with 400."""
    payload = {
        "cluster_id": "CLUSTER_NON_EXISTENT_999",
        "decision": "REVIEW",
        "reason": "Testing invalid cluster."
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_16_decision_malformed_json_rejected(client):
    """Test 16: Malformed or missing JSON body rejected with 400."""
    response = client.post("/api/decisions", data="Not a json", content_type="text/plain")
    assert response.status_code == 400


def test_17_api_audit_logs(client):
    """Test 17: GET /api/audit returns recorded decisions."""
    response = client.get("/api/audit")
    assert response.status_code == 200
    logs = response.get_json()
    assert isinstance(logs, list)
    assert len(logs) > 0


def test_18_audit_persisted():
    """Test 18: Audit entry persists in audit_log.json."""
    assert os.path.exists(AUDIT_LOG_PATH)
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        logs = json.load(f)
    assert len(logs) > 0
    assert "timestamp" in logs[0]
    assert "decision" in logs[0]
    assert "reason" in logs[0]
