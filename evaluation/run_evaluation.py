"""Run account-level evaluation for baseline and adversarial NEXUS outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from evaluation.metrics import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "generated"
ADV_DIR = DATA_DIR / "adversarial"
OUT_DIR = DATA_DIR / "evaluation"

CASES = {
    "baseline": (
        DATA_DIR / "synthetic_data.csv",
        DATA_DIR / "cluster_results.json",
    ),
    "device_rotation": (
        ADV_DIR / "device_rotation_data.csv",
        ADV_DIR / "device_rotation_cluster_results.json",
    ),
    "ip_rotation": (
        ADV_DIR / "ip_rotation_data.csv",
        ADV_DIR / "ip_rotation_cluster_results.json",
    ),
    "combined_rotation": (
        ADV_DIR / "combined_data.csv",
        ADV_DIR / "combined_cluster_results.json",
    ),
}


def load_records(data_path: Path) -> list[dict[str, str]]:
    return pd.read_csv(data_path, dtype=str).fillna("").to_dict("records")


def load_clusters(cluster_path: Path) -> list[dict[str, object]]:
    with cluster_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run() -> dict[str, object]:
    results = {}
    for name, (data_path, cluster_path) in CASES.items():
        results[name] = evaluate_case(
            name,
            load_records(data_path),
            load_clusters(cluster_path),
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / "evaluation_summary.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    return results


def _line(metrics: dict[str, object]) -> str:
    return (
        f"Precision={metrics['precision']:.1%} "
        f"Recall={metrics['recall']:.1%} "
        f"F1={metrics['f1']:.1%} "
        f"FPR={metrics['false_positive_rate']:.1%}"
    )


if __name__ == "__main__":
    results = run()

    print("NEXUS Evaluation")
    print("=" * 88)
    print("Candidate-cluster membership (broad network candidate signal)")
    for name, result in results.items():
        print(f"{name:20} {_line(result['candidate_cluster_metrics'])}")

    print("\nHigh-severity cluster membership (operational escalation signal)")
    for name, result in results.items():
        print(f"{name:20} {_line(result['high_severity_metrics'])}")

    print(f"\nSaved: {OUT_DIR / 'evaluation_summary.json'}")
