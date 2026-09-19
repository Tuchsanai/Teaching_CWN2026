import os,subprocess
from pathlib import Path
r='img/dynamic-workflow-template.png'
names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
assert names and all(n.startswith('Basic_AI_WORFLOW/img/') and n.endswith(('.png','.svg')) for n in names)
helper='!f() { if [ "$1" = get ]; then printf "%s\\n" "username=${GITHUB_LOGIN:-${GITHUB_USER:-x-access-token}}" "password=$GITHUB_TOKEN"; fi; }; f'
env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0';env['GIT_PAGER']='cat'
args=['git','-c','credential.helper=','-c','credential.helper='+helper]
p=subprocess.run(args+['fetch','origin'],env=env,capture_output=True,text=True)
assert p.returncode==0,'Fetch failed'
counts=subprocess.check_output(['git','rev-list','--left-right','--count','HEAD...origin/main'],text=True).split()
assert counts==['0','0'],counts
subprocess.run(['git','commit','-m','docs: remove images not referenced by README'],env=env,check=True,stdout=subprocess.DEVNULL)
p=subprocess.run(args+['push','origin','main'],env=env,capture_output=True,text=True)
assert p.returncode==0,'Push failed'
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
p=subprocess.run(args+['ls-remote','origin','refs/heads/main'],env=env,capture_output=True,text=True)
assert p.returncode==0 and p.stdout.split()[0]==commit
print('PUSH_VERIFIED',commit,'FILES',len(names))
