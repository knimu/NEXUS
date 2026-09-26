"""Account-level evaluation metrics for NEXUS.

Ground truth is used only after detection, for evaluation. It is never
passed into graph construction, clustering, scoring, or adversarial mutation.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


def binary_metrics(
    actual_positive: Iterable[str],
    predicted_positive: Iterable[str],
    population: Iterable[str],
) -> dict[str, float | int]:
    """Calculate account-level classification metrics."""
    actual = set(actual_positive)
    predicted = set(predicted_positive)
    universe = set(population)

    if not actual.issubset(universe) or not predicted.issubset(universe):
        raise ValueError("Actual and predicted accounts must belong to the population.")

    tp = len(actual & predicted)
    fp = len(predicted - actual)
    fn = len(actual - predicted)
    tn = len(universe - actual - predicted)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "population_count": len(universe),
        "actual_positive_count": len(actual),
        "predicted_positive_count": len(predicted),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_rate": round(false_positive_rate, 4),
    }


def evaluate_case(
    name: str,
    records: Sequence[Mapping[str, str]],
    clusters: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Evaluate candidate coverage and high-severity escalation coverage.

    Candidate metrics treat membership in any connected candidate cluster as
    a positive. High-severity metrics treat membership in a HIGH cluster as
    a positive operational escalation signal.

    Ground truth is used only here, after detection.
    """
    population = {str(row["account_id"]).strip() for row in records}
    actual_positive = {
        str(row["account_id"]).strip()
        for row in records
        if str(row.get("ground_truth_cluster", "")).strip().upper() != "NONE"
    }

    candidate_positive = {
        str(account).strip()
        for cluster in clusters
        for account in cluster.get("account_ids", [])
        if str(account).strip()
    }

    high_severity_positive = {
        str(account).strip()
        for cluster in clusters
        if str(cluster.get("severity", "")).strip().upper() == "HIGH"
        for account in cluster.get("account_ids", [])
        if str(account).strip()
    }

    return {
        "case": name,
        "candidate_cluster_metrics": binary_metrics(
            actual_positive, candidate_positive, population
        ),
        "high_severity_metrics": binary_metrics(
            actual_positive, high_severity_positive, population
        ),
        "detected_cluster_count": len(clusters),
        "clustered_account_count": len(candidate_positive),
        "high_severity_cluster_count": sum(
            str(cluster.get("severity", "")).strip().upper() == "HIGH"
            for cluster in clusters
        ),
        "high_severity_account_count": len(high_severity_positive),
    }
