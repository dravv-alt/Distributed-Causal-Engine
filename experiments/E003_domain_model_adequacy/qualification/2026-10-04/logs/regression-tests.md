# Regression verification

Interpreter: repository `.venv-e002/Scripts/python.exe`.

Command: `.venv-e002/Scripts/python.exe -m pytest -q`.

Observed result during V002 execution: **91 passed in 3.23 seconds**, exit code 0.

This includes the original repository tests, 13 qualification tests and two compressed-storage tests. Tests establish exercised software behavior, not full-corpus adequacy; that requires the separate completed census and replay artifacts.

Additional independent-validator fixture: same-trace parent/child projection reconstructs two resource nodes and one typed CALLS edge; digest agrees with the repository canonical serializer. Fixture passed. The independent validator still needs execution against the completed V002 replay outputs.

Governance command: `.venv-e002/Scripts/python.exe scripts/check_project_governance.py`.

Observed result: PASS, 116 protected files unchanged; 38 stages. Its historical checkpoint still reports `BLOCKED / HUMAN REVIEW PENDING`. That checkpoint is preserved, not overridden by this engineering execution.
