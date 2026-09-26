"""
Resilience Analyzer for NEXUS Member 3.

Compares baseline detector results against results obtained
after an adversarial attack.
"""


def _account_set(clusters):
    """Return all accounts participating in detected clusters."""
    accounts = set()

    for cluster in clusters:
        accounts.update(cluster.get("account_ids", []))

    return accounts


def _sum_field(clusters, field):
    """Sum a numeric field across all detected clusters."""
    return sum(cluster.get(field, 0) for cluster in clusters)


def _evidence_count(clusters):
    """Count all evidence items across detected clusters."""
    return sum(
        len(cluster.get("evidence", []))
        for cluster in clusters
    )


def summarize_results(clusters):
    """
    Extract resilience-relevant metrics from detector output.
    """

    accounts = _account_set(clusters)

    return {
        "cluster_count": len(clusters),
        "detected_account_count": len(accounts),
        "shared_device_count": _sum_field(clusters, "Ndev"),
        "shared_ip_count": _sum_field(clusters, "Nip"),
        "shared_beneficiary_count": _sum_field(clusters, "Nben"),
        "temporal_evidence_count": _sum_field(clusters, "Ntemp"),
        "behavioral_evidence_count": _sum_field(clusters, "Nbeh"),
        "total_evidence_count": _evidence_count(clusters),
        "total_cluster_risk": round(
            sum(cluster.get("cluster_risk", 0) for cluster in clusters),
            4,
        ),
        "average_cluster_risk": round(
            (
                sum(cluster.get("cluster_risk", 0) for cluster in clusters)
                / len(clusters)
            )
            if clusters
            else 0,
            4,
        ),
        "average_confidence": round(
            (
                sum(cluster.get("confidence", 0) for cluster in clusters)
                / len(clusters)
            )
            if clusters
            else 0,
            4,
        ),
        "severity_counts": {
            "LOW": sum(
                1 for cluster in clusters
                if cluster.get("severity") == "LOW"
            ),
            "MEDIUM": sum(
                1 for cluster in clusters
                if cluster.get("severity") == "MEDIUM"
            ),
            "HIGH": sum(
                1 for cluster in clusters
                if cluster.get("severity") == "HIGH"
            ),
        },
    }


def compare_results(baseline_clusters, attacked_clusters):
    """
    Compare baseline and attacked detector results.

    Returns absolute changes and percentage survival
    for important detection signals.
    """

    baseline = summarize_results(baseline_clusters)
    attacked = summarize_results(attacked_clusters)

    def survival(attacked_value, baseline_value):
        if baseline_value == 0:
            return None

        return round(
            (attacked_value / baseline_value) * 100,
            2,
        )

    comparison = {
        "baseline": baseline,
        "attacked": attacked,
        "change": {
            "cluster_count": (
                attacked["cluster_count"]
                - baseline["cluster_count"]
            ),
            "detected_account_count": (
                attacked["detected_account_count"]
                - baseline["detected_account_count"]
            ),
            "shared_device_count": (
                attacked["shared_device_count"]
                - baseline["shared_device_count"]
            ),
            "shared_ip_count": (
                attacked["shared_ip_count"]
                - baseline["shared_ip_count"]
            ),
            "shared_beneficiary_count": (
                attacked["shared_beneficiary_count"]
                - baseline["shared_beneficiary_count"]
            ),
            "total_evidence_count": (
                attacked["total_evidence_count"]
                - baseline["total_evidence_count"]
            ),
        },
        "survival_percentage": {
            "clusters": survival(
                attacked["cluster_count"],
                baseline["cluster_count"],
            ),
            "detected_accounts": survival(
                attacked["detected_account_count"],
                baseline["detected_account_count"],
            ),
            "shared_devices": survival(
                attacked["shared_device_count"],
                baseline["shared_device_count"],
            ),
            "shared_ips": survival(
                attacked["shared_ip_count"],
                baseline["shared_ip_count"],
            ),
            "shared_beneficiaries": survival(
                attacked["shared_beneficiary_count"],
                baseline["shared_beneficiary_count"],
            ),
            "evidence": survival(
                attacked["total_evidence_count"],
                baseline["total_evidence_count"],
            ),
        },
    }

    return comparison