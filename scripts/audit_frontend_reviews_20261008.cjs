// Read-only Chromium audit through localhost CDP. Outputs new dated evidence only.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const output = 'frontend/research-updates-2026-10-08/browser-audit-final';
fs.mkdirSync(output, {recursive:true});
async function main() {
  const target = await (await fetch('http://127.0.0.1:9223/json/new?about:blank', {method:'PUT'})).json();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(resolve => ws.addEventListener('open', resolve, {once:true}));
  let id = 0;
  const pending = new Map(), errors = [];
  ws.addEventListener('message', event => {
    const m = JSON.parse(event.data);
    if (m.id) { const task = pending.get(m.id); pending.delete(m.id); m.error ? task.reject(Error(JSON.stringify(m.error))) : task.resolve(m.result); }
    if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text);
  });
  const call = (method, params = {}) => new Promise((resolve,reject) => { const n = ++id; pending.set(n,{resolve,reject}); ws.send(JSON.stringify({id:n,method,params})); });
  const evaluate = async expression => (await call('Runtime.evaluate', {expression, returnByValue:true, awaitPromise:true})).result.value;
  await call('Page.enable'); await call('Runtime.enable');
  const routes = ['start','home','timeline','where','acquisition','incident','experiment/E001','experiment/E002','experiment/E003','experiment/E004'];
  const checked = [];
  for (const route of routes) {
    await call('Page.navigate', {url:'http://127.0.0.1:8080/frontend/research-cockpit/#'+route});
    let content;
    for(let i=0;i<50;i++) { content = await evaluate('document.querySelector("#app")?.innerText'); if(content && !content.includes('Loading')) break; await new Promise(r=>setTimeout(r,100)); }
    assert.ok(content && !content.includes('Cannot load'),route);
    if(route==='experiment/E004') {assert.ok(content.includes('Execution accepted on 8 October 2026'));assert.ok(!content.includes('pending human review'));}
    if(route==='experiment/E002') assert.ok(content.includes('R002 REVISE approved separately'));
    if(route==='acquisition') {assert.ok(content.includes('1,869'));assert.ok(content.includes('27 varying series'));assert.ok(content.includes('NOT ESTABLISHED'));assert.ok(content.includes('No detector development'));}
    checked.push({route,characters:content.length});
  }
  await call('Page.captureScreenshot', {format:'png',captureBeyondViewport:false}).then(r=>fs.writeFileSync(output+'/existing-e004.png',Buffer.from(r.data,'base64')));
  for(const width of [1440,390]) {
    await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width===390});
    await call('Page.navigate', {url:'http://127.0.0.1:8080/frontend/research-reader-2026-10-08/#E004'});
    for(let i=0;i<50;i++) { if(await evaluate('document.querySelector("#record")?.innerText.includes("3.08%")')) break; await new Promise(r=>setTimeout(r,100)); }
    assert.ok(await evaluate('document.querySelector("#record").innerText.includes("3.08%")'));
    assert.ok(await evaluate('document.documentElement.scrollWidth <= innerWidth'), 'viewport overflow '+width);
    assert.ok(await evaluate('document.querySelector("#summary").innerText.includes("Approved reviews")'));
    assert.ok(await evaluate('document.querySelector("#summary").innerText.includes("1,869")'));
    assert.ok(await evaluate('document.querySelector("#record").innerText.includes("Execution accepted on 8 October 2026")'));
    await call('Page.captureScreenshot', {format:'png',captureBeyondViewport:false}).then(r=>fs.writeFileSync(output+'/reader-'+width+'.png',Buffer.from(r.data,'base64')));
  }
  for(const e of ['E001','E002','E003','E004']) {
    await evaluate(`location.hash=${JSON.stringify('#'+e)}`);
    await new Promise(r=>setTimeout(r,100));
    assert.ok(await evaluate(`document.querySelector('#record').innerText.includes(${JSON.stringify(e==='E003'?'E003-AM002-V006':e+'-R00'+(e==='E002'?'2':'1'))})`));
    const details = await evaluate('(()=>{document.querySelectorAll("#record details").forEach(d=>d.open=true);return [...document.querySelectorAll("#record a")].map(a=>a.href)})()');
    for(const href of details) assert.equal((await fetch(href)).status,200,href);
  }
  const acquisitionLinks = await evaluate('[...document.querySelectorAll("#summary a")].map(a=>a.href)');
  for(const href of acquisitionLinks) assert.equal((await fetch(href)).status,200,href);
  await call('Page.navigate',{url:'http://127.0.0.1:8080/frontend/research-cockpit/#acquisition'});
  for(let i=0;i<100;i++){if(await evaluate('document.querySelector("#app")?.innerText.includes("Bounded evidence acquisition complete")')) break;await new Promise(r=>setTimeout(r,100));}
  assert.ok(await evaluate('document.documentElement.scrollWidth <= innerWidth'), 'cockpit mobile overflow');
  await evaluate('(async()=>{window.originalFetch=window.fetch; window.fetch=()=>Promise.reject(new Error("Synthetic network failure")); await load();return document.querySelector("#app").innerText;})()');
  await new Promise(r=>setTimeout(r,100));
  assert.ok(await evaluate('!!document.querySelector("#retry") && document.querySelector("#app").innerText.includes("Synthetic network failure")'));
  await evaluate('window.fetch=window.originalFetch;document.querySelector("#retry").click();');
  await new Promise(r=>setTimeout(r,400));
  assert.ok(await evaluate('document.querySelector("#app").innerText.includes("Bounded evidence acquisition complete")'));
  assert.equal(errors.length,0,errors.join('\n'));
  fs.writeFileSync(output+'/report.json',JSON.stringify({checked,reader_experiments:4,viewports:[1440,390],linked_evidence_http:'all 200',runtime_exceptions:errors,checked_at:new Date().toISOString()},null,2),{flag:'wx'});
  await call('Page.close'); ws.close();
  console.log('PASS: 10 cockpit routes; approved review and acquisition content; error/Retry recovery; 4 reader experiments; desktop/mobile overflow; evidence HTTP links; no runtime exceptions.');
}
main().catch(e=>{console.error(e);process.exit(1);});
