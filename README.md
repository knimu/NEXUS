# NEXUS — Adversarial Fraud Network Investigation & Resilience

> **AI Defense Lab 2026 — Track 2: Fraud, Scam & Identity Defense**

NEXUS is an adversarial fraud-network investigation platform that detects suspicious relationships between accounts, explains the evidence behind those relationships, and tests how resilient the detection is when an adversary changes infrastructure such as devices and IP addresses.

Instead of only asking **“Can we detect a suspicious network?”**, NEXUS also asks:

> **“What happens to our detection evidence when the network changes its infrastructure?”**

The system uses controlled synthetic data and keeps the final decision with a human analyst.

---

## 🔗 Demo & Repository

**Live Demo:**
https://nexus-1-epu2.onrender.com/

**Source Code:**
https://github.com/knimu/NEXUS

---

## 🎯 Problem

Fraud detection can become difficult when multiple accounts are connected through shared infrastructure.

For example, several accounts may:

* use the same device
* use the same IP address
* send money to the same beneficiary
* perform transactions close together in time
* exhibit overlapping suspicious behavioral patterns

These relationships can reveal a potential fraud network.

However, an adversary may attempt to evade infrastructure-based detection by rotating devices or IP addresses.

A detector that only looks at one type of infrastructure signal may therefore lose important relationships after an adversarial change.

NEXUS addresses this by combining **relationship-based detection, explainable evidence, risk scoring, and adversarial resilience testing**.

---

## 🛡️ Security Objective

### Threat

A coordinated synthetic fraud network attempts to reduce its visibility by changing infrastructure identifiers.

### Protected asset

The ability of an analyst to identify and investigate suspicious account relationships.

### Security outcome

NEXUS measures:

* suspicious network relationships
* supporting evidence
* cluster risk
* severity
* confidence
* evidence lost after adversarial infrastructure changes
* remaining relationships after the attack

The system does **not** automatically identify real criminals, freeze accounts, or make irreversible financial decisions.

---

# 🔄 End-to-End Workflow

```text
Synthetic Transaction Signals
            │
            ▼
     Individual Risk
            │
            ▼
    Relationship Graph
            │
            ▼
    Candidate Clusters
            │
            ▼
   Evidence Extraction
            │
            ▼
 Risk / Severity / Confidence
            │
            ▼
       Dashboard
            │
            ▼
 Adversarial Device/IP Rotation
            │
            ▼
       Mutated Data
            │
            ▼
   SAME Detection Pipeline
            │
            ▼
    Before vs After
            │
            ▼
   Resilience Analysis
            │
            ▼
      Human Decision
            │
            ▼
        Audit Log
```

The adversarial experiment intentionally reuses the same graph and evidence pipeline rather than creating a separate detector. This makes the before/after comparison reproducible and avoids changing the detection method between experiments.

---

# 🧩 Core Components

## 1. Synthetic Data

NEXUS operates on controlled synthetic transaction data.

The dataset contains 50 synthetic accounts/events across scenarios including:

* `LEGIT_SHARED`
* `FRAUD_OBVIOUS`
* `FRAUD_EVASIVE`
* `LEGIT_BORDERLINE`
* `FRAUD_MIXED`

The data contains relationship attributes such as:

* account ID
* device ID
* IP ID
* beneficiary ID
* timestamp
* transaction amount
* behavioral indicators

No real customer or banking data is required.

---

## 2. Individual Risk

The first stage assigns individual risk signals to transaction/account activity.

These signals are then available to the downstream network analysis pipeline.

Output:

```text
data/generated/risk_results.csv
```

---

## 3. Relationship Graph

NEXUS builds an account relationship graph using shared attributes.

Relevant relationships include:

* shared device
* shared IP
* shared beneficiary

The graph is implemented using **NetworkX**.

Connected account components are converted into candidate clusters.

Importantly, `ground_truth_cluster` and `scenario_id` are not used to construct the detection graph.

---

## 4. Evidence Engine

Each candidate cluster is accompanied by structured evidence.

Evidence includes:

### Infrastructure evidence

* shared devices
* shared IP addresses
* shared beneficiaries

### Temporal evidence

Accounts conducting transactions within a defined time window can contribute temporal evidence.

### Behavioral evidence

The system looks for overlapping suspicious behavior patterns, including:

* high amount
* high frequency
* rapid transactions
* suspicious beneficiary behavior

The evidence is stored in machine-readable form rather than being represented only as a model probability or dashboard visualization.

---

# 📊 Risk, Severity & Confidence

Candidate clusters are scored using the available relationship and evidence signals.

The dashboard exposes:

* cluster risk
* severity
* confidence
* relationship evidence
* temporal evidence
* behavioral evidence

This allows an analyst to inspect **why a cluster was surfaced**, rather than receiving only a black-box fraud label.

---

# 🧨 Adversarial Resilience Testing

This is the distinguishing part of NEXUS.

The attacker simulation supports three controlled infrastructure attacks:

### 1. Device Rotation

Accounts retain their identity and transaction information but receive different device identifiers.

```text
Before:

A101 → D20
A102 → D20
A103 → D20

After:

A101 → D101
A102 → D102
A103 → D103
```

Only the device infrastructure is changed.

### 2. IP Rotation

Accounts receive different IP identifiers while other transaction information remains unchanged.

```text
Before:

A101 → IP20
A102 → IP20
A103 → IP20

After:

A101 → IP101
A102 → IP102
A103 → IP103
```

### 3. Combined Device + IP Rotation

Both infrastructure identifiers are changed.

```text
Before:

A101 → D20 + IP20
A102 → D20 + IP20
A103 → D20 + IP20

After:

A101 → D101 + IP101
A102 → D102 + IP102
A103 → D103 + IP103
```

The attack simulator does not modify account identity, beneficiary, amount, timestamp, scenario, or ground-truth fields for these experiments.

---

# 🔁 Same Detector Principle

The adversarial experiment follows:

```text
Baseline Data
     ↓
Existing Detection Pipeline
     ↓
Baseline Clusters + Evidence
     ↓
Infrastructure Mutation
     ↓
Mutated Data
     ↓
Same Detection Pipeline
     ↓
New Clusters + Evidence
     ↓
Before / After Comparison
```

This is important because the experiment measures the effect of the adversarial change rather than comparing two different detection systems.

Ground truth is reserved for evaluation and is not used to decide which accounts belong to detected clusters or how the mutation is selected.

---

# 📈 Resilience Experiment Results

NEXUS was tested against three controlled infrastructure changes.

| Scenario             | Clusters | Clustered Accounts | Shared Devices | Shared IPs | Shared Beneficiaries | Evidence | Evidence Survival |
| -------------------- | -------: | -----------------: | -------------: | ---------: | -------------------: | -------: | ----------------: |
| Baseline             |       13 |                 50 |              8 |         23 |                    6 |       63 |              100% |
| Device Rotation      |       13 |                 50 |              0 |         23 |                    6 |       55 |             87.3% |
| IP Rotation          |        4 |                 30 |              8 |          0 |                    6 |       28 |             44.4% |
| Device + IP Rotation |        6 |                 30 |              0 |          0 |                    6 |       30 |             47.6% |

### What this demonstrates

Device rotation removed shared-device relationships, but other evidence remained available.

IP rotation caused a larger fragmentation of the relationship graph because shared IP relationships were removed.

Combined rotation removed both shared-device and shared-IP relationships.

However, remaining relationships such as:

* shared beneficiaries
* temporal proximity
* behavioral overlap

continued to provide evidence for the remaining candidate clusters.

Therefore, the experiment demonstrates both **residual detection evidence** and a **limitation of infrastructure-dependent graph detection**.

---

# ⚠️ Important Interpretation of the Results

`Clustered Accounts` means accounts that belong to connected candidate components. It is **not equivalent to the number of confirmed fraudulent accounts**.

For example, after IP rotation:

```text
Candidate-clustered accounts:
50 → 30
```

This means the relationship graph became more fragmented.

It should **not** be interpreted as:

> “20 fraud accounts escaped detection.”

The evaluation and dashboard distinguish candidate network membership from the ground-truth labels used only for post-detection evaluation.

---

# 🧪 Evaluation

NEXUS includes a separate evaluation layer that compares candidate-cluster outputs against the synthetic ground truth **after detection**.

Metrics include:

* population
* actual positives
* predicted positives
* true positives
* false positives
* false negatives
* true negatives
* precision
* recall
* F1
* false-positive rate

Ground truth is not used to construct the detection graph, perform clustering, calculate the detection evidence, or select adversarial mutations.

This separation helps prevent evaluation information from leaking into the detection process.

---

# 👩‍💻 Human Analyst Control

NEXUS does not automatically freeze, block, or close accounts.

The analyst can review a candidate cluster and record a decision such as:

* `ALLOW`
* `REVIEW`
* `ESCALATE`

Each decision can include:

* timestamp
* cluster ID
* decision
* analyst reason

This creates an audit trail of the human-controlled response.

The system therefore treats the automated pipeline as **decision support**, not autonomous enforcement.

---

# 🧾 Auditability

Example audit records:

```json
{
  "cluster_id": "CLUSTER_006",
  "decision": "ESCALATE",
  "reason": "Multiple independent relationship and behavioral signals require analyst review."
}
```

```json
{
  "cluster_id": "CLUSTER_013",
  "decision": "REVIEW",
  "reason": "Strong relationship evidence requires additional analyst verification before escalation."
}
```

```json
{
  "cluster_id": "CLUSTER_001",
  "decision": "ALLOW",
  "reason": "Legitimate shared office network verified."
}
```

The audit trail demonstrates that the final operational decision remains with the analyst.

---

# 🖥️ Dashboard

The live dashboard provides:

### System Overview

* total accounts
* candidate clusters
* clustered accounts
* high-severity clusters
* evidence count

### Cluster Investigation

* cluster membership
* relationship evidence
* risk
* severity
* confidence
* evidence details

### Adversarial Resilience

* baseline vs device rotation
* baseline vs IP rotation
* combined rotation
* evidence survival
* cluster changes
* risk changes
* confidence changes

### Evaluation

* precision
* recall
* F1
* false-positive rate
* membership metrics

### Human Analyst Audit Trail

* analyst decision
* reason
* cluster
* timestamp

---

# 🧱 Architecture

```text
                    ┌──────────────────────┐
                    │  Synthetic Dataset   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Individual Risk   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Relationship Graph   │
                    │      NetworkX        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Candidate Clusters   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Evidence Engine    │
                    │ Device / IP / Ben.   │
                    │ Temporal / Behavior  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Risk / Severity /    │
                    │ Confidence           │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │      Dashboard       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Adversarial Simulator│
                    │ Device / IP Rotation │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Same Detection     │
                    │      Pipeline        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Resilience Analyzer  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Human Decision +     │
                    │ Audit Log            │
                    └──────────────────────┘
```

---

# 📁 Project Structure

```text
NEXUS/
│
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   └── routes.py
│
├── risk_engine/
│   ├── risk_rules.py
│   └── process_data.py
│
├── graph_engine/
│   ├── relationships.py
│   ├── graph_builder.py
│   └── cluster_detector.py
│
├── evidence/
│   ├── evidence_engine.py
│   └── scoring.py
│
├── adversarial/
│   ├── attack_simulator.py
│   ├── device_rotation.py
│   ├── ip_rotation.py
│   └── resilience_analyzer.py
│
├── evaluation/
│   ├── metrics.py
│   └── run_evaluation.py
│
├── tests/
│
├── data/
│   └── generated/
│
├── run_graph_evidence.py
├── run_adversarial.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Technology Stack

| Technology          | Purpose                                     |
| ------------------- | ------------------------------------------- |
| Python              | Core implementation                         |
| Pandas              | Synthetic data processing                   |
| NetworkX            | Relationship graph and connected components |
| Flask               | Web dashboard/API                           |
| Gunicorn            | Production web server                       |
| Pytest              | Automated testing                           |
| HTML/CSS/JavaScript | Dashboard interface                         |
| Render              | Live deployment                             |

NEXUS intentionally uses a lightweight architecture. The adversarial module does not require Kafka, Neo4j, microservices, graph neural networks, or distributed infrastructure. The participant handoff specifically recommends deterministic Pandas + NetworkX logic for this prototype.

---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/knimu/NEXUS.git
cd NEXUS
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the application

```bash
python -m app
```

The dashboard will be available at:

```text
http://127.0.0.1:5000
```

---

# 🧪 Running the Tests

Run the complete test suite:

```bash
python -m pytest -q
```

The final development test suite currently contains **39 passing tests**.

The tests cover areas including:

* graph construction
* relationship detection
* evidence extraction
* integration
* adversarial mutation
* determinism
* data integrity
* evaluation metrics
* application behavior

---

# 🧨 Running Adversarial Experiments

Device rotation:

```bash
python run_adversarial.py --attack device
```

IP rotation:

```bash
python run_adversarial.py --attack ip
```

Combined device + IP rotation:

```bash
python run_adversarial.py --attack both
```

The adversarial process creates mutated outputs rather than silently modifying the original synthetic dataset. The experiment requirements explicitly require preservation of the original data and reproducible before/after analysis.

---

# 🔬 Reproducibility

The adversarial experiment is deterministic.

Given the same input dataset and attack mode:

```text
same input
    +
same attack
    ↓
same mutated data
    ↓
same detection pipeline
    ↓
same resilience measurements
```

This makes the demonstration reproducible for evaluation.

---

# 🔐 Privacy & Safety

NEXUS is designed as a controlled security research prototype.

### The project uses:

* synthetic data
* synthetic account IDs
* synthetic infrastructure identifiers
* controlled adversarial mutations

### The project does not:

* use real customer banking data
* identify real criminals
* automatically freeze accounts
* automatically block transactions
* make real financial decisions
* claim that a candidate cluster is proof of criminal activity

Candidate clusters represent **investigation signals**, not confirmed fraud findings.

---

# ⚠️ Limitations

NEXUS is a prototype and has several limitations.

### Infrastructure dependence

Device and IP relationships are useful signals, but an adversary can modify them.

### Synthetic data

The experiments are controlled and synthetic. Results should not be interpreted as production fraud-detection performance.

### Candidate clustering

Connected components identify relationship candidates. A candidate cluster is not automatically a confirmed fraud case.

### Limited behavioral features

The current prototype uses a controlled set of behavioral signals rather than a production-scale behavioral model.

### No real-time banking integration

The application does not connect to real banking infrastructure or transaction systems.

### Human review remains necessary

The system provides evidence and prioritization for investigation. The final decision remains with a human analyst.

---

# 🧠 Key Takeaway

Traditional detection evaluation can ask:

> **Can the system detect the suspicious network?**

NEXUS adds another question:

> **How much of that detection survives when the adversary changes infrastructure?**

The project therefore evaluates both:

```text
Detection
   +
Explainability
   +
Adversarial Resilience
   +
Human Decision Control
```

The central result is not that the adversarial attack completely defeats the system.

Instead, NEXUS makes the impact measurable:

```text
Infrastructure changes
        ↓
Relationship evidence changes
        ↓
Graph structure changes
        ↓
Candidate visibility changes
        ↓
Remaining evidence is measured
        ↓
Analyst receives an auditable result
```

---

# 🏆 AI Defense Lab 2026

**Track:** Fraud, Scam & Identity Defense

**Project:** NEXUS — Adversarial Fraud Network Investigation & Resilience

NEXUS demonstrates a complete security workflow from synthetic signals to investigation evidence, adversarial testing, resilience measurement, and human-controlled action.

---

## Team

Built by a team of 4 for AI Defense Lab 2026.

---

## License

This project is provided as a hackathon/research prototype. See the repository for the applicable project licensing information.
