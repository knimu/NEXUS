# NEXUS — Adversarial Fraud Network Detection & Resilience

> AI Defense Lab 2026 — Track 2: Fraud, Scam & Identity Defense

NEXUS is an adversarial fraud-network investigation platform that detects suspicious relationships between synthetic accounts, extracts supporting evidence, calculates risk, severity and confidence, and evaluates how detection changes when an adversary rotates infrastructure such as devices and IP addresses.

The main objective is not only to detect suspicious networks, but also to measure how much detection evidence survives when an adversary changes its infrastructure.

NEXUS uses synthetic data, deterministic security logic, controlled adversarial mutations, evidence-based analysis, evaluation metrics, and human-controlled analyst decisions.

---

## Project Links

### GitHub Repository

https://github.com/knimu/NEXUS

### Live Demo

https://nexus-1-epu2.onrender.com/

### Demo Video

https://youtu.be/hlY9bTJmhkU

---

## Problem

Coordinated fraud can involve multiple accounts that are connected through shared infrastructure or behavioral patterns.

Examples of useful relationship signals include:

- Shared device
- Shared IP address
- Shared beneficiary
- Temporal proximity
- Behavioral overlap

An adversary can attempt to reduce its visibility by changing infrastructure identifiers such as devices and IP addresses.

A detection system that depends heavily on a single infrastructure relationship may therefore lose evidence when those identifiers change.

NEXUS addresses this problem by combining:

- Relationship-based detection
- Graph analysis
- Evidence extraction
- Risk scoring
- Severity and confidence
- Adversarial infrastructure mutation
- Before/after resilience analysis
- Human-controlled decisions
- Audit logging

---

## Security Objective

### Threat

A coordinated synthetic fraud network attempts to reduce its visibility by rotating infrastructure identifiers.

### Protected Asset

The ability of an analyst to identify, investigate, and prioritize suspicious account relationships.

### Security Outcome

NEXUS measures:

- Suspicious account relationships
- Supporting evidence
- Candidate cluster risk
- Severity
- Confidence
- Evidence lost after adversarial changes
- Remaining relationships after infrastructure rotation
- Changes in candidate-cluster structure

The system does not identify real criminals, freeze accounts, block real transactions, or make irreversible financial decisions.

---

## End-to-End Workflow

```text
Synthetic Transaction Signals
            |
            v
     Individual Risk
            |
            v
    Relationship Graph
            |
            v
    Candidate Clusters
            |
            v
   Evidence Extraction
            |
            v
 Risk / Severity / Confidence
            |
            v
       Dashboard
            |
            v
 Adversarial Device/IP Rotation
            |
            v
       Mutated Data
            |
            v
   Same Detection Pipeline
            |
            v
    Before / After
            |
            v
   Resilience Analysis
            |
            v
      Human Decision
            |
            v
        Audit Log
Core Components
1. Synthetic Data

NEXUS operates on controlled synthetic transaction data.

The dataset contains synthetic accounts and events representing different scenarios, including:

LEGIT_SHARED
FRAUD_OBVIOUS
FRAUD_EVASIVE
LEGIT_BORDERLINE
FRAUD_MIXED

The data contains attributes such as:

Account ID
Device ID
IP ID
Beneficiary ID
Timestamp
Transaction amount
Behavioral indicators
Scenario information used for evaluation

No real customer, banking, or personally identifiable information is used.

2. Individual Risk Analysis

The first stage processes transaction and account activity and generates individual risk signals.

These signals are used by the downstream relationship and evidence-analysis pipeline.

3. Relationship Graph

NEXUS builds an account relationship graph using shared attributes.

The main relationship signals include:

Shared device
Shared IP
Shared beneficiary

The graph is implemented using NetworkX.

Connected account components are converted into candidate clusters.

Ground-truth labels are not used to construct the detection graph.

4. Evidence Extraction

Each candidate cluster is accompanied by structured evidence.

Infrastructure Evidence
Shared devices
Shared IP addresses
Shared beneficiaries
Temporal Evidence

Accounts conducting transactions within a defined time window can contribute temporal evidence.

Behavioral Evidence

The system evaluates controlled behavioral indicators including:

High transaction amount
High transaction frequency
Rapid transactions
Suspicious beneficiary behavior

The evidence is retained as structured data so that an analyst can inspect why a candidate cluster was surfaced.

Risk, Severity & Confidence

NEXUS exposes multiple dimensions of the investigation result:

Cluster risk
Severity
Confidence
Relationship evidence
Temporal evidence
Behavioral evidence

This allows the analyst to inspect why a candidate cluster was surfaced instead of relying only on a single probability.

Candidate-cluster membership is an investigation signal and is not equivalent to confirmed fraud.

Adversarial Resilience Testing

The distinguishing component of NEXUS is controlled adversarial infrastructure rotation.

Three adversarial scenarios are evaluated:

Device Rotation
IP Rotation
Combined Device + IP Rotation
1. Device Rotation

Accounts retain their other information but receive different device identifiers.

Example:

Before:

A101 -> D20
A102 -> D20
A103 -> D20


After:

A101 -> D101
A102 -> D102
A103 -> D103

The shared-device relationship is therefore removed.

2. IP Rotation

Accounts receive different IP identifiers while other transaction information remains unchanged.

Example:

Before:

A101 -> IP20
A102 -> IP20
A103 -> IP20


After:

A101 -> IP101
A102 -> IP102
A103 -> IP103

The shared-IP relationship is therefore removed.

3. Combined Device + IP Rotation

Both infrastructure identifiers are changed.

Example:

Before:

A101 -> D20 + IP20
A102 -> D20 + IP20
A103 -> D20 + IP20


After:

A101 -> D101 + IP101
A102 -> D102 + IP102
A103 -> D103 + IP103

The adversarial simulator does not intentionally modify the other core synthetic signals used in the experiment.

Same Detector Principle

The adversarial experiment uses the same detection and evidence pipeline before and after mutation.

Baseline Data
      |
      v
Detection Pipeline
      |
      v
Baseline Results
      |
      v
Infrastructure Mutation
      |
      v
Mutated Data
      |
      v
Same Detection Pipeline
      |
      v
Adversarial Results
      |
      v
Before / After Comparison
      |
      v
Resilience Analysis

This allows the experiment to measure the effect of infrastructure changes rather than comparing different detection systems.

Ground truth is reserved for post-detection evaluation and is not used to:

Construct the detection graph
Perform clustering
Calculate detection evidence
Select the adversarial mutation
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

The graph still retained other relationship and behavioral evidence.

Evidence:
63 -> 55

Evidence survival:
87.3%
IP Rotation

Shared-IP relationships were removed.

The relationship graph became more fragmented.

Clusters:
13 -> 4

Clustered accounts:
50 -> 30

Evidence:
63 -> 28

Evidence survival:
44.4%
Combined Device + IP Rotation

Both shared-device and shared-IP relationships were removed.

Remaining evidence included other signals such as:

Shared beneficiaries
Temporal proximity
Behavioral overlap

Results:

Clusters:
13 -> 6

Clustered accounts:
50 -> 30

Evidence:
63 -> 30

Evidence survival:
47.6%

The experiment demonstrates both:

Residual detection evidence after infrastructure rotation
The limitation of infrastructure-dependent relationship detection
Important Interpretation of Clustered Accounts

Clustered Accounts means accounts belonging to connected candidate components.

It does not mean confirmed fraudulent accounts.

For example:

Before IP Rotation:
50 clustered accounts

After IP Rotation:
30 clustered accounts

This means that the relationship graph became more fragmented.

It should not be interpreted as:

"20 fraud accounts escaped detection."

Candidate-cluster membership and ground-truth labels are kept separate.

The ground truth is used only for post-detection evaluation.

Evaluation

NEXUS includes a separate evaluation layer that compares candidate-cluster outputs against synthetic ground truth after the detection process.

Metrics include:

Precision
Recall
F1 score
False-positive rate
True positives
False positives
False negatives
True negatives
Candidate Cluster Evaluation
Scenario	Precision	Recall	F1	False Positive Rate
Baseline	60%	100%	75%	100%
Device Rotation	60%	100%	75%	100%
IP Rotation	100%	100%	100%	0%
Combined Device + IP Rotation	100%	100%	100%	0%
High-Severity Evaluation

For the high-severity subset:

Scenario	Precision	Recall	F1	False Positive Rate
Baseline	100%	100%	100%	0%
Device Rotation	100%	100%	100%	0%
IP Rotation	100%	100%	100%	0%
Combined Device + IP Rotation	100%	100%	100%	0%

These metrics are based on the controlled synthetic evaluation dataset and should not be interpreted as production fraud-detection performance.

Evaluation Data Separation

Ground-truth labels are intentionally separated from the detection process.

Ground truth is not used to:

Construct the relationship graph
Create candidate clusters
Calculate detection evidence
Calculate detection risk
Select the adversarial mutation
Alter the detection algorithm

Ground truth is used after detection to evaluate the resulting candidate clusters.

Human Analyst Control

NEXUS does not automatically freeze, block, or close accounts.

The automated system provides evidence and prioritization for analyst review.

Available analyst decisions include:

ALLOW
REVIEW
ESCALATE

A decision can include:

Timestamp
Cluster ID
Decision
Analyst reason

This creates an auditable record of the human-controlled response.

NEXUS therefore acts as decision support rather than autonomous enforcement.

Audit Trail

Example analyst decisions:

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

Total accounts
Candidate clusters
Clustered accounts
High-severity clusters
Evidence count
Candidate Cluster Investigation

Displays:

Cluster membership
Relationship evidence
Risk
Severity
Confidence
Supporting evidence
Adversarial Resilience Analysis

Displays:

Baseline
Device rotation
IP rotation
Combined rotation
Cluster changes
Evidence survival
Risk changes
Confidence changes
Evaluation

Displays:

Precision
Recall
F1
False-positive rate
Evaluation results across adversarial cases
Human Analyst Audit Trail

Displays:

Cluster
Analyst decision
Reason
Timestamp
Architecture

The high-level architecture is:

                    +--------------------------+
                    |   Synthetic Transaction  |
                    |          Data            |
                    |                          |
                    | Accounts / Devices / IPs |
                    | Beneficiaries / Time     |
                    | Amounts / Behavior       |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |    Individual Risk       |
                    |        Analysis          |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |    Relationship Graph    |
                    |         NetworkX         |
                    |                          |
                    | Shared Device / IP /     |
                    | Beneficiary Relationships |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   Candidate Clusters     |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |    Evidence Extraction   |
                    |                          |
                    | Relationship / Temporal  |
                    | Behavioral Evidence      |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    | Risk / Severity /         |
                    | Confidence                |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |      Flask API            |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |       Dashboard           |
                    +------+-------------------+
                           |
              +------------+-------------+
              |                          |
              v                          v
   +----------------------+    +--------------------------+
   | Human Analyst        |    | Adversarial Testing      |
   |                      |    |                          |
   | ALLOW                |    | Device Rotation          |
   | REVIEW               |    | IP Rotation              |
   | ESCALATE             |    | Combined Rotation        |
   +----------+-----------+    +------------+-------------+
              |                             |
              v                             v
   +----------------------+      +-------------------------+
   |      Audit Log       |      |      Mutated Data       |
   +----------------------+      +------------+------------+
                                             |
                                             v
                                  +-------------------------+
                                  | SAME Detection Pipeline |
                                  +------------+------------+
                                               |
                                               v
                                  +-------------------------+
                                  | Before / After          |
                                  | Resilience Analysis     |
                                  +-------------------------+

The adversarial experiment intentionally sends the mutated data back through the same detection pipeline.

Technology Stack
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

Project Structure
NEXUS/
|
+-- app/
|   +-- __init__.py
|   +-- __main__.py
|   +-- routes.py
|
+-- risk_engine/
|
+-- graph_engine/
|
+-- evidence/
|
+-- adversarial/
|   +-- attack_simulator.py
|   +-- device_rotation.py
|   +-- ip_rotation.py
|   +-- resilience_analyzer.py
|   +-- run_adversarial.py
|
+-- evaluation/
|   +-- __init__.py
|   +-- metrics.py
|   +-- run_evaluation.py
|
+-- tests/
|   +-- test_evaluation.py
|
+-- data/
|   +-- generated/
|
+-- requirements.txt
+-- .gitignore
+-- README.md
Installation
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
Running the Application

Run:

python -m app

The local application will be available at:

http://127.0.0.1:5000
Running Tests

Run the test suite:

python -m pytest -q

The current test suite covers areas including:

Graph construction
Relationship detection
Evidence extraction
Integration
Adversarial mutation
Determinism
Data integrity
Evaluation metrics
Application behavior
Running the Adversarial Experiments

Run the complete adversarial experiment suite from the repository root:

python -m adversarial.run_adversarial

The runner evaluates:

Baseline
Device rotation
IP rotation
Combined device + IP rotation

The generated results are used by the resilience analysis and dashboard.

Running the Evaluation

Run:

python -m evaluation.run_evaluation

The evaluation compares detection outputs against synthetic ground truth after the detection process has completed.

API

NEXUS exposes a Flask API.

Main Application
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

Testing Coverage

NEXUS was tested using multiple categories of security scenarios.

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

Privacy & Safety

NEXUS is a controlled security research and hackathon prototype.

The project uses
Synthetic transaction data
Synthetic account identifiers
Synthetic infrastructure identifiers
Controlled adversarial mutations
Synthetic ground-truth labels for evaluation
The project does not
Use real customer banking data
Use confidential personal information
Identify real criminals
Connect to real banking systems
Automatically freeze accounts
Automatically block transactions
Execute financial transactions
Make irreversible financial decisions
Treat candidate clusters as proof of criminal activity

Candidate clusters represent investigation signals that require analyst interpretation.

Dataset & Data Sources

All data used for the NEXUS demonstration is synthetic.

No external private or confidential dataset is used.

Synthetic data includes controlled:

Account identifiers
Device identifiers
IP identifiers
Beneficiary identifiers
Timestamps
Transaction amounts
Behavioral indicators
Scenario labels

The ground-truth fields are reserved for post-detection evaluation.

No real customer or banking information is required to run the project.

APIs & External Services

NEXUS does not depend on an external fraud-detection API or banking API.

GitHub

Used for:

Source-code hosting
Version control
Project submission
Render

Used for:

Live deployment of the Flask application

The core detection pipeline does not require external API credentials.

Dependencies

The Python dependencies are listed in:

requirements.txt

Core dependencies include:

pandas
networkx
flask
gunicorn
pytest

These are standard open-source libraries used for:

Data processing
Graph analysis
Web application development
Production serving
Automated testing
Pre-existing Components

NEXUS was developed as a project for AI Defense Lab 2026.

No pre-existing NEXUS implementation was intentionally reused as the core project.

The project uses standard open-source libraries including:

Pandas
NetworkX
Flask
Gunicorn
Pytest
Secrets & Credentials

No API keys, passwords, authentication tokens, private credentials, or confidential data are required for the core project.

Do not add credentials or secrets to the repository.

Reproducibility

The adversarial experiments use controlled mutations and the same detection pipeline for comparison.

The experimental principle is:

Same Input
    +
Same Mutation
    +
Same Detection Pipeline
    |
    v
Reproducible Output

This allows baseline and adversarial cases to be compared consistently.

Limitations
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

Banking infrastructure
Payment processors
Real transaction systems
Customer identity systems
6. Human Review

The system provides investigation evidence and prioritization.

Final operational decisions remain under human control.

7. Adversarial Coverage

The current resilience experiments focus on controlled device and IP rotation.

Other evasion techniques, such as more complex behavioral mimicry or coordinated changes across additional attributes, are outside the current prototype scope.

Demo

The demonstration covers:

Fraud-network detection
Candidate cluster generation
Evidence extraction
Risk, severity and confidence
Device rotation
IP rotation
Combined device + IP rotation
Before/after resilience analysis
Evaluation results
Human analyst decisions
Audit logging
YouTube Demo

https://youtu.be/hlY9bTJmhkU

Live Application

https://nexus-1-epu2.onrender.com/

AI Defense Lab 2026

Event: AI Defense Lab 2026

Track: Track 2 — Fraud, Scam & Identity Defense

Project: NEXUS — Adversarial Fraud Network Detection & Resilience

NEXUS implements the following security workflow:

Signal
  |
  v
Security Analysis
  |
  v
Evidence
  |
  v
Decision
  |
  v
Controlled Action

The system additionally incorporates:

Adversarial Testing
        +
Evaluation
        +
Auditability
        +
Human Control
Team

NEXUS was developed by a team of 4 for AI Defense Lab 2026.

Team-member details are provided through the official hackathon submission form.

Key Takeaway

NEXUS does not treat fraud detection as a single classification result.

Instead, it evaluates:

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
        |
        v
Relationship Evidence Changes
        |
        v
Graph Structure Changes
        |
        v
Candidate Visibility Changes
        |
        v
Remaining Evidence Is Measured
        |
        v
Analyst Receives an Auditable Result

The objective is to make the effect of adversarial infrastructure changes measurable while keeping the final security decision human-controlled.

License

This project is provided as a hackathon/research prototype.

No separate open-source license is currently specified for this repository.
