# Distributed Causal Engine (DCE) 🌐

## Permanent research workspace

The current repository is the DCE project root. Start with [PRD](PRD.md),
[research questions](RESEARCH_QUESTIONS.md), [architecture](ARCHITECTURE.md),
and the [permanent experiment index](EXPERIMENT_INDEX.md).
Every substantial experiment receives a permanent E-number, a preregistered protocol,
versioned configuration, execution evidence and a decision.

The delivered [R0 package](dce-r0/dce/README.md) is the current executable research foundation.
The package and original notebooks have not been moved. The separate `src/dce_foundation` package now implements the E003 OpenRCA representation/replay path, not reasoning.
The E001 and E002 run ledgers currently record no registered runs. Result directories with E001-R001 and E002-R001/R002 names are present, but are not reconciled with those ledgers; treat them as unverified artifacts rather than registered results until their provenance is resolved.

E003-R001 executed eight bounded cross-system scopes. Later, E003-V006 was accepted as representation/replay infrastructure within its stated scope; it did not establish downstream RCA adequacy. See the [implementation report](docs/E003-implementation-report.md),
[dataset audit](docs/openrca-dataset-analysis.md), [E003 decision](experiments/E003_domain_model_adequacy/decision.md), and dated [V006 review](docs/governance/amendments/2026-10-06-E003-V006-acceptance-and-E004-scope.md).

E004-R001 compared a structural ranking with simpler references and was reviewed as **REVISE / structural prior only**. It is not evidence of causal inference or neuro-symbolic superiority. E005-R001 exercised synthetic telemetry ingestion locally; exact metric timestamp preservation remains unresolved, and it says nothing about RCA effectiveness. Keep these scopes distinct when reading the experiment records.

From the repository root in PowerShell (Python 3.11+ and NetworkX required):

```powershell
$env:PYTHONPATH = 'src'
python -m dce_foundation.replay.openrca --incident Bank@2 --max-rows-per-file 2000
python -m pytest -q tests
```

Use `--output data/processed/openrca/<new-directory>` to serialize separate operational/evaluation outputs.
Preserve run artifacts and their provenance. Do not treat a result directory name, a successful parser, or ingestion correctness as evidence of RCA effectiveness.

The description below is the historical notebook overview. Its production-ready and true-causal-discovery
language is not a statement of current qualification; use the PRD and experiment evidence for current scope.

The **Distributed Causal Engine (DCE)** is an advanced data science and machine learning pipeline engineered to transition network telemetry analysis from traditional, correlation-based predictive modeling to **true causal discovery**. By fusing Deep Learning (Temporal Graph Convolution) with Symbolic Reasoning (Dependency Graphs), DCE isolates the genuine root causes of system anomalies within distributed microservice architectures.

## 🧠 Core Architecture & Components

The engine is modularized into 5 distinct pipeline components orchestrated within `DCE_Final.ipynb`:

### 1. Realistic Synthetic Telemetry Generator
Models a realistic microservice topology (Gateways, Load Balancers, API Services, Caches, and Databases). It generates highly authentic telemetry features—such as queue depths, queuing delays, CPU utilization, and packet drops—while injecting realistic, cascading network failures.

### 2. Windowing & Tensor Assembly
Processes massive datasets (e.g., `network_telemetry_v1.csv` and `failure_ground_truth.csv`) into shape-safe temporal tensors. Uses sliding window techniques (`WINDOW_SIZE=10`, `STEP_SIZE=5`, `LOOKAHEAD=5`) to build a historical sequence matrix across all network nodes.

### 3. Deep Temporal Graph Predictor
A custom PyTorch neural network (`TemporalGraphPredictor`) utilizing 1D Convolutions (`Conv1D`) and Adaptive Average Pooling. It forecasts systemic failures by identifying temporal anomalies across the entire mesh. The model is fully parity-tested and exported to **ONNX** format for high-speed, language-agnostic production inference.

### 4. Symbolic Causal Engine
While the deep learning model flags *when* and *if* a failure will occur, the Symbolic Engine uses `networkx` directed graphs to trace *why* it occurred. It traverses the dependency topology backward from the point of failure, applying latency and utilization thresholds to isolate the exact microservice (the root cause) responsible for the cascading collapse.

### 5. Live Pipeline Integration
A robust, asynchronous integration layer that fuses the ONNX runtime (`InferenceSession`) with the Symbolic Causal Engine. It enables real-time ingestion of telemetry streams to provide instant anomaly predictions paired directly with structural root-cause diagnoses.

## 🚀 Key Technical Highlights
- **Hardware Agnostic**: Fully supports GPU/CPU fallbacks for distributed training.
- **Production-Ready ML**: Uses ONNX for lightweight, low-latency deployment.
- **Idempotent Executions**: Notebook runs are entirely idempotent, allowing for safe retries and pipeline resilience.

## 🛠️ Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/dravv-alt/Distributed-Causal-Engine.git
   cd Distributed-Causal-Engine
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Provide the Dataset**:
   The `network_telemetry_v1.csv` and `failure_ground_truth.csv` datasets are required for training and tensor assembly. Due to their size, they are **excluded from version control**. Please place them in the root directory before running the engine.

4. **Launch the Engine**:
   ```bash
   jupyter notebook DCE_Final.ipynb
   ```
