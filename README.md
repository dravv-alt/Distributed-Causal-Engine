# Distributed Causal Engine (DCE)

The Distributed Causal Engine is a data science and machine learning pipeline aimed at analyzing massive network telemetry datasets (`network_telemetry_v1.csv`). It transitions from standard correlative modeling to complex causal discovery, helping identify root causes of network anomalies and behaviors.

## Features
- **Network Telemetry Modeling**: Processes large-scale network telemetry data.
- **Causal Inference**: Implements causal graphs and discovery algorithms to move beyond correlations and uncover genuine causal drivers of network states.

## Setup
1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch Jupyter Notebook or JupyterLab:
   ```bash
   jupyter notebook
   ```
4. Open `DCE_Final.ipynb` or any of the exploratory notebooks to run the causal analysis pipeline.

## Note
The `network_telemetry_v1.csv` dataset is required to run the pipeline but is excluded from version control due to its size. Please ensure you place the dataset in the root directory before running the notebooks.
