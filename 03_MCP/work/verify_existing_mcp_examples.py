from pathlib import Path
import subprocess,json,datetime
root=Path.cwd(); r=root/'lab-results'/'documentation-check'/datetime.datetime.now(datetime.timezone.utc).strftime('run-%Y-%m-%d-%H%M%S');r.mkdir(parents=True)
(root/'work/documentation-check-state.json').write_text(json.dumps({'run':str(r)}))
results=[]
for server in ['hello','tts']:
 with (r/(server+'-stdout.txt')).open('w') as out,(r/(server+'-stderr.txt')).open('w') as err:
  p=subprocess.run(['/opt/venv/bin/python','labs/my-mcp-server/client_test.py','--server',server,'--wire',str(r/(server+'-wire.jsonl'))],stdout=out,stderr=err,timeout=180)
 results.append({'server':server,'exit':p.returncode})
(r/'test-results.json').write_text(json.dumps(results,indent=2)); print(json.dumps(results))
