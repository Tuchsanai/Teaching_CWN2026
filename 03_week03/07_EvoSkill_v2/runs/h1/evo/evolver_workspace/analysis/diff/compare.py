import json, subprocess, sys, os, glob, shutil, tempfile, collections
ROOT='/evo'
TASKS=['t1-cafe-bill','t2-split-bill','t3-shipping-fee','t4-cashback']
DRV='/evo/evolver_workspace/analysis/diff/driver.py'
ep=sys.argv[1]
def run(mod_dir, task):
    p=subprocess.run(['python3','-I',DRV,mod_dir,task],capture_output=True,text=True,timeout=60)
    if p.returncode!=0: return None, p.stderr[-300:]
    return json.loads(p.stdout), None
def stage(src, task):
    d=tempfile.mkdtemp(prefix='m_',dir='/tmp'); shutil.copy(src, os.path.join(d,'solve.py')); return d
summary={}
for task in TASKS:
    ref_dir=stage(f'/evo/reference/baankafe/answers/{task}/solve.py', task)
    ref,err=run(ref_dir,task); assert ref, err
    for name in sorted(os.listdir(f'{ROOT}/solver_workspaces/epoch_{ep}')):
        if not name.startswith(task+'_s'): continue
        d=stage(f'{ROOT}/solver_workspaces/epoch_{ep}/{name}/solve.py', task)
        out,err=run(d,task)
        if out is None:
            print(name,'LOAD/RUN FAIL',err); continue
        mism=[]
        for c,r,s in zip(ref['cases'],ref['res'],out['res']):
            if r!=s: mism.append((c,r,s))
        summary[name]=len(mism)
        print(f'== {name}: mismatches {len(mism)}/{len(ref["res"])}')
        for c,r,s in mism[:40]:
            print('   in=',json.dumps(c,ensure_ascii=False,default=str)[:140],' ref=',r,' solver=',s)
        shutil.rmtree(d)
    shutil.rmtree(ref_dir)
