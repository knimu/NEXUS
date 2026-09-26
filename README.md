# NEXUS — Adversarial Fraud Network Detection & Resilience

> **AI Defense Lab 2026 · Track 2: Fraud, Scam & Identity Defense**

NEXUS is a fraud-network investigation platform that detects suspicious relationships between synthetic accounts, extracts supporting evidence, assigns risk/severity/confidence, and evaluates how detection changes when an adversary rotates infrastructure such as devices and IP addresses.

The system combines **graph-based relationship analysis, evidence extraction, adversarial testing, evaluation, and human-controlled decisions**.

---

## 🔗 Links

- **GitHub:** https://github.com/knimu/NEXUS
- **Live Demo:** https://nexus-1-epu2.onrender.com/
- **Demo Video:** https://youtu.be/hlY9bTJmhkU

---

## 🎯 Problem

Coordinated fraud networks can connect multiple accounts through shared:

- Devices
- IP addresses
- Beneficiaries
- Temporal patterns
- Behavioral signals

An adversary can rotate infrastructure identifiers to weaken relationship-based detection.

**NEXUS asks:**  
> How much detection evidence remains when shared infrastructure is removed?

---

## 🛡️ Solution

NEXUS follows an evidence-based investigation workflow:

```text
Synthetic Signals
       ↓
Individual Risk
       ↓
Relationship Graph
       ↓
Candidate Clusters
       ↓
Evidence Extraction
       ↓
Risk / Severity / Confidence
       ↓
Human Decision
       ↓
Audit Log
```

Adversarial testing then modifies infrastructure and sends the data through the **same detection pipeline**:

```text
Baseline Data
     ↓
Detection Pipeline
     ↓
Baseline Results
     ↓
Device / IP Rotation
     ↓
Mutated Data
     ↓
Same Detection Pipeline
     ↓
Adversarial Results
     ↓
Resilience Analysis
```

---

## 🔍 Detection Signals

NEXUS uses synthetic signals including:

| Signal | Purpose |
|---|---|
| Shared Device | Infrastructure relationship |
| Shared IP | Infrastructure relationship |
| Shared Beneficiary | Account relationship |
| Temporal Proximity | Activity correlation |
| Behavioral Indicators | Suspicious activity evidence |

Candidate clusters are **investigation signals, not confirmed fraud verdicts**.

---

## ⚔️ Adversarial Testing

Three controlled scenarios are evaluated:

1. **Device Rotation**
2. **IP Rotation**
3. **Combined Device + IP Rotation**

### Results

| Scenario | Clusters | Clustered Accounts | Shared Devices | Shared IPs | Evidence | Evidence Survival |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 13 | 50 | 8 | 23 | 63 | 100% |
| Device Rotation | 13 | 50 | 0 | 23 | 55 | 87.3% |
| IP Rotation | 4 | 30 | 8 | 0 | 28 | 44.4% |
| Combined Rotation | 6 | 30 | 0 | 0 | 30 | 47.6% |

### Key observation

Infrastructure rotation fragments the relationship graph and removes evidence, but other signals such as **shared beneficiaries, temporal proximity, and behavioral overlap** can remain.

The experiment also demonstrates the limitation of infrastructure-dependent detection.

---

## 📊 Evaluation

Ground truth is used **only after detection** for evaluation. It is not used to construct the graph, perform clustering, calculate evidence, or select adversarial mutations.

### Candidate Cluster Metrics

| Scenario | Precision | Recall | F1 | False Positive Rate |
|---|---:|---:|---:|---:|
| Baseline | 60% | 100% | 75% | 100% |
| Device Rotation | 60% | 100% | 75% | 100% |
| IP Rotation | 100% | 100% | 100% | 0% |
| Combined Rotation | 100% | 100% | 100% | 0% |

These results are from the controlled synthetic evaluation dataset and **do not represent production fraud-detection performance**.

---

## 👤 Human Control & Auditability

NEXUS does not automatically freeze accounts or block transactions.

The analyst can choose:

```text
ALLOW
REVIEW
ESCALATE
```

Each decision can be recorded with:

- Cluster ID
- Decision
- Reason
- Timestamp

This provides an auditable human-controlled response.

---

## 🏗️ Architecture

```text
┌─────────────────────┐
│  Synthetic Dataset  │
│ Accounts / Devices  │
│ IPs / Beneficiaries │
│ Time / Behavior     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Individual Risk    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Relationship Graph  │
│     NetworkX        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Candidate Clusters  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Evidence Extraction │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Risk / Severity /   │
│ Confidence          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Flask API +         │
│ Dashboard           │
└───────┬─────────────┘
        │
   ┌────┴─────┐
   ↓          ↓
Human      Adversarial
Analyst      Testing
   ↓          ↓
Audit      Mutated Data
Log           ↓
          Same Pipeline
               ↓
        Resilience Analysis
```

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Pandas | Data processing |
| NetworkX | Relationship graph analysis |
| Flask | API and web application |
| HTML/CSS/JavaScript | Dashboard |
| Gunicorn | Production server |
| Pytest | Testing |
| Render | Deployment |

---

## 📁 Project Structure

```text
NEXUS/
├── app/
├── risk_engine/
├── graph_engine/
├── evidence/
├── adversarial/
├── evaluation/
├── tests/
├── data/
│   └── generated/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### Requirements

- Python 3.9+
- Git
- pip

### Setup

```bash
git clone https://github.com/knimu/NEXUS.git
cd NEXUS

python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run

Start the application:

```bash
python -m app
```

Open:

```text
http://127.0.0.1:5000
```

### Run tests

```bash
python -m pytest -q
```

### Run adversarial experiments

```bash
python -m adversarial.run_adversarial
```

### Run evaluation

```bash
python -m evaluation.run_evaluation
```

---

## 🔌 API

| Endpoint | Purpose |
|---|---|
| `GET /` | Dashboard |
| `GET /api/overview` | System overview |
| `GET /api/clusters` | Candidate clusters |
| `GET /api/clusters/<cluster_id>` | Cluster details |
| `GET /api/adversarial` | Resilience results |
| `GET /api/adversarial/<attack_type>` | Specific adversarial case |
| `GET /api/evaluation` | Evaluation metrics |
| `GET /api/audit` | Analyst audit log |
| `POST /api/decisions` | Record analyst decision |

Supported adversarial cases:

```text
baseline
device_rotation
ip_rotation
combined
```

---

## 🔐 Data & Safety

NEXUS uses **synthetic data only**.

The project does not:

- Use real customer or banking data
- Connect to real banking systems
- Identify real criminals
- Execute financial transactions
- Automatically freeze accounts
- Automatically block transactions

No API keys or private credentials are required.

---

## ⚠️ Limitations

- Results are based on synthetic data.
- Infrastructure rotation can fragment relationship graphs.
- The current prototype evaluates a controlled set of behavioral signals.
- Candidate clusters are investigation signals, not confirmed fraud.
- The adversarial experiments focus on device and IP rotation.
- No real-time banking integration is implemented.

---

## 🏆 Project Context

**Event:** AI Defense Lab 2026  
**Track:** Fraud, Scam & Identity Defense  
**Project:** NEXUS — Adversarial Fraud Network Detection & Resilience  
**Team:** 4 members

### Core Security Workflow

```text
Signal
  ↓
Analysis
  ↓
Evidence
  ↓
Decision
  ↓
Controlled Action
```

NEXUS extends this workflow with **adversarial resilience testing, evaluation, and auditability** while keeping the final decision human-controlled.

---

## 📜 License

This project is provided as a hackathon/research prototype.  
No separate open-source license is currently specified.
