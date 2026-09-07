import subprocess,json,socket,uuid,time
from pathlib import Path
root=Path.cwd(); out=root/'examples/clinic-simple';out.mkdir(exist_ok=True)
case="""โจทย์สมมติ: คลินิกเพื่อนสัตว์ต้องการรายการนัดกลาง
คลินิก 1 สาขา เปิด 09:00–19:00 มีสัตวแพทย์ 2 คนและพนักงานต้อนรับ 4 คนแบ่ง 2 กะ ลูกค้าติดต่อทางโทรศัพท์ แชต หรือหน้าร้าน ปัจจุบันจดสมุดและตารางแยกกัน จึงรับเวลาซ้ำและเลื่อนนัดแล้วอีกกะไม่รู้
ขอบเขตการฝึก: ออกแบบขั้นตอนธุรกิจและฟีเจอร์ ไม่สร้างเว็บหรือโค้ด ใช้ข้อมูลสมมติเท่านั้น
สมมติฐานเพื่อลดความซับซ้อน (ไม่ใช่นโยบายจริง): นัดละ 30 นาที เริ่มตรงชั่วโมงหรือครึ่งชั่วโมง ตารางเวลาว่างของแพทย์กำหนดไว้ล่วงหน้าและไม่เปลี่ยนระหว่างการฝึก หนึ่งนัดต่อสัตว์หนึ่งตัวและแพทย์หนึ่งคน พนักงานคนอื่นรับเรื่องได้ แต่มีผู้รับผิดชอบแก้/ยืนยันรายการกลางเพียงคนเดียวในแต่ละขณะ ส่งมอบสิทธิ์และงานค้างเมื่อเปลี่ยนกะ จึงไม่ทดสอบการเขียนพร้อมกัน
P1 รับนัด: บันทึกชื่อสมมติของเจ้าของ สัตว์ แพทย์ วันเวลา และช่องทางในรายการกลาง แยกคำขอออกจากนัดยืนยัน คำขอไม่กันคิว ตรวจเวลาว่างก่อนยืนยัน ถ้าเต็มเสนอช่องอื่น และต้องได้รับความตกลงจากลูกค้าสำหรับช่องที่จะยืนยัน ห้ามมีสองนัดยืนยันในช่องเดียวกันของแพทย์เดียวกัน
P2 เลื่อน/ยกเลิก: แก้ในนัดเดิม เมื่อขอเลื่อนให้คิวเดิมยังมีผลจนลูกค้าตกลงและตรวจช่องใหม่ว่างแล้วจึงเปลี่ยนเวลาและปล่อยคิวเดิม ถ้าช่องใหม่เต็มหรือยังไม่ตกลงให้คงเดิม ไม่กันคิวใหม่ชั่วคราว ไม่สร้างนัดซ้ำ ยกเลิกเมื่อได้รับคำยกเลิกชัดเจนและปล่อยคิว เก็บผู้แก้และการเปลี่ยนแปลง
P3 ส่งต่องาน: รายการเดียวแสดงนัดล่าสุด ผลการติดต่อล่าสุด และผู้รับผิดชอบงานที่ยังรอลูกค้าตอบ ก่อนติดต่อลูกค้าให้เปิดอ่านข้อมูลกลางล่าสุด และส่งต่องานค้างให้ผู้รับผิดชอบกะใหม่ ไม่ต้องออกแบบการอัปเดตหน้าจออัตโนมัติหรือโทรเตือนอัตโนมัติ
เสนอไม่เกิน 3 กลุ่มฟีเจอร์ เชื่อม P1–P3 กับขั้นตอนและเกณฑ์ตรวจให้ครบ ไม่เพิ่มขั้นตอนซับซ้อนนอกโจทย์
นอกขอบเขต: การแก้เวรแพทย์ การถือคิวชั่วคราว การแก้ข้อมูลพร้อมกันหลายคน รายงานมา/ไม่มา การแจ้งเตือนอัตโนมัติ การรักษา คลังยา การเงิน และข้อมูลจริง
ตรวจ 4 สถานการณ์: จองช่องว่าง; ขอช่องที่มีนัดยืนยันแล้ว; เลื่อนนัด (สำเร็จ/ช่องใหม่เต็มหรือยังไม่ตกลง); ยกเลิกและส่งต่องานข้ามกะ
ผลที่ต้องได้คือข้อเสนอที่ทำตามเป็นขั้นตอนได้ พร้อมข้อจำกัดของสมมติฐาน ไม่กล่าวอ้างว่าทดสอบซอฟต์แวร์จริง
"""
(out/'case.txt').write_text(case)
tasks=[('plan-v1.md','Fable',[], 'วิเคราะห์สาเหตุ เสนอไม่เกิน 3 กลุ่มฟีเจอร์ ตาราง P1–P3 → ฟีเจอร์ → ขั้นตอน → เกณฑ์ตรวจ ระบุสมมติฐานและจุดอ่อน 2 ข้อ'),('review-1.md','Astra',['plan-v1.md'],'วิจารณ์แผนตามโจทย์ ระบุปัญหาจริง ผลกระทบ และข้อเสนอแก้ พร้อมจุดอ่อนของข้อเสนอของคุณ ห้ามเพิ่มข้อกำหนดนอกขอบเขต ถ้าไม่มีข้อขัดแย้งให้บอกตามจริง'),('plan-v2.md','Fable',['plan-v1.md','review-1.md'],'ตอบข้อทักท้วงว่ารับหรือไม่รับพร้อมเหตุผล แล้วเขียนแผนฉบับสมบูรณ์ที่ปรับแล้วในคำตอบเดียว ครบ P1–P3 สถานะ ขั้นตอน และเกณฑ์ตรวจ ทบทวนจุดอ่อนของแผนตนเอง'),('review-final.md','Astra',['plan-v2.md','review-1.md'],'ตรวจแผนฉบับปรับปรุงเทียบโจทย์และข้อทักท้วง ไม่เพิ่มเกณฑ์นอกขอบเขต READY เมื่อครบ P1–P3 ไม่มีข้อขัดแย้งสำคัญ และรองรับสถานการณ์ที่กำหนด หากยังมีช่องโหว่สำคัญระบุให้ชัด ลงท้าย VERDICT: READY หรือ VERDICT: NOT READY ตามจริง ห้ามผ่านเพียงเพราะอีกโมเดลบอกว่าแก้แล้ว'),('solution.md','Astra',['plan-v2.md','review-final.md'],'หาก review-final ไม่ใช่ READY ให้ระบุว่ายังสรุปไม่ได้และรายการที่ต้องแก้ หาก READY ให้สรุปโซลูชันเป็นขั้นตอนที่พนักงานทำตามได้ ตารางฟีเจอร์กับ P1–P3 และ Mermaid สั้นๆ รักษากฎทุกข้อของแผน ไม่อ้างประสิทธิภาพที่ไม่ได้วัด'),('scenario-results.md','Astra',['plan-v2.md','solution.md'],'ประเมินเอกสาร solution กับโจทย์ทั้ง 4 สถานการณ์ รวมทางเลือกย่อยของการเลื่อน ระบุตัวอย่างข้อมูลสมมติ สิ่งที่คาดหวัง สิ่งที่ขั้นตอนรองรับ PASS/FAIL และเหตุผล ตามจริง หากพบข้อขัดแย้งให้ FAIL เฉพาะกรณีที่เกี่ยวข้องและอธิบาย นี่คือการประเมินเอกสารไม่ใช่รันซอฟต์แวร์')]
(out/'tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2))
def run(args,**kw):return subprocess.run(args,check=True,capture_output=True,text=True,**kw)
names=run(['docker','ps','--filter','name=^devtools-','--format','{{.Names}}']).stdout.splitlines()
assert len(names)<7,'Container limit'
ports=run(['docker','ps','--format','{{.Ports}}']).stdout
port=2222
while True:
 if ':'+str(port)+'->' not in ports:
  sock=socket.socket()
  try:sock.bind(('127.0.0.1',port));sock.close();break
  except OSError:sock.close()
 port+=1
name='devtools-clinic-simple-'+uuid.uuid4().hex[:6]
records=[]
try:
 run(['docker','run','-dit','--name',name,'--privileged','-p',f'127.0.0.1:{port}:22','tuchsanai/devtools:2569_1'])
 assert run(['docker','inspect','-f','{{.State.Running}}',name]).stdout.strip()=='true'
 run(['docker','exec',name,'mkdir','-p','/root/.claude','/root/.codex','/lab'])
 copies=[('/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe','/usr/local/bin/claude'),('/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex','/usr/local/bin/codex'),('/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex-code-mode-host','/usr/local/bin/codex-code-mode-host'),('/root/workspace/.Claude/yolo1/.credentials.json','/root/.claude/.credentials.json'),('/root/workspace/.Codex/cyolo1/auth.json','/root/.codex/auth.json')]
 for src,dst in copies:run(['docker','cp',src,name+':'+dst])
 run(['docker','exec',name,'sh','-c','chmod 600 /root/.claude/.credentials.json /root/.codex/auth.json; chmod +x /usr/local/bin/claude /usr/local/bin/codex /usr/local/bin/codex-code-mode-host'])
 for wrapper,body in [('yolo1','export CLAUDE_CONFIG_DIR=/root/.claude\nexport IS_SANDBOX=1\nexec claude --dangerously-skip-permissions "$@"'),('cyolo1','export CODEX_HOME=/root/.codex\nexec codex --dangerously-bypass-approvals-and-sandbox "$@"')]:
  run(['docker','exec','-i',name,'sh','-c',f'cat > /usr/local/bin/{wrapper}; chmod 700 /usr/local/bin/{wrapper}'],input='#!/bin/sh\n'+body+'\n')
 print('START',name,'port',port,flush=True)
 for file,vendor,inputs,instruction in tasks:
  if file=='solution.md' and 'VERDICT: READY' not in (out/'review-final.md').read_text():break
  prompt='ตอบเป็นภาษาไทย กระชับแต่ครบ ประมาณ 600–1000 คำ เขียนเฉพาะเนื้อหาเอกสาร ห้ามใส่ข้อมูลบัญชี\n'+case+'\nงาน: '+instruction
  for f in inputs:prompt+='\n\nINPUT FILE: '+f+'\n'+(out/f).read_text()
  inp=file.replace('.md','-input.txt');(out/inp).write_text(prompt)
  print('RUN',file,vendor,'high',flush=True)
  if vendor=='Fable':
   r=run(['docker','exec','-w','/lab',name,'yolo1','--safe-mode','--model','fable','--effort','high','--tools','','--output-format','json','-p',prompt],timeout=600)
   data=json.loads(r.stdout);assert not data.get('is_error');result=data['result'];models=list(data.get('modelUsage',{}))
  else:
   r=run(['docker','exec','-w','/lab',name,'cyolo1','exec','--skip-git-repo-check','--model','gpt-6-astra','-c','model_reasoning_effort=high','-o','/lab/'+file,prompt],timeout=600)
   result=run(['docker','exec',name,'cat','/lab/'+file]).stdout;models=['gpt-6-astra']
  assert result.strip();(out/file).write_text(result)
  records.append(dict(file=file,vendor=vendor,effort='high',reported_models=models,inputs=['case.txt']+inputs,prompt_file=inp,exit_code=r.returncode))
  (out/'execution.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
  print('DONE',file,len(result),'chars',flush=True)
finally:
 subprocess.run(['docker','rm','-f',name],capture_output=True)
 gone=name not in run(['docker','ps','-a','--format','{{.Names}}']).stdout.splitlines()
 (out/'runtime.json').write_text(json.dumps(dict(container=name,port=port,cleanup=gone),indent=2))
 print('CLEANUP',gone,flush=True)
 assert gone
