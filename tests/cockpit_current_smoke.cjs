// DOM-light rendering check; not a replacement for a real browser visual audit.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const snapshot = JSON.parse(fs.readFileSync('frontend/research-cockpit/data/experiments.json','utf8'));
const code = fs.readFileSync('frontend/research-cockpit/current.js','utf8');
const tick = () => new Promise(resolve=>setImmediate(resolve));
async function harness(response) {
  const app={innerHTML:'',focus(){}}, nav={innerHTML:'',querySelectorAll(){return [];}}, retry={addEventListener(_event,fn){this.click=fn;}};
  const context=vm.createContext({document:{querySelector(s){return s==='#app'?app:s==='#nav'?nav:retry;}},location:{hash:''},fetch:async()=>response,addEventListener(){}});
  vm.runInContext(code,context); await tick();
  return {app,nav,retry,context};
}
(async()=>{
  const h=await harness({ok:true,json:async()=>snapshot});
  assert.match(h.app.innerHTML,/3\.08%/);
  assert.match(h.app.innerHTML,/4\.78%/);
  assert.match(h.nav.innerHTML,/E004-R001/);
  for(const route of ['start','home','timeline','where','incident','experiment/E001','experiment/E002','experiment/E003','experiment/E004']){
    h.context.location.hash='#'+route;vm.runInContext('render()',h.context);
    assert.ok(h.app.innerHTML.length>200,route);
    assert.ok(!h.app.innerHTML.includes('undefined'),route);
  }
  assert.match(h.app.innerHTML,/335/);
  const failure=await harness({ok:false,status:404});
  assert.match(failure.app.innerHTML,/Retry/);
  assert.equal(typeof failure.retry.click,'function');
  failure.context.fetch=async()=>({ok:true,json:async()=>snapshot});
  await failure.retry.click();assert.match(failure.app.innerHTML,/3\.08%/);
  const stale=await harness({ok:true,json:async()=>({schema_version:'dce.research-cockpit.v1'})});
  assert.match(stale.app.innerHTML,/Snapshot outdated/);
  console.log('PASS: 9 routes, primary scores, fetch failure, Retry recovery, stale snapshot rejection');
})().catch(e=>{console.error(e);process.exitCode=1;});
