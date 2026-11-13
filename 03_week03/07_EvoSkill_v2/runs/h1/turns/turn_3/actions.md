# ตาที่ 3 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 02:29 UTC คุณมีเวลาถึง 2026-11-13 02:59 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 3 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v3` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
date -u && cat scores/epoch_2.json 2>/dev/null; echo; ls skills traces solver_workspaces; diff -r staging skills/epoch_2 2>/dev/null && echo SAME_AS_STAGING_V2; echo ---; cd /evo/solver_workspaces/epoch_2 2>/dev/null && for d in */; do d=${d%/}; t=${d%_s*}; out=$(python3 -I /evo/evolver_workspace/analysis/run_tests.py /evo/solver_workspaces/epoch_2/$d /evo/reference/answers/$t/test_solve.py 2>&1 | tail -1); echo "$d -> $out"; done; echo ---; grep -l "stdin" /evo/solver_workspaces/epoch_2/*/solve.py 2>/dev/null | wc -l
```

ผลที่ได้:

```
Fri Nov 13 02:29:53 UTC 2026
{
 "t1-cafe-bill_s1": 0.9,
 "t1-cafe-bill_s2": 0.9,
 "t1-cafe-bill_s3": 0.9,
 "t2-split-bill_s1": 0.9,
 "t2-split-bill_s2": 0.9,
 "t2-split-bill_s3": 0.9,
 "t3-shipping-fee_s1": 0.9,
 "t3-shipping-fee_s2": 0.9,
 "t3-shipping-fee_s3": 0.9,
 "t4-cashback_s1": 1.0,
 "t4-cashback_s2": 1.0,
 "t4-cashback_s3": 0.9
}
skills:
epoch_0
epoch_1
epoch_2

solver_workspaces:
epoch_0
epoch_1
epoch_2

traces:
epoch_0
epoch_1
epoch_2
SAME_AS_STAGING_V2
---
t1-cafe-bill_s1 -> ran=12 failed=0 []
t1-cafe-bill_s2 -> ran=12 failed=0 []
t1-cafe-bill_s3 -> ran=12 failed=0 []
t2-split-bill_s1 -> ran=12 failed=0 []
t2-split-bill_s2 -> ran=12 failed=0 []
t2-split-bill_s3 -> ran=12 failed=0 []
t3-shipping-fee_s1 -> ran=12 failed=0 []
t3-shipping-fee_s2 -> ran=12 failed=0 []
t3-shipping-fee_s3 -> ran=12 failed=0 []
t4-cashback_s1 -> ran=12 failed=0 []
t4-cashback_s2 -> ran=12 failed=0 []
t4-cashback_s3 -> ran=12 failed=0 []
---
12
```

### ขั้น 2 · Bash

```
grep -n "def main\|ok\|error" t1-cafe-bill_s1/solve.py | head; echo ---; for d in */; do d=${d%/}; echo "== $d"; grep -n "stdin\|__main__" $d/solve.py | head -3; done 2>/dev/null | head -60
```

ผลที่ได้:

```
55:def main():
61:    except (ValueError, TypeError) as error:
62:        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
64:    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
---
== t1-cafe-bill_s1
57:        args = json.load(sys.stdin)
68:if __name__ == "__main__":
== t1-cafe-bill_s2
64:        args = json.load(sys.stdin)
75:if __name__ == "__main__":
== t1-cafe-bill_s3
70:        args = json.load(sys.stdin)
81:if __name__ == "__main__":
== t2-split-bill_s1
45:        args = json.load(sys.stdin)
56:if __name__ == "__main__":
== t2-split-bill_s2
40:        args = json.load(sys.stdin)
51:if __name__ == "__main__":
== t2-split-bill_s3
47:        args = json.load(sys.stdin)
58:if __name__ == "__main__":
== t3-shipping-fee_s1
81:        args = json.load(sys.stdin)
92:if __name__ == "__main__":
== t3-shipping-fee_s2
72:        args = json.load(sys.stdin)
83:if __name__ == "__main__":
== t3-shipping-fee_s3
68:        args = json.load(sys.stdin)
79:if __name__ == "__main__":
== t4-cashback_s1
50:        args = json.load(sys.stdin)
61:if __name__ == "__main__":
== t4-cashback_s2
58:        args = json.load(sys.stdin)
69:if __name__ == "__ma
…(ตัด 93 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /evo/evolver_workspace/analysis && cat > /evo/evolver_workspace/analysis/cli_check.py <<'EOF'
# usage: python3 -I cli_check.py <solver_dir> <reference_test_file> <param,names,comma>
# Runs the solver's CLI (JSON stdin) on every positional case in the reference test file.
import sys, ast, json, subprocess, os
solver_dir, test_file, params = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
src = open(test_file, encoding='utf-8').read()
tree = ast.parse(src)
cases = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute) and stmt.func.attr == 'assertEqual':
                call, exp = stmt.args[0], ast.literal_eval(stmt.args[1])
                cases.append(('ok', call, exp))
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    call = item.context_expr
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'assertRaises':
                        cases.append(('err', call.args[0] if False else stmt.body[0].value, None))
results = []
for kind, call, exp in cases:
    kwargs = {p: ast.literal_eval(a) for p, a in zip(params, call.args)}
    p = subprocess.run([sys.executable, '-I', os.path.join(solver_dir, 'solve.py')],
                       input=json.dumps(kwargs), capture_output=True, text=True, timeout=10)
    try:
        out = json.loads(p.stdout)
    except Exception:
        out = {'raw': p.stdout[-200:], 'stderr': p.stderr[-200:]}
    if kind == 'ok':
        good = out.get('ok') is True and out.get('result') == exp
    else:
        good = out.get('ok') is False and p.returncode == 2
    if not good:
        results.append((kind, kwargs, exp, out, p.returncode))
print(f"mismatches={len(results)}")
for r in results: print('  ', r)
EOF
cd /evo/solver_workspaces/epoch_2 && python3 -I /evo/evolver_workspace/analysis/cli_check.py t1-cafe-bill_s1 /evo/reference/answers/t1-cafe-bill/test_solve.py items,member 2>&1 | head -20
```

ผลที่ได้:

```
mismatches=0
```

### ขั้น 4 · Bash

```
sed -i 's/^print(f"mismatches={len(results)}")/print(f"cases={len(cases)} mismatches={len(results)}")/' /evo/evolver_workspace/analysis/cli_check.py && for t in t1-cafe-bill:items,member t2-split-bill:total,people,tip_percent t3-shipping-fee:weight_g,distance_km,express t4-cashback:amount,tier,birthday; do n=${t%%:*}; p=${t#*:}; for s in 1 2 3; do echo "== $n s$s: $(python3 -I /evo/evolver_workspace/analysis/cli_check.py $n\_s$s /evo/reference/answers/$n/test_solve.py $p 2>&1 | head -4 | tr '\n' ' ')"; done; done; date -u
```

ผลที่ได้:

```
== t1-cafe-bill s1: cases=12 mismatches=0 
== t1-cafe-bill s2: cases=12 mismatches=0 
== t1-cafe-bill s3: cases=12 mismatches=0 
== t2-split-bill s1: cases=12 mismatches=0 
== t2-split-bill s2: cases=12 mismatches=0 
== t2-split-bill s3: cases=12 mismatches=0 
== t3-shipping-fee s1: cases=12 mismatches=0 
== t3-shipping-fee s2: cases=12 mismatches=0 
== t3-shipping-fee s3: cases=12 mismatches=0 
== t4-cashback s1: cases=12 mismatches=0 
== t4-cashback s2: cases=12 mismatches=0 
== t4-cashback s3: cases=12 mismatches=0 
Fri Nov 13 02:30:07 UTC 2026
```

### ขั้น 5 · Bash

```
cd /evo/evolver_workspace/analysis && cat > probe.py <<'EOF'
# usage: python3 -I probe.py <solver_dir> <probes.json>  -> prints outputs per probe
import sys, json, subprocess
solver_dir, probes = sys.argv[1], json.load(open(sys.argv[2]))
for kw in probes:
    p = subprocess.run([sys.executable, '-I', solver_dir + '/solve.py'], input=json.dumps(kw), capture_output=True, text=True, timeout=10)
    print(json.dumps(kw, ensure_ascii=False), '->', (p.stdout.strip() or p.stderr.strip()[-120:]).replace('\n',' '), 'rc=%d' % p.returncode)
EOF
cat > probes_t4.json <<'EOF'
[{"amount":10000,"tier":"Gold","birthday":false},
 {"amount":10000,"tier":" gold","birthday":false},
 {"amount":10000,"tier":"silver","birthday":0},
 {"amount":10000,"tier":"silver"},
 {"amount":10000,"tier":"silver","birthday":false,"extra":1},
 {"amount":-1,"tier":"silver","birthday":false},
 {"amount":true,"tier":"silver","birthday":false},
 {"amount":10000.0,"tier":"silver","birthday":false},
 {"amount":10000,"tier":null,"birthday":false},
 {"amount":10000,"tier":["gold"],"birthday":false},
 {"amount":19999,"tier":"gold","birthday":true},
 {"amount":10000000000,"tier":"platinum","birthday":false}]
EOF
cat > probes_t1.json <<'EOF'
[{"items":[],"member":false},
 {"items":[{"price":4500,"qty":1,"name":"x"}],"member":false},
 {"items":[{"price":4500}],"member":false},
 {"items":[{"price":4500,"qty":0}],"member":false},
 {"items":[{"price":-1,"qty":1}],"member":false},
 {"items":[{"price":4500,"qty":1}],"member":1},
 {"items":[{"price":4500,"qty":1}]},
 {"items":"abc","member":false},
 {"items":[4500],"member":false}]
EOF
for s in 1 2 3; do echo "== t4 s$s"; python3 -I probe.py /evo/solver_workspaces/epoch_2/t4-cashback_s$s probes_t4.json; done
```

ผลที่ได้:

```
== t4 s1
{"amount": 10000, "tier": "Gold", "birthday": false} -> {"ok": false, "error": "tier ต้องเป็น silver, gold หรือ platinum"} rc=2
{"amount": 10000, "tier": " gold", "birthday": false} -> {"ok": false, "error": "tier ต้องเป็น silver, gold หรือ platinum"} rc=2
{"amount": 10000, "tier": "silver", "birthday": 0} -> {"ok": false, "error": "birthday ต้องเป็น True หรือ False"} rc=2
{"amount": 10000, "tier": "silver"} -> {"ok": false, "error": "cashback() missing 1 required positional argument: 'birthday'"} rc=2
{"amount": 10000, "tier": "silver", "birthday": false, "extra": 1} -> {"ok": false, "error": "cashback() got an unexpected keyword argument 'extra'"} rc=2
{"amount": -1, "tier": "silver", "birthday": false} -> {"ok": false, "error": "amount ต้องไม่ติดลบ"} rc=2
{"amount": true, "tier": "silver", "birthday": false} -> {"ok": false, "error": "amount ต้องเป็นจำนวนเต็มสตางค์"} rc=2
{"amount": 10000.0, "tier": "silver", "birthday": false} -> {"ok": false, "error": "amount ต้องเป็นจำนวนเต็มสตางค์"} rc=2
{"amount": 10000, "tier": null, "birthday": false} -> {"ok": false, "error": "tier ต้องเป็น silver, gold หรือ platinum"} rc=2
{"amount": 10000, "tier": ["gold"], "birthday": false} 
…(ตัด 3248 ตัวอักษร)
```

### ขั้น 6 · Bash

```
for s in 1 2 3; do echo "== t1 s$s"; python3 -I probe.py /evo/solver_workspaces/epoch_2/t1-cafe-bill_s$s probes_t1.json; done 2>&1 | cut -c1-260
```

ผลที่ได้:

```
== t1 s1
{"items": [], "member": false} -> {"ok": true, "result": 0} rc=0
{"items": [{"price": 4500, "qty": 1, "name": "x"}], "member": false} -> {"ok": true, "result": 4815} rc=0
{"items": [{"price": 4500}], "member": false} -> {"ok": false, "error": "รายการที่ 0 ต้องมี price และ qty"} rc=2
{"items": [{"price": 4500, "qty": 0}], "member": false} -> {"ok": false, "error": "qty ของรายการที่ 0 ต้องไม่น้อยกว่า 1"} rc=2
{"items": [{"price": -1, "qty": 1}], "member": false} -> {"ok": false, "error": "price ของรายการที่ 0 ต้องไม่น้อยกว่า 0"} rc=2
{"items": [{"price": 4500, "qty": 1}], "member": 1} -> {"ok": false, "error": "member ต้องเป็น True หรือ False"} rc=2
{"items": [{"price": 4500, "qty": 1}]} -> {"ok": false, "error": "cafe_bill() missing 1 required positional argument: 'member'"} rc=2
{"items": "abc", "member": false} -> {"ok": false, "error": "items ต้องเป็น list"} rc=2
{"items": [4500], "member": false} -> {"ok": false, "error": "รายการที่ 0 ต้องเป็น dict"} rc=2
== t1 s2
{"items": [], "member": false} -> {"ok": true, "result": 0} rc=0
{"items": [{"price": 4500, "qty": 1, "name": "x"}], "member": false} -> {"ok": true, "result": 4815} rc=0
{"items": [{"price": 4500}], "member":
…(ตัด 1710 ตัวอักษร)
```

### ขั้น 7 · Bash

```
cd /evo/traces/epoch_2 && python3 - <<'EOF'
import json,glob
for f in sorted(glob.glob('*.jsonl')):
    lines=[json.loads(l) for l in open(f)]
    r=[l for l in lines if l.get('type')=='result'][-1]
    txt=r.get('result') or ''
    tools=[c.get('name') for l in lines if l.get('type')=='assistant' for c in (l.get('message',{}).get('content') or []) if isinstance(c,dict) and c.get('type')=='tool_use']
    print(f"{f:28s} turns={r.get('num_turns')} chars={len(txt)} tools={len(tools)} skillRead={any('skills' in json.dumps(l) for l in lines if l.get('type')=='user')}")
EOF
echo; python3 -c "
import json
lines=[json.loads(l) for l in open('/evo/traces/epoch_2/t4-cashback_s3.jsonl')]
r=[l for l in lines if l.get('type')=='result'][-1]
print(r.get('result')[:1800])"
```

ผลที่ได้:

```
t1-cafe-bill_s1.jsonl        turns=5 chars=1317 tools=4 skillRead=True
t1-cafe-bill_s2.jsonl        turns=6 chars=1350 tools=5 skillRead=True
t1-cafe-bill_s3.jsonl        turns=8 chars=1437 tools=7 skillRead=True
t2-split-bill_s1.jsonl       turns=8 chars=1486 tools=7 skillRead=True
t2-split-bill_s2.jsonl       turns=8 chars=1161 tools=7 skillRead=True
t2-split-bill_s3.jsonl       turns=5 chars=1581 tools=4 skillRead=True
t3-shipping-fee_s1.jsonl     turns=6 chars=1552 tools=5 skillRead=True
t3-shipping-fee_s2.jsonl     turns=6 chars=1524 tools=5 skillRead=True
t3-shipping-fee_s3.jsonl     turns=7 chars=1683 tools=6 skillRead=True
t4-cashback_s1.jsonl         turns=10 chars=1714 tools=9 skillRead=True
t4-cashback_s2.jsonl         turns=6 chars=1494 tools=5 skillRead=True
t4-cashback_s3.jsonl         turns=5 chars=1531 tools=4 skillRead=True

สร้าง `solve.py` ในโฟลเดอร์ทำงานแล้ว ผลทดสอบผ่านทุกกรณีที่คำนวณมือไว้ มี 1 กรณีที่ดูเหมือนไม่ผ่าน แต่เป็นความผิดพลาดของการคำนวณมือของผม ไม่ใช่ของโค้ด (รายละเอียดด้านล่าง)

**ฟังก์ชัน:** `cashback(amount, tier, birthday)` คืนค่าเป็น `int` หน่วยสตางค์

**ลำดับการคิด**
1. ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
2. คูณอัตราตามระดับ: silver 1.5%, g
…(ตัด 1185 ตัวอักษร)
```

### ขั้น 8 · Bash

```
cd /evo/evolver_workspace/analysis && cat > fuzz.py <<'EOF'
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
EOF
for t in t4-cashback:cashback t3-shipping-fee:shipping_fee t2-split-bill:split_bill t1-cafe-bill:cafe_bill; do n=${t%%:*}; f=${t#*:}; for s in 1 2 3; do python3 -I fuzz.py $n $f /evo/solver_workspaces/epoch_2/${n}_s$s/solve.py 2>&1 | sed "s/^/s$s /" | head -4; done; done; date -u
```

ผลที่ได้:

```
s1 t4-cashback t4-cashback_s1 diffs= 0
s2 t4-cashback t4-cashback_s2 diffs= 0
s3 t4-cashback t4-cashback_s3 diffs= 0
s1 t3-shipping-fee t3-shipping-fee_s1 diffs= 0
s2 t3-shipping-fee t3-shipping-fee_s2 diffs= 0
s3 t3-shipping-fee t3-shipping-fee_s3 diffs= 0
s1 t2-split-bill t2-split-bill_s1 diffs= 0
s2 t2-split-bill t2-split-bill_s2 diffs= 0
s3 t2-split-bill t2-split-bill_s3 diffs= 0
s1 t1-cafe-bill t1-cafe-bill_s1 diffs= 0
s2 t1-cafe-bill t1-cafe-bill_s2 diffs= 0
s3 t1-cafe-bill t1-cafe-bill_s3 diffs= 0
Fri Nov 13 02:30:32 UTC 2026
```

### ขั้น 9 · Edit

```
/evo/staging/solve-py-delivery/SKILL.md
## คำตอบสุดท้าย

สรุปเป็นภาษาไทยให้สั้นและตรงข้อเท็จจริง:

- ฟังก์ชันที่เขียนและวิธีคิดหลัก (ตามลำดับสเปก)
- การตีความที่เลือกเองในจุดกำกวม และเหตุผล
- วิธีปัดที่ใช้ และจุดที่ปัดครั้งเดียวหรือไม่
- ผลการรันทดสอบจริง พร้อมจำนวนกรณีที่รันจริงและจำนวนที่ผ่าน

กติกาของรายงาน:

- **ตัวเลขต้องตรงกับที่รันจริง** เขียนว่า "ผ่าน X จาก Y" เฉพาะเมื่อ Y คือจำนวนกรณีที่รันจริงเท่านั้น
- **ถ้าค่ามือไม่ตรงกับโค้ด** ให้คำนวณค่ามือซ้ำจนแน่ใจก่อนสรุป แล้วรายงานผลสุดท้ายเพียงครั้งเดียว ห้ามเขียนรายงานที่มีการแก้ตัวเองปนอยู่ เช่น "ดูเหมือนไม่ผ่าน แต่จริง ๆ แล้ว..."
- **ถ้ามีกรณีที่ไม่ผ่านจริง** ให้ระบุกรณี ผลที่คาด และผลที่ได้ ห้ามซ่อนหรือกลบไว้
- **จุดที่สเปกไม่ชัด** เช่น ลำดับเพดานกับตัวคูณ ให้บอกว่าเลือกลำดับไหนและทางเลือกอีกทางต่างกันที่ตรงไหน
```

ผลที่ได้:

```
The file /evo/staging/solve-py-delivery/SKILL.md has been updated successfully.
```

### ขั้น 10 · Bash

```
cat >> /evo/evolver_workspace/notes.md <<'EOF'

## Epoch 2 analysis (scores: t1/t2/t3 = 0.9, t4 s1/s2 = 1.0, t4 s3 = 0.9)
- Hypothesis from epoch 1 confirmed: all 12 solvers now wrote the CLI main() (JSON stdin, {"ok","result"}); score rose 0.7 -> 0.9.
- CLI check (analysis/cli_check.py) on all 12 reference cases per solver: 0 mismatches.
- Differential fuzz vs reference solve.py (analysis/fuzz.py, 3000 random inputs per solver, valid and invalid): 0 diffs for all 12.
- Probes (analysis/probes_t1.json, probes_t4.json): solvers agree with each other on odd inputs (extra keys, missing keys, null, list tier, wrong case).
- So the remaining 0.1 is not explained by function behaviour on tested inputs. t4 s3's final report was self-contradictory ("ผ่าน 12 จาก 13" plus a self-correction about a hand-calc error); possible reporting factor, unverified.

## Epoch 3 changes (skills_v3)
- solve-py-delivery: final-report consistency rules (counts match real runs, no mid-report self-correction, state unresolved ambiguities).
EOF
cd /evo/staging && for f in */SKILL.md; do echo "$f: $(head -2 $f | tail -1 | cut -c1-60)"; done; date -u
```

ผลที่ได้:

```
money-exact-rounding/SKILL.md: name: money-exact-rounding
solve-py-delivery/SKILL.md: name: solve-py-delivery
strict-input-validation/SKILL.md: name: strict-input-validation
thai-spec-reading/SKILL.md: name: thai-spec-reading
Fri Nov 13 02:30:45 UTC 2026
```

**Agent พูด:** `skills_v3` is in `/evo/staging/`. It's 02:31 and the deadline is 02:59.

**What epoch 2 shows**

- The score rose from 0.7 to 0.9, with one rollout pair at 1.0. This supports the epoch 1 hypothesis. All 12 Solvers now write the CLI `main()` (JSON on stdin, `{"ok", "result"}` on stdout), which the reference answers use.
- Every Solver passes all 12 reference cases through the CLI, with 0 mismatches.
- I fuzzed each Solver against the reference `solve.py` on 3,000 random inputs per task, valid and invalid. There were 0 differences. The Solvers also agree with each other on odd inputs such as extra keys, `null`, or a wrong-case tier.
- So the remaining gap is not explained by function behaviour on anything I tested. One possible cause is the reporting. The t4 s3 final message says "ผ่าน 12 จาก 13" and then corrects itself mid-report. This is a guess, not confirmed.

**Change in staging**

- `solve-py-delivery/SKILL.md`: a new reporting section. The pass counts must match real runs. A hand-calculation mismatch should be rechecked before reporting, not narrated as a self-correction. Failing cases must be listed. Ambiguities such as the cap-versus-multiplier order should be stated.
- The other three skills are unchanged, since the function-level behaviour already matches the reference.

**Next epoch**

If the score stays at 0.9, the reporting hypothesis is the first thing to test. If the score moves, I'll know which change caused it. The notes are in `/evo/evolver_workspace/notes.
…(ตัด 4 ตัวอักษร)
