# E016 — variable service membership pilot

Planning alignment: XP013. The experiment compares a fixed-eight neural scorer with a shared per-service topology-aware neural scorer trained from the same 300 synthetic eight-service cases. Held-out inputs contain 8, 12, and 20 services, plus service-order permutations. Malformed topology inputs challenge the dynamic model's validation.

All signals are arbitrary generated numeric values. Test labels are stored separately and opened only after predictions are sealed. This is a controlled architecture pilot, not real RCA evidence.

```powershell
python experiments/E016_membership_adaptation/scripts/generate_fixtures.py
python experiments/E016_membership_adaptation/scripts/train_models.py
python experiments/E016_membership_adaptation/scripts/run_predictions.py
python experiments/E016_membership_adaptation/scripts/evaluate.py
python experiments/E016_membership_adaptation/scripts/independent_audit.py
```
