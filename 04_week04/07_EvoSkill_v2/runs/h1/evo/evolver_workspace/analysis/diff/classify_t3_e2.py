import json, subprocess, shutil, tempfile, os, collections
def stage(src):
    d=tempfile.mkdtemp(prefix='c_',dir='/tmp'); shutil.copy(src, os.path.join(d,'solve.py')); return d
def run(d):
    p=subprocess.run(['python3','-I','/evo/evolver_workspace/analysis/diff/driver.py',d,'t3-shipping-fee'],capture_output=True,text=True)
    return json.loads(p.stdout)
ref=run(stage('/evo/reference/baankafe/answers/t3-shipping-fee/solve.py'))
so=run(stage('/evo/solver_workspaces/epoch_'+ep+'/t3-shipping-fee_s1/solve.py'))
cat=collections.Counter(); ex={}
for args,r,x in zip(ref['cases'],ref['res'],so['res']):
    if r==x: continue
    w,d,e=args
    if r[0]=='err' and e and w>20000: k='express_over_20000_policy'
    elif r[0]=='ok' and d==0 and r[1]==0: k='zero_distance_pickup_policy'
    elif r[0]=='ok' and x[0]=='ok' and abs(r[1]-x[1])<=1: k='rounding_1'
    else: k='other:'+str(r)+' vs '+str(x)
    cat[k]+=1; ex.setdefault(k,(args,r,x))
print(dict(cat))
for k,v in ex.items(): print(' ',k,v)
