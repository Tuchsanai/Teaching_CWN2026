import subprocess,json,socket,uuid,re
from pathlib import Path
baseout=Path('examples/clinic-booking-workflow');out=Path('examples/clinic-booking-cross');out.mkdir(exist_ok=True)
(out/'case.txt').write_bytes((baseout/'case.txt').read_bytes());records=[];status={}
def cmd(args,**kw):
 r=subprocess.run(args,capture_output=True,text=True,**kw)
 if r.returncode:raise RuntimeError('Command failed; arguments omitted')
 return r
def call(vendor,file,template,inputs):
 prompt=(baseout/template).read_text().split('\nINPUT ')[0]
 for f in inputs:prompt+='\nINPUT '+f+'\n'+(out/f).read_text()
 inf=file.replace('.md','-input.txt');(out/inf).write_text(prompt);print('RUN',vendor,file,flush=True)
 if vendor=='Fable':
  r=subprocess.run(['docker','exec','-w','/lab',name,'yolo1','--safe-mode','--model','fable','--effort','high','--tools','','--output-format','json','-p',prompt],capture_output=True,text=True,timeout=600)
  data=json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
  if r.returncode or data.get('is_error'):
   status['error']='Fable OAuth expired' if 'expired' in str(data.get('result','')).lower() else 'Fable CLI failed';raise RuntimeError(status['error'])
  result=data['result'];models=list(data.get('modelUsage',{}))
 else:
  r=cmd(['docker','exec','-w','/lab',name,'cyolo1','exec','--skip-git-repo-check','--model','gpt-6-astra','-c','model_reasoning_effort=high','-o','/lab/'+file,prompt],timeout=600)
  result=cmd(['docker','exec',name,'cat','/lab/'+file]).stdout;models=['gpt-6-astra']
 assert result.strip();(out/file).write_text(result);records.append(dict(file=file,vendor=vendor,effort='high',inputs=['case.txt']+inputs,prompt_file=inf,reported_models=models,exit_code=r.returncode));(out/'execution.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print('DONE',file,flush=True)
name='devtools-booking-cross-'+uuid.uuid4().hex[:6];port=2222
assert len(cmd(['docker','ps','--filter','name=^devtools-','--format','{{.Names}}']).stdout.splitlines())<7
ports=cmd(['docker','ps','--format','{{.Ports}}']).stdout
while True:
 if ':'+str(port)+'->' not in ports:
  sock=socket.socket()
  try:sock.bind(('127.0.0.1',port));sock.close();break
  except OSError:sock.close()
 port+=1
try:
 cmd(['docker','run','-dit','--name',name,'--privileged','-p',f'127.0.0.1:{port}:22','tuchsanai/devtools:2569_1'])
 assert cmd(['docker','inspect','-f','{{.State.Running}}',name]).stdout.strip()=='true'
 cmd(['docker','exec',name,'mkdir','-p','/root/.claude','/root/.codex','/lab'])
 binary='/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/'
 for src,dst in [('/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe','/usr/local/bin/claude'),(binary+'codex','/usr/local/bin/codex'),(binary+'codex-code-mode-host','/usr/local/bin/codex-code-mode-host'),('/root/workspace/.Claude/yolo1/.credentials.json','/root/.claude/.credentials.json'),('/root/workspace/.Codex/cyolo1/auth.json','/root/.codex/auth.json')]:cmd(['docker','cp',src,name+':'+dst])
 cmd(['docker','exec',name,'sh','-c','chmod 600 /root/.claude/.credentials.json /root/.codex/auth.json; chmod +x /usr/local/bin/claude /usr/local/bin/codex /usr/local/bin/codex-code-mode-host'])
 for w,body in [('yolo1','export CLAUDE_CONFIG_DIR=/root/.claude\nexport IS_SANDBOX=1\nexec claude --dangerously-skip-permissions "$@"'),('cyolo1','export CODEX_HOME=/root/.codex\nexec codex --dangerously-bypass-approvals-and-sandbox "$@"')]:cmd(['docker','exec','-i',name,'sh','-c',f'cat > /usr/local/bin/{w}; chmod 700 /usr/local/bin/{w}'],input='#!/bin/sh\n'+body+'\n')
 print('START',name,port,flush=True)
 call('Fable','plan-v1.md','plan-v1-input.txt',[])
 call('Astra','review-1.md','review-1-input.txt',['plan-v1.md'])
 latest='plan-v1.md';review='review-1.md'
 for n in range(2,4):
  if re.search(r'VERDICT:\s*READY\b',(out/review).read_text()):break
  # Reuse original drafting rules while adding targeted revision instruction and actual previous artifacts.
  fix=(baseout/'plan-v1-input.txt').read_text().split('\nINPUT ')[0]+'\nแก้เฉพาะข้อผิดพลาดจากผลตรวจที่แนบ คงส่วนที่ถูกและเกณฑ์เดิม เขียนแผนฉบับสมบูรณ์ ไม่บังคับให้ผ่าน'
  temp=baseout/'revision-template-input.txt';temp.write_text(fix)
  nxt=f'plan-v{n}.md';call('Fable',nxt,temp.name,[latest,review]);temp.unlink()
  latest=nxt;review=f'review-{n}.md';call('Astra',review,'review-1-input.txt',[latest])
 (out/'review-final.md').write_bytes((out/review).read_bytes());status.update(latest_plan=latest,review_source=review)
 if re.search(r'VERDICT:\s*READY\b',(out/review).read_text()):
  call('Astra','solution.md','solution-input.txt',['review-final.md',latest])
  call('Astra','scenario-results.md','scenario-results-input.txt',[latest,'solution.md'])
finally:
 subprocess.run(['docker','rm','-f',name],capture_output=True)
 status.update(container=name,port=port,cleanup=name not in cmd(['docker','ps','-a','--format','{{.Names}}']).stdout.splitlines())
 (out/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2));print('END',json.dumps(status),flush=True);assert status['cleanup']
