from evaluation.metrics import binary_metrics, evaluate_case


def test_binary_metrics_basic():
    result = binary_metrics(
        actual_positive={"A1", "A2"},
        predicted_positive={"A2", "A3"},
        population={"A1", "A2", "A3", "A4"},
    )

    assert result["true_positive"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1
    assert result["true_negative"] == 1
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5
    assert result["false_positive_rate"] == 0.5


def test_nexus_evaluation_separates_candidate_and_high_severity():
    records = [
        {"account_id": "A1", "ground_truth_cluster": "FRAUD_CLUSTER_01"},
        {"account_id": "A2", "ground_truth_cluster": "FRAUD_CLUSTER_01"},
        {"account_id": "A3", "ground_truth_cluster": "NONE"},
        {"account_id": "A4", "ground_truth_cluster": "NONE"},
    ]
    clusters = [
        {"cluster_id": "CLUSTER_001", "account_ids": ["A1", "A2"], "severity": "HIGH"},
        {"cluster_id": "CLUSTER_002", "account_ids": ["A3"], "severity": "LOW"},
    ]

    result = evaluate_case("test", records, clusters)

    assert result["candidate_cluster_metrics"]["true_positive"] == 2
    assert result["candidate_cluster_metrics"]["false_positive"] == 1
    assert result["high_severity_metrics"]["true_positive"] == 2
    assert result["high_severity_metrics"]["false_positive"] == 0
