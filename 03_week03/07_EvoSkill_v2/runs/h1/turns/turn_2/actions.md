# ตาที่ 2 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-14 21:21 UTC คุณมีเวลาถึง 2026-11-14 21:51 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 2 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v2` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
date -u && ls scores traces skills solver_workspaces staging && echo "--- scores e1" && cat scores/epoch_1.json 2>/dev/null; echo; echo "--- skills e1"; find skills/epoch_1 -type f 2>/dev/null; echo "--- staging"; find staging -type f; echo "--- trace files e1"; ls traces/epoch_1 2>/dev/null; echo "--- ws e1"; ls solver_workspaces/epoch_1 2>/dev/null
```

ผลที่ได้:

```
Sat Nov 14 21:21:31 UTC 2026
scores:
epoch_0.json
epoch_1.json

skills:
epoch_0
epoch_1

solver_workspaces:
epoch_0
epoch_1

staging:
money-rounding-satang
thai-spec-solve-py

traces:
epoch_0
epoch_1
--- scores e1
{
 "t1-cafe-bill_s1": 0.9,
 "t1-cafe-bill_s2": 0.9,
 "t1-cafe-bill_s3": 0.9,
 "t2-split-bill_s1": 0.9,
 "t2-split-bill_s2": 0.9,
 "t2-split-bill_s3": 0.9,
 "t3-shipping-fee_s1": 0.8182,
 "t3-shipping-fee_s2": 0.6364,
 "t3-shipping-fee_s3": 0.8182,
 "t4-cashback_s1": 0.8,
 "t4-cashback_s2": 0.8,
 "t4-cashback_s3": 0.8
}
--- skills e1
skills/epoch_1/money-rounding-satang/SKILL.md
skills/epoch_1/money-rounding-satang/money_helpers.py
skills/epoch_1/thai-spec-solve-py/SKILL.md
--- staging
staging/money-rounding-satang/SKILL.md
staging/money-rounding-satang/money_helpers.py
staging/thai-spec-solve-py/SKILL.md
--- trace files e1
t1-cafe-bill_s1.jsonl
t1-cafe-bill_s2.jsonl
t1-cafe-bill_s3.jsonl
t2-split-bill_s1.jsonl
t2-split-bill_s2.jsonl
t2-split-bill_s3.jsonl
t3-shipping-fee_s1.jsonl
t3-shipping-fee_s2.jsonl
t3-shipping-fee_s3.jsonl
t4-cashback_s1.jsonl
t4-cashback_s2.jsonl
t4-cashback_s3.jsonl
--- ws e1
t1-cafe-bill_s1
t1-cafe-bill_s2
t1-cafe-bill_s3
t2-split-bill_s1
t2-spli
…(ตัด 128 ตัวอักษร)
```

### ขั้น 2 · Bash

```
diff -r skills/epoch_1 staging && echo SAME; rm -rf /tmp/ev2 && mkdir -p /tmp/ev2 && for d in /evo/solver_workspaces/epoch_1/*/; do n=$(basename $d); task=$(echo $n | sed 's/_s[0-9]$//'); mkdir -p /tmp/ev2/$n; cp $d/solve.py /tmp/ev2/$n/ 2>/dev/null; cp /evo/reference/baankafe/answers/$task/test_solve.py /tmp/ev2/$n/; out=$(cd /tmp/ev2/$n && timeout 20 python3 -m unittest test_solve 2>&1 | grep -E "^(FAIL|ERROR):|^OK|^FAILED"); echo "== $n"; echo "$out"; done; echo; ls /evo/solver_workspaces/epoch_1/t3-shipping-fee_s2/
```

ผลที่ได้:

```
SAME
== t1-cafe-bill_s1
OK
== t1-cafe-bill_s2
OK
== t1-cafe-bill_s3
OK
== t2-split-bill_s1
OK
== t2-split-bill_s2
OK
== t2-split-bill_s3
OK
== t3-shipping-fee_s1
OK
== t3-shipping-fee_s2
OK
== t3-shipping-fee_s3
OK
== t4-cashback_s1
OK
== t4-cashback_s2
OK
== t4-cashback_s3
OK

solve.py
```

### ขั้น 3 · Bash

```
cd /tmp/ev2 && cat > grid.py << 'EOF'
import sys, importlib.util, itertools, json
def load(p, name):
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
task, fn, sol = sys.argv[1], sys.argv[2], sys.argv[3]
ref = load(f"/evo/reference/baankafe/answers/{task}/solve.py","ref")
s = load(sol,"s")
grids = {
 "t1-cafe-bill": [([{'price':p,'qty':q}],m) for p in [0,1,4999,5000,10000,49999,50000,50001,99999,123456] for q in [1,2,3] for m in [False,True]],
 "t2-split-bill": [(t,p,tp) for t in [0,1,50,101,9999,12345] for p in [1,2,3,5] for tp in [0,1,7,50,99,100]],
 "t3-shipping-fee": [(w,d,e) for w in [1,999,1000,1001,4999,5000,5001,10000,20000,20001,30000] for d in [0,1,100,101,500] for e in [False,True]],
 "t4-cashback": [(a,t,b) for a in [0,1,9999,10000,10001,50000,100000,1000000] for t in ["silver","gold","platinum"] for b in [False,True]],
}[task]
diffs=[]
for args in grids:
    try: r = getattr(ref,fn)(*args) if task!="t1-cafe-bill" else ref.cafe_bill(*args)
    except Exception as e: r = "E:"+type(e).__name__
    try: x = getattr(s,fn)(*args) if task!="t1-cafe-bill" else s.cafe_bill(*args)
    except Exception as e: x = "E:"+type(e).__name__
    if r!=x: diffs.append((args,r,x))
print(task, "total", len(grids), "diffs", len(diffs))
for d in diffs[:25]: print(d)
EOF
S=/evo/solver_workspaces/epoch_1
python3 grid.py t3-shipping-fee shipping_fee $S/t3-shipping-fee_s2/solve.py; python3 grid.py t3-shipping-fee shipping_fee $S/t3-shipping-fee_s1/solve.py | head -3
python3 grid.py t4-cashback cashback $S/t4-cashback_s1/solve.py
```

ผลที่ได้:

```
t3-shipping-fee total 110 diffs 30
((1, 0, False), 0, 4000)
((1, 0, True), 0, 6000)
((999, 0, False), 0, 4000)
((999, 0, True), 0, 6000)
((1000, 0, False), 0, 4000)
((1000, 0, True), 0, 6000)
((1001, 0, False), 0, 8000)
((1001, 0, True), 0, 12000)
((4999, 0, False), 0, 8000)
((4999, 0, True), 0, 12000)
((5000, 0, False), 0, 8000)
((5000, 0, True), 0, 12000)
((5001, 0, False), 0, 8002)
((5001, 0, True), 0, 12002)
((10000, 0, False), 0, 15500)
((10000, 0, True), 0, 23250)
((20000, 0, False), 0, 30500)
((20000, 0, True), 0, 45750)
((20001, 0, False), 0, 30502)
((20001, 0, True), 'E:ValueError', 45752)
((20001, 1, True), 'E:ValueError', 45752)
((20001, 100, True), 'E:ValueError', 45752)
((20001, 101, True), 'E:ValueError', 54903)
((20001, 500, True), 'E:ValueError', 54903)
((30000, 0, False), 0, 45500)
t3-shipping-fee total 110 diffs 30
((1, 0, False), 0, 4000)
((1, 0, True), 0, 6000)
t4-cashback total 48 diffs 5
((10000, 'silver', True), 150, 300)
((10001, 'silver', True), 150, 300)
((50000, 'silver', True), 750, 1500)
((100000, 'silver', True), 1500, 3000)
((1000000, 'silver', True), 15000, 20000)
Shell cwd was reset to /evo
```

### ขั้น 4 · Bash

```
cd /evo/traces/epoch_1 && grep -o 'รับเอง[^"]\{0,60\}\|20,000[^"]\{0,40\}\|20000[^"]\{0,40\}\|เดือนเกิด[^"]\{0,60\}\|ระยะทาง[^"]\{0,50\}' *.jsonl | sort | uniq -c | sort -rn | head -30; echo ---; python3 /tmp/summ.py t3-shipping-fee_s2.jsonl 300 | tail -30
```

ผลที่ได้:

```
      6 t4-cashback_s3.jsonl:20000,\
      4 t4-cashback_s3.jsonl:2000000,'silver',True),20000),\n ((0,'gold',T
      4 t4-cashback_s3.jsonl:20000,'silver',False),300),\n ((20000,'silver
      3 t4-cashback_s3.jsonl:เดือนเกิด) แล้วเพดาน แล้วปัดลงครั้งเดียว ---\n    rate = RATE_PERCENT
      3 t4-cashback_s3.jsonl:เดือนเกิด ได้เงินคืน 2 เท่า\n- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) 
      3 t4-cashback_s3.jsonl:20000 สตางค์) ต่อบิล (ใช้หลังคูณ 2 เท่าเดือนเ
      3 t4-cashback_s2.jsonl:เดือนเกิด) -> เงินคืนเป็น 2 เท่า\n- เงินคืนสูงสุด 200 บาท (20000 สตาง
      3 t4-cashback_s2.jsonl:20000  # 200 บาท\nRATES = {\n    \
      3 t4-cashback_s1.jsonl:เดือนเกิด ได้เงินคืน 2 เท่า\n- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) 
      3 t4-cashback_s1.jsonl:20000 สตางค์) ต่อบิล (จำกัดหลังคูณ 2 เท่าแล้ว
      3 t4-cashback_s1.jsonl:20000    # 200 บาท\nRATES_PERCENT = {\
      3 t3-shipping-fee_s3.jsonl:ระยะทางเกิน 100 กม. (> 100)   : คิดเพิ่ม 20% จากยอดที่ได้
      3 t3-shipping-fee_s2.jsonl:ระยะทางเกิน 100 กม. คิดเพิ่ม 20%\n    if distance > 100:\
      3 t3-shipping-fee_s2.jsonl:ระยะทาง distance_km ต้องไม่ติดลบ ถ้าเกิน 100 กม. คิดเพิ่ม
      3 t3-shipping-fee_s1.jsonl:ระยะทางเกิน 100 กม. คิดเพิ่ม 
…(ตัด 3757 ตัวอักษร)
```

### ขั้น 5 · Bash

```
cd /tmp/ev2 && S=/evo/solver_workspaces/epoch_1; for t in t1-cafe-bill:cafe_bill t2-split-bill:split_bill; do task=${t%%:*}; fn=${t##*:}; for s in s1 s2 s3; do echo "## $task $s"; python3 grid.py $task $fn $S/$(echo $task | sed 's/-cafe-bill\|-split-bill//')/dev/null 2>/dev/null; done; done 2>/dev/null | head -0; for task in t1-cafe-bill t2-split-bill; do fn=$([ $task = t1-cafe-bill ] && echo cafe_bill || echo split_bill); for s in s1 s2 s3; do echo "## $task $s"; python3 grid.py $task $fn $S/$task\_$s/solve.py | head -8; done; done; echo "## t3 s2 vs s1 reject probes"; python3 - << 'EOF'
import importlib.util
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S="/evo/solver_workspaces/epoch_1"
R=load("/evo/reference/baankafe/answers/t3-shipping-fee/solve.py","r")
for name in ["t3-shipping-fee_s1","t3-shipping-fee_s2","t3-shipping-fee_s3"]:
    m=load(f"{S}/{name}/solve.py",name)
    for args in [(1000,1.0,False),(1000,0.0,False),(1000,True,False),(1000,10,"yes"),(1000.0,10,False),(1000,10,1),(0,10,False)]:
        def run(f):
            try: return f(*args)
            except Exception as e: return "E:"+type(e).__name__
        print(name,args,"ref=",run(R.shipping_fee),"sol=",run(m.shipping_fee))
EOF
```

ผลที่ได้:

```
## t1-cafe-bill s1
t1-cafe-bill total 60 diffs 0
## t1-cafe-bill s2
t1-cafe-bill total 60 diffs 0
## t1-cafe-bill s3
t1-cafe-bill total 60 diffs 0
## t2-split-bill s1
t2-split-bill total 144 diffs 0
## t2-split-bill s2
t2-split-bill total 144 diffs 0
## t2-split-bill s3
t2-split-bill total 144 diffs 0
## t3 s2 vs s1 reject probes
t3-shipping-fee_s1 (1000, 1.0, False) ref= E:ValueError sol= 4000
t3-shipping-fee_s1 (1000, 0.0, False) ref= E:ValueError sol= 4000
t3-shipping-fee_s1 (1000, True, False) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s1 (1000, 10, 'yes') ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s1 (1000.0, 10, False) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s1 (1000, 10, 1) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s1 (0, 10, False) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s2 (1000, 1.0, False) ref= E:ValueError sol= 4000
t3-shipping-fee_s2 (1000, 0.0, False) ref= E:ValueError sol= 4000
t3-shipping-fee_s2 (1000, True, False) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s2 (1000, 10, 'yes') ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s2 (1000.0, 10, False) ref= E:ValueError sol= E:ValueError
t3-shipping-fee_s2 
…(ตัด 657 ตัวอักษร)
```

### ขั้น 6 · Bash

```
cd /evo/solver_workspaces/epoch_1 && for f in */solve.py; do printf "%-32s main=%s  ok_key=%s  stdin=%s\n" $f $(grep -c "def main" $f) $(grep -c '"ok"' $f) $(grep -c "stdin" $f); done; echo; cd /evo/traces/epoch_1 && grep -l "subprocess\|stdin" *.jsonl | head; echo; python3 /tmp/summ.py t2-split-bill_s1.jsonl 200 | grep TEXT | tail -1 | cut -c1-1500
```

ผลที่ได้:

```
t1-cafe-bill_s1/solve.py         main=1  ok_key=2  stdin=1
t1-cafe-bill_s2/solve.py         main=1  ok_key=2  stdin=1
t1-cafe-bill_s3/solve.py         main=1  ok_key=2  stdin=2
t2-split-bill_s1/solve.py        main=1  ok_key=2  stdin=1
t2-split-bill_s2/solve.py        main=1  ok_key=2  stdin=1
t2-split-bill_s3/solve.py        main=1  ok_key=2  stdin=1
t3-shipping-fee_s1/solve.py      main=1  ok_key=2  stdin=2
t3-shipping-fee_s2/solve.py      main=0  ok_key=0  stdin=0
t3-shipping-fee_s3/solve.py      main=1  ok_key=2  stdin=1
t4-cashback_s1/solve.py          main=1  ok_key=2  stdin=1
t4-cashback_s2/solve.py          main=1  ok_key=2  stdin=1
t4-cashback_s3/solve.py          main=1  ok_key=2  stdin=1

t1-cafe-bill_s2.jsonl
t1-cafe-bill_s1.jsonl
t2-split-bill_s1.jsonl
t1-cafe-bill_s3.jsonl
t3-shipping-fee_s1.jsonl
t2-split-bill_s2.jsonl
t2-split-bill_s3.jsonl
t3-shipping-fee_s3.jsonl
t4-cashback_s3.jsonl
t4-cashback_s1.jsonl

TEXT: สร้างไฟล์ `solve.py` ในโฟลเดอร์ปัจจุบันแล้ว มีฟังก์ชัน `split_bill(total, people, tip_percent)` ที่คืน list ของยอดที่แต่ละคนจ่ายเป็นจำนวนเต็มสตางค์
```

### ขั้น 7 · Bash

```
cd /tmp/ev2 && S=/evo/solver_workspaces/epoch_1; cli(){ d=$1; shift; (cd $d && printf '%s' "$2" | timeout 10 python3 solve.py; echo " [exit $?]"); }; mkdir -p refcli && cp /evo/reference/baankafe/answers/*/solve.py refcli/ 2>/dev/null; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do echo "### $t"; done; 
REFT1=/evo/reference/baankafe/answers/t1-cafe-bill; REFT2=/evo/reference/baankafe/answers/t2-split-bill
for pair in "$REFT1 $S/t1-cafe-bill_s1" "$REFT2 $S/t2-split-bill_s1"; do set -- $pair; echo "## $(basename $1)"; for inp in '{"items":[{"price":4500,"qty":2}],"member":true}' '{"items":[{"price":4500,"qty":0}],"member":true}' '[1]' '{"items":[],"member":true,"x":1}' '{"total":10000,"people":3,"tip_percent":0}' '{"total":10000,"people":0,"tip_percent":0}' ; do echo "in: $inp"; for d in $1 $2; do echo -n "  $(basename $d): "; (cd $d && printf '%s' "$inp" | timeout 10 python3 solve.py 2>&1 | tr '\n' ' '; echo "[exit ${PIPESTATUS[1]}]"); done; done; done 2>&1 | head -80
```

ผลที่ได้:

```
### t1-cafe-bill
### t2-split-bill
### t3-shipping-fee
### t4-cashback
## t1-cafe-bill
in: {"items":[{"price":4500,"qty":2}],"member":true}
  t1-cafe-bill: {"ok": true, "result": 8667} [exit 0]
  t1-cafe-bill_s1: {"ok": true, "result": 8667} [exit 0]
in: {"items":[{"price":4500,"qty":0}],"member":true}
  t1-cafe-bill: {"ok": false, "error": "qty \u0e2d\u0e22\u0e39\u0e48\u0e19\u0e2d\u0e01\u0e0a\u0e48\u0e27\u0e07\u0e17\u0e35\u0e48\u0e01\u0e33\u0e2b\u0e19\u0e14"} [exit 2]
  t1-cafe-bill_s1: {"ok": false, "error": "qty ของรายการที่ 0 ต้องไม่น้อยกว่า 1"} [exit 2]
in: [1]
  t1-cafe-bill: {"ok": false, "error": "input \u0e15\u0e49\u0e2d\u0e07\u0e40\u0e1b\u0e47\u0e19 JSON object"} [exit 2]
  t1-cafe-bill_s1: {"ok": false, "error": "input ต้องเป็น JSON object"} [exit 2]
in: {"items":[],"member":true,"x":1}
  t1-cafe-bill: {"ok": false, "error": "cafe_bill() got an unexpected keyword argument 'x'"} [exit 2]
  t1-cafe-bill_s1: {"ok": false, "error": "cafe_bill() got an unexpected keyword argument 'x'"} [exit 2]
in: {"total":10000,"people":3,"tip_percent":0}
  t1-cafe-bill: {"ok": false, "error": "cafe_bill() got an unexpected keyword argument 'total'"} [exit 2]
  t1-cafe-bill_s1: {"ok": false
…(ตัด 1884 ตัวอักษร)
```

### ขั้น 8 · Bash

```
cd /tmp/ev2 && python3 - << 'EOF'
import importlib.util, random
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S="/evo/solver_workspaces/epoch_1"; RF="/evo/reference/baankafe/answers"
random.seed(1)
def run(f,*a):
    try: return f(*a)
    except Exception as e: return "E:"+type(e).__name__
R1=load(f"{RF}/t1-cafe-bill/solve.py","r1")
R2=load(f"{RF}/t2-split-bill/solve.py","r2")
R4=load(f"{RF}/t4-cashback/solve.py","r4")
for s in ["s1","s2","s3"]:
    M1=load(f"{S}/t1-cafe-bill_{s}/solve.py","m1"); M2=load(f"{S}/t2-split-bill_{s}/solve.py","m2")
    d1=[];d2=[]
    for _ in range(4000):
        items=[{"price":random.choice([random.randint(0,200000),random.randint(0,999)*5+random.choice([0,5]),random.randint(0,60000)]),"qty":random.randint(1,6)} for _ in range(random.randint(0,4))]
        m=random.random()<0.5
        a=run(R1.cafe_bill,items,m); b=run(M1.cafe_bill,items,m)
        if a!=b: d1.append((items,m,a,b))
        t=random.randint(0,300000); p=random.randint(1,12); tp=random.randint(0,100)
        a=run(R2.split_bill,t,p,tp); b=run(M2.split_bill,t,p,tp)
        if a!=b: d2.append((t,p,tp,a,b))
    print(s,"t1 diffs",len(d1),d1[:2]," t2 diffs",len(d2),d2[:2])
# t4 random
for s in ["s1","s2","s3"]:
    M4=load(f"{S}/t4-cashback_{s}/solve.py","m4"); d4=[]
    for _ in range(4000):
        a=random.choice([random.randint(0,3000000),random.randint(0,20000)]); t=random.choice(["silver","gold","platinum"]); b=random.random()<0.5
        x=run(R4.cashback,a,t,b); y=run(M4.cashback,a,t,b)
        if x!=y: d4.append((a,t,b,x,y))
    print(s,"t4 diffs",len(d4),sorted(set((t,b) for _,t,b,_,_ in d4)), d4[:2])
EOF
```

ผลที่ได้:

```
s1 t1 diffs 0 []  t2 diffs 0 []
s2 t1 diffs 0 []  t2 diffs 0 []
s3 t1 diffs 0 []  t2 diffs 0 []
s1 t4 diffs 313 [('silver', True)] [(627893, 'silver', True, 9418, 18836), (13609, 'silver', True, 204, 408)]
s2 t4 diffs 322 [('silver', True)] [(18630, 'silver', True, 279, 558), (15412, 'silver', True, 231, 462)]
s3 t4 diffs 315 [('silver', True)] [(11592, 'silver', True, 173, 347), (14359, 'silver', True, 215, 430)]
Shell cwd was reset to /evo
```

### ขั้น 9 · Bash

```
cd /tmp/ev2 && python3 - << 'EOF'
import importlib.util
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S="/evo/solver_workspaces/epoch_1"; RF="/evo/reference/baankafe/answers"
def run(f,*a):
    try: return ("OK",f(*a))
    except Exception as e: return ("E:"+type(e).__name__)
cases={
 "t1-cafe-bill":("cafe_bill",[
   ([{'price':4500,'qty':1}],1),([{'price':4500,'qty':1}],"no"),([{'price':4500,'qty':1}],None),
   ([{'price':4500,'qty':True}],False),([{'price':True,'qty':1}],False),([{'qty':1}],False),
   ([{'price':4500,'qty':1,'x':2}],False),(({'price':4500,'qty':1},),False),("abc",False),([],False),
   ([{'price':-1,'qty':1}],False),([{'price':4500,'qty':10**30}],False)]),
 "t2-split-bill":("split_bill",[
   (10000,3,True),(10000,3,50.0),(10000.0,3,0),(10000,3.0,0),(10000,3,101),(-1,3,0),(10000,3,-1),(True,1,0),(10000,True,0),(0,1,0),(10000,1,0)]),
 "t4-cashback":("cashback",[
   (10000,"silver",1),(10000,"Gold",False),(10000,None,False),(-1,"gold",False),(10000,"gold",None),(True,"gold",False),(10000.0,"gold",False)]),
}
for task,(fn,cs) in cases.items():
    R=load(f"{RF}/{task}/solve.py","r")
    for s in ["s1","s2","s3"]:
        M=load(f"{S}/{task}_{s}/solve.py","m")
        for c in cs:
            a=run(getattr(R,fn),*c); b=run(getattr(M,fn),*c)
            if a!=b: print(task,s,c,"ref=",a,"sol=",b)
print("done")
EOF
```

ผลที่ได้:

```
done
Shell cwd was reset to /evo
```

### ขั้น 10 · Bash

```
date -u; cat /evo/staging/thai-spec-solve-py/SKILL.md | sed -n '1,20p'
```

ผลที่ได้:

```
Sat Nov 14 21:22:28 UTC 2026
---
name: thai-spec-solve-py
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชัน Python ในไฟล์ solve.py ตามข้อกำหนดภาษาไทย เช่น คิดเงิน หารบิล ค่าส่ง ส่วนลด หรือเงินคืน ขั้นตอนนี้ครอบคลุมการแตกกติกา การตรวจ input แบบเข้มงวด และการทดสอบขอบเขต
---

# เขียน solve.py จากสเปคภาษาไทย

สกิลนี้เป็นขั้นตอนทำงาน ส่วนเรื่องการปัดเศษและการคำนวณเงินอยู่ในสกิล `money-rounding-satang` ใช้ประกอบกัน

## 1. แตกกติกาก่อนเขียนโค้ด
- อ่านโจทย์ทีละประโยค แล้วเขียนรายการกติกาเป็น comment ไว้หัวไฟล์ `solve.py`
- ตัวเลขขอบเขต: "ตั้งแต่ X ขึ้นไป" = `>= X`, "เกิน X" = `> X`, "ไม่เกิน X" = `<= X`, "ต่ำกว่า X" = `< X` อย่าสลับเครื่องหมาย
- "คูณต่อจากข้อก่อน" หรือ "คิดเพิ่มจากยอดที่ได้แล้ว" = คำนวณทบต้นตามลำดับ ไม่ใช่บวกรวมจากฐานเดิม
- กติกาที่ผูกกับ tier, ประเภท หรือ flag ให้ใช้เฉพาะกับกลุ่มที่โจทย์เขียนไว้ ไม่ขยายไปกลุ่มอื่นเอง

## 2. ตรวจ input แบบเข้มงวด
ตัวตรวจมักมีกรณี reject ที่ต้องการ `ValueError` ตรง ๆ จึงต้องทำดังนี้
- ตรวจชนิดด้วย `type(x) is int`, `type(x) is bool`, `type(x) is str` อย่าใช้ `isinstance` เพราะ `isinstance(True, int)` เป็นจริง
- ค่า float ต้อง reject แม้จะเป็น `4500.0` และ string เช่น `"2"` ต้อง reject
- ตรวจช่วงค่าตามโจทย์: จำนวนชิ้น >= 1, จำนวนคน >= 1, เปอร์เซ็นต
…(ตัด 20 ตัวอักษร)
```

### ขั้น 11 · Edit

```
/evo/staging/thai-spec-solve-py/SKILL.md
- ค่า float ต้อง reject แม้จะเป็น `4500.0` และ string เช่น `"2"` ต้อง reject
- พารามิเตอร์ตัวเลขทุกตัวเป็น int เป็นค่าเริ่มต้น รวมถึงระยะทาง น้ำหนัก จำนวน และเปอร์เซ็นต์ เว้นแต่โจทย์ระบุชัดว่ารับทศนิยม อย่าเปิดรับ float เพราะโจทย์เขียนว่า "ตั้งแต่ 0" หรือ "กิโลเมตร" เฉย ๆ
- ตัวอย่างที่พลาดมาแล้ว: ฟังก์ชันค่าส่งที่รับ `distance_km=1.0` แล้วคืนค่าปกติ ไม่ reject จึงพลาดชุดทดสอบ reject และให้คะแนนต่ำที่สุดในรอบก่อน
- ตรวจช่วงค่าตามโจทย์: จำนวนชิ้น >= 1, จำนวนคน >= 1, เปอร์เซ็นต์ 0–100, น้ำหนัก ฯลฯ
```

ผลที่ได้:

```
The file /evo/staging/thai-spec-solve-py/SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### ขั้น 12 · Edit

```
/evo/staging/thai-spec-solve-py/SKILL.md
- ตัวอย่างจากรอบก่อน: solver ของค่าส่งที่รับ `distance_km=1.0` แล้วคืนค่าปกติ และไม่มี `main()` ได้คะแนนต่ำที่สุดในกลุ่มเดียวกัน
```

ผลที่ได้:

```
The file /evo/staging/thai-spec-solve-py/SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### ขั้น 13 · Edit

```
/evo/staging/thai-spec-solve-py/SKILL.md
- ถ้าโจทย์เงียบเรื่องกรณีพิเศษ ให้เลือกการอ่านตามตัวอักษรที่แคบที่สุด แล้วเขียนไว้ใน final message ว่าเลือกอะไร
- ค่าศูนย์หรือค่าขอบของพารามิเตอร์บางตัวอาจมีความหมายพิเศษ เช่น รับเองที่ร้านหรือไม่มีการคิดค่าบริการ ถ้าโจทย์ไม่ได้เขียนไว้ ให้ทำตามตัวอักษรของโจทย์และระบุในสรุปว่าเป็นจุดที่ควรยืนยัน
- อย่าแต่งกติกาที่โจทย์ไม่มี และอย่าเพิกเฉยต่อกติกาที่โจทย์เขียนไว้
```

ผลที่ได้:

```
The file /evo/staging/thai-spec-solve-py/SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### ขั้น 14 · Edit

```
/evo/staging/thai-spec-solve-py/SKILL.md
## 6. CLI (ต้องมีทุกครั้ง)
ไฟล์ solve.py ต้องมี `main()` เสมอ เพราะตัวตรวจอาจเรียกผ่าน stdin เป็น JSON โดยไม่ได้บอกล่วงหน้า
- อ่าน JSON จาก stdin ต้องเป็น object มิฉะนั้น raise `ValueError` แล้วเรียกฟังก์ชันด้วย `**args`
- สำเร็จ พิมพ์ `{"ok": true, "result": ...}` และ exit 0 (ผลเป็นจำนวนเต็มสตางค์หรือ list ของจำนวนเต็ม)
- error พิมพ์ `{"ok": false, "error": "..."}` และ exit 2 โดยจับ `(ValueError, TypeError)`
- key ที่ไม่รู้จักใน JSON ทำให้ TypeError จากการเรียกฟังก์ชัน ให้จับแล้วตอบ error เช่นเดียวกัน
- ปิดท้ายด้วย `if __name__ == "__main__": sys.exit(main())` เพื่อให้ import ได้โดยไม่รัน main
- ทดสอบ CLI จริงด้วย `echo '{...}' | python3 solve.py` ทั้งกรณีสำเร็จและกรณี error ตรวจว่าได้ exit code ตามที่กำหนด
```

ผลที่ได้:

```
The file /evo/staging/thai-spec-solve-py/SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### ขั้น 15 · Bash

```
date -u && head -5 staging/thai-spec-solve-py/SKILL.md && grep -n "^## " staging/thai-spec-solve-py/SKILL.md && find staging -type f | sort
```

ผลที่ได้:

```
Sat Nov 14 21:22:43 UTC 2026
---
name: thai-spec-solve-py
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชัน Python ในไฟล์ solve.py ตามข้อกำหนดภาษาไทย เช่น คิดเงิน หารบิล ค่าส่ง ส่วนลด หรือเงินคืน ขั้นตอนนี้ครอบคลุมการแตกกติกา การตรวจ input แบบเข้มงวด และการทดสอบขอบเขต
---

10:## 1. แตกกติกาก่อนเขียนโค้ด
16:## 2. ตรวจ input แบบเข้มงวด
26:## 3. คำนวณให้ตรงลำดับและปัดครั้งเดียว
31:## 4. ขอบเขตที่ต้องทดสอบเสมอ
38:## 5. เรื่องที่โจทย์ไม่ได้บอก
43:## 6. CLI (ต้องมีทุกครั้ง)
52:## 7. ทดสอบในโฟลเดอร์ทำงาน
58:## 8. ผลลัพธ์ที่ส่ง
staging/money-rounding-satang/SKILL.md
staging/money-rounding-satang/money_helpers.py
staging/thai-spec-solve-py/SKILL.md
```

### ขั้น 16 · Bash

```
cat >> /evo/evolver_workspace/notes.md << 'EOF'

## Epoch 1 (ผล: t1 0.9 ×3 · t2 0.9 ×3 · t3 0.8182, 0.6364, 0.8182 · t4 0.8 ×3)
- ผ่านชุดทดสอบ reference ทุกตัว และผลตรงกับ reference ในการสุ่มทดสอบ t1/t2 ทุกกรณี
- t4 ต่างจาก reference เฉพาะ silver + เดือนเกิด (solver ให้ 2 เท่า, reference ไม่ให้) ซึ่งขัดกับตัวโจทย์ที่เขียนว่า "เดือนเกิด ได้ 2 เท่า" จึงไม่สามารถแก้ได้จากสกิลโดยไม่เดา
- t3 ต่างจาก reference ที่กรณี distance=0 และ express น้ำหนัก > 20000 (กติกาซ่อน ไม่อยู่ในโจทย์)
- t3 s2 รับ distance เป็น float และไม่มี main() ได้คะแนนต่ำสุด → เพิ่มในสกิล: พารามิเตอร์ตัวเลขเป็น int เสมอ และ main() บังคับ
- t1/t2 ได้ 0.9 ทั้งที่ตรงกับ reference ทุกกรณีที่ทดสอบ ยังไม่ทราบสาเหตุของ 0.1 ที่หายไป (อาจเป็นกรณีที่ไม่เคยเห็น)

## Epoch 2 (สิ่งที่เขียนใน /evo/staging)
- `thai-spec-solve-py/SKILL.md`: ปรับ section 2 (พารามิเตอร์ตัวเลขเป็น int เสมอ), section 5 (ค่าศูนย์ให้ระบุเป็นจุดที่ควรยืนยัน), section 6 (main() บังคับ พร้อมวิธีทดสอบ CLI จริง)
- `money-rounding-satang/` ไม่เปลี่ยน
EOF
tail -3 /evo/evolver_workspace/notes.md
```

ผลที่ได้:

```
## Epoch 2 (สิ่งที่เขียนใน /evo/staging)
- `thai-spec-solve-py/SKILL.md`: ปรับ section 2 (พารามิเตอร์ตัวเลขเป็น int เสมอ), section 5 (ค่าศูนย์ให้ระบุเป็นจุดที่ควรยืนยัน), section 6 (main() บังคับ พร้อมวิธีทดสอบ CLI จริง)
- `money-rounding-satang/` ไม่เปลี่ยน
```

### ขั้น 17 · Read

```
/evo/evolver_workspace/notes.md
```

ผลที่ได้:

```
1	# บันทึกของ Skill Evolver
2	
3	## Epoch 0 (ผล: t1 0.5/0.6/0.5 · t2 0.6 ×3 · t3 0.5455 ×3 · t4 0.4 ×3)
4	
5	### การวินิจฉัย (รันชุดทดสอบของ reference กับ solve.py ของ Solver ใน /tmp/ev)
6	- Reject (กรณีรับ input ผิด) ล้มเกือบทุกตัว:
7	  - รับ float ที่ควร reject เช่น ราคา 4500.0 หรือ 1000.0 แล้วคืนค่าปกติ
8	  - รับ string เช่น qty "2" หรือ express "yes" แล้วคืนค่าปกติ
9	  - qty = 0 ไม่ถูก reject (t1 s1)
10	  - raise TypeError แทน ValueError (t3 s1, t4 s1 ที่ amount float)
11	- No-drift (ปัดกลางทาง) ล้มใน t1 s3 และ t4 ทุก rollout: ใช้ float หรือปัดระหว่างทาง
12	- t2 ผ่านชุดทดสอบ reference ทุกตัว แต่ได้ 0.6 เพราะปัดทิปแยกแล้วบวก (floor) ต่างจากปัดยอดรวมครั้งเดียว
13	  เช่น total=101, tip=50 ได้ 151 แทน 152 (ตรวจแล้วด้วยการรันจริง)
14	- ไม่พบการเรียก CLI ใน trace ของ epoch 0 แต่ reference มี main() แบบ stdin JSON จึงแนะนำให้ใส่ไว้ (ไม่เสียหาย)
15	- trace ไม่มีตัวโจทย์ฉบับเต็ม: Solver ไม่เห็นเนื้อโจทย์ใน trace ดังนั้นสกิลต้องอธิบายหลักทั่วไปให้ครอบคลุมโจทย์ที่ไม่เคยเห็น
16	
17	### สิ่งที่ reference มีแต่ไม่ได้อยู่ในโจทย์ (มีกติกาซ่อนอยู่)
18	- ค่าส่งเป็น 0 เมื่อระยะทาง 0, จำกัดน้ำหนักของส่งด่วน, เงินคืนของ silver ไม่ได้สิทธิ์เดือนเกิด
19	- เงินคืนปัดลง ขณะที่ยอดลูกค้าจ่ายปัดครึ่งขึ้น

…(ตัด 1854 ตัวอักษร)
```

**Agent พูด:** `skills_v2` is in `/evo/staging/`. I finished at about 21:23 UTC, well before the 21:51 deadline.

**What epoch 1 showed.** Scores rose from epoch 0: t1 and t2 are at 0.9, t3 at 0.82 or 0.64, and t4 at 0.8. Every epoch 1 solution passes the reference unit tests. On random and boundary inputs, t1 and t2 match the reference exactly, including wrong-type inputs.

The remaining gaps are:
- **t4 (0.8):** the solvers give silver members the birthday 2× bonus, which the brief literally allows, while the reference denies it. The brief doesn't state the restriction, so no skill can fix this without guessing.
- **t3 (0.82, one at 0.64):** the reference has rules the brief doesn't state, for zero distance and for the express weight limit. The 0.64 solver also accepted float `distance_km` and had no `main()`, so I changed the skill to address that.
- **t1 and t2 (0.9):** I can't find the missing 0.1. Every case I tested matches the reference, so it may be a hidden case I haven't seen.

**What changed in `thai-spec-solve-py/SKILL.md`:**
- Section 2: every numeric parameter must be `int` by default, including distance and weight. Float is rejected unless the spec explicitly allows decimals.
- Section 5: zero or boundary values that may carry special meaning should be followed literally and flagged in the final message as points to confirm.
- Section 6: `main()` is now required, not optional, and the skill says to test the CLI with real stdin and check exit codes.

`money-rounding-satang` i
…(ตัด 295 ตัวอักษร)
