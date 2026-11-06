# Current E001–E004 cockpit

Historical adapters and scientific records stay unchanged. The current viewer uses E001-R001, E002-R002, E003-AM002-V006 and E004-R001; recorded results, not live progress.

From the repository root:

```powershell
python -m scripts.build_research_cockpit_current
python -m http.server 8080 --bind 127.0.0.1
```

Open `http://localhost:8080/frontend/research-cockpit/`.

Serve the repository root so original evidence links work. Bind only to localhost: local research artifacts are not public website content. The older README's folder-only command cannot expose evidence outside that folder. Its older adapter produces a historical v1 snapshot which the current UI explicitly rejects.

E001-R001 and E002-R001 were accepted by the user. E002-R002 qualified its local environment; its separate proposal remains pending. E003 is accepted only as representation/replay infrastructure via the dated review. E004's engineering gate passed, but its scientific REVISE proposal is pending. No successor approval is inferred.

E004 tables use primary tie-aware scoring, not favorable deterministic tie ordering. All absent-root cases remain in the denominator. Evidence includes SHA-256 identities. The traffic-spike example is educational, not a demonstrated diagnosis or remediation.
