"""
Candidate Cluster Detection Module for NEXUS Member 2.

Detects candidate account clusters using graph connected components.
Only components with >= 2 connected accounts form candidate clusters.
Single/isolated accounts are excluded from candidate clusters.

Note: ground_truth_cluster and scenario_id are intentionally NOT used.
"""

import networkx as nx


def detect_candidate_clusters(G: nx.Graph) -> list[dict]:
    """
    Detect candidate clusters from a NetworkX account graph.

    Parameters:
        G (nx.Graph): Account graph.

    Returns:
        list[dict]: List of candidate cluster objects:
            [
                {
                    "cluster_id": "CLUSTER_001",
                    "account_ids": ["A101", "A102", ...]
                },
                ...
            ]
    """
    if G is None or not isinstance(G, nx.Graph):
        raise ValueError("Input graph must be a valid NetworkX Graph instance.")

    # Find connected components
    raw_components = list(nx.connected_components(G))

    candidate_components = []

    for comp in raw_components:
        sorted_accs = sorted([str(acc).strip() for acc in comp if str(acc).strip()])
        # Filter out isolated accounts (components with < 2 nodes)
        if len(sorted_accs) >= 2:
            candidate_components.append(sorted_accs)

    # Sort components deterministically by minimum account ID
    candidate_components.sort(key=lambda accs: (accs[0], len(accs)))

    clusters = []
    for idx, accs in enumerate(candidate_components, start=1):
        cluster_id = f"CLUSTER_{idx:03d}"
        clusters.append({
            "cluster_id": cluster_id,
            "account_ids": accs
        })

    return clusters
