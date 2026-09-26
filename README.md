# NEXUS — Adversarial Fraud Network Detection & Resilience

> **AI Defense Lab 2026 — Track 2: Fraud, Scam & Identity Defense**

NEXUS is an adversarial fraud-network investigation platform that detects suspicious relationships between synthetic accounts, extracts supporting evidence, calculates risk/severity/confidence, and evaluates how detection changes when an adversary rotates infrastructure such as devices and IP addresses.

Instead of evaluating only whether a suspicious network can be detected, NEXUS also measures:

> **How much detection evidence survives when the adversary changes its infrastructure?**

The system uses synthetic data, controlled adversarial mutations, deterministic security logic, and human-controlled analyst decisions.

---

## Project Links

### Source Code

https://github.com/knimu/NEXUS

### Live Demo

https://nexus-1-epu2.onrender.com/

### Presentation / Demo Video

https://youtu.be/hlY9bTJmhkU

---

# Problem

Coordinated fraud can involve multiple accounts that are connected through shared infrastructure or behavioral patterns.

For example, multiple accounts may:

- share a device
- share an IP address
- send funds to the same beneficiary
- perform transactions within a similar time window
- exhibit overlapping suspicious behavioral patterns

These relationships can reveal a potential fraud network.

However, an adversary can attempt to reduce its visibility by changing infrastructure identifiers such as devices and IP addresses.

A detection system that depends heavily on a single infrastructure relationship may therefore lose evidence when those identifiers change.

NEXUS addresses this problem by combining:

- relationship-based detection
- graph analysis
- evidence extraction
- risk scoring
- severity and confidence
- adversarial infrastructure mutation
- before/after resilience analysis
- human-controlled decisions
- audit logging

---

# Security Objective

## Threat

A coordinated synthetic fraud network attempts to reduce its visibility by rotating infrastructure identifiers.

## Protected Asset

The ability of an analyst to identify, investigate, and prioritize suspicious account relationships.

## Security Outcome

NEXUS measures:

- suspicious account relationships
- supporting evidence
- candidate cluster risk
- severity
- confidence
- evidence lost after adversarial changes
- remaining relationships after infrastructure rotation
- changes in candidate-cluster structure

The system does **not** identify real criminals, freeze accounts, block real transactions, or make irreversible financial decisions.

---

# End-to-End Workflow

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

The adversarial experiment reuses the same detection and evidence pipeline after mutation. This allows the experiment to measure the effect of the infrastructure change rather than comparing different detection systems.

Core Components
1. Synthetic Data

NEXUS operates on controlled synthetic transaction data.

The dataset contains 50 synthetic accounts/events across scenarios including:

LEGIT_SHARED
FRAUD_OBVIOUS
FRAUD_EVASIVE
LEGIT_BORDERLINE
FRAUD_MIXED

The data contains attributes such as:

account ID
device ID
IP ID
beneficiary ID
timestamp
transaction amount
behavioral indicators
scenario information used for evaluation

No real customer, banking, or personally identifiable information is used.

2. Individual Risk Analysis

The first stage processes transaction/account activity and generates individual risk signals.

These signals are used by the downstream relationship and evidence analysis pipeline.

Generated output includes:

data/generated/risk_results.csv
3. Relationship Graph

NEXUS builds an account relationship graph using shared attributes.

The main relationship signals include:

shared device
shared IP
shared beneficiary

The graph is implemented using NetworkX.

Connected account components are converted into candidate clusters.

Ground-truth labels are not used to construct the detection graph.

4. Evidence Extraction

Each candidate cluster is accompanied by structured evidence.

Infrastructure Evidence
shared devices
shared IP addresses
shared beneficiaries
Temporal Evidence

Accounts conducting transactions within a defined time window can contribute temporal evidence.

Behavioral Evidence

The system evaluates controlled behavioral indicators including:

high transaction amount
high transaction frequency
rapid transactions
suspicious beneficiary behavior

The evidence is retained as structured data so that analysts can inspect why a candidate cluster was surfaced.

 Risk, Severity & Confidence

NEXUS exposes multiple dimensions of the investigation result:

cluster risk
severity
confidence
relationship evidence
temporal evidence
behavioral evidence

This allows the analyst to inspect the evidence supporting a candidate cluster instead of relying only on a single black-box probability.

Candidate-cluster membership is an investigation signal and is not equivalent to confirmed fraud.

 Adversarial Resilience Testing

The distinguishing component of NEXUS is controlled adversarial infrastructure rotation.

Three attack scenarios are evaluated.

1. Device Rotation

Accounts retain their other information but receive different device identifiers.

Example:

Before:

A101 → D20
A102 → D20
A103 → D20

After:

A101 → D101
A102 → D102
A103 → D103

The shared-device relationship is therefore removed.

2. IP Rotation

Accounts receive different IP identifiers while the other transaction information remains unchanged.

Example:

Before:

A101 → IP20
A102 → IP20
A103 → IP20

After:

A101 → IP101
A102 → IP102
A103 → IP103

The shared-IP relationship is therefore removed.

3. Combined Device + IP Rotation

Both infrastructure identifiers are changed.

Before:

A101 → D20 + IP20
A102 → D20 + IP20
A103 → D20 + IP20

After:

A101 → D101 + IP101
A102 → D102 + IP102
A103 → D103 + IP103

The adversarial simulator does not intentionally modify:

account identity
beneficiary
transaction amount
timestamp
scenario
ground-truth fields

for these experiments.

 Same Detector Principle

The adversarial experiment follows the same detection process before and after mutation:

Baseline Data
     │
     ▼
Existing Detection Pipeline
     │
     ▼
Baseline Clusters + Evidence
     │
     ▼
Infrastructure Mutation
     │
     ▼
Mutated Data
     │
     ▼
Same Detection Pipeline
     │
     ▼
New Clusters + Evidence
     │
     ▼
Before / After Comparison
     │
     ▼
Resilience Analysis

This allows NEXUS to measure how the attack changes the graph and evidence rather than changing the detector itself.

Ground truth is reserved for post-detection evaluation and is not used to construct the detection graph, perform clustering, calculate detection evidence, or choose the adversarial mutation.

 Adversarial Resilience Results

NEXUS was tested against three controlled infrastructure changes.

Scenario	Clusters	Clustered Accounts	Shared Devices	Shared IPs	Shared Beneficiaries	Evidence	Evidence Survival
Baseline	13	50	8	23	6	63	100%
Device Rotation	13	50	0	23	6	55	87.3%
IP Rotation	4	30	8	0	6	28	44.4%
Combined Device + IP Rotation	6	30	0	0	6	30	47.6%
Interpretation
Device Rotation

Shared-device relationships were removed.

The graph still retained other relationship and behavioral evidence, resulting in:

Evidence:
63 → 55

Evidence survival:
87.3%
IP Rotation

Shared-IP relationships were removed.

The relationship graph became substantially more fragmented:

Clusters:
13 → 4

Clustered accounts:
50 → 30

Evidence:
63 → 28

Evidence survival:
44.4%
Combined Device + IP Rotation

Both shared-device and shared-IP relationships were removed.

The remaining evidence included other signals such as:

shared beneficiaries
temporal proximity
behavioral overlap

Results:

Clusters:
13 → 6

Clustered accounts:
50 → 30

Evidence:
63 → 30

Evidence survival:
47.6%

The experiment therefore demonstrates both:

residual detection evidence after infrastructure rotation
the limitation of infrastructure-dependent relationship detection

 Important Interpretation of Clustered Accounts

Clustered Accounts means accounts belonging to connected candidate components.

It does not mean confirmed fraudulent accounts.

For example:

Before IP Rotation:
50 clustered accounts

After IP Rotation:
30 clustered accounts

This means the relationship graph became more fragmented.

It should not be interpreted as:

"20 fraud accounts escaped detection."

Candidate-cluster membership and ground-truth labels are kept separate.

The ground truth is used only for post-detection evaluation.

Evaluation

NEXUS includes a separate evaluation layer that compares candidate-cluster outputs against synthetic ground truth after the detection process.

Metrics include:

population
actual positives
predicted positives
true positives
false positives
false negatives
true negatives
precision
recall
F1
false-positive rate
Candidate Cluster Evaluation
Scenario	Precision	Recall	F1	False Positive Rate
Baseline	60%	100%	75%	100%
Device Rotation	60%	100%	75%	100%
IP Rotation	100%	100%	100%	0%
Combined Device + IP Rotation	100%	100%	100%	0%
High-Severity Evaluation

For the high-severity subset, the evaluation results are:

Scenario	Precision	Recall	F1	False Positive Rate
Baseline	100%	100%	100%	0%
Device Rotation	100%	100%	100%	0%
IP Rotation	100%	100%	100%	0%
Combined Device + IP Rotation	100%	100%	100%	0%

These metrics are based on the controlled synthetic evaluation dataset and should not be interpreted as production fraud-detection performance.

 Evaluation Data Separation

Ground-truth labels are intentionally separated from the detection process.

Ground truth is not used to:

construct the relationship graph
create candidate clusters
calculate detection evidence
calculate detection risk
select the adversarial mutation
alter the detection algorithm

Ground truth is used after detection to evaluate the resulting candidate clusters.

This separation reduces evaluation leakage into the detection workflow.

 Human Analyst Control

NEXUS does not automatically freeze, block, or close accounts.

The automated system provides evidence and prioritization for analyst review.

Available analyst decisions include:

ALLOW
REVIEW
ESCALATE

A decision can include:

timestamp
cluster ID
decision
analyst reason

This creates an auditable record of the human-controlled response.

The system therefore acts as decision support rather than autonomous enforcement.

Audit Trail

Example audit decisions:

{
  "cluster_id": "CLUSTER_006",
  "decision": "ESCALATE",
  "reason": "Multiple independent relationship and behavioral signals require analyst review."
}
{
  "cluster_id": "CLUSTER_013",
  "decision": "REVIEW",
  "reason": "Strong relationship evidence requires additional analyst verification before escalation."
}
{
  "cluster_id": "CLUSTER_001",
  "decision": "ALLOW",
  "reason": "Legitimate shared office network verified."
}

The audit trail makes the final operational decision traceable to the analyst.

Dashboard

The dashboard contains the following major sections.

System Overview

Displays:

total accounts
candidate clusters
clustered accounts
high-severity clusters
evidence count
Candidate Cluster Investigation

Displays:

cluster membership
relationship evidence
risk
severity
confidence
supporting evidence
Adversarial Resilience Analysis

Displays:

baseline
device rotation
IP rotation
combined rotation
cluster changes
evidence survival
risk changes
confidence changes
Evaluation

Displays:

precision
recall
F1
false-positive rate
evaluation results across adversarial cases
Human Analyst Audit Trail

Displays:

cluster
analyst decision
reason
timestamp

Architecture
                 ┌────────────────────────┐
                 │   Synthetic Dataset   │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │    Individual Risk     │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   Relationship Graph   │
                 │        NetworkX        │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   Candidate Clusters   │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │    Evidence Engine     │
                 │ Device / IP / Benef.   │
                 │ Temporal / Behavioral  │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │ Risk / Severity /      │
                 │ Confidence             │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │       Flask API        │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │       Dashboard        │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │ Adversarial Simulator  │
                 │ Device / IP Rotation   │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   Same Detection       │
                 │      Pipeline          │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │ Resilience Analyzer    │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │ Human Decision +       │
                 │ Audit Log               │
                 └────────────────────────┘
📁 Project Structure
NEXUS/
│
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   └── routes.py
│
├── risk_engine/
│
├── graph_engine/
│
├── evidence/
│
├── adversarial/
│   ├── attack_simulator.py
│   ├── device_rotation.py
│   ├── ip_rotation.py
│   ├── resilience_analyzer.py
│   └── run_adversarial.py
│
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py
│   └── run_evaluation.py
│
├── tests/
│   └── test_evaluation.py
│
├── data/
│   └── generated/
│
├── requirements.txt
├── .gitignore
└── README.md
⚙️ Technology Stack
Technology	Purpose
Python	Core implementation
Pandas	Synthetic data processing
NetworkX	Relationship graph and graph analysis
Flask	REST API and web application
Gunicorn	Production web server
Pytest	Automated testing
HTML/CSS/JavaScript	Dashboard interface
Render	Live deployment

NEXUS intentionally uses a lightweight architecture suitable for a reproducible security prototype.

🚀 Installation
Requirements
Python 3.9+
Git
pip
1. Clone the Repository
git clone https://github.com/knimu/NEXUS.git
cd NEXUS
2. Create a Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
▶️ Running the Application

Run:

python -m app

The local dashboard/API will be available at:

http://127.0.0.1:5000
🧪 Running Tests

Run the complete test suite:

python -m pytest -q

The current development test suite contains 39 passing tests.

The tests cover areas including:

graph construction
relationship detection
evidence extraction
integration
adversarial mutation
determinism
data integrity
evaluation metrics
application behavior
🧨 Running the Adversarial Experiments

Run the complete adversarial experiment suite from the repository root:

python -m adversarial.run_adversarial

The runner evaluates:

baseline
device rotation
IP rotation
combined device + IP rotation

The generated results are used by the dashboard and resilience analysis.

The original synthetic dataset is preserved; adversarial experiments operate on controlled mutated data.

📊 Evaluation Pipeline

The evaluation can be run with:

python -m evaluation.run_evaluation

The evaluation results are written to the generated evaluation output directory.

The evaluation layer compares detection outputs against synthetic ground truth only after the detection process has completed.

🔌 API

NEXUS exposes a Flask API.

Overview
GET /

Returns the main application/dashboard.

System Overview
GET /api/overview

Returns system-level statistics including accounts, clusters, severity, and evidence.

Candidate Clusters
GET /api/clusters

Returns candidate clusters.

Cluster Details
GET /api/clusters/<cluster_id>

Returns detailed information and evidence for a specific cluster.

Adversarial Summary
GET /api/adversarial

Returns the available adversarial resilience results.

Specific Adversarial Case
GET /api/adversarial/<attack_type>

Supported attack types:

baseline
device_rotation
ip_rotation
combined

Example:

GET /api/adversarial/ip_rotation
Evaluation Results
GET /api/evaluation

Returns evaluation metrics.

Audit Log
GET /api/audit

Returns recorded analyst decisions.

Record Analyst Decision
POST /api/decisions

Records a human analyst decision.

Supported decisions include:

ALLOW
REVIEW
ESCALATE

The endpoint validates malformed or invalid requests and returns appropriate error responses.

🧪 Testing Coverage

NEXUS was tested using multiple categories required for a security prototype:

Normal Case

Legitimate account behavior and shared infrastructure relationships are processed.

Positive / Attack Case

Synthetic fraud relationships are processed and candidate clusters are generated.

Negative Case

Legitimate relationships are included to evaluate false-positive behavior.

Failure Case

Malformed or invalid API inputs are tested to ensure the application handles them safely.

Adversarial Case

Device and IP identifiers are rotated and the same detection pipeline is rerun.

🔐 Privacy & Safety

NEXUS is a controlled security research and hackathon prototype.

The project uses
synthetic transaction data
synthetic account identifiers
synthetic infrastructure identifiers
controlled adversarial mutations
synthetic ground-truth labels for evaluation
The project does not
use real customer banking data
use confidential personal information
identify real criminals
connect to real banking systems
automatically freeze accounts
automatically block transactions
execute financial transactions
make irreversible financial decisions
treat candidate clusters as proof of criminal activity

Candidate clusters represent investigation signals that require analyst interpretation.

📦 Dataset & Data Sources

All data used for the NEXUS demonstration is synthetic.

No external private or confidential dataset is used.

Synthetic data includes controlled:

account identifiers
device identifiers
IP identifiers
beneficiary identifiers
timestamps
transaction amounts
behavioral indicators
scenario labels

The ground-truth fields are reserved for post-detection evaluation.

No real customer or banking information is required to run the project.

🌐 APIs & External Services

NEXUS does not depend on an external fraud-detection API or banking API.

External / Infrastructure Services
GitHub

Used for:

source-code hosting
version control
project submission
Render

Used for:

live deployment of the Flask application

The application does not require external API credentials for its core detection pipeline.

📚 Dependencies

The main Python dependencies are listed in:

requirements.txt

Core dependencies include:

pandas
networkx
flask
gunicorn
pytest

These are standard open-source software libraries used for data processing, graph analysis, web serving, deployment, and testing.

🧩 Pre-existing Components

NEXUS was developed as a project for AI Defense Lab 2026.

No pre-existing NEXUS implementation was intentionally reused as the core project.

The project uses standard open-source libraries such as Pandas, NetworkX, Flask, Gunicorn, and Pytest.

🔑 Secrets & Credentials

No API keys, passwords, authentication tokens, private credentials, or confidential data are required for the core project.

Do not add credentials or secrets to the repository.

🔬 Reproducibility

The adversarial experiment is deterministic for the same input and mutation configuration.

The experimental principle is:

Same Input
    +
Same Mutation
    +
Same Detection Pipeline
    ↓
Reproducible Output

This allows the baseline and adversarial cases to be compared consistently.

⚠️ Limitations

NEXUS is a prototype and has several important limitations.

1. Infrastructure Dependence

Device and IP relationships provide useful signals, but an adversary can change them.

The adversarial experiments demonstrate that removing infrastructure relationships can fragment the graph and reduce available evidence.

2. Synthetic Data

The experiments use controlled synthetic data.

Therefore, the reported metrics should not be interpreted as production fraud-detection performance.

3. Candidate Clustering

Connected components identify relationship candidates.

A candidate cluster is not automatically a confirmed fraud case.

4. Limited Behavioral Features

The prototype uses a controlled set of behavioral indicators rather than a production-scale behavioral model.

5. No Real-Time Banking Integration

NEXUS does not connect to:

banking infrastructure
payment processors
real transaction systems
customer identity systems
6. Human Review

The system provides investigation evidence and prioritization.

Final operational decisions remain under human control.

7. Adversarial Coverage

The current resilience experiments focus on controlled device and IP rotation.

Other evasion techniques, such as more complex behavioral mimicry or coordinated changes across additional attributes, are outside the current prototype scope.

🎥 Demo

The demonstration shows:

the fraud-network detection workflow
candidate cluster generation
evidence extraction
risk/severity/confidence
adversarial device rotation
adversarial IP rotation
combined device + IP rotation
before/after resilience analysis
evaluation results
human analyst decisions
audit logging
YouTube

https://youtu.be/hlY9bTJmhkU

Live Application

https://nexus-1-epu2.onrender.com/

🏆 AI Defense Lab 2026

Event: AI Defense Lab 2026

Track: Track 2 — Fraud, Scam & Identity Defense

Project: NEXUS — Adversarial Fraud Network Detection & Resilience

NEXUS implements a complete security workflow:

Signal
  ↓
Security Analysis
  ↓
Evidence
  ↓
Decision
  ↓
Controlled Action

with additional:

Adversarial Testing
        +
Evaluation
        +
Auditability
        +
Human Control
👥 Team

NEXUS was developed by a team of 4 for AI Defense Lab 2026.

Team-member details are provided through the official hackathon submission form.

📌 Key Takeaway

NEXUS does not treat fraud detection as a single classification result.

It evaluates:

Relationship Detection
        +
Evidence
        +
Risk
        +
Adversarial Resilience
        +
Evaluation
        +
Human Decision Control

The central experiment is:

Infrastructure Rotation
        ↓
Relationship Evidence Changes
        ↓
Graph Structure Changes
        ↓
Candidate Visibility Changes
        ↓
Remaining Evidence Is Measured
        ↓
Analyst Receives an Auditable Result

The objective is to make the effect of adversarial infrastructure changes measurable while keeping the final security decision human-controlled.

License

This project is provided as a hackathon/research prototype.

No separate open-source license is currently specified for this repository.
