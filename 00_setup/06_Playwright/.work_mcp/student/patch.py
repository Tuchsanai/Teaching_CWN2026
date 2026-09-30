import sys
p='/root/workspace/CWN/Teaching/00_setup/06_Playwright/01_playwright-mcp/README.md'
s=open(p,encoding='utf-8').read()
def R(old,new):
    global s
    n=s.count(old)
    if n!=1: sys.exit(f'count={n} for: {old[:80]!r}')
    s=s.replace(old,new)
exec(open(sys.argv[1],encoding='utf-8').read())
open(p,'w',encoding='utf-8').write(s)
print('ok')
