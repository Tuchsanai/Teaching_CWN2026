"""Instructor only; Linux/Python stdlib. State and process ownership are scoped."""
import argparse, fcntl, json, os, signal, socket, subprocess, sys, time, uuid
from pathlib import Path
from urllib.request import urlopen
BASE=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description='Prepared local shop commands; no code editing needed')
p.add_argument('command',choices=['setup','open','status','logs','start','rollback','verify','reset','stop'])
p.add_argument('scenario',nargs='?',choices=['basic-A','basic-B','rollback-A','rollback-B','transfer-C'])
a=p.parse_args()
# Each learner receives a separate package copy. Tests may choose a child runtime.
name=os.environ.get('SHOP_LAB_INSTANCE','learner')
if not name.replace('-','').replace('_','').isalnum(): p.error('invalid local instance label')
R=BASE/'.lab-runtime'/name; R.mkdir(parents=True,exist_ok=True)
lock=(R/'lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX)
statefile=R/'state.json'
def save(s):
 q=R/'state.tmp'; q.write_text(json.dumps(s,ensure_ascii=False)); q.replace(statefile)
def read():
 if not statefile.exists(): raise RuntimeError('Run ./labctl setup first')
 return json.loads(statefile.read_text())
def log(msg):
 with (R/'events.log').open('a') as f: f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())+' '+msg+'\n')
def owned(s):
 try:
  pid=s.get('pid'); raw=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
  return str(BASE/'instructor/runtime/server.py').encode() in raw and str(R).encode() in raw and s['token'].encode() in raw
 except (OSError,KeyError): return False
def stop(s):
 if owned(s):
  # pidfd targets exactly this process even if its numeric PID is recycled.
  fd=os.pidfd_open(s['pid'])
  try:
   if owned(s): signal.pidfd_send_signal(fd,signal.SIGTERM)
   for _ in range(60):
    if not owned(s): break
    time.sleep(.05)
   if owned(s): raise RuntimeError('Owned process did not stop; no broad kill attempted')
  finally: os.close(fd)
 s['pid']=None; save(s); log('STOP scoped service')
def start(s):
 if owned(s): print('RUNNING already; release unchanged: '+s['release']); return
 # Bind and listen on port 0, then pass the still-open socket to the child: no reservation race.
 sock=socket.socket(); sock.bind(('127.0.0.1',0)); sock.listen(32)
 s['port']=sock.getsockname()[1]; s['token']=uuid.uuid4().hex
 (R/'ready').unlink(missing_ok=True); save(s)
 with (R/'server.log').open('ab') as out:
  child=subprocess.Popen([sys.executable,str(BASE/'instructor/runtime/server.py'),'--runtime',str(R),'--token',s['token'],'--fd',str(sock.fileno())],stdin=subprocess.DEVNULL,stdout=out,stderr=out,pass_fds=(sock.fileno(),),start_new_session=True)
 sock.close(); s['pid']=child.pid; save(s)
 for _ in range(80):
  if (R/'ready').exists() and (R/'ready').read_text()==s['token']: break
  if child.poll() is not None: raise RuntimeError('Startup failed: inspect ./labctl logs')
  time.sleep(.025)
 else:
  stop(s); raise RuntimeError('Startup timeout')
 log('START '+s['release']); print('RUNNING '+s['release'])
def url(s): return f"http://127.0.0.1:{s.get('port',0)}/"
def verify(s):
 if not owned(s): print('FAIL stopped; no owned service; HTTP not available'); return False
 ok=True
 for path in ('','api/products','api/order-smoke'):
  try:
   with urlopen(url(s)+path,timeout=2) as r:
    raw=r.read().decode(); good=r.status==200
    if path=='': good=good and '<h1>'+s['shop']+'</h1>' in raw
    else:
     data=json.loads(raw); good=good and data.get('shop')==s['shop']
     if path=='api/products': good=good and data.get('products')==[{'id':'DEMO-1','name':'สมุดฝึกงาน','price':99}]
     else: good=good and all(data.get(k)==v for k,v in {'order_id':'DEMO-ORDER','product_id':'DEMO-1','quantity':2,'total':198,'persisted':False}.items())
    print(('PASS' if good else 'FAIL')+' HTTP 200 /'+path+' content '+('valid' if good else 'invalid')); ok=ok and good
  except Exception as e: print('FAIL /'+path+' '+str(e)); ok=False
 print('VERIFIED healthy shop + products + simulated order' if ok else 'NOT RECOVERED'); return ok
try:
 if a.command in ('setup','reset'):
  if a.command=='setup' and statefile.exists():
   s=read(); print('SETUP already exists; kept scenario '+s['scenario'])
  else:
   if statefile.exists(): stop(read())
   scenario=a.scenario or 'basic-A'; s={'scenario':scenario,'shop':{'basic-A':'ร้านใบชา A','basic-B':'ร้านดอกไม้ B','rollback-A':'ร้านใบชา A','rollback-B':'ร้านดอกไม้ B','transfer-C':'ร้านสมุด C'}[scenario],'release':'v2-bad' if scenario.startswith('rollback') or scenario=='transfer-C' else 'v1-good','pid':None,'port':0,'token':uuid.uuid4().hex}
   save(s); log('RESET '+scenario+'; synthetic fixtures only; no stored orders')
   if s['release']=='v2-bad': start(s)
   print('READY '+scenario+' '+s['shop'])
  print('Runtime: '+str(R)); print('URL: '+url(s) if s.get('port') else 'URL: assigned on ./labctl start (currently stopped)')
 elif a.command=='stop':
  if statefile.exists(): stop(read())
  print('STOPPED only this lab instance')
 else:
  s=read()
  if a.command=='start': start(s); print('URL: '+url(s))
  elif a.command=='rollback':
   if s['release']!='v2-bad': print('NO_CHANGE already v1-good; rollback does not start a stopped good release')
   else: stop(s); s['release']='v1-good'; save(s); log('ROLLBACK v2-bad -> v1-good'); start(s); print('URL: '+url(s))
  elif a.command=='status': print(('RUNNING' if owned(s) else 'STOPPED')+' release='+s['release']+' shop='+s['shop']); print('URL: '+url(s) if s.get('port') else 'URL: not assigned'); print('Status alone does not prove health. Run ./labctl verify')
  elif a.command=='open': print('Open in browser: '+url(s) if s.get('port') else 'No URL yet. Collect status/logs; start only when evidence supports it.')
  elif a.command=='logs':
   for f in ('events.log','http.log','server.log'):
    print('['+f+']'); print('\n'.join((R/f).read_text(errors='replace').splitlines()[-15:]) if (R/f).exists() else '(empty)')
  elif a.command=='verify': sys.exit(0 if verify(s) else 1)
except (RuntimeError,OSError,ValueError) as e: print('LAB ERROR: '+str(e),file=sys.stderr); sys.exit(2)
