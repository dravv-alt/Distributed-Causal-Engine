const experiments = [
  {
    id: "E001",
    title: "Can we repeat the original demo?",
    badge: "YES — simulation repeated",
    tone: "good",
    answer: "Yes. The same synthetic demo produced the same five result tables.",
    means: "The old demo was not a one-off accident.",
    notMeans: "It does not prove DCE works on real company data or that its combined AI approach is better.",
    next: "Keep it as a baseline. Do not market it as real-world RCA.",
    evidence: [
      ["Run summary", "../../experiments/E001/results/E001-R001/SUMMARY.md"],
      ["Full execution record", "../../experiments/E001/logs/E001-R001.md"]
    ]
  },
  {
    id: "E002",
    title: "Does cleaner timing information improve the answer?",
    badge: "MIXED — repeatable, no improvement",
    tone: "warn",
    answer: "The same run repeated exactly three times. Preventing mixed timestamp sources did not improve the root-cause ranking in this simulator.",
    means: "The timing comparison is mechanically stable, and we know this change did not help here.",
    notMeans: "It does not prove timing is useless. The software environment had a compatibility warning, so this is not a clean final result.",
    next: "Pin the exact software versions, review the rerun plan, then rerun without changing the question.",
    evidence: [
      ["Simple result table", "../../experiments/E002/results/E002-R001/derived-metrics.md"],
      ["Decision proposal", "../../experiments/E002/results/E002-R001/decision-proposal.md"],
      ["Frozen recipe", "../../experiments/E002/results/E002-R001/frozen-configuration.json"]
    ]
  },
  {
    id: "E003",
    title: "Can we safely understand the real OpenRCA data?",
    badge: "NO — blocked until data gaps are fixed",
    tone: "stop",
    answer: "Partly. DCE can read and replay some real data, but timestamps, service relationships, and metric meanings are incomplete or inconsistent.",
    means: "The data-reading foundation exists and the gaps are visible instead of hidden.",
    notMeans: "It does not mean DCE can diagnose real outages. Building the RCA brain on top now would make unreliable guesses look scientific.",
    next: "Fix and review the data representation gaps before any real-data diagnosis experiment.",
    evidence: [
      ["Decision gate", "../../experiments/E003_domain_model_adequacy/decision.md"],
      ["Plain implementation report", "../../docs/E003-implementation-report.md"]
    ]
  }
];

const cards = document.querySelector("#experiment-cards");
cards.innerHTML = experiments.map((item) => `
  <article class="experiment-card ${item.tone}">
    <div class="card-top"><span class="experiment-id">${item.id}</span><span class="badge">${item.badge}</span></div>
    <h3>${item.title}</h3>
    <p class="answer">${item.answer}</p>
    <details>
      <summary>What this really means</summary>
      <div class="details-content">
        <p><strong>You can trust this much:</strong> ${item.means}</p>
        <p><strong>Do not conclude this:</strong> ${item.notMeans}</p>
        <p><strong>Next move:</strong> ${item.next}</p>
        <div class="evidence-links">${item.evidence.map(([name, href]) => `<a href="${href}" target="_blank" rel="noreferrer">${name} ↗</a>`).join("")}</div>
      </div>
    </details>
  </article>
`).join("");

document.querySelector("#expand-all").addEventListener("click", (event) => {
  const allOpen = [...document.querySelectorAll("details")].every((detail) => detail.open);
  document.querySelectorAll("details").forEach((detail) => { detail.open = !allOpen; });
  event.currentTarget.textContent = allOpen ? "Show all details" : "Hide all details";
});
