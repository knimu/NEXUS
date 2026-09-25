"""
Run NEXUS adversarial resilience experiments.

Workflow:
Baseline
   ↓
Attack mutation
   ↓
Same graph + evidence detector
   ↓
Attacked results
   ↓
Baseline vs attacked comparison
"""

import json
from pathlib import Path

import pandas as pd

from adversarial.attack_simulator import apply_attack
from adversarial.resilience_analyzer import compare_results
from run_graph_evidence import run_pipeline


DATA_PATH = Path(
    "data/generated/synthetic_data.csv"
)

RISK_RESULTS_PATH = Path(
    "data/generated/risk_results.csv"
)

BASELINE_RESULTS_PATH = Path(
    "data/generated/cluster_results.json"
)

OUTPUT_DIR = Path(
    "data/generated/adversarial"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


ATTACK_TYPES = [
    "device_rotation",
    "ip_rotation",
    "combined",
]


def load_clusters(path):
    """Load cluster results from JSON."""

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def run_attack(
    attack_type,
    baseline_clusters
):
    """Run one adversarial attack and compare results."""

    print()
    print("=" * 60)
    print(
        f" NEXUS ADVERSARIAL ATTACK: "
        f"{attack_type.upper()}"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load original dataset
    # ---------------------------------------------------------

    original_df = pd.read_csv(
        DATA_PATH
    )

    # ---------------------------------------------------------
    # 2. Apply adversarial mutation
    # ---------------------------------------------------------

    mutated_df = apply_attack(
        original_df,
        attack_type
    )

    mutated_data_path = (
        OUTPUT_DIR
        / f"{attack_type}_data.csv"
    )

    mutated_df.to_csv(
        mutated_data_path,
        index=False
    )

    print(
        f"Mutated dataset saved: "
        f"{mutated_data_path}"
    )

    # ---------------------------------------------------------
    # 3. Define attack-specific detector outputs
    # ---------------------------------------------------------

    attacked_json_path = (
        OUTPUT_DIR
        / f"{attack_type}_cluster_results.json"
    )

    attacked_csv_path = (
        OUTPUT_DIR
        / f"{attack_type}_cluster_results.csv"
    )

    # ---------------------------------------------------------
    # 4. Run SAME graph + evidence pipeline
    # ---------------------------------------------------------

    attacked_clusters = run_pipeline(
        synthetic_data_path=mutated_data_path,
        risk_results_path=RISK_RESULTS_PATH,
        output_json_path=attacked_json_path,
        output_csv_path=attacked_csv_path,
    )

    # ---------------------------------------------------------
    # 5. Compare baseline vs attacked results
    # ---------------------------------------------------------

    comparison = compare_results(
        baseline_clusters,
        attacked_clusters
    )

    comparison_path = (
        OUTPUT_DIR
        / f"{attack_type}_comparison.json"
    )

    with open(
        comparison_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            comparison,
            file,
            indent=2
        )

    print()
    print(
        f"Baseline clusters: "
        f"{len(baseline_clusters)}"
    )

    print(
        f"Attacked clusters: "
        f"{len(attacked_clusters)}"
    )

    print(
        f"Comparison saved: "
        f"{comparison_path}"
    )

    return comparison


def main():
    """Run all adversarial attack experiments."""

    # ---------------------------------------------------------
    # Load clean baseline
    # ---------------------------------------------------------

    baseline_clusters = load_clusters(
        BASELINE_RESULTS_PATH
    )

    print(
        f"NEXUS baseline clusters: "
        f"{len(baseline_clusters)}"
    )

    all_results = {}

    # ---------------------------------------------------------
    # Run each attack
    # ---------------------------------------------------------

    for attack_type in ATTACK_TYPES:

        all_results[attack_type] = run_attack(
            attack_type,
            baseline_clusters
        )

    # ---------------------------------------------------------
    # Save overall summary
    # ---------------------------------------------------------

    summary_path = (
        OUTPUT_DIR
        / "resilience_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            all_results,
            file,
            indent=2
        )

    print()
    print("=" * 60)
    print(
        " ADVERSARIAL RESILIENCE "
        "EXPERIMENT COMPLETE"
    )
    print("=" * 60)

    print(
        f"Summary saved: "
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()