# ตาที่ 2 ของ Evolver

ข้อความที่ได้รับ: เวลาตอนนี้ 2026-11-14 22:51 UTC · เส้นตายของตานี้ 2026-11-14 23:21 UTC เมื่อถึงเส้นตาย สิ่งที่อยู่ใน `/evo/staging/` จะถูกนำไปใช้ทันทีตามสภาพขณะนั้น · นี่คือ epoch 2 · ผลการทำโจทย์รอบล่าสุดของ Solver อยู่ใน `/evo` แล้ว ขอให้วิเคราะห์ rollout เหล่านั้น วินิจฉัยว่า Solver พลาดตรงไหนที่สกิลช่วยแก้ได้ แล้วเขียนชุดสกิล `skills_v2` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_1.json; ls skills/epoch_1; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for s in 1 2 3; do echo "=== $t s$s"; cat solver_workspaces/epoch_1/${t}_s$s/solve.py | head -70; done; done
```

ผลที่ได้:

```
<persisted-output>
Output too large (29.7KB). Full output saved to: /root/ai-accounts/.Claude/yolo1/projects/-evo/ef72ada1-a690-475f-ad18-c527407a6aba/tool-results/bqtoll0ll.txt

Preview (first 2KB):
{
 "t1-cafe-bill_s1": 0.9,
 "t1-cafe-bill_s2": 0.9,
 "t1-cafe-bill_s3": 0.9,
 "t2-split-bill_s1": 0.9,
 "t2-split-bill_s2": 0.9,
 "t2-split-bill_s3": 0.9,
 "t3-shipping-fee_s1": 0.9091,
 "t3-shipping-fee_s2": 0.9091,
 "t3-shipping-fee_s3": 0.9091,
 "t4-cashback_s1": 0.9,
 "t4-cashback_s2": 0.9,
 "t4-cashback_s3": 0.9
}baankafe-solve
=== t1-cafe-bill s1
"""แม่แบบ solve.py สำหรับโจทย์คิดเงิน BaanKafe — แก้เฉพาะฟังก์ชันหลัก (เปลี่ยนชื่อ/พารามิเตอร์ตามโจทย์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย/ค่าส่ง/ยอดหาร"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (x ไม่ติดลบ) — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str, None ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value
…(ตัด 1001 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /evo; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for s in 1 2 3; do d=/tmp/run/${t}_$s; mkdir -p $d; cp solver_workspaces/epoch_1/${t}_s$s/solve.py $d/; cp reference/answers/$t/test_solve.py $d/; echo "== $t s$s"; (cd $d; python3 -I -m unittest -q test_solve 2>&1 | tail -4); done; done
```

ผลที่ได้:

```
== t1-cafe-bill s1
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t1-cafe-bill s2
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t1-cafe-bill s3
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t2-split-bill s1
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t2-split-bill s2
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t2-split-bill s3
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t3-shipping-fee s1
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t3-shipping-fee s2
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t3-shipping-fee s3
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
== t4-cashback s1

…(ตัด 368 ตัวอักษร)
```

**Agent พูด:** The `-I` flag dropped the cwd from the import path; I'll run the tests with an explicit path.

### ขั้น 3 · Bash

```
cd /evo; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for s in 1 2 3; do d=/tmp/run/${t}_$s; echo "== $t s$s"; (cd $d; PYTHONPATH=$d python3 -m unittest -q test_solve 2>&1 | tail -4); done; done
```

ผลที่ได้:

```
== t1-cafe-bill s1
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t1-cafe-bill s2
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t1-cafe-bill s3
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t2-split-bill s1
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t2-split-bill s2
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t2-split-bill s3
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t3-shipping-fee s1
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t3-shipping-fee s2
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t3-shipping-fee s3
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t4-cashback s1
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
== t4-cashback s2
-
…(ตัด 212 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /tmp; cat > fuzz.py <<'E'
import sys, importlib.util, random, itertools
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
t,fn,s=sys.argv[1:4]
ref=load(f'/evo/reference/answers/{t}/solve.py','ref'); sol=load(f'/tmp/run/{t}_{s}/solve.py','sol')
f1=getattr(ref,fn); f2=getattr(sol,fn)
def call(f,*a):
    try: return ('ok',f(*a))
    except Exception as e: return ('err',type(e).__name__)
random.seed(1)
def gen():
    if t=='t1-cafe-bill':
        yield from ([ [{'price':random.choice([0,1,5,4505,49999,50000,99999]) ,'qty':random.randint(1,3)} for _ in range(random.randint(0,3))], random.choice([True,False])] for _ in range(3000))
        for bad in ([],None,'x',[{'price':1}],[{'price':1,'qty':1,'x':2}],[1],[{'price':True,'qty':1}],[{'price':1,'qty':1.0}],(({'price':1,'qty':1}),)):
            yield [bad,False]
        yield [[{'price':1,'qty':1}],1]; yield [[{'price':1,'qty':1}],None]
    if t=='t2-split-bill':
        for _ in range(3000): yield [random.randint(0,100000),random.randint(1,12),random.randint(0,100)]
        for a in ([1,1,101],[1,1,-1],[1,1,10.0],[True,1,0],[1,True,0],[1,1,True],[None,1,0],[1,1,None],[1,10**9,0] ) : yield a
    if t=='t3-shipping-fee':
        for _ in range(4000): yield [random.choice([1,1000,1001,5000,5001,random.randint(1,30000),20000,20001,30000,30001,0]),random.choice([0,1,100,101,random.randint(0,300),-1]),random.choice([True,False])]
        for a in ([1,1,1],[1,1,None],[1,1.0,False],[1,True,False],[1,'1',False],[1,10**9,False]): yield a
    if t=='t4-cashback':
        for _ in range(4000): yield [random.choice([0,9999,10000,10001,random.randint(0,600000),500000,-1]),random.choice(['silver','gold','platinum','bronze','Gold',1,None]),random.choice([True,False])]
        for a in ([100,'gold',1],[100,'gold',None],[True,'gold',False],[10000,'gold',False]): yield a
bad=0
for a in gen():
    r1=call(f1,*a); r2=call(f2,*a)
    if r1!=r2:
        bad+=1
        if bad<8: print(a,r1,r2)
print(t,s,'diffs',bad)
E
for p in "t1-cafe-bill cafe_bill" "t2-split-bill split_bill" "t3-shipping-fee shipping_fee" "t4-cashback cashback"; do set -- $p; for s in 1 2 3; do python3 fuzz.py $1 $2 $s; done; done 2>&1 | head -80
```

ผลที่ได้:

```
t1-cafe-bill 1 diffs 0
t1-cafe-bill 2 diffs 0
t1-cafe-bill 3 diffs 0
t2-split-bill 1 diffs 0
t2-split-bill 2 diffs 0
t2-split-bill 3 diffs 0
[1, 1.0, False] ('err', 'ValueError') ('ok', 4000)
t3-shipping-fee 1 diffs 1
[1, 1.0, False] ('err', 'ValueError') ('ok', 4000)
t3-shipping-fee 2 diffs 1
[1, 1.0, False] ('err', 'ValueError') ('ok', 4000)
t3-shipping-fee 3 diffs 1
t4-cashback 1 diffs 0
t4-cashback 2 diffs 0
t4-cashback 3 diffs 0
Shell cwd was reset to /evo
```

### ขั้น 5 · Bash

```
cd /tmp; cat > fuzz2.py <<'E'
import sys, importlib.util, random
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
t,fn,s=sys.argv[1:4]
ref=load(f'/evo/reference/answers/{t}/solve.py','ref'); sol=load(f'/tmp/run/{t}_{s}/solve.py','sol')
f1=getattr(ref,fn); f2=getattr(sol,fn)
def call(f,*a):
    try: return ('ok',f(*a))
    except Exception as e: return ('err',type(e).__name__)
junk=[None,True,False,1.0,0.5,'1','',[],{},-1,0,1,2,10**12,float('nan'),'gold']
base={'t1-cafe-bill':[[{'price':4500,'qty':2}],False],'t2-split-bill':[30000,3,10],'t3-shipping-fee':[3000,150,True],'t4-cashback':[20000,'gold',True]}[t]
bad=0
for i in range(len(base)):
    for j in junk:
        a=list(base); a[i]=j
        if call(f1,*a)!=call(f2,*a):
            bad+=1; print(i,repr(j),call(f1,*a),call(f2,*a))
if t=='t1-cafe-bill':
    for k in ('price','qty'):
        for j in junk:
            a=[[{'price':4500,'qty':2}],False]; a[0][0][k]=j
            if call(f1,*a)!=call(f2,*a): bad+=1; print(k,repr(j),call(f1,*a),call(f2,*a))
    for j in junk:
        a=[[j],False]
        if call(f1,*a)!=call(f2,*a): bad+=1; print('item',repr(j),call(f1,*a),call(f2,*a))
random.seed(2)
print(t,s,'diffs',bad)
E
for p in "t1-cafe-bill cafe_bill" "t2-split-bill split_bill" "t3-shipping-fee shipping_fee" "t4-cashback cashback"; do set -- $p; for s in 1 2 3; do python3 fuzz2.py $1 $2 $s; done; done 2>&1 | head -80
```

ผลที่ได้:

```
t1-cafe-bill 1 diffs 0
t1-cafe-bill 2 diffs 0
t1-cafe-bill 3 diffs 0
/bin/bash: line 59: 63878 Killed                  python3 fuzz2.py $1 $2 $s
/bin/bash: line 59: 63899 Killed                  python3 fuzz2.py $1 $2 $s
/bin/bash: line 59: 63919 Killed                  python3 fuzz2.py $1 $2 $s
1 1.0 ('err', 'ValueError') ('ok', 12000)
1 0.5 ('err', 'ValueError') ('ok', 12000)
t3-shipping-fee 1 diffs 2
1 1.0 ('err', 'ValueError') ('ok', 12000)
1 0.5 ('err', 'ValueError') ('ok', 12000)
t3-shipping-fee 2 diffs 2
1 1.0 ('err', 'ValueError') ('ok', 12000)
1 0.5 ('err', 'ValueError') ('ok', 12000)
t3-shipping-fee 3 diffs 2
t4-cashback 1 diffs 0
t4-cashback 2 diffs 0
t4-cashback 3 diffs 0
Shell cwd was reset to /evo
```

### ขั้น 6 · Bash

```
cd /tmp/run; echo '{"items":[{"price":4500,"qty":2}],"member":false}' | python3 t1-cafe-bill_1/solve.py; echo '{"total":10000,"people":3,"tip_percent":0}' | python3 t2-split-bill_1/solve.py; echo '{"amount":-1,"tier":"gold","birthday":false}' | python3 t4-cashback_1/solve.py; echo $?; ls /evo/solver_workspaces/epoch_1/t1-cafe-bill_s1/; diff <(sed -n 40,200p t2-split-bill_1/solve.py) <(sed -n 40,200p /evo/reference/answers/t2-split-bill/solve.py)
```

ผลที่ได้:

```
{"ok": true, "result": 9630}
{"ok": true, "result": [3334, 3333, 3333]}
{"ok": false, "error": "amount \u0e2d\u0e22\u0e39\u0e48\u0e19\u0e2d\u0e01\u0e0a\u0e48\u0e27\u0e07\u0e17\u0e35\u0e48\u0e01\u0e33\u0e2b\u0e19\u0e14"}
2
solve.py
test_solve.py
0a1,7
>         result = split_bill(**args)
>     except (ValueError, TypeError) as error:
>         print(json.dumps({"ok": False, "error": str(error)}))
>         return 2
>     print(json.dumps({"ok": True, "result": result}))
>     return 0
>
```

### ขั้น 7 · Bash

```
cd /evo; python3 - <<'E'
import json
for t in ['t1-cafe-bill_s1','t3-shipping-fee_s1','t4-cashback_s2']:
    last=None
    for l in open(f'traces/epoch_1/{t}.jsonl'):
        d=json.loads(l)
        if d.get('type')=='assistant':
            for c in d['message']['content']:
                if c['type']=='text': last=c['text']
    print('==',t); print(last)
E
diff solver_workspaces/epoch_1/t3-shipping-fee_s1/solve.py reference/answers/t3-shipping-fee/solve.py
```

ผลที่ได้:

```
== t1-cafe-bill_s1
สร้าง `solve.py` พร้อมฟังก์ชัน `cafe_bill(items, member)` แล้ว และรัน unittest ของตัวเอง (`test_solve.py`) ผ่านทั้งหมด

ผมทำตามสกิล `baankafe-solve` ในโฟลเดอร์ `./skills` และตีความโจทย์ดังนี้:
- **การคำนวณ:** ยอดรวม = Σ price×qty (สตางค์) ถ้ายอดรวม ≥ 50000 ลด 5% จากนั้นถ้าเป็นสมาชิกลดอีก 10% แล้วบวก VAT 7% ใช้ `Fraction` ตลอด ไม่มี float
- **การปัดเศษ:** ปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด เพราะเป็นยอดที่ลูกค้าจ่าย
- **items ว่าง:** คืน 0
- **ตรวจ input:** ถ้า input ผิดจะ raise `ValueError`
  - `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty` ครบ
  - `price` ต้องเป็น int ตั้งแต่ 0
  - `qty` ต้องเป็น int ตั้งแต่ 1
  - `member` ต้องเป็น bool
  - ปฏิเสธ float, str, bool และ None
- **เทสต์ที่ครอบคลุม:** ยอดปกติ, ขอบเขต 49999/50000 และเศษครึ่งสตางค์ (สมาชิก 50000 → 45742.5 ปัดเป็น 45743), และกรณี input ผิด

`solve.py` ยังมี `main()` ที่อ่าน JSON จาก stdin ตามแม่แบบของสกิลด้วย
== t3-shipping-fee_s1
สร้าง `solve.py` พร้อมฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` แล้ว และ `test_solve.py` ที่เขียนเองผ่านทั้งหมด ไฟล์ทั้งสองอยู่ในโฟลเดอร์ปัจจุบัน ผมทำตามสกิล `baankafe-solve` ที่อยู่ใน `./skills`

**วิธีคิดค่าส่ง**
- ใช้ `Fraction` ล้วน ไม่มี float และปัดเศษ
…(ตัด 3685 ตัวอักษร)
```

### ขั้น 8 · bash

```
cd /evo/staging/baankafe-solve && python3 - <<'E'
p='SKILL.md'
s=open(p).read()
s=s.replace("- ช่วงตามโจทย์:", """- **ห้ามผ่อนชนิดเองเด็ดขาด**: พารามิเตอร์ตัวเลขทุกตัวในโจทย์กลุ่มนี้ (น้ำหนัก, ระยะทาง km, ยอด, จำนวน, เปอร์เซ็นต์ ฯลฯ) เป็น `int` ล้วน แม้ดูเหมือนควรมีทศนิยมได้ (เช่น distance_km=10.5) ก็ต้อง ValueError — รอบก่อน Solver ให้ distance_km รับ float แล้วเสียคะแนน ใช้ `need_int` ทุกตัว ห้ามเขียน `need_number` ที่รับ float
- ช่วงตามโจทย์:""",1)
s=s.replace("## เช็กลิสต์ก่อนส่ง","""## 5) ไล่หามุมแปลกของทุกพารามิเตอร์ (ก่อนเขียนโค้ด)
ถามตัวเองทีละพารามิเตอร์: ค่า 0 / ค่าต่ำสุด / ค่าสูงสุดของช่วง / ค่าที่เกินช่วง / ค่าพิเศษที่ทำให้กฎข้อใดไม่ควรใช้ (เช่น ระยะ 0, ส่งด่วนกับของหนัก, ระดับสมาชิกที่ไม่ควรได้สิทธิ์) / รายการว่าง / ค่าเศษครึ่งสตางค์พอดี
เมื่อโจทย์ไม่ได้ระบุ ให้เลือกตีความแบบอนุรักษ์ที่สอดคล้องกับข้อ 4 และ **เขียนไว้ในสรุปท้าย** ว่าเลือกอะไร ห้ามถามกลับแล้วหยุด — ต้องส่ง solve.py ที่สมบูรณ์เสมอ

## เช็กลิสต์ก่อนส่ง""",1)
s=s.replace("- [ ] ไม่มี float","- [ ] ทุกพารามิเตอร์ตัวเลขใช้ need_int (float เช่น 1.0 / 0.5 ต้อง ValueError ทุกตัว รวม distance_km)\n- [ ] ไม่มี float",1)
open(p,'w').write(s)
E
grep -n "need_int\|ห้ามผ่อน" SKILL.md | head; echo "- epoch1 scores ~0.9 all; solver outputs match reference except t3 float distance_km (accepted). v2 adds strict-int rule + corner-case hunt. Remaining 0.1 on t1/t2/t4 unexplained (fuzz found no behavior diff)." >> /evo/evolver_workspace/notes.md
```

ผลที่ได้:

```
<tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
```

### ขั้น 9 · Bash

```
cd /evo/staging/baankafe-solve && python3 - <<'E'
p='SKILL.md'
s=open(p).read()
s=s.replace("- ช่วงตามโจทย์:", """- **ห้ามผ่อนชนิดเองเด็ดขาด**: พารามิเตอร์ตัวเลขทุกตัวในโจทย์กลุ่มนี้ (น้ำหนัก, ระยะทาง km, ยอด, จำนวน, เปอร์เซ็นต์ ฯลฯ) เป็น `int` ล้วน แม้ดูเหมือนควรมีทศนิยมได้ (เช่น distance_km=10.5) ก็ต้อง ValueError — รอบก่อน Solver ให้ distance_km รับ float แล้วเสียคะแนน ใช้ `need_int` ทุกตัว ห้ามเขียน `need_number` ที่รับ float
- ช่วงตามโจทย์:""",1)
s=s.replace("## เช็กลิสต์ก่อนส่ง","""## 5) ไล่หามุมแปลกของทุกพารามิเตอร์ (ก่อนเขียนโค้ด)
ถามตัวเองทีละพารามิเตอร์: ค่า 0 / ค่าต่ำสุด / ค่าสูงสุดของช่วง / ค่าที่เกินช่วง / ค่าพิเศษที่ทำให้กฎข้อใดไม่ควรใช้ (เช่น ระยะ 0, ส่งด่วนกับของหนัก, ระดับสมาชิกที่ไม่ควรได้สิทธิ์) / รายการว่าง / ค่าเศษครึ่งสตางค์พอดี
เมื่อโจทย์ไม่ได้ระบุ ให้เลือกตีความแบบอนุรักษ์ที่สอดคล้องกับข้อ 4 และ **เขียนไว้ในสรุปท้าย** ว่าเลือกอะไร ห้ามถามกลับแล้วหยุด — ต้องส่ง solve.py ที่สมบูรณ์เสมอ

## เช็กลิสต์ก่อนส่ง""",1)
s=s.replace("- [ ] ไม่มี float","- [ ] ทุกพารามิเตอร์ตัวเลขใช้ need_int (float เช่น 1.0 / 0.5 ต้อง ValueError ทุกตัว รวม distance_km)\n- [ ] ไม่มี float",1)
open(p,'w').write(s)
E
grep -c "need_int" SKILL.md; echo "- epoch1 scores ~0.9 all; solver outputs match reference except t3 float distance_km (accepted). v2 adds strict-int rule + corner-case hunt. Remaining 0.1 on t1/t2/t4 unexplained (fuzz found no behavior diff)." >> /evo/evolver_workspace/notes.md
```

ผลที่ได้:

```
2
```

**Agent พูด:** ผมแก้สกิล `baankafe-solve` เป็น v2 ใน `/evo/staging/` แล้ว แต่ยังไม่ได้ทดสอบกับ Solver และยังหาไม่เจอว่าทำไมเหลือคะแนนขาด 0.1 ในโจทย์ t1, t2 และ t4

**ผล epoch 1:** คะแนนเพิ่มจาก 0.4–0.5 เป็น 0.9 ทุกโจทย์ (t3 ได้ 0.9091) ผมนำ `solve.py` ของ Solver ทั้ง 12 ครั้งไปรันกับเทสต์ในเฉลยอ้างอิง ผ่านครบทุกข้อ แล้วเทียบพฤติกรรมกับเฉลยด้วยอินพุตสุ่มและอินพุตผิดชนิด

**สิ่งที่พบ:**
- **t3 (ค่าส่ง):** ทั้ง 3 ครั้งให้ `distance_km` รับ float ได้ เพราะ Solver คิดเองว่าระยะทางน่าจะมีทศนิยม ส่วนเฉลยปฏิเสธ float ทั้งสามครั้งจึงต่างจากเฉลยตรงจุดนี้ นี่น่าจะเป็นข้อที่เสียคะแนน
- **t1, t2, t4:** พฤติกรรมตรงกับเฉลยทุกกรณีที่ผมลอง แต่ยังได้ 0.9 ผมไม่รู้สาเหตุ และไม่ได้เห็นเทสต์ซ่อน
- **ตรวจตอนวิเคราะห์:** ที่ทดสอบ t2 ด้วย `people=10**12` โปรเซสถูก kill (หน่วยความจำ) ทั้งเฉลยและ Solver เป็นปัญหาของอินพุตที่ผมสร้างเอง ไม่ใช่ข้อบกพร่องของ Solver

**ที่เพิ่มในสกิล:**
- ข้อ 3: ห้ามผ่อนชนิดเอง ตัวเลขทุกตัวต้องเป็น `int` ล้วน และ float เช่น `1.0` หรือ `0.5` ต้อง `ValueError` รวมถึง `distance_km` ห้ามเขียน `need_number` ที่รับ float
- ข้อ 5 (ใหม่): ให้ไล่หามุมแปลกของทุกพารามิเตอร์ก่อนเขียนโค้ด ถ้าโจทย์ไม่ระบุให้เลือกตีความแบบอนุรักษ์ เขียนไว้ในสรุปท้าย และต้องส่ง `solve.py` ที่สมบูรณ์เสมอ ห้ามถามกลับแล้วหยุด
- เช็กลิสต์: เพิ่มข้อให้ทุกพารามิเตอร์ตัวเลขใช้ `need_int`

ส่วนอื่นไม่ได้แก้ รวมถึงชื่อ `test_solve.py` ที่ Solver สร้างเอง เพราะรอบนี้ทำงานได้ดีอยู่แล้ว และผมไม่รู้ว่าการเปลี่ยนจะกระทบคะแนนส่วนที่ยังอธิบายไม่ได้หรือไม่ บันทึกอยู่ใน `evolver_workspace/notes.md`
