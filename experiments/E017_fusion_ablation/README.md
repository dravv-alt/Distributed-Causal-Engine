# E017 — XP014 synthetic fusion ablation

This pilot compares the five XP014 method arms on identical generated cases. All modalities are synthetic. It exercises ablation bookkeeping and label separation, not DCE's real-data fusion capability.

Run scripts in order: `generate_fixtures.py`, `run_predictions.py`, `evaluate.py`, `independent_audit.py`. Inference reads only test inputs. The evaluator opens labels only after a prediction seal is written.
