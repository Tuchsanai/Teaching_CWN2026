# usage: python3 -I driver.py <module_dir> <task_id>  -> prints JSON list of outcomes for fixed generated cases
import sys, json, random, importlib
mod_dir, task = sys.argv[1], sys.argv[2]
sys.path.insert(0, mod_dir)
FN = {'t1-cafe-bill':'cafe_bill','t2-split-bill':'split_bill','t3-shipping-fee':'shipping_fee','t4-cashback':'cashback'}[task]
f = getattr(importlib.import_module('solve'), FN)
rng = random.Random(12345)
def cases():
    out = []
    if task == 't1-cafe-bill':
        for _ in range(300):
            n = rng.randint(0, 3)
            items = [{'price': rng.randint(0, 30000), 'qty': rng.randint(1, 4)} for _ in range(n)]
            out.append([items, rng.random() < .5])
        # invalid
        out += [[[{'price':100,'qty':True}], False], [[{'price':True,'qty':1}], False],
                [[{'price':100,'qty':1}], 1], [[{'price':100,'qty':1}], None], [[{'price':100,'qty':1}], 'yes'],
                [[{'price':None,'qty':1}], False], [[{'price':100}], False], [[{'qty':1}], False],
                [[{'price':-5,'qty':1}], False], [[{'price':100,'qty':1.5}], False], [({'price':100,'qty':1},), False],
                [{'price':100,'qty':1}, False], [[100], False], [[{'price':10**12,'qty':1}], False]]
    elif task == 't2-split-bill':
        for _ in range(300):
            out.append([rng.randint(0, 200000), rng.randint(1, 9), rng.randint(0, 100)])
        out += [[100, True, 0], [100, 2, True], [True, 2, 0], [100, 2, False], [100, 0, 0], [100, 2, 101],
                [100, 2, -1], [100, 2, 1.5], [100, None, 0], [100.0, 2, 0], [100, 2.0, 0], [-1, 2, 0]]
    elif task == 't3-shipping-fee':
        for _ in range(300):
            out.append([rng.randint(1, 30000), rng.randint(0, 250), rng.random() < .5])
        out += [[0, 10, False], [30001, 10, False], [1000, 0, True], [1000, 0, False], [25000, 10, True],
                [25000, 10, False], [5000, 100, False], [5000, 101, False], [1000, 100.5, False],
                [1000, -1, False], [1000, 10, 1], [1000, 10, None], [True, 10, False], [1000, True, False],
                [5001, 10, False], [20000, 10, True], [20001, 10, True], [1000.0, 10, False], [1000, 10, 'yes']]
    elif task == 't4-cashback':
        tiers = ['silver','gold','platinum']
        for _ in range(300):
            out.append([rng.randint(0, 1000000), rng.choice(tiers), rng.random() < .5])
        out += [[10000, 'Gold', False], [10000, ' gold', False], [10000, 'bronze', False], [10000, None, False],
                [10000, 'silver', 1], [10000, 'silver', None], [True, 'gold', False], [10000.0, 'gold', False],
                [-1, 'gold', False], [9999, 'platinum', True], [0, 'gold', False], [10000, 'silver', True],
                [10015, 'silver', True], [20000, 'silver', True], [10000, 'gold', True], [1000000, 'platinum', True]]
    return out
CASES = cases()
res = []
for args in CASES:
    try:
        if task == 't1-cafe-bill':
            v = f(args[0], args[1])
        else:
            v = f(*args)
        res.append(['ok', v if not isinstance(v, list) else v])
    except Exception as e:
        res.append(['err', type(e).__name__])
print(json.dumps({'cases': CASES, 'res': res}, ensure_ascii=False, default=str))
