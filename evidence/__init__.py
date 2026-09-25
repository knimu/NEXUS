"""
Evidence Engine package for NEXUS Member 2.
Provides post-detection evidence extraction and deterministic cluster risk & confidence scoring.
"""

from .evidence_engine import extract_cluster_evidence
from .scoring import calculate_cluster_score

__all__ = [
    "extract_cluster_evidence",
    "calculate_cluster_score",
]
