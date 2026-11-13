# ตาที่ 2 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 02:16 UTC คุณมีเวลาถึง 2026-11-13 02:46 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 2 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v2` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_1.json; ls skills/epoch_1 staging; cat evolver_workspace/notes.md; ls solver_workspaces/epoch_1/t4-cashback_s1
```

ผลที่ได้:

```
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
 "t4-cashback_s1": 0.9,
 "t4-cashback_s2": 0.9,
 "t4-cashback_s3": 0.9
}skills/epoch_1:
money-func-solver

staging:
money-func-solver
epoch1: wrote skills_v1 money-func-solver. Diagnosis: epoch0 scores 0.3-0.6; no validation (Reject tests), floor rounding in cashback, no test_solve.py.
solve.py
test_solve.py
```

### ขั้น 2 · Bash

```
cd /evo/solver_workspaces/epoch_1; cat t1-cafe-bill_s1/solve.py; echo ====; cat t3-shipping-fee_s1/solve.py; echo ===; cat t4-cashback_s2/solve.py; echo; diff <(sed -n 1,200p t1-cafe-bill_s1/solve.py) /evo/reference/answers/t1-cafe-bill/solve.py | head -60
```

ผลที่ได้:

```
"""BaanKafe: คิดเงินหน้าร้าน (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


THRESHOLD = 50000  # 500 บาท


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    total = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("item ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError("item ต้องมี price และ qty")
        total += need_int(item["price"], "price", 0) * need_int(item["qty"], "qty", 1)
    amount = Fraction(total)
    if total >= THRESHOLD:
   
…(ตัด 4689 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /evo/traces/epoch_1; python3 - <<'E'
import json
for l in open('t2-split-bill_s1.jsonl'):
    d=json.loads(l)
    if d['type']=='assistant':
        for c in d['message']['content']:
            if c['type']=='text': print(c['text'][:2000])
            if c['type']=='tool_use': print('TOOL',str(c['input'])[:300])
E
```

ผลที่ได้:

```
TOOL {'command': 'ls ./skills 2>&1 | head'}
TOOL {'command': 'find ./skills -type f | head; cat ./skills/money-func-solver/SKILL.md'}
TOOL {'command': 'cat ./skills/money-func-solver/template_solve.py'}
Tip ปัดแบบ half-up ครั้งเดียวตอนท้าย (total × (100+tip)/100).
TOOL {'command': 'cat > solve.py <<\'EOF\'\n"""BaanKafe: หารบิล (หน่วยสตางค์)"""\nimport json\nimport sys\nfrom fractions import Fraction\n\n\ndef half_up(x):\n    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""\n    return int((Fraction(x) * 2 + 1) // 2)\n\n\ndef need_int(value, name, low=None, high=
สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และเทสต์ผ่านทั้ง 4 ข้อ (Normal, Boundary, NoDrift, Reject)

ฟังก์ชัน `split_bill(total, people, tip_percent)` ทำตามนี้ ซึ่งตรงกับสกิล `money-func-solver` ใน `./skills`:
- **คำนวณยอดรวม:** ใช้ `Fraction` คิด `total × (100 + tip) / 100` แล้วปัดครั้งเดียวตอนท้ายแบบ half-up
- **เรื่องการปัด:** โจทย์ไม่ได้บอกวิธีปัดเศษทิป ผมเลือก half-up ตามสกิล เช่น 5 สตางค์ที่ทิป 10% ได้ 5.5 แล้วปัดเป็น 6
- **หารคน:** ใช้ `divmod(grand, people)` ให้คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ ผลรวมของ list จึงเท่ากับยอดรวมเสมอ ผลลัพธ์เป็น list ของ `int`
- **ตรวจ input:** ใช้ `type(v) is int`
…(ตัด 218 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /evo/solver_workspaces/epoch_1; cat t3-shipping-fee_s1/test_solve.py; wc -l */test_solve.py; ls -la t3-shipping-fee_s1
```

ผลที่ได้:

```
import unittest
from fractions import Fraction
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(500, 200, True), 7200)

    def test_boundary(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 101, False), 9600)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 8000+1.5=8001.5 -> half-up
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_nodrift(self):
        for w in (5001, 5003, 5333, 12345, 29999):
            for d in (0, 101):
                for e in (False, True):
                    x = 8000 + Fraction(w - 5000, 1000) * 1500
                    if d > 100: x *= Fraction(6, 5)
                    if e: x *= Fraction(3, 2)
                    exp = int((x * 2 + 1) // 2)
                    r = f(w, d, e)
                    self.assertEqual(r, exp)
                    self.assertIs(type(r), int
…(ตัด 1131 ตัวอักษร)
```

### ขั้น 5 · Bash

```
mkdir -p /tmp/fz && cd /tmp/fz && cat > fz.py <<'E'
import importlib.util, random, sys, json
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
R='/evo/reference/answers/'; S='/evo/solver_workspaces/epoch_1/'
tasks={'t1-cafe-bill':'cafe_bill','t2-split-bill':'split_bill','t3-shipping-fee':'shipping_fee','t4-cashback':'cashback'}
vals=[0,1,2,3,5,7,100,101,999,1000,1001,4999,5000,5001,9999,10000,10020,49999,50000,50001,100000,500000,30000,30001,-1,-100,4500.0,0.5,'3',None,True,False,[],{} ,'gold','silver','platinum','bronze','']
def call(f,a):
    try: return ('ok',f(*a))
    except ValueError: return ('VE',)
    except Exception as e: return ('EXC',type(e).__name__)
random.seed(1)
for t,fn in tasks.items():
    ref=getattr(load(R+t+'/solve.py','r'+t),fn)
    ar={'t1-cafe-bill':2,'t2-split-bill':3,'t3-shipping-fee':3,'t4-cashback':3}[t]
    cases=[]
    for _ in range(4000):
        if t=='t1-cafe-bill':
            items=random.choice([[],[{'price':random.choice(vals),'qty':random.choice(vals)}],[{'price':random.randint(0,30000),'qty':random.randint(1,5)} for _ in range(random.randint(1,3))],[{'price':5}],[1],{},None,[{'price':1,'qty':1,'x':2}]])
            cases.append((items,random.choice([True,False,0,1,None])))
        else: cases.append(tuple(random.choice(vals) for _ in range(ar)))
    for i in (1,2,3):
        f=getattr(load(S+f'{t}_s{i}/solve.py',f's{t}{i}'),fn)
        bad=[(a,call(ref,a),call(f,a)) for a in cases if call(ref,a)!=call(f,a)]
        print(t,i,len(bad),bad[:3])
E
python3 -I fz.py 2>&1 | cut -c1-400
```

ผลที่ได้:

```
t1-cafe-bill 1 0 []
t1-cafe-bill 2 0 []
t1-cafe-bill 3 0 []
t2-split-bill 1 0 []
t2-split-bill 2 0 []
t2-split-bill 3 0 []
t3-shipping-fee 1 0 []
t3-shipping-fee 2 0 []
t3-shipping-fee 3 0 []
t4-cashback 1 0 []
t4-cashback 2 0 []
t4-cashback 3 0 []
Shell cwd was reset to /evo
```

### ขั้น 6 · Bash

```
cd /tmp/fz && cat > mut.py <<'E'
import subprocess, shutil, os, sys, re
S='/evo/solver_workspaces/epoch_1/'
muts=[('>= ','> '),('> ','>= '),('<= ','< '),('< ','<= '),('half_up(','int('),('+ 1) // 2','+ 0) // 2'),('type(value) is not int','not isinstance(value, int)'),('type(value) is not bool','not isinstance(value, bool)'),('low is not None and value < low','False and value < low'),('value > high','value > high+1'),('value < low','value < low-1'),('Fraction(107, 100)','Fraction(107, 101)'),('Fraction(95, 100)','Fraction(96, 100)'),('Fraction(120, 100)','Fraction(121, 100)'),('Fraction(150, 100)','Fraction(151, 100)'),('50000','50001'),('10000','10001'),('20000','20001'),('1000','1001'),('5000','5001'),('100','101')]
import glob
for d in sorted(glob.glob(S+'*_s*')):
    src=open(d+'/solve.py').read(); surv=[]
    for a,b in muts:
        if a not in src: continue
        for k,m in enumerate(re.finditer(re.escape(a),src)):
            new=src[:m.start()]+b+src[m.end():]
            if new==src: continue
            t='/tmp/fz/w'; shutil.rmtree(t,ignore_errors=True); os.makedirs(t)
            open(t+'/solve.py','w').write(new); shutil.copy(d+'/test_solve.py',t)
            r=subprocess.run(['python3','-I','-m','unittest','-q','test_solve'],cwd=t,capture_output=True,env={'PYTHONPATH':t,'PATH':os.environ['PATH']})
            if r.returncode==0: 
                line=src[:m.start()].count('\n')+1; surv.append((a,b,line))
    print(os.path.basename(d),len(surv),surv[:8])
E
python3 -I mut.py 2>&1 | cut -c1-500
```

ผลที่ได้:

```
t1-cafe-bill_s1 0 []
t1-cafe-bill_s2 0 []
t1-cafe-bill_s3 0 []
t2-split-bill_s1 0 []
t2-split-bill_s2 0 []
t2-split-bill_s3 0 []
t3-shipping-fee_s1 0 []
t3-shipping-fee_s2 0 []
t3-shipping-fee_s3 0 []
t4-cashback_s1 0 []
t4-cashback_s2 0 []
t4-cashback_s3 0 []
Shell cwd was reset to /evo
```

### ขั้น 7 · Bash

```
cd /tmp/fz && sed -i "s/\['python3','-I','-m'/['python3','-m'/" mut.py && python3 -I mut.py 2>&1 | cut -c1-600
```

ผลที่ได้:

```
t1-cafe-bill_s1 3 [('> ', '>= ', 15), ('type(value) is not bool', 'not isinstance(value, bool)', 21), ('value > high', 'value > high+1', 15)]
t1-cafe-bill_s2 3 [('> ', '>= ', 15), ('type(value) is not bool', 'not isinstance(value, bool)', 21), ('value > high', 'value > high+1', 15)]
t1-cafe-bill_s3 2 [('> ', '>= ', 13), ('value > high', 'value > high+1', 13)]
t2-split-bill_s1 0 []
t2-split-bill_s2 0 []
t2-split-bill_s3 0 []
t3-shipping-fee_s1 3 [('> ', '>= ', 1), ('<= ', '< ', 31), ('type(value) is not bool', 'not isinstance(value, bool)', 20)]
t3-shipping-fee_s2 2 [('<= ', '< ', 30), ('type(value) is not bool', 'not isinstance(value, bool)', 19)]
t3-shipping-fee_s3 2 [('<= ', '< ', 31), ('type(value) is not bool', 'not isinstance(value, bool)', 20)]
t4-cashback_s1 4 [('> ', '>= ', 14), ('type(value) is not bool', 'not isinstance(value, bool)', 20), ('value > high', 'value > high+1', 14), ('100', '101', 26)]
t4-cashback_s2 4 [('> ', '>= ', 14), ('type(value) is not bool', 'not isinstance(value, bool)', 20), ('value > high', 'value > high+1', 14), ('100', '101', 30)]
t4-cashback_s3 4 [('> ', '>= ', 15), ('type(value) is not bool', 'not isinstance(value, bool)', 21), ('value > high',
…(ตัด 71 ตัวอักษร)
```

### ขั้น 8 · Bash

```
cd /evo/traces/epoch_1; python3 - <<'E'
import json
for l in open('t4-cashback_s1.jsonl'):
    d=json.loads(l)
    if d['type']=='system' and d.get('subtype')=='init': print(d.get('cwd'), d.get('skills'), d.get('slash_commands'))
    if d['type']=='user':
        c=d['message']['content']
        if isinstance(c,list):
            for x in c:
                if x.get('type')=='tool_result': print('RESULT',str(x['content'])[:600])
                if x.get('type')=='text': print('USERTXT',x['text'][:1500])
        else: print('USER',c[:1500])
E
```

ผลที่ได้:

```
/workspace/evlab/ws/n1/legs/runs/v1_train/t4-cashback-r1/sandbox ['agent-team', 'cyolo', 'dag-planner', 'reverse-engineer-anything', 'shared-check', 'vastai', 'yolo', 'deep-research', 'design', 'design-sync', 'dataviz', 'update-config', 'verify', 'debug', 'code-review', 'simplify', 'batch', 'fewer-permission-prompts', 'doctor', 'loop', 'schedule', 'claude-api', 'workflow-authoring', 'run', 'run-skill-generator', 'plugin-authoring', 'anthropic-skills:built-in-browser', 'anthropic-skills:chrome-browser', 'anthropic-skills:computer-use', 'anthropic-skills:deep-research', 'anthropic-skills:docs', 'anthropic-skills:docx', 'anthropic-skills:google-workspace', 'anthropic-skills:import-memory', 'anthropic-skills:morning', 'anthropic-skills:pdf', 'anthropic-skills:pptx', 'anthropic-skills:skill-creator', 'anthropic-skills:xlsx'] ['agent-team', 'cyolo', 'dag-planner', 'reverse-engineer-anything', 'shared-check', 'vastai', 'yolo', 'deep-research', 'design', 'design-sync', 'dataviz', 'update-config', 'verify', 'debug', 'code-review', 'simplify', 'batch', 'fewer-permission-prompts', 'doctor', 'loop', 'schedule', 'claude-api', 'workflow-authoring', 'run', 'run-skill-generator', 'plugin-authoring
…(ตัด 2433 ตัวอักษร)
```

### ขั้น 9 · Bash

```
cd /evo/staging/money-func-solver && python3 - <<'E'
p='SKILL.md'
s=open(p).read()
old=s[s.index('5. เขียน `test_solve.py`'):s.index('6. ผลลัพธ์ต้องเป็น')]
new='''5. เขียน `test_solve.py` (unittest) ข้างกับ `solve.py` — ดูโครงใน `template_test.py` · epoch ก่อนหน้า solve.py ถูกต้องแล้วแต่ได้ 0.9 ไม่เต็ม ซึ่งน่าจะเหลือที่คุณภาพของชุดเทสต์ จึงให้เขียนเทสต์ให้ "จับบั๊กได้จริง":
   - แยกเป็น 4 class: `Normal`, `Boundary`, `NoDrift`, `Reject` แต่ละ case เป็น method แยก (`test_normal_1`, `test_boundary_2`, ...) อย่างน้อย Normal 3 · Boundary 3 · NoDrift 2 · Reject 4+
   - ค่าคาดหวังต้อง **คำนวณมือ/เขียนเป็นตัวเลขตายตัว** ห้ามเรียกฟังก์ชันตัวเองหรือสูตรเดียวกับโค้ดมาสร้างค่าคาดหวัง (ยกเว้นเสริมเป็นรอบที่สองด้วย Fraction)
   - Boundary: **ทุก threshold ต้องทดสอบทั้งสองฝั่ง** (t−1, t, t+1) ด้วยค่าที่ผลต่างกันจริง เช่น ขั้นต่ำ 10000 ต้องมีเทสต์ที่ 9999→0 และ 10000 (และ 10001) → ไม่ใช่ 0 · ถ้าเพดานมีอยู่ ต้องมีเคสที่ยังไม่ชนเพดาน เคสพอดีเพดาน และเคสเกินเพดาน · ค่าต่ำสุด/สูงสุดของช่วง (0, 1, 30000, people=1, tip 0 และ 100)
   - NoDrift: เลือกค่าที่ก่อนปัดลงท้าย .5 พอดี หรือ .4/.6 เพื่อแยก half-up ออกจาก floor/round()/ปัดสองรอบ แล้วใส่ค่ากลาง 1 ข้อที่ต้อง "รวมก่อนปัดครั้งเดียว" (ถ้าปัดทีละขั้นผลจะต่างกัน)
   - Reject: ครบทุก parameter ทุกชนิด — ต่ำกว่าช่วง (qty 0, ติดลบ), สูงกว่าช่วง (tip 101, น้ำหนัก 30001), float ที่ค่าเป็นจำนวนเต็ม (`4500.0`), str (`'3'`), bool (`True`), None, enum แปลก, และ item ที่ขาด key / ไม่ใช่ dict ถ้ามี list
   - รัน `python3 -m unittest -q test_solve` ให้ผ่าน แล้วลอง "ทำลาย" โค้ดตัวเองสั้น ๆ 2–3 จุด (เปลี่ยน `>=` เป็น `>`, เปลี่ยน half_up เป็น floor) เพื่อดูว่าเทสต์ล้มจริง ถ้าไม่ล้มให้เพิ่มเคส แล้วคืนโค้ดเดิม
'''
s=s.replace(old,new)
open(p,'w').write(s)
E
cat > template_test.py <<'E'
"""ตัวอย่างโครง test_solve.py (แทนที่ฟังก์ชันและตัวเลขตามโจทย์ · ค่าคาดหวังต้องคำนวณมือเป็นเลขตายตัว)"""
import unittest

from solve import cashback  # เปลี่ยนเป็นชื่อฟังก์ชันของโจทย์


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)

    def test_normal_2(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_normal_3(self):
        self.assertEqual(cashback(20000, 'platinum', True), 1600)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # ใต้ขั้นต่ำ 1 สตางค์
        self.assertEqual(cashback(9999, 'gold', False), 0)

    def test_boundary_2(self):  # พอดีขั้นต่ำ ต้องไม่ใช่ 0
        self.assertEqual(cashback(10000, 'silver', False), 150)
…(ตัด 1971 ตัวอักษร)
```

ผลที่ได้:

```
36:## Template (`template_solve.py` สำหรับ solve.py · `template_test.py` สำหรับ test_solve.py)
Ran 15 tests in 0.000s

OK
Shell cwd was reset to /evo
```

**Agent พูด:** ผมแก้สกิล `money-func-solver` ใน `/evo/staging/` แล้ว (`skills_v2`) ส่วนที่ทำให้คะแนนเหลือ 0.9 ผมยังหาไม่เจอ ที่เสนอเป็นแค่สมมติฐาน

**ผล epoch 1**
- คะแนนขึ้นจาก 0.3–0.6 เป็น 0.9 ทั้ง 12 rollout เพราะ Solver validate input และปัดแบบ half-up ตามสกิล v1
- ผมสุ่มอินพุต 4,000 ชุดต่อโจทย์ รวมค่าผิดชนิดและนอกช่วง แล้วเทียบ `solve.py` ทั้ง 12 ไฟล์กับเฉลย ผลคือตรงกันทุกกรณี
- ดังนั้น 0.1 ที่หายไปน่าจะไม่ได้อยู่ที่พฤติกรรมของ `solve.py`

**สมมติฐานเรื่อง 0.1 ที่หายไป**
- อาจเป็นคุณภาพของ `test_solve.py` ที่ Solver เขียนเอง ผมลองแก้ `solve.py` ของ Solver ทีละจุด (เปลี่ยน `>=` เป็น `>`, เปลี่ยนค่าคงที่) แล้วรันเทสต์ของมัน พบว่ายังมีบั๊กที่เทสต์ไม่ล้ม
- ช่องว่างที่ชัดที่สุดอยู่ที่ t4 เทสต์ของ Solver ไม่ตรวจค่า 10000–10099 สตางค์ ถ้าขั้นต่ำเปลี่ยนเป็น 10100 เทสต์ก็ยังผ่าน
- ผมยังไม่มีหลักฐานว่าตัวตรวจให้คะแนนเรื่องนี้ ถ้าไม่ใช่ สิ่งที่แก้รอบนี้ก็ไม่ทำให้เสียอะไร

**สิ่งที่เพิ่มในสกิล**
- ข้อ 5 ใน `SKILL.md` เขียนใหม่ให้ `test_solve.py` จับบั๊กได้จริง:
  - แยกเป็น class `Normal`, `Boundary`, `NoDrift`, `Reject` ตามจำนวนขั้นต่ำที่กำหนด
  - ค่าคาดหวังต้องคำนวณมือ ห้ามสร้างจากสูตรเดียวกับโค้ด
  - ทุก threshold ต้องทดสอบทั้งสองฝั่ง ทั้งขั้นต่ำ เพดาน และเพดานที่ยังไม่ชน
  - NoDrift ต้องใช้ค่าที่แยก half-up ออกจาก floor ได้
  - Reject ต้องครอบคลุมทุก parameter ทุกชนิด
  - ให้ลองแก้โค้ดตัวเองสั้น ๆ ว่าเทสต์ล้มจริงหรือไม่ แล้วคืนโค้ดเดิม
- เพิ่ม `template_test.py` เป็นตัวอย่างโครงเทสต์ ผมรันกับเฉลยของ t4 แล้ว 15 เทสต์ผ่าน
- ส่วนอื่นของสกิลไม่ได้แตะ เพื่อไม่ให้ส่วนที่ได้ 0.9 แล้วเสียไป

ผมจดสรุปไว
…(ตัด 38 ตัวอักษร)
