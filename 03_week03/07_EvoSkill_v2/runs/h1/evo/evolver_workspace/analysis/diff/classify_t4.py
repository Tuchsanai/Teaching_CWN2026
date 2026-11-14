import json, subprocess, shutil, tempfile, os, collections, sys
ep=sys.argv[1]
def stage(src):
    d=tempfile.mkdtemp(prefix='c_',dir='/tmp'); shutil.copy(src, os.path.join(d,'solve.py')); return d
def run(d):
    p=subprocess.run(['python3','-I','/evo/evolver_workspace/analysis/diff/driver.py',d,'t4-cashback'],capture_output=True,text=True)
    return json.loads(p.stdout)
ref=run(stage('/evo/reference/baankafe/answers/t4-cashback/solve.py'))
for s in ['t4-cashback_s1','t4-cashback_s2','t4-cashback_s3']:
    so=run(stage(f'/evo/solver_workspaces/epoch_{ep}/{s}/solve.py'))
    cat=collections.Counter(); examples={}
    for (args,r,x) in zip(ref['cases'],ref['res'],so['res']):
        if r==x: continue
        amt,tier,bd=args
        if r[0]=='ok' and x[0]=='ok' and abs(r[1]-x[1])==1: k='rounding_off_by_1'
        elif tier=='silver' and bd: k='silver_birthday_policy'
        elif r[0]=='ok' and x[0]=='ok': k='other_value'
        else: k='error_mismatch:'+str(r)+' vs '+str(x)
        cat[k]+=1; examples.setdefault(k,(args,r,x))
    print(s, dict(cat))
    for k,v in examples.items(): print('   ',k,v)
