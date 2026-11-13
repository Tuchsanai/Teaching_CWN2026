# ตาที่ 3 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 02:08 UTC คุณมีเวลาถึง 2026-11-13 02:38 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 3 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v3` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_2.json; ls solver_workspaces/epoch_2/t1-cafe-bill_s1; cat solver_workspaces/epoch_2/t3-shipping-fee_s1/solve.py
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
}solve.py
test_mine.py
import json
import sys
from fractions import Fraction


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def _need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    _need_int(weight_g, "weight_g", 1, 30000)
    _need_int(distance_km, "distance_km", 0)
    _need_bool(express, "express")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        fee = Fractio
…(ตัด 621 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /evo; cat > /tmp/fuzz.py <<'EOF'
import sys, importlib.util, itertools, subprocess, json
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
t,fn,s=sys.argv[1:4]
ref=load(f'/evo/reference/answers/{t}/solve.py','ref'); me=load(f'/evo/solver_workspaces/epoch_2/{t}_s{s}/solve.py','me')
def run(m,a):
    try: return ('ok',getattr(m,fn)(*a))
    except ValueError: return ('VE',)
    except Exception as e: return ('EXC',type(e).__name__)
ints=[0,1,2,3,-1,999,1000,1001,5000,5001,9999,10000,10020,49999,50000,100,101,30000,30001,12345,True,False,None,4500.0,'2',1.5,[],float('nan')]
bools=[True,False,0,1,None,'x']
tiers=['silver','gold','platinum','Gold','',None,[],1]
items=[[],[{'price':4500,'qty':2}],[{'price':0,'qty':1}],[{'price':1,'qty':1,'x':1}],[{'price':1}],[{'qty':1}],[1],None,{},'a',[{'price':True,'qty':1}],[{'price':100,'qty':1.0}],[{'price':25075,'qty':2},{'price':1,'qty':3}]]
args={'t1-cafe-bill':[items,bools],'t2-split-bill':[ints,ints,ints],'t3-shipping-fee':[ints,ints,bools],'t4-cashback':[ints,tiers,bools]}[t]
bad=0
for a in itertools.product(*args):
    r,m=run(ref,a),run(me,a)
    if r!=m:
        bad+=1
        if bad<6: print(t,s,a,r,m)
print(t,s,'diffs',bad)
EOF
for t in "t1-cafe-bill cafe_bill" "t2-split-bill split_bill" "t3-shipping-fee shipping_fee" "t4-cashback cashback"; do set -- $t; for s in 1 2 3; do python3 -I /tmp/fuzz.py $1 $2 $s 2>&1 | tail -7; done; done
```

ผลที่ได้:

```
t1-cafe-bill 1 diffs 0
t1-cafe-bill 2 diffs 0
t1-cafe-bill 3 ([], True) ('ok', 0) ('VE',)
t1-cafe-bill 3 ([], False) ('ok', 0) ('VE',)
t1-cafe-bill 3 diffs 2
t2-split-bill 1 diffs 0
t2-split-bill 2 diffs 0
t2-split-bill 3 diffs 0
t3-shipping-fee 1 diffs 0
t3-shipping-fee 2 diffs 0
t3-shipping-fee 3 diffs 0
t4-cashback 1 diffs 0
t4-cashback 2 diffs 0
t4-cashback 3 diffs 0
```

### ขั้น 3 · Bash

```
cd /evo; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for s in 1 2 3; do for inp in '' 'abc' '[1]' '{}' '{"zz":1}' 'null' '{"total":1,"people":2,"tip_percent":0}' '{"weight_g":500,"distance_km":1,"express":false}' '{"amount":20000,"tier":"gold","birthday":false}' '{"items":[{"price":100,"qty":2}],"member":true}' '{"items":[{"price":100,"qty":2}],"member":"x"}'; do a=$(echo -n "$inp" | python3 -I reference/answers/$t/solve.py 2>&1; echo "rc=$?"); b=$(echo -n "$inp" | python3 -I solver_workspaces/epoch_2/${t}_s$s/solve.py 2>&1; echo "rc=$?"); [ "$a" != "$b" ] && echo "DIFF $t s$s [$inp] ref=$a me=$b"; done; done; done 2>&1 | head -30; diff <(cat skills/epoch_2/*/SKILL.md) staging/*/SKILL.md && echo same
```

ผลที่ได้:

```
DIFF t1-cafe-bill s1 [{"items":[{"price":100,"qty":2}],"member":"x"}] ref={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True \u0e2b\u0e23\u0e37\u0e2d False"}
rc=2 me={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True/False"}
rc=2
DIFF t1-cafe-bill s2 [{"items":[{"price":100,"qty":2}],"member":"x"}] ref={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True \u0e2b\u0e23\u0e37\u0e2d False"}
rc=2 me={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True/False"}
rc=2
DIFF t1-cafe-bill s3 [{"items":[{"price":100,"qty":2}],"member":"x"}] ref={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True \u0e2b\u0e23\u0e37\u0e2d False"}
rc=2 me={"ok": false, "error": "member \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 True/False"}
rc=2
same
```

### ขั้น 4 · Bash

```
cd /evo/traces/epoch_2; for t in t1-cafe-bill_s1 t4-cashback_s2; do python3 -I - $t <<'EOF'
import json,sys
for l in open(sys.argv[1]+'.jsonl'):
    d=json.loads(l)
    if d.get('type')=='assistant':
        for c in d['message']['content']:
            if c['type']=='text': print('A:',c['text'][:2500])
            if c['type']=='tool_use': print('TOOL:',json.dumps(c['input'],ensure_ascii=False)[:600])
    if d.get('type')=='result': print('RESULT turns',d.get('num_turns'),d.get('duration_ms'))
EOF
done
```

ผลที่ได้:

```
TOOL: {"command": "ls -R ./skills 2>/dev/null | head -50"}
TOOL: {"file_path": "/workspace/evlab/ws/e1/legs/runs/v2_train/t1-cafe-bill-r1/sandbox/skills/baankafe-money-function/SKILL.md"}
TOOL: {"command": "cat > solve.py <<'EOF'\nimport json\nimport sys\nfrom fractions import Fraction\n\n\ndef _need_int(v, name, low=None, high=None):\n    if type(v) is not int:\n        raise ValueError(f\"{name} ต้องเป็นจำนวนเต็ม\")\n    if (low is not None and v < low) or (high is not None and v > high):\n        raise ValueError(f\"{name} อยู่นอกช่วง\")\n    return v\n\n\ndef _half_up(x):\n    return int((Fraction(x) * 2 + 1) // 2)\n\n\ndef cafe_bill(items, member):\n    if type(items) is not list:\n        raise ValueError(\"items ต้องเป็น list\")\n    if type(member) is not bool:\n        raise
TOOL: {"command": "sed -i 's/51308/45743/' test_mine.py && python3 -m unittest -q test_mine 2>&1 | tail -3"}
A: ผมเขียน `cafe_bill(items, member)` ไว้ใน `solve.py` แล้ว และเทสต์ที่เขียนเอง (`test_mine.py`) ผ่านครบ 4 ชุด ผมทำตามสกิล `baankafe-money-function` ที่อยู่ใน `./skills`

**วิธีคิดเงิน**
- รวมยอดเป็นสตางค์ (`price × qty`) ถ้ายอดตั้งแต่ 50000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้า `member` เป็น T
…(ตัด 3090 ตัวอักษร)
```

### ขั้น 5 · Bash

```
cd /evo/staging/baankafe-money-function; python3 -I - <<'EOF'
p='SKILL.md'
s=open(p,encoding='utf-8').read()
s=s.replace('(หลังแก้สองจุดนี้ได้ 0.7 — ส่วนที่เหลือคือ CLI ในข้อ 6 และความเข้มงวดของ input)','(หลังแก้สองจุดนี้ได้ 0.7 และหลังเพิ่ม CLI ในข้อ 6 ได้ 0.9 — ส่วนที่เหลือ 0.1 ยังไม่ทราบสาเหตุ จึงให้ทำข้อ 7 ให้ครบเพื่อกันพลาดรายละเอียด)')
s+='''
## 7) ตรวจท้ายงานก่อนส่ง (ชุดสุดท้ายที่ยังเหลือคะแนน 0.1 — กันรายละเอียดเล็ก ๆ)
ผลของ Solver รอบก่อนตรงกับเฉลยทุกอินพุตที่เราลองสุ่ม ดังนั้นให้เน้นความเรียบร้อยของงานที่ส่ง:
- โฟลเดอร์งานควรเหลือไฟล์ส่งมอบคือ `solve.py` ให้เขียนไฟล์เทสต์ชั่วคราวของตัวเองไว้นอกโฟลเดอร์งาน (เช่น `/tmp/test_mine.py` แล้วตั้ง `PYTHONPATH` ชี้โฟลเดอร์งาน) หรือไม่ก็ลบทิ้งหลังรันผ่าน อย่าทิ้ง `__pycache__` หรือไฟล์ขยะ
- `solve.py` ไม่พิมพ์อะไรตอน import, ไม่แก้ค่า input ที่ส่งเข้ามา (ห้าม mutate `items` หรือ dict ข้างใน), ไม่พึ่งไฟล์อื่น, ใช้เฉพาะ standard library
- ฟังก์ชันคืน `int` จริง (ไม่ใช่ `Fraction`, `float`, `bool`) และสำหรับหารบิลคืน `list` ของ `int` จริง ผลรวมเท่ายอดที่ต้องหารเสมอ
- ข้อความ error ของ `ValueError` ควรเป็นภาษาไทยสั้น ๆ ที่บอกชื่อพารามิเตอร์ที่ผิด (เช่น "member ต้องเป็น True หรือ False")
- อ่านโจทย์ซ้ำอีกรอบเทียบกับโค้ดทีละบรรทัดว่ากฎครบทุกข้อและลำดับถูก (ลดก่อน/บวก VAT ท้ายสุด, คูณสะสมต่อกัน, เพดานหลังคูณ) ก่อนสรุปงาน
- ไม่ต้องทำสิ่งอื่นนอกเหนือจากที่โจทย์ขอ (ไม่เพิ่มฟีเจอร์ ไม่ถามกลับ)
'''
open(p,'w',encoding='utf-8').write(s)
EOF
grep -n "## " SKILL.md
```

ผลที่ได้:

```
11:## 1) ตรวจ input ทุกตัวแปรก่อนคำนวณ (สำคัญมาก — โจทย์ไม่เขียนบอก แต่ตัวตรวจทดสอบเสมอ)
36:## 2) คำนวณด้วยเลขตรง ห้ามใช้ float
41:## 3) วิธีปัด: ปัดครึ่งขึ้น (half-up) เป็นค่าเริ่มต้นของร้าน
51:## 4) ลำดับกฎและเงื่อนไขขอบ
59:## 5) เขียนเทสต์เองและรันก่อนส่งงาน (ต้องทำ ห้ามข้าม)
67:## 6) ข้อกำหนดไฟล์และอินเทอร์เฟซ CLI (ทำให้ครบ — คะแนนส่วนหนึ่งยังหายไปแม้เทสต์ฟังก์ชันผ่านหมด)
95:## 7) ตรวจท้ายงานก่อนส่ง (ชุดสุดท้ายที่ยังเหลือคะแนน 0.1 — กันรายละเอียดเล็ก ๆ)
```

### ขั้น 6 · Bash

```
cd /evo/staging/baankafe-money-function; python3 -I - <<'EOF'
p='SKILL.md'
s=open(p,encoding='utf-8').read()
s=s.replace('สร้างไฟล์เทสต์แยก (เช่น `test_mine.py` ในโฟลเดอร์งาน) แล้วรันด้วย `python3 -m unittest -q`','สร้างไฟล์เทสต์แยก (เช่น `/tmp/test_mine.py` นอกโฟลเดอร์งาน) แล้วรันด้วย `PYTHONPATH=<โฟลเดอร์งาน> python3 -m unittest -q test_mine` (ถ้าอยู่ในโฟลเดอร์ /tmp ให้ `cd /tmp` ก่อน)')
s=s.replace('- ไฟล์เทสต์ของตัวเอง (`test_mine.py`) ควรมีโค้ดที่รันได้โดยไม่ error (อย่าลืมให้ `python3 -m unittest -q test_mine` ผ่าน ไม่ใช่รันเปล่า ๆ แล้วได้ "Ran 1 test … FAILED" จาก discovery ผิด) ลบไฟล์ชั่วคราวที่ไม่ใช้ออก','- รันเทสต์ด้วยชื่อโมดูลให้ถูก (`unittest -q test_mine`) ไม่ใช่รันเปล่า ๆ แล้วได้ "Ran 1 test … FAILED" จาก discovery ผิด')
open(p,'w',encoding='utf-8').write(s)
EOF
grep -n "test_mine" SKILL.md
```

ผลที่ได้:

```
60:สร้างไฟล์เทสต์แยก (เช่น `/tmp/test_mine.py` นอกโฟลเดอร์งาน) แล้วรันด้วย `PYTHONPATH=<โฟลเดอร์งาน> python3 -m unittest -q test_mine` (ถ้าอยู่ในโฟลเดอร์ /tmp ให้ `cd /tmp` ก่อน) ครอบคลุม:
91:- รันเทสต์ด้วยชื่อโมดูลให้ถูก (`unittest -q test_mine`) ไม่ใช่รันเปล่า ๆ แล้วได้ "Ran 1 test … FAILED" จาก discovery ผิด
97:- โฟลเดอร์งานควรเหลือไฟล์ส่งมอบคือ `solve.py` ให้เขียนไฟล์เทสต์ชั่วคราวของตัวเองไว้นอกโฟลเดอร์งาน (เช่น `/tmp/test_mine.py` แล้วตั้ง `PYTHONPATH` ชี้โฟลเดอร์งาน) หรือไม่ก็ลบทิ้งหลังรันผ่าน อย่าทิ้ง `__pycache__` หรือไฟล์ขยะ
```

**Agent พูด:** ผมอัปเดต `skills_v3` ใน `/evo/staging/baankafe-money-function/SKILL.md` แล้ว แต่ยังไม่รู้ว่าอะไรทำให้ขาดอีก 0.1

**ผล epoch 2:** ทุก rollout ได้ 0.9 เท่ากันหมด คะแนนขึ้นจาก 0.7 ใน epoch 1 หลังสกิลให้ใส่ `main()` อ่าน JSON จาก stdin ซึ่งสอดคล้องกับข้อสันนิษฐานของ epoch 2

**สิ่งที่ตรวจแล้ว:**
- รัน `solve.py` ทั้ง 12 ไฟล์เทียบกับเฉลยอ้างอิงด้วยอินพุตสุ่มหลายพันชุด (ชนิดข้อมูลผิด ค่าขอบ ค่าติดลบ NaN และอื่น ๆ) ผลต่างเกิดครั้งเดียว: `t1-cafe-bill` rollout 3 ปฏิเสธ `items=[]` ขณะที่เฉลยคืน 0 แต่คะแนนของ rollout นี้ก็ยังเป็น 0.9 เท่ากัน
- ทดสอบ CLI กับ stdin ผิดรูปแบบหลายแบบ ผลตรงกับเฉลยทั้ง exit code และโครงสร้าง JSON ต่างกันแค่ข้อความ error ของ `member` ใน `t1-cafe-bill`

เพราะโค้ดทำงานเหมือนเฉลย ผมจึงบอกสาเหตุของ 0.1 ที่เหลือไม่ได้ ผมเดาว่าอาจเป็นความเรียบร้อยของงานที่ส่ง เช่น `test_mine.py` ที่ถูกทิ้งไว้ในโฟลเดอร์งาน แต่ไม่มีหลักฐานยืนยัน

**สิ่งที่เปลี่ยนใน v3:** เพิ่มหัวข้อ 7 "ตรวจท้ายงานก่อนส่ง" เพื่อกันรายละเอียดเล็ก ๆ:
- ให้เขียนไฟล์เทสต์ไว้นอกโฟลเดอร์งาน (เช่น `/tmp`) ให้โฟลเดอร์งานเหลือแค่ `solve.py` แล้วแก้หัวข้อ 5 ให้ตรงกัน
- ห้ามแก้ค่า input ที่ส่งเข้ามา
- ผลลัพธ์ต้องเป็น `int` จริง
- ข้อความ error เป็นภาษาไทยสั้น ๆ ที่บอกชื่อพารามิเตอร์ที่ผิด
- ให้อ่านโจทย์เทียบกับโค้ดอีกรอบก่อนสรุปงาน

สกิลนี้ยังเป็นแบบทั่วไปสำหรับฟังก์ชันคิดเงินของ BaanKafe ไม่ได้ผูกกับโจทย์ train ทั้งสี่ข้อ
