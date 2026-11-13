# usage: python3 -I fuzz.py <task_id> <func> <solver_solve.py path> ; compares with reference solve.py on random inputs
import sys, random, importlib.util, json
task, func, path = sys.argv[1], sys.argv[2], sys.argv[3]
def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ref = load(f'/evo/reference/answers/{task}/solve.py', 'ref'); sol = load(path, 'sol')
R = getattr(ref, func); S = getattr(sol, func)
def run(f, args):
    try: return ('ok', f(*args))
    except ValueError: return ('ValueError', None)
    except Exception as e: return ('other:'+type(e).__name__, None)
random.seed(1)
def rnd_args():
    if task == 't4-cashback':
        return [random.choice([random.randint(0,3000000), random.choice([9999,10000,10001,20000,400000,500000,19999,20001])]), random.choice(['silver','gold','platinum','x']), random.choice([True,False])]
    if task == 't3-shipping-fee':
        return [random.choice([random.randint(1,30000), random.choice([1000,1001,5000,5001,30000])]), random.choice([random.randint(0,300), 100, 101]), random.choice([True,False])]
    if task == 't2-split-bill':
        return [random.randint(0,200000), random.randint(1,12), random.randint(0,100)]
    if task == 't1-cafe-bill':
        items=[{'price':random.randint(0,60000),'qty':random.randint(1,5)} for _ in range(random.randint(0,4))]
        return [items, random.choice([True,False])]
diffs=[]
for _ in range(3000):
    a=rnd_args(); r=run(R,a); s=run(S,a)
    if r!=s: diffs.append((a,r,s))
print(task, path.split('/')[-2] if '/' in path else path, 'diffs=',len(diffs))
for d in diffs[:4]: print('  ',json.dumps(d[0],ensure_ascii=False)[:150], 'ref=',d[1],'sol=',d[2])
