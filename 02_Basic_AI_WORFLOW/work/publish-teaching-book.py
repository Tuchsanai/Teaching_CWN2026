import os,subprocess
from pathlib import Path
r='img/dynamic-workflow-template.png'
assert not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip()
subprocess.run(['git','add','--']+['AI_Workflow_Interactive_Book.html', 'tools/build-teaching-book.py', 'tools/teaching-book-shell.html', 'tools/test-teaching-book.py', 'tools/test-book-artifacts.py', 'tools/teaching-book-build.json', 'tools/teaching-book-verification.json', 'tools/teaching-book-artifact-verification.json'],check=True)
names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
assert set(names)==set('Basic_AI_WORFLOW/'+x for x in ['AI_Workflow_Interactive_Book.html', 'tools/build-teaching-book.py', 'tools/teaching-book-shell.html', 'tools/test-teaching-book.py', 'tools/test-book-artifacts.py', 'tools/teaching-book-build.json', 'tools/teaching-book-verification.json', 'tools/teaching-book-artifact-verification.json'])
subprocess.run(['git','diff','--cached','--check'],check=True)
helper='!f() { if [ "$1" = get ]; then printf "%s\\n" "username=${GITHUB_LOGIN:-${GITHUB_USER:-x-access-token}}" "password=$GITHUB_TOKEN"; fi; }; f'
env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0';env['GIT_PAGER']='cat'
args=['git','-c','credential.helper=','-c','credential.helper='+helper]
p=subprocess.run(args+['fetch','origin'],env=env,capture_output=True,text=True)
assert p.returncode==0,'Fetch failed'
counts=subprocess.check_output(['git','rev-list','--left-right','--count','HEAD...origin/main'],text=True).split()
assert counts==['0','0'],counts
subprocess.run(['git','commit','-m','feat: add single-file offline AI workflow teaching book'],env=env,check=True,stdout=subprocess.DEVNULL)
p=subprocess.run(args+['push','origin','main'],env=env,capture_output=True,text=True)
assert p.returncode==0,'Push failed'
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
p=subprocess.run(args+['ls-remote','origin','refs/heads/main'],env=env,capture_output=True,text=True)
assert p.returncode==0 and p.stdout.split()[0]==commit
print('PUSH_VERIFIED',commit,'FILES',len(names))
