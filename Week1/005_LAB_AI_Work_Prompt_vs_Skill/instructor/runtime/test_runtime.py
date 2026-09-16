"""Functional checks with real HTTP, wrong repairs, repeat reset and isolation."""
import datetime,json,os,subprocess,sys,time,uuid
from pathlib import Path
from urllib.request import urlopen
BASE=Path(__file__).resolve().parents[2]
instances=['test-'+uuid.uuid4().hex[:10] for _ in range(2)]
def run(command,expected=0,which=0):
 env=dict(os.environ,SHOP_LAB_INSTANCE=instances[which])
 result=subprocess.run([str(BASE/'labctl'),*command.split()],cwd=BASE,env=env,text=True,capture_output=True,timeout=15)
 print('$ SHOP_LAB_INSTANCE='+instances[which]+' ./labctl '+command,flush=True); print(result.stdout+result.stderr,end='',flush=True)
 assert result.returncode==expected,(command,result.returncode,expected)
 return result.stdout
print('UTC',datetime.datetime.now(datetime.timezone.utc).isoformat(),'Python',sys.version,flush=True)
try:
 run('setup'); run('setup'); run('verify',1); run('rollback'); run('verify',1)
 run('start'); run('verify'); run('open'); run('status'); run('logs')
 run('setup basic-B',which=1); run('start',which=1); run('verify',which=1)
 state1=json.loads((BASE/'.lab-runtime'/instances[0]/'state.json').read_text()); state2=json.loads((BASE/'.lab-runtime'/instances[1]/'state.json').read_text())
 assert state1['port']!=state2['port']; print('PASS distinct concurrently reserved loopback ports')
 run('stop'); run('verify',1); run('verify',which=1)
 for scenario in ['basic-B','rollback-A','rollback-B','transfer-C','basic-A','basic-A']:
  run('reset '+scenario)
  if scenario.startswith('basic'):
   run('verify',1); run('start'); run('verify')
  else:
   run('verify',1); run('start'); run('verify',1); run('rollback'); run('verify')
  state=json.loads((BASE/'.lab-runtime'/instances[0]/'state.json').read_text())
  with urlopen(f"http://127.0.0.1:{state['port']}/api/order-smoke") as r: assert json.load(r)['total']==198
  assert not list((BASE/'.lab-runtime'/instances[0]).glob('*orders*')); print('PASS smoke endpoint has no persistent order side effect')
 print('ALL FUNCTIONAL CHECKS PASSED')
finally:
 for i in range(2):
  run('stop',which=i)
  path=BASE/'.lab-runtime'/instances[i]/'state.json'
  if path.exists(): assert json.loads(path.read_text())['pid'] is None
 print('CLEANUP PASS: both test services stopped; scoped evidence retained')
