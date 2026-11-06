const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct = x => (x * 100).toFixed(2) + '%';
let records;
function step(n, title, content, cls = '') { return `<section class="step ${cls}"><span class="number">${n}</span><div><h3>${title}</h3>${content}</div></section>`; }
function table(e) {
  if (!e.comparison) return '';
  return `<div class="table-scroll"><table><caption>All 335 windows retained · primary tie-aware scoring · higher is better</caption><thead><tr><th>Method</th><th>First guess credit</th><th>First three credit</th></tr></thead><tbody>${e.comparison.map(r => `<tr><th scope="row">${esc(r.label)}</th><td>${pct(r.top1_tie_aware)}<progress max="1" value="${r.top1_tie_aware}" aria-label="${esc(r.label)} Top-1 ${pct(r.top1_tie_aware)}"></progress></td><td>${pct(r.top3_tie_aware)}</td></tr>`).join('')}</tbody></table></div><p>Tied candidates share expected credit. These scores are not confidence or fault probabilities. Counts scored highest, but observation volume is not a symptom detector.</p>`;
}
function render() {
  const e = records.experiments.find(e => e.experiment_id === location.hash.slice(1)) || records.experiments[0];
  $('tabs').className = 'tabs';
  $('tabs').innerHTML = records.experiments.map(x => `<a href="#${x.experiment_id}" ${x === e ? 'aria-current="page"' : ''}>${x.experiment_id} · ${x.experiment_id === 'E003' ? 'Replay' : x.experiment_id === 'E004' ? 'Graph ranking' : x.experiment_id === 'E002' ? 'Timing' : 'Reproduction'}</a>`).join('');
  $('record').innerHTML = `<p class="eyebrow">${esc(e.run_id)} / ${esc(e.population)}</p><h2>${esc(e.question)}</h2><div class="grid"><div class="status"><b>Execution</b>${esc(e.execution_status)}</div><div class="status"><b>Scientific disposition</b>${esc(e.decision)}${e.experiment_id === 'E003' ? ' · restricted readiness' : e.experiment_id === 'E004' ? ' · structural prior only' : ''}</div><div class="status"><b>Human review</b>${esc(e.review_status)}</div></div>` +
    step('01', 'Why ask this question?', `<p>${esc(e.rationale)}</p>`) +
    step('02', 'What did we actually do?', `<p>${esc(e.what_we_did)}</p><details><summary>Hypothesis, controls and frozen configuration</summary><p>These are original records. Drafts describe earlier intent; run-specific freezes and amendments describe later execution.</p>${e.documents.map(d => `<details><summary>${esc(d.path)}</summary><a href="../../${encodeURI(d.path)}" target="_blank" rel="noreferrer">Open original</a><pre>${esc(d.text)}</pre><small>SHA-256 ${esc(d.sha256)}</small></details>`).join('')}</details>`) +
    step('03', 'What happened?', `<p><b>${esc(e.result)}</b></p>${table(e)}<ul>${e.facts.map(f => `<li>${esc(f)}</li>`).join('')}</ul>`) +
    step('04', 'What does it mean?', `<p>${esc(e.meaning)}</p>`) +
    step('05', 'What does it leave unanswered?', `<p>${esc(e.not_established)}</p>`, 'limits') +
    step('06', 'Decision and next permitted step', `<p>${esc(e.waiting)}</p><p>${esc(e.blocking)}</p><p><small>Review provenance: ${esc(e.review_provenance)}</small></p>`) +
    `<details><summary>Run history, including unsuccessful attempts</summary><ul>${(e.history || ['E001-R001: CLI reproduced; original R0 test failures remain recorded.']).map(h => `<li>${esc(h)}</li>`).join('')}</ul><p>Open the original run ledgers above for the detailed sequence; this summary does not replace them.</p></details>` +
    (e.per_system ? `<details><summary>Did results differ across systems?</summary><div class="table-scroll"><table><thead><tr><th>System</th><th>Cases</th><th>Root available</th><th>Graph Top-1 / Top-3</th><th>Count Top-1 / Top-3</th><th>Chance Top-1 / Top-3</th></tr></thead><tbody>${e.per_system.map(s => `<tr><th>${esc(s.system)}</th><td>${s.cases}</td><td>${s.root_present}/${s.cases}</td>${['symbolic_topology_v1','activity_reference_v1','graph_disabled_uniform_v1'].map(m => `<td>${pct(s.methods[m].top1_tie_aware)} / ${pct(s.methods[m].top3_tie_aware)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p>Root availability is coverage, not accuracy. All absent-root windows remain scored.</p></details>` : '') +
    `<details><summary>Verify the original results</summary><div class="evidence">${e.artifacts.map(a => `<div><a href="../../${encodeURI(a.path)}" target="_blank" rel="noreferrer">${esc(a.label)}</a><pre>${esc(a.path)}\nSHA-256 ${esc(a.sha256)}</pre></div>`).join('')}</div></details>`;
}
async function load() {
  try {
    const response = await fetch('../research-updates-2026-10-08/records.json', {cache:'no-store'});
    if (!response.ok) throw Error(`Evidence request failed (${response.status}).`);
    records = await response.json();
    if (records.reader_version !== 1 || !Array.isArray(records.experiments) || records.experiments.length !== 4 || records.frontend_update_version !== 1 || !records.acquisition) throw Error('Unsupported evidence preview.');
    $('summary').innerHTML = `<div class="panel queue"><h2>Approved reviews; scientific REVISE retained</h2><ul>${['E004-R001: execution accepted; REVISE / structural prior only retained.', 'E002-R002: separate REVISE approved; no tested timing-policy improvement.'].map(q => `<li>${esc(q)}</li>`).join('')}</ul><p>E003 infrastructure acceptance is narrow. No successor or automatic fixing is approved.</p></div>${DCEAcquisition.render(records.acquisition)}`;
    $('provenance').textContent = `Evidence hashes checked when this preview was built: ${new Date(records.verified_at).toLocaleString('en-IN', {timeZone:'Asia/Kolkata'})} IST. Original snapshot preserved; dated approval amendments and acquisition evidence are included. This is a dated recorded-results preview, not a live monitor; changes after the build are not automatically detected.`;
    render();
  } catch (error) {
    records = null;
    $('record').innerHTML = `<div class="panel limits"><h2>Could not load evidence</h2><p>${esc(error.message)}</p><button id="retry" type="button">Retry</button></div>`;
    $('retry').addEventListener('click', load);
  }
}
addEventListener('hashchange', () => { if (records) { render(); $('record').focus(); } });
load();
