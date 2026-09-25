# NEXUS — Adversarial Fraud-Network Investigation Platform

NEXUS is an adversarial fraud-network investigation platform using controlled synthetic data and human-controlled decisions.

## Member 2 Module: Graph, Candidate Clusters, Evidence & Cluster Risk Engine

Member 2 is responsible for:
**GRAPH → CLUSTERS → EVIDENCE → CLUSTER RISK**

It consumes Member 1's individual account risk scores (`data/generated/risk_results.csv`) and synthetic transaction event data (`data/generated/synthetic_data.csv`), and produces structured candidate network clusters and explainable evidence for Member 3 (Adversarial Testing) and Member 4 (Dashboard & Investigation).

---

## Module Architecture

```
Synthetic Events (synthetic_data.csv) + Individual Risk (risk_results.csv)
                                │
                                ▼
         Relationship Extraction (graph_engine/relationships.py)
        (shared_device, shared_ip, shared_beneficiary)
                                │
                                ▼
         NetworkX Graph Construction (graph_engine/graph_builder.py)
                                │
                                ▼
     Candidate Cluster Detection (graph_engine/cluster_detector.py)
            (Connected Components, size >= 2)
                                │
                                ▼
       Post-Detection Evidence Engine (evidence/evidence_engine.py)
   (Shared Attributes, Temporal Proximity <=30m, Suspicious Behaviors)
                                │
                                ▼
       Deterministic Scoring & Confidence (evidence/scoring.py)
     (Base Risk + Capped Network Contribution, Severity, Confidence)
                                │
                                ▼
       Structured Contract Outputs (cluster_results.json / .csv)
```

---

## Core Operational Rules

1. **Ground Truth & Scenario ID Isolation**:
   - `ground_truth_cluster` and `scenario_id` are strictly evaluation metadata.
   - They are NEVER used in graph building, relationship extraction, cluster detection, evidence extraction, or risk/confidence scoring.
   - They are reserved exclusively for post-detection verification in test suites.

2. **Candidate Network vs. Fraud Verdict**:
   - Graph connectivity represents candidate topological grouping, NOT a fraud conclusion.
   - Downstream evidence and scoring evaluate whether a connected component represents coordinated fraud or legitimate shared infrastructure.

3. **Legitimate Shared Infrastructure Protection**:
   - Shared IP alone is weak network evidence because every IP in public/office networks can be shared.
   - If a candidate cluster contains ONLY `shared_ip` relationships (no shared devices, no shared beneficiaries), its `network_contribution` is capped at **15.0 points**.
   - Shared IP alone can NEVER escalate a cluster to **HIGH** severity without elevated individual account risk or independent relationship types.

4. **Temporal Proximity ($\le 30$ Minutes)**:
   - Evaluated post-detection between connected account pairs in candidate clusters.
   - Accounts transacting within 30 minutes provide temporal evidence supporting co-activity.

5. **Behavioral Feature Overlap**:
   - Parsed strictly by semicolon splitting (`behavior_features.split(";")`).
   - Only suspicious tags (`high_amount`, `high_frequency`, `rapid_transactions`, `suspicious_beneficiary`) shared by $\ge 2$ accounts count toward behavioral evidence.
   - Benign/contextual tags (`normal_amount`, `normal_frequency`, `shared_office_network`, `shared_ip`, `shared_device`, `shared_beneficiary`) are excluded.

---

## Exact Mathematical Formulas

### Base Individual Risk
$$\text{base\_risk} = 0.60 \times \max_{a \in C}(\text{risk\_score}_a) + 0.40 \times \text{mean}_{a \in C}(\text{risk\_score}_a)$$

### Network Raw Score
$$\text{network\_raw} = 20 \cdot N_{\text{dev}} + 25 \cdot N_{\text{ben}} + 5 \cdot N_{\text{ip}} + \text{diversity\_bonus} + \text{temporal\_bonus} + \text{behavioral\_bonus}$$

- **Diversity Bonus**: $0$ for $T_{\text{rel}} \le 1$; $15$ for $T_{\text{rel}} = 2$; $30$ for $T_{\text{rel}} = 3$.
- **Temporal Bonus**: $10$ if $N_{\text{temp}} \ge 1$; else $0$.
- **Behavioral Bonus**: $\min(15, 5 \cdot N_{\text{beh}})$.

### Network Contribution Cap
- If $N_{\text{dev}} == 0$ AND $N_{\text{ben}} == 0$ (IP only): $\text{network\_contribution} = \min(\text{network\_raw}, 15.0)$.
- Else: $\text{network\_contribution} = \min(\text{network\_raw}, 50.0)$.

### Cluster Risk Score
$$\text{cluster\_risk} = \min(100.0, \max(0.0, \text{base\_risk} + \text{network\_contribution}))$$

### Severity Classification
- `LOW`: $0.0 \le \text{cluster\_risk} < 30.0$
- `MEDIUM`: $30.0 \le \text{cluster\_risk} < 60.0$
- `HIGH`: $60.0 \le \text{cluster\_risk} \le 100.0$

### Evidence-Strength Confidence Metric
$$\text{confidence} = \min\left(1.0, \max\left(0.10, 0.40 \times \frac{T_{\text{rel}}}{3.0} + 0.35 \times \min\left(1.0, \frac{N_{\text{items}}}{5.0}\right) + 0.25 \times \text{support\_factor}\right)\right)$$
- $N_{\text{items}} = N_{\text{dev}} + N_{\text{ben}} + N_{\text{ip}} + \mathbb{I}(N_{\text{temp}} > 0) + N_{\text{beh}}$.
- $\text{support\_factor} = 1.0$ if both temporal and behavioral evidence present; $0.5$ if one present; $0.0$ if neither.

---

## How to Run

### 1. Run Member 1 Risk Engine
```bash
python risk_engine/process_data.py
```

### 2. Run Member 2 Graph & Evidence Pipeline
```bash
python run_graph_evidence.py
```
This generates:
- `data/generated/cluster_results.json` (complete nested contract)
- `data/generated/cluster_results.csv` (tabular summary)

### 3. Run Test Suite
```bash
pytest tests/
```
