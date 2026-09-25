"""
Graph Construction Module for NEXUS Member 2.

Constructs a deterministic NetworkX undirected graph where:
- Nodes represent account IDs.
- Edges represent candidate relationships with aggregated attributes.
"""

import networkx as nx
import pandas as pd


def build_account_graph(df: pd.DataFrame, relationships: list[dict]) -> nx.Graph:
    """
    Build a NetworkX undirected account graph from event data and relationships.

    Parameters:
        df (pd.DataFrame): Input event DataFrame (used to populate all account nodes).
        relationships (list[dict]): Extracted relationship records.

    Returns:
        nx.Graph: Deterministic NetworkX graph with node and edge metadata.
    """
    if df is None or "account_id" not in df.columns:
        raise ValueError("DataFrame missing required column: 'account_id'")

    G = nx.Graph()

    # Add all accounts as nodes (sorted deterministically)
    all_accounts = sorted(
        df["account_id"].astype(str).str.strip().unique().tolist()
    )
    for account_id in all_accounts:
        if account_id:
            G.add_node(account_id)

    # Populate edges with relationship metadata
    for rel in relationships:
        acc_a = str(rel["account_a"]).strip()
        acc_b = str(rel["account_b"]).strip()
        rel_type = str(rel["relationship_type"]).strip()
        shared_val = str(rel["shared_value"]).strip()

        if not acc_a or not acc_b or acc_a == acc_b:
            continue

        # Ensure nodes exist
        if not G.has_node(acc_a):
            G.add_node(acc_a)
        if not G.has_node(acc_b):
            G.add_node(acc_b)

        if G.has_edge(acc_a, acc_b):
            edge_data = G[acc_a][acc_b]
            if rel_type not in edge_data["relationship_types"]:
                edge_data["relationship_types"].append(rel_type)
            if rel_type not in edge_data["shared_values_map"]:
                edge_data["shared_values_map"][rel_type] = []
            if shared_val not in edge_data["shared_values_map"][rel_type]:
                edge_data["shared_values_map"][rel_type].append(shared_val)
        else:
            G.add_edge(
                acc_a,
                acc_b,
                relationship_types=[rel_type],
                shared_values_map={rel_type: [shared_val]},
            )

    # Clean up and sort edge attribute lists for determinism
    for u, v in G.edges():
        edge_data = G[u][v]
        edge_data["relationship_types"] = sorted(edge_data["relationship_types"])
        for r_type in edge_data["shared_values_map"]:
            edge_data["shared_values_map"][r_type] = sorted(
                edge_data["shared_values_map"][r_type]
            )

    return G
