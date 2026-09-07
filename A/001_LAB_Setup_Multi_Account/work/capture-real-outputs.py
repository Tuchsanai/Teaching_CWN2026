import subprocess,socket,secrets,json,time
from pathlib import Path

def run(args,**kw): return subprocess.run(args,check=True,**kw)
assert len(subprocess.check_output(['docker','ps','--filter','name=^devtools-','--format','{{.Names}}'],text=True).splitlines())<7
port=2222
while True:
    sock=socket.socket()
    try: sock.bind(('127.0.0.1',port)); sock.close(); break
    except OSError: sock.close(); port+=1
name='devtools-lab001-output-'+secrets.token_hex(3)
meta={'owner':'current-task','name':name,'port':port}
Path('work/output-container.json').write_text(json.dumps(meta))
def dex(cmd): return run(['docker','exec',name,'bash','-lc',cmd])
def typecmd(cmd):
    run(['docker','exec','-e','DISPLAY=:99',name,'xdotool','type','--clearmodifiers',cmd])
    run(['docker','exec','-e','DISPLAY=:99',name,'xdotool','key','Return'])
def capture(filename):
    dex('export DISPLAY=:99; import -window $(xdotool search --onlyvisible --name "LAB output capture" | head -1) /tmp/'+filename)
    run(['docker','cp',name+':/tmp/'+filename,'work/'+filename],stdout=subprocess.DEVNULL)
try:
    run(['docker','run','-dit','--name',name,'--privileged','-p',f'127.0.0.1:{port}:22','tuchsanai/devtools:2569_1'],stdout=subprocess.DEVNULL)
    run(['docker','inspect','--format','{{.State.Running}} {{json .NetworkSettings.Ports}}',name])
    with Path('work/output-setup.log').open('w') as log:
        run(['docker','exec',name,'bash','-lc','apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb xterm xdotool imagemagick curl ca-certificates && npm install -g @openai/codex'],stdout=log,stderr=subprocess.STDOUT)
    print('Tools installed',flush=True)
    dex("export DISPLAY=:99; Xvfb :99 -screen 0 1440x800x24 -nolisten tcp >/tmp/xvfb.log 2>&1 & sleep 1; mkdir -p /workspace/lab001; cd /workspace/lab001; export PATH=/root/.local/bin:$PATH; export PS1='$ '; xterm -geometry 110x24 -fa 'DejaVu Sans Mono' -fs 15 -bg '#151c29' -fg '#e1e7f0' -title 'LAB output capture' -e bash --noprofile --norc >/tmp/xterm.log 2>&1 & sleep 2")
    typecmd('curl -fsSL https://claude.ai/install.sh | bash')
    for i in range(120):
        ok=subprocess.run(['docker','exec',name,'test','-x','/root/.local/bin/claude'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if ok: break
        time.sleep(2)
    else: raise RuntimeError('Native installer timeout')
    time.sleep(3)
    capture('install-output-real.png')
    print('Native install completed and screenshot saved',flush=True)
    typecmd('clear'); time.sleep(1)
    typecmd('claude --version'); time.sleep(2)
    dex('export DISPLAY=:99; xdotool windowsize $(xdotool search --onlyvisible --name "LAB output capture" | head -1) 1434 200; sleep 1')
    capture('version-output-real.png')
    setup=r"""from pathlib import Path
import subprocess
claude='/root/.local/bin/claude'
for binary,flag in [(claude,'--dangerously-skip-permissions'),('codex','--dangerously-bypass-approvals-and-sandbox')]:
    assert flag in subprocess.check_output([binary,'--help'],text=True)
for prefix,tool,env,binary,flag in [('yolo','.Claude','CLAUDE_CONFIG_DIR',claude,'--dangerously-skip-permissions'),('cyolo','.Codex','CODEX_HOME','/usr/bin/codex','--dangerously-bypass-approvals-and-sandbox')]:
    if prefix=='cyolo': binary=subprocess.check_output(['which','codex'],text=True).strip()
    for i in range(1,6):
        root=Path('/workspace/lab001/ai-accounts')/tool/(prefix+str(i)); root.mkdir(parents=True,exist_ok=True)
        p=Path('/usr/local/bin')/(prefix+str(i))
        p.write_text('#!/bin/sh\nexport IS_SANDBOX=1\nexport '+env+'="'+str(root)+'"\nexec "'+binary+'" '+flag+' "$@"\n')
        p.chmod(0o755)
"""
    run(['docker','exec',name,'python3','-c',setup])
    dex('export DISPLAY=:99; xdotool windowsize $(xdotool search --onlyvisible --name "LAB output capture" | head -1) 1434 450; sleep 1')
    typecmd('clear'); time.sleep(1)
    outputs=[]
    for i in range(1,4):
        command=f'yolo{i} --version; cyolo{i} --version'
        result=subprocess.check_output(['docker','exec',name,'bash','-lc',command],text=True)
        assert 'Claude Code' in result and 'codex-cli' in result
        outputs.append(command+'\n'+result)
        typecmd(command); time.sleep(2)
    capture('accounts-version-output-real.png')
    Path('work/accounts-version-results.txt').write_text('\n'.join(outputs))
    print('All six account commands returned actual versions; screenshots saved',flush=True)
finally:
    run(['docker','rm','-f',name],stdout=subprocess.DEVNULL)
    assert not subprocess.check_output(['docker','ps','-a','--filter','name=^'+name+'$','--format','{{.Names}}'],text=True).strip()
    Path('work/output-cleanup.txt').write_text('Container '+name+'; SSH port '+str(port)+'; cleanup verified. No credentials copied for this run.\n')
    print('Cleanup verified',flush=True)
