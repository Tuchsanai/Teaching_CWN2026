// Offline evaluator: Node builtins only; invokes the two authorized Python checkers once.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const session = path.resolve(__dirname, '..');
const lab = path.resolve(session, '../..');
const html = path.join(session, 'ui-mockup-v2.html');
const tmp = path.join(session, 'browser-temp');
const root = path.join(__dirname, 'ui-v2-evaluator-runtime');
const observations = path.join(__dirname, 'ui-v2-observations.json');
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const expected = '249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc';
const regression = path.resolve(lab, '../004_LAB_Conditional_Graph_UI_Mockup/tests/ui-check.py');
const features = path.join(lab, 'reference/step-05-execute-v2/ui-browser/ui-scenarios-v2-round-2.py');
for (const p of [root, observations]) if (fs.existsSync(p)) throw Error('Refusing overwrite: '+p);
if (hash(html) !== expected) throw Error('Canonical HTML hash mismatch');
fs.mkdirSync(tmp, {recursive:true});
fs.mkdirSync(root);
const started = new Date().toISOString();
const env = {...process.env, TMPDIR:tmp, TMP:tmp, TEMP:tmp, PYTHONDONTWRITEBYTECODE:'1'};
const jobs = [
 {id:'regression',script:regression,args:['--html',html,'--out',path.join(root,'regression.json'),'--shots',path.join(root,'regression-shots')],report:path.join(root,'regression.json')},
 {id:'features',script:features,args:['--html',html,'--run-dir',path.join(root,'features'),'--shots',path.join(root,'feature-shots'),'--prefix','screen-v2-evaluator'],report:path.join(root,'features/ui-feature-check-v2.json')}
];
const executions = [];
for (const job of jobs) {
 const at = new Date().toISOString();
 const result = spawnSync('python',[job.script,...job.args],{env,cwd:lab,encoding:'utf8',maxBuffer:8*1024*1024,timeout:240000});
 const stdout = path.join(root,job.id+'.stdout.txt'), stderr = path.join(root,job.id+'.stderr.txt');
 fs.writeFileSync(stdout,result.stdout||'',{flag:'wx'}); fs.writeFileSync(stderr,result.stderr||'',{flag:'wx'});
 const report = fs.existsSync(job.report)?JSON.parse(fs.readFileSync(job.report,'utf8')):null;
 executions.push({id:job.id,command:['python',job.script,...job.args],script_sha256:hash(job.script),started_at:at,ended_at:new Date().toISOString(),exit_code:result.status,signal:result.signal,error:result.error?.message||null,stdout,stderr,report_path:job.report,report_sha256:report?hash(job.report):null,actual:report});
 console.log(JSON.stringify({id:job.id,exit_code:result.status,passed:report?.passed,failed:report?.failed}));
}
const allPass=executions.every(x=>x.exit_code===0&&x.actual?.failed===0)&&executions[0].actual?.passed===19&&executions[1].actual?.passed===8;
const document={review_mode:'artifacts',task_id:'revise-ui',verify_task:'verify-ui',run_id:'ui-v2-review',plan:'plan-v2',started_at:started,ended_at:new Date().toISOString(),wrapper_runs:1,node_version:process.version,tmpdir:tmp,html,html_sha256_before:expected,html_sha256_after:hash(html),wrapper_sha256:hash(__filename),plan_sha256:hash(path.join(session,'plan-v2.json')),contract_sha256:hash(path.join(session,'ui-contract-v2.md')),executions,runtime_verdict:allPass&&hash(html)===expected?'PASS_OFFLINE_MOCK_CHECKS':'FAIL_OR_BLOCKED',real_system:'NOT_TESTED',limitations:['No LAN or multi-device timing/sample acceptance tests','No real payment or refund','No production security','No fullETA / 7-day history','No installation or real-system internet disconnect','Feature runs: six distinct scenarios, eight executions; N=5 repeated three times at reset 12:00, not three distinct threshold windows','US-09/14 five-of-five acceptance suites not executed','Full contract extras, five original orders, pending-payment return and internal duplicate command not covered by these checkers']};
fs.writeFileSync(observations,JSON.stringify(document,null,2)+'\n',{flag:'wx'});
process.exitCode=document.runtime_verdict==='PASS_OFFLINE_MOCK_CHECKS'?0:1;
