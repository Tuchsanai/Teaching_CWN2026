#!/usr/bin/env python3
"""Instructor-provisioned, loopback-only real shop. Learners run prescribed ./shop verbs."""
import argparse,datetime,fcntl,json,os,signal,socket,subprocess,sys,tempfile,time,urllib.request,urllib.error,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
# Runtime state outside package; unique to checkout and Unix user, overridable for instructor tests.
import hashlib
STATE=Path(os.environ.get('WEEK2_SHOP_STATE',str(Path(tempfile.gettempdir())/('week2-shop-'+hashlib.sha256(str(ROOT).encode()).hexdigest()[:10]))))
STATE.mkdir(parents=True,exist_ok=True)
CONF=STATE/'state.json'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read():return json.loads(CONF.read_text()) if CONF.exists() else {'version':'v1','scenario':'basic-A','port':18762,'owner':uuid.uuid4().hex,'pid':None}
def save(s):CONF.write_text(json.dumps(s))
def emit(s,event,**kw):
 with (STATE/'events.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'version':s['version'],'scenario':s['scenario'],'event':event,**kw},ensure_ascii=False)+'\n')
def url(s):return 'http://127.0.0.1:'+str(s['port'])
def req(s,path='/api/status',data=None):
 b=json.dumps(data).encode() if data is not None else None
 with urllib.request.urlopen(urllib.request.Request(url(s)+path,data=b,headers={'Content-Type':'application/json'}),timeout=2) as r:return json.loads(r.read())
def live(s):
 try:
  a=req(s);return a if a.get('owner')==s['owner'] else None
 except Exception:return None
def stop(s):
 # Verify identity via /proc cmdline as well as token, never kill arbitrary PIDs.
 pid=s.get('pid')
 if pid:
  try:
   cmd=Path(f'/proc/{pid}/cmdline').read_bytes()
   if str(Path(__file__).resolve()).encode() in cmd and s['owner'].encode() in cmd:
    os.kill(pid,signal.SIGTERM)
    for _ in range(80):
     if not live(s):break
     time.sleep(.025)
  except (FileNotFoundError,ProcessLookupError):pass
 s['pid']=None;save(s)
def start(s):
 if live(s):return False
 with socket.socket() as sock:
  sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  try:sock.bind(('127.0.0.1',s['port']))
  except OSError:raise RuntimeError('PORT BUSY: หยุดแล้วแจ้งผู้สอน ไม่หยุด process อื่น')
 log=(STATE/'server.log').open('a')
 p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'_serve',s['owner']],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 s['pid']=p.pid;save(s)
 deadline=time.monotonic()+8
 while time.monotonic()<deadline:
  if live(s):return True
  if p.poll() is not None:raise RuntimeError('SERVER FAILED: ดู logs')
  time.sleep(.05)
 raise RuntimeError('SERVER TIMEOUT')

def serve(token):
 s=read()
 if token!=s['owner']:raise SystemExit('owner mismatch')
 title={'A':'ละมุน','B':'อุ่นใจ','C':'พร้อมขาย'}.get(s['scenario'][-1],'ร้านฝึก')
 bookings=[]
 class H(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def send(self,status,body,ctype='application/json'):
   b=(json.dumps(body,ensure_ascii=False) if ctype=='application/json' else body).encode();self.send_response(status);self.send_header('Content-Type',ctype+'; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  def do_GET(self):
   if self.path=='/api/status':return self.send(200,{'running':True,'version':s['version'],'owner':s['owner'],'bookings':len(bookings)})
   if self.path=='/api/bookings':return self.send(200,{'items':bookings})
   if self.path=='/favicon.ico':self.send_response(204);self.end_headers();return
   if self.path!='/':return self.send(404,{'error':'not found'})
   emit(s,'PAGE_OPEN')
   return self.send(200,'''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ร้านฝึก '''+title+'''</title><style>body{margin:0;background:#f3f0e8;color:#14213d;font:20px/1.7 Tahoma,sans-serif}main{max-width:800px;margin:6vh auto;padding:32px}article{background:white;padding:32px;border-radius:24px;border:1px solid #dcd6c8}h1{font-size:40px}button{font:inherit;padding:16px 28px;background:#2364aa;color:white;border:0;border-radius:14px;cursor:pointer}#result{padding:18px;background:#eef3fa;min-height:48px;border-radius:12px;margin-top:20px}.tag{color:#287a63}a{color:#2364aa}</style><main><p class="tag">WEEK 2 • ร้านจำลอง • ไม่มีการชำระเงินจริง</p><h1>ร้าน'''+title+'''พร้อมแคมเปญ</h1><article><p>รุ่น <strong id="version">'''+s['version']+'''</strong></p><h2>ชุดแก้วประจำวัน · 120 บาท</h2><p>จองสินค้าฝึก 1 ชุด แล้วตรวจเลขรายการจากบริการจริง</p><button id="book">จองสินค้า</button><div id="result" role="status">ยังไม่มีรายการจอง</div></article></main><script>document.querySelector('#book').onclick=async()=>{const el=document.querySelector('#result');el.textContent='กำลังจอง';try{const r=await fetch('/api/book',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item:'cup-set',quantity:1})});const d=await r.json();el.textContent=r.ok?'จองสำเร็จ เลข '+d.booking+' • รุ่น '+d.version:'จองไม่สำเร็จ: '+d.error;}catch(e){el.textContent='ติดต่อบริการไม่ได้';}};</script></html>''','text/html')
  def do_POST(self):
   if self.path!='/api/book':return self.send(404,{'error':'not found'})
   try:data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
   except Exception:return self.send(400,{'error':'invalid request'})
   if data!={'item':'cup-set','quantity':1}:return self.send(400,{'error':'invalid item'})
   if s['version']=='v2':
    emit(s,'BOOKING_ERROR',cause='UPDATE_V2_BOOKING_BROKEN')
    return self.send(503,{'error':'รุ่น v2 จองสินค้าไม่ได้ (UPDATE_V2_BOOKING_BROKEN)'})
   b={'booking':'W2-'+uuid.uuid4().hex[:8].upper(),'item':'cup-set','quantity':1,'version':s['version'],'utc':utc()};bookings.append(b);emit(s,'BOOKED',booking=b['booking']);return self.send(201,b)
 server=ThreadingHTTPServer(('127.0.0.1',s['port']),H)
 emit(s,'STARTED');server.serve_forever()

def main():
 if len(sys.argv)>1 and sys.argv[1]=='_serve':serve(sys.argv[2]);return
 ap=argparse.ArgumentParser(description='ร้านฝึก Week2 — ใช้เฉพาะคำสั่งที่คู่มือให้')
 ap.add_argument('command',choices=['open','preflight','status','logs','start','rollback','check','reset','stop'])
 ap.add_argument('scenario',nargs='?',choices=['basic-A','basic-B','advanced-A','advanced-B','transfer-C']);a=ap.parse_args()
 with (STATE/'control.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);s=read()
  if not CONF.exists():save(s)
  if a.command=='open':print(url(s));return
  if a.command=='preflight':
   ok=live(s)
   if not ok:
    with socket.socket() as sock:
     sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
     try:sock.bind(('127.0.0.1',s['port']))
     except OSError:raise RuntimeError('PORT BUSY: แจ้งผู้สอน')
   print('PREFLIGHT OK Python='+sys.version.split()[0]+' '+url(s));return
  if a.command=='status':
   status=live(s);print(('RUNNING version='+status['version']+' bookings='+str(status['bookings'])) if status else 'STOPPED version='+s['version']);return
  if a.command=='logs':
   print((STATE/'events.jsonl').read_text() if (STATE/'events.jsonl').exists() else 'NO EVENTS');return
  if a.command=='stop':stop(s);emit(s,'STOPPED');print('STOPPED');return
  if a.command=='reset':
   if not a.scenario:raise RuntimeError('reset ต้องเลือก basic-A/basic-B/advanced-A/advanced-B/transfer-C')
   stop(s);s.update(scenario=a.scenario,version='v1' if a.scenario.startswith('basic') else 'v2');save(s)
   (STATE/'events.jsonl').write_text('');emit(s,'RESET')
   if s['version']=='v2':start(s);emit(s,'UPDATE_APPLIED',cause='UPDATE_V2_BOOKING_BROKEN')
   else:emit(s,'SERVICE_STOPPED',cause='SERVICE_NOT_STARTED')
   print('RESET '+a.scenario+' '+('RUNNING' if live(s) else 'STOPPED')+' version='+s['version']);return
  if a.command=='start':
   changed=start(s);print(('STARTED' if changed else 'ALREADY RUNNING')+' version='+s['version']);return
  if a.command=='rollback':
   if s['version']=='v1':print('ALREADY v1; หาก STOPPED ให้ใช้ start');return
   stop(s);s['version']='v1';save(s);start(s);emit(s,'ROLLED_BACK');print('ROLLED BACK version=v1');return
  if a.command=='check':
   try:
    status=req(s)
    assert status.get('owner')==s['owner'], 'wrong shop identity'
    b=req(s,'/api/book',{'item':'cup-set','quantity':1})
    assert b['version']==status['version'] and b['booking']
    print('CHECK PASS booking='+b['booking']+' version='+b['version']+' (endpoint; ต้องตรวจ browser เพิ่ม)')
   except Exception as e:print('CHECK FAIL '+type(e).__name__);raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except RuntimeError as e:print(str(e),file=sys.stderr);sys.exit(2)
