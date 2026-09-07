import subprocess,socket,secrets,json,time,hashlib,re
from pathlib import Path

def run(args,**kw): return subprocess.run(args,check=True,**kw)
assert len(subprocess.check_output(['docker','ps','--filter','name=^devtools-','--format','{{.Names}}'],text=True).splitlines())<7
port=2222
while True:
    sock=socket.socket()
    try: sock.bind(('127.0.0.1',port)); sock.close(); break
    except OSError: sock.close(); port+=1
name='devtools-lab001-models-'+secrets.token_hex(3)
Path('work/models-container.json').write_text(json.dumps({'owner':'current-task','name':name,'port':port}))
credentials=[Path('/root/workspace/.Claude/yolo1/.credentials.json'),Path('/root/workspace/.Codex/cyolo1/auth.json')]
hashes=[hashlib.sha256(p.read_bytes()).digest() for p in credentials]
def dex(cmd): return run(['docker','exec',name,'bash','-lc',cmd])
try:
 run(['docker','run','-dit','--name',name,'--privileged','-p',f'127.0.0.1:{port}:22','tuchsanai/devtools:2569_1'],stdout=subprocess.DEVNULL)
 run(['docker','inspect','--format','{{.State.Running}} {{json .NetworkSettings.Ports}}',name])
 dex('mkdir -p /root/.claude /root/.codex /workspace/lab001')
 for src,dst in [('/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe','/usr/local/bin/claude'),('/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex','/usr/local/bin/codex'),(str(credentials[0]),'/root/.claude/.credentials.json'),(str(credentials[1]),'/root/.codex/auth.json')]:
  run(['docker','cp',src,name+':'+dst],stdout=subprocess.DEVNULL)
 dex('chmod 600 /root/.claude/.credentials.json /root/.codex/auth.json; chmod 755 /usr/local/bin/claude /usr/local/bin/codex')
 setup=r"""from pathlib import Path
import json
Path('/usr/local/bin/yolo1').write_text('#!/bin/sh\nexport CLAUDE_CONFIG_DIR=/root/.claude\nexport IS_SANDBOX=1\nexec claude --dangerously-skip-permissions "$@"\n')
Path('/usr/local/bin/cyolo1').write_text('#!/bin/sh\nexport CODEX_HOME=/root/.codex\nexec codex --dangerously-bypass-approvals-and-sandbox "$@"\n')
for n in ['yolo1','cyolo1']: Path('/usr/local/bin/'+n).chmod(0o755)
Path('/root/.claude.json').write_text(json.dumps({'hasCompletedOnboarding':True,'theme':'dark'}))
"""
 run(['docker','exec',name,'python3','-c',setup])
 with Path('work/models-setup.log').open('w') as log:
  run(['docker','exec',name,'bash','-lc','apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb xterm xdotool xclip imagemagick fonts-thai-tlwg'],stdout=log,stderr=subprocess.STDOUT)
 run(['docker','cp','/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex-code-mode-host',name+':/usr/local/bin/codex-code-mode-host'],stdout=subprocess.DEVNULL)
 dex('chmod 755 /usr/local/bin/codex-code-mode-host')
 print('Terminal ready; complete Codex runtime installed',flush=True)
 dex("export DISPLAY=:99; Xvfb :99 -screen 0 1440x1000x24 -nolisten tcp >/tmp/xvfb.log 2>&1 & sleep 1; cd /workspace/lab001; export PS1='$ '; export PROMPT_COMMAND='printf \"%s\" \"$?\" > /tmp/last-exit'; xterm -geometry 110x34 -fa 'DejaVu Sans Mono' -fs 14 -bg '#151c29' -fg '#e1e7f0' -title 'LAB model response' -e script -q -f /tmp/terminal-session.log -c 'bash --noprofile --norc' >/tmp/xterm.log 2>&1 & sleep 2")
 text=Path('README.md').read_text()
 section=text[text.index('### 3.2 '):text.index('### 3.3 ')]
 commands=re.findall(r'```bash\n(.*?)\n```',section,re.S)
 assert len(commands)==2
 results=json.loads(Path('work/models-results.json').read_text())
 for label,cmd in zip(['fable','astra'],commands):
  if label=='fable': continue
  dex('export DISPLAY=:99; xdotool type --clearmodifiers clear; xdotool key Return; sleep 1; rm -f /tmp/last-exit')
  Path('work/model-command.txt').write_text(cmd)
  run(['docker','cp','work/model-command.txt',name+':/tmp/model-command.txt'],stdout=subprocess.DEVNULL)
  dex('export DISPLAY=:99; xclip -selection primary -i /tmp/model-command.txt; xdotool key shift+Insert Return')
  time.sleep(2)
  for tick in range(150):
   finished=subprocess.run(['docker','exec',name,'test','-f','/tmp/last-exit'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
   if finished: break
   time.sleep(2)
  else: raise RuntimeError(label+' model request timeout')
  result=subprocess.check_output(['docker','exec',name,'cat','/tmp/last-exit'],text=True).strip()
  results[label]={'exit_code':int(result)}
  dex('export DISPLAY=:99; import -window $(xdotool search --onlyvisible --name "LAB model response" | head -1) /tmp/'+label+'-response.png')
  run(['docker','cp',name+':/tmp/'+label+'-response.png','work/'+label+'-response.png'],stdout=subprocess.DEVNULL)
  print(label+' request finished, exit code '+result,flush=True)
 run(['docker','cp',name+':/tmp/terminal-session.log','work/models-terminal-session.log'],stdout=subprocess.DEVNULL)
 Path('work/models-results.json').write_text(json.dumps(results))
finally:
 run(['docker','rm','-f',name],stdout=subprocess.DEVNULL)
 assert not subprocess.check_output(['docker','ps','-a','--filter','name=^'+name+'$','--format','{{.Names}}'],text=True).strip()
 assert hashes==[hashlib.sha256(p.read_bytes()).digest() for p in credentials]
 Path('work/models-cleanup.txt').write_text('Experiment: LAB001 Fable/Astra medium; container '+name+'; SSH port '+str(port)+'; cleanup verified; credential copies removed; host credentials unchanged.\n')
 print('Cleanup verified; credential copies removed',flush=True)
