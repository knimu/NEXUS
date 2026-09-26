"""
Flask Routes and REST API Endpoints for NEXUS Member 4 Dashboard.
"""

from flask import Blueprint, jsonify, render_template, request
from app.services import (
    get_overview_metrics,
    get_all_clusters,
    get_cluster_detail,
    get_audit_log,
    record_decision,
    get_adversarial_comparison,
    get_evaluation_data,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Render the main Investigation Dashboard UI."""
    return render_template("index.html")


@main_bp.route("/api/overview", methods=["GET"])
def api_overview():
    """GET /api/overview — Dynamic system overview metrics."""
    try:
        data = get_overview_metrics()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to calculate overview metrics: {str(e)}"}), 500


@main_bp.route("/api/clusters", methods=["GET"])
def api_clusters():
    """GET /api/clusters — List all candidate clusters."""
    try:
        clusters = get_all_clusters()
        return jsonify(clusters), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve clusters: {str(e)}"}), 500


@main_bp.route("/api/clusters/<cluster_id>", methods=["GET"])
def api_cluster_detail(cluster_id: str):
    """GET /api/clusters/<cluster_id> — Complete cluster detail with topology & accounts."""
    try:
        c_id = str(cluster_id).strip()
        detail = get_cluster_detail(c_id)
        if detail is None:
            return jsonify({"error": f"Cluster '{c_id}' not found"}), 404
        return jsonify(detail), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving cluster detail: {str(e)}"}), 500


@main_bp.route("/api/adversarial", methods=["GET"])
def api_adversarial_summary():
    """GET /api/adversarial — Adversarial resilience experiment summary."""
    try:
        data = get_adversarial_comparison()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving adversarial comparison: {str(e)}"}), 500


@main_bp.route("/api/adversarial/<attack_type>", methods=["GET"])
def api_adversarial_attack(attack_type: str):
    """GET /api/adversarial/<attack_type> — Specific attack comparison data."""
    valid_attacks = {"baseline", "device_rotation", "ip_rotation", "combined"}
    at = str(attack_type).strip()

    if at not in valid_attacks:
        return jsonify({"error": f"Invalid attack type '{at}'. Must be one of: {sorted(list(valid_attacks))}"}), 400

    try:
        data = get_adversarial_comparison(at)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Error processing adversarial attack data: {str(e)}"}), 500


@main_bp.route("/api/evaluation", methods=["GET"])
def api_evaluation():
    """GET /api/evaluation — Generated evaluation and resilience summary."""
    try:
        return jsonify(get_evaluation_data()), 200
    except ValueError as e:
        return jsonify({"error": f"Evaluation data unavailable: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"Error retrieving evaluation data: {str(e)}"}), 500


@main_bp.route("/api/audit", methods=["GET"])
def api_audit():
    """GET /api/audit — Recorded human analyst decisions (newest first)."""
    try:
        logs = get_audit_log()
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": f"Error loading audit log: {str(e)}"}), 500


@main_bp.route("/api/decisions", methods=["POST"])
def api_decisions():
    """POST /api/decisions — Record human analyst decision."""
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json"}), 400

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    cluster_id = data.get("cluster_id")
    decision = data.get("decision")
    reason = data.get("reason")

    try:
        record_decision(cluster_id, decision, reason)
        return jsonify({"success": True, "message": "Decision recorded"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error saving decision: {str(e)}"}), 500
