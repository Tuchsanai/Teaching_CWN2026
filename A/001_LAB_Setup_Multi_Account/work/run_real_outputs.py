import subprocess as sp, json, uuid, re, socket, datetime
from pathlib import Path
root=Path.cwd(); work=root/'work'; dest=root/'examples'/'clinic-real'; dest.mkdir(parents=True,exist_ok=True)
name='devtools-clinic-real-'+uuid.uuid4().hex[:8]
used=sp.check_output(['docker','ps','--format','{{.Ports}}'],text=True)
port=2222
while True:
 sock=socket.socket()
 try:
  if re.search(r':'+str(port)+r'->',used): port+=1; continue
  sock.bind(('127.0.0.1',port)); break
 except OSError:port+=1
 finally:sock.close()
assert len(sp.check_output(['docker','ps','--filter','name=^devtools-','-q'],text=True).split())<7
(work/'real-container.json').write_text(json.dumps({'name':name,'port':port}))
def run(args,**kw):return sp.run(args,check=True,**kw)
def put(text,path):run(['docker','exec','-i',name,'sh','-c','cat > '+path],input=text.encode(),stdout=sp.DEVNULL)
def copy(src,dst):run(['docker','cp',src,name+':'+dst],stdout=sp.DEVNULL)
records=[]
def ask(vendor,output,instruction,inputs):
 context='\n\n'.join('SOURCE FILE: '+p+'\n'+(dest/p).read_text() for p in inputs)
 prompt=instruction+'\n\n'+context+'\n\nตอบเป็นเนื้อหา Markdown ของไฟล์ที่ระบุเท่านั้น ไม่ใส่กรอบครอบทั้งคำตอบ ให้เหตุผลสั้น ๆ ที่ตรวจสอบได้ ไม่กล่าวอ้างผลใช้งานจริง ไม่เรียกเครื่องมือหรือรันคำสั่ง'
 pn=output.replace('.md','')+'-input.txt';(dest/pn).write_text(prompt)
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 print('Running',vendor,output,flush=True)
 if vendor=='Fable':
  args=['docker','exec','-w','/lab',name,'yolo1','--safe-mode','--model','fable','--effort','medium','--tools','','--output-format','json','-p',prompt]
  r=sp.run(args,capture_output=True,text=True,timeout=300)
  (work/(output+'.log')).write_text(r.stdout+'\n'+r.stderr)
  if r.returncode:raise RuntimeError('Fable call failed')
  data=json.loads(r.stdout)
  if data.get('is_error'):raise RuntimeError('Fable returned error')
  result=data.get('result',''); model=list(data.get('modelUsage',{}))
 else:
  put(prompt,'/lab/task.txt')
  args=['docker','exec','-w','/lab',name,'cyolo1','exec','--skip-git-repo-check','--model','gpt-6-astra','-c','model_reasoning_effort=medium','-o','/lab/result.md',prompt]
  r=sp.run(args,capture_output=True,text=True,timeout=300)
  (work/(output+'.log')).write_text(r.stdout+'\n'+r.stderr)
  if r.returncode:raise RuntimeError('Astra call failed')
  result=sp.check_output(['docker','exec',name,'cat','/lab/result.md'],text=True)
  model=['gpt-6-astra'] if 'gpt-6-astra' in r.stderr+r.stdout else []
 assert len(result)>100
 (dest/output).write_text(result)
 records.append({'file':output,'vendor':vendor,'requested_model':'fable' if vendor=='Fable' else 'gpt-6-astra','effort':'medium','reported_models':model,'inputs':inputs,'prompt_file':pn,'exit_code':r.returncode,'started_utc':started})
 (dest/'execution.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 print('Saved',output,flush=True)
try:
 run(['docker','run','-dit','--name',name,'--privileged','-p',f'127.0.0.1:{port}:22','tuchsanai/devtools:2569_1'],stdout=sp.DEVNULL)
 run(['docker','exec',name,'mkdir','-p','/root/.claude','/root/.codex','/lab'])
 copy('/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe','/usr/local/bin/claude')
 base='/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/'
 for f in ['codex','codex-code-mode-host']:copy(base+f,'/usr/local/bin/'+f)
 copy('/root/workspace/.Claude/yolo1/.credentials.json','/root/.claude/.credentials.json')
 copy('/root/workspace/.Codex/cyolo1/auth.json','/root/.codex/auth.json')
 put('#!/bin/sh\nexport CLAUDE_CONFIG_DIR=/root/.claude\nexport IS_SANDBOX=1\nexec claude --dangerously-skip-permissions "$@"\n','/usr/local/bin/yolo1')
 put('#!/bin/sh\nexport CODEX_HOME=/root/.codex\nexec codex --dangerously-bypass-approvals-and-sandbox "$@"\n','/usr/local/bin/cyolo1')
 run(['docker','exec',name,'chmod','700','/usr/local/bin/yolo1','/usr/local/bin/cyolo1'])
 run(['docker','exec',name,'chmod','600','/root/.claude/.credentials.json','/root/.codex/auth.json'])
 s=(root/'README.md').read_text();a=s.index('## ขั้นที่ 4');prompt=re.search(r'```text\n(.*?)\n```',s[a:],re.S).group(1)
 case=prompt.split('ใช้ Fable medium วิเคราะห์ก่อน')[0]
 (dest/'case.txt').write_text(case)
 ask('Fable','plan-v1.md','จากโจทย์ต่อไปนี้ เขียน plan-v1.md: วิเคราะห์สาเหตุ ผู้ใช้ และตาราง Pain point | ฟีเจอร์ | ขั้นตอนที่ช่วยแก้ | เกณฑ์ตรวจ จัดเป็นไม่เกิน 3 กลุ่มฟีเจอร์ พร้อมทำก่อน/ภายหลัง สมมติฐาน และจุดอ่อนของแผน 2 ข้อ ความยาวไม่เกิน 650 คำภาษาไทย',['case.txt'])
 ask('Astra','review-1.md','เขียน review-1.md วิจารณ์แผนเทียบโจทย์ไม่เกิน 3 ประเด็น ระบุเหตุผล ทางเลือก และจุดอ่อนของทางเลือก โดยเฉพาะคิวชนพร้อมกัน การเลื่อนนัดระหว่างกะ และข้อมูลสถานะ ห้ามแก้แผน ไม่เกิน 500 คำ',['case.txt','plan-v1.md'])
 ask('Fable','response.md','เขียน response.md เป็นตาราง ข้อทักท้วง | รับ/ไม่รับ/ต้องหาข้อมูลเพิ่ม | เหตุผล | สิ่งที่จะปรับ วิจารณ์คำแนะนำของผู้ตรวจด้วย ไม่จำเป็นต้องเห็นตรงกัน ไม่เกิน 400 คำ',['plan-v1.md','review-1.md'])
 ask('Fable','plan-v2.md','เขียน plan-v2.md โดยปรับแผนตามการตอบข้อทักท้วง เชื่อม P1–P5 ให้ครบ ไม่เกิน 3 กลุ่มฟีเจอร์ มีขั้นตอน เกณฑ์ตรวจ ขอบเขตทำก่อน/ภายหลัง และคำถามที่ต้องถามคลินิก ไม่เกิน 600 คำ',['case.txt','plan-v1.md','review-1.md','response.md'])
 ask('Astra','review-final.md','เขียน review-final.md ตรวจว่าข้อทักท้วงได้รับการจัดการหรือยัง พิจารณาเหตุผลของผู้วิเคราะห์และปรับความเห็นเดิมของผู้ตรวจหากควร สรุปท้าย READY หรือ NOT READY สำหรับสรุปข้อเสนอเท่านั้น ไม่ใช่พร้อมพัฒนาหรือใช้งานจริง READY เมื่อเชื่อมปัญหาครบ ขั้นตอนและเกณฑ์ตรวจชัด ไม่มีข้อขัดแย้งสำคัญในขอบเขตการสรุปเอกสาร ไม่เกิน 450 คำ',['case.txt','plan-v1.md','review-1.md','response.md','plan-v2.md'])
 gate=(dest/'review-final.md').read_text()
 if 'NOT READY' not in gate and re.search(r'\bREADY\b',gate):
  ask('Astra','solution.md','เขียน solution.md สรุปตาราง P1–P5 | ฟีเจอร์ | ทำก่อน/ภายหลัง | เหตุผล พร้อมขั้นตอนผู้ใช้ไม่เกิน 5 ขั้นและ Mermaid ง่าย ๆ รับนัด ตรวจเวลา ยืนยัน/เสนอเวลาอื่น เลื่อน/ยกเลิก และคำถามที่ต้องถามคลินิก ไม่เกิน 650 คำ',['case.txt','plan-v2.md','response.md','review-final.md'])
  ask('Astra','scenario-results.md','เขียน scenario-results.md ประเมินสถานการณ์สมมติ 3 กรณี เวลาว่าง สองช่องทางขอเวลาทับซ้อน และเลื่อนนัดช่วงเปลี่ยนกะ เป็นตาราง สถานการณ์ | ขั้นตอนและฟีเจอร์ที่ใช้ | ผลที่ควรเกิด | PASS/FAIL | เหตุผล รายงานช่องโหว่ตามจริง PASS หมายถึงมีขั้นตอนรองรับในเอกสาร ไม่ใช่ผลทดสอบซอฟต์แวร์หรือคลินิกจริง ไม่เกิน 500 คำ',['case.txt','solution.md'])
 else:print('Stopped at review gate',flush=True)
finally:
 run(['docker','rm','-f',name],stdout=sp.DEVNULL)
 assert sp.run(['docker','inspect',name],stdout=sp.DEVNULL,stderr=sp.DEVNULL).returncode!=0
 print('Cleaned container and credential copies',flush=True)
