import json

from scripts.build_research_cockpit_data import build


def test_cockpit_adapter_reads_current_experiment_artifacts():
    data = build()
    assert data["schema_version"] == "dce.research-cockpit.v1"
    experiments = {item["experiment_id"]: item for item in data["experiments"]}
    assert set(experiments) == {"E001", "E002", "E003"}
    assert experiments["E001"]["run_id"] == "E001-R001"
    assert experiments["E002"]["gates"][0]["status"] == "PASS"
    assert experiments["E002"]["gates"][2]["status"] == "FAIL"
    assert experiments["E003"]["status"] == "BLOCKED"
    assert "does not prove" in experiments["E003"]["not_established"].lower()


def test_cockpit_data_is_json_serializable():
    json.dumps(build())
