# Distributed Causal Engine (DCE) 🌐

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
