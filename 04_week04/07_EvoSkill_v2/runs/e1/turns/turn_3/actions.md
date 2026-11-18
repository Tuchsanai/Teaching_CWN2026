# ตาที่ 3 ของ Evolver

ข้อความที่ได้รับ: เวลาตอนนี้ 2026-11-14 22:56 UTC · เส้นตายของตานี้ 2026-11-14 23:26 UTC เมื่อถึงเส้นตาย สิ่งที่อยู่ใน `/evo/staging/` จะถูกนำไปใช้ทันทีตามสภาพขณะนั้น · นี่คือ epoch 3 · ผลการทำโจทย์รอบล่าสุดของ Solver อยู่ใน `/evo` แล้ว ขอให้วิเคราะห์ rollout เหล่านั้น วินิจฉัยว่า Solver พลาดตรงไหนที่สกิลช่วยแก้ได้ แล้วเขียนชุดสกิล `skills_v3` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_2.json | tr -d '\n '; echo; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for s in 1 2 3; do d=/tmp/run2/${t}_$s; mkdir -p $d; cp solver_workspaces/epoch_2/${t}_s$s/solve.py $d/; cp reference/answers/$t/test_solve.py $d/; echo "== $t s$s"; (cd $d; PYTHONPATH=$d python3 -m unittest -q test_solve 2>&1 | tail -2); done; done
```

ผลที่ได้:

```
{"t1-cafe-bill_s1":0.9,"t1-cafe-bill_s2":0.9,"t1-cafe-bill_s3":0.9,"t2-split-bill_s1":0.9,"t2-split-bill_s2":0.9,"t2-split-bill_s3":0.9,"t3-shipping-fee_s1":0.9091,"t3-shipping-fee_s2":0.9091,"t3-shipping-fee_s3":0.9091,"t4-cashback_s1":0.9,"t4-cashback_s2":0.9,"t4-cashback_s3":0.9}
== t1-cafe-bill s1

OK
== t1-cafe-bill s2

OK
== t1-cafe-bill s3

OK
== t2-split-bill s1

OK
== t2-split-bill s2

OK
== t2-split-bill s3

OK
== t3-shipping-fee s1

OK
== t3-shipping-fee s2

OK
== t3-shipping-fee s3

OK
== t4-cashback s1

OK
== t4-cashback s2

OK
== t4-cashback s3

OK
```

### ขั้น 2 · Bash

```
cd /tmp; sed 's#/tmp/run/#/tmp/run2/#' fuzz.py > fuzz_b.py; sed 's#/tmp/run/#/tmp/run2/#; s/10\*\*12,//' fuzz2.py > fuzz2_b.py; for p in "t1-cafe-bill cafe_bill" "t2-split-bill split_bill" "t3-shipping-fee shipping_fee" "t4-cashback cashback"; do set -- $p; for s in 1 2 3; do python3 fuzz_b.py $1 $2 $s; done; done 2>&1 | grep -v "^$" | head -30; ls /evo/solver_workspaces/epoch_2/t1-cafe-bill_s1 /evo/skills/epoch_2/*; diff -r /evo/skills/epoch_2/baankafe-solve /evo/staging/baankafe-solve && echo same
```

ผลที่ได้:

```
t1-cafe-bill 1 diffs 0
t1-cafe-bill 2 diffs 0
t1-cafe-bill 3 diffs 0
t2-split-bill 1 diffs 0
t2-split-bill 2 diffs 0
t2-split-bill 3 diffs 0
t3-shipping-fee 1 diffs 0
t3-shipping-fee 2 diffs 0
t3-shipping-fee 3 diffs 0
t4-cashback 1 diffs 0
t4-cashback 2 diffs 0
t4-cashback 3 diffs 0
/evo/skills/epoch_2/baankafe-solve:
SKILL.md
solve_template.py

/evo/solver_workspaces/epoch_2/t1-cafe-bill_s1:
solve.py
test_solve.py
same
Shell cwd was reset to /evo
```

### ขั้น 3 · Bash

```
cd /tmp; cat > cli.py <<'E'
import subprocess,json,sys
ins={'t1-cafe-bill':['{"items":[{"price":4500,"qty":2}],"member":true}','{"items":[],"member":false}','{"items":[{"price":4500,"qty":0}],"member":false}','{"items":[{"price":4500}],"member":false}','{"member":false}','[1]','nope','{"items":[{"price":4500,"qty":2}],"member":false,"x":1}','{"items":[{"price":4500.0,"qty":2}],"member":false}'],
't2-split-bill':['{"total":10000,"people":3,"tip_percent":0}','{"total":10000,"people":0,"tip_percent":0}','{"total":10000,"people":3}','{"total":1.5,"people":3,"tip_percent":0}','nope','{"total":10000,"people":3,"tip_percent":0,"x":1}'],
't3-shipping-fee':['{"weight_g":3000,"distance_km":150,"express":true}','{"weight_g":25000,"distance_km":10,"express":true}','{"weight_g":3000,"distance_km":10.5,"express":false}','{"weight_g":3000}','nope'],
't4-cashback':['{"amount":20000,"tier":"gold","birthday":true}','{"amount":20000,"tier":"x","birthday":true}','{"amount":20000.0,"tier":"gold","birthday":true}','{"amount":20000,"tier":"gold"}','[]']}
bad=0
for t,L in ins.items():
    for s in (1,2,3):
        for i in L:
            r=[subprocess.run([sys.executable,p],input=i,capture_output=True,text=True) for p in (f'/evo/reference/answers/{t}/solve.py',f'/tmp/run2/{t}_{s}/solve.py')]
            a=[(x.returncode,x.stdout.strip().split('"error"')[0]) for x in r]
            if a[0]!=a[1]: bad+=1; print(t,s,i,r[0].returncode,r[0].stdout.strip()[:80],'|',r[1].returncode,r[1].stdout.strip()[:80],r[1].stderr[-100:])
print('bad',bad)
E
python3 cli.py
```

ผลที่ได้:

```
bad 0
Shell cwd was reset to /evo
```

### ขั้น 4 · Bash

```
cd /evo/staging/baankafe-solve && python3 - <<'E'
p='SKILL.md'
s=open(p).read()
old="3. เขียน unittest เอง (`test_solve.py`) ให้ครบ 4 กลุ่ม แล้วรัน `python3 -m unittest -q test_solve` ก่อนส่ง"
assert old in s
new="3. เขียน unittest เอง ให้ครบ 4 กลุ่ม **ไว้นอกโฟลเดอร์งาน** (เช่น `/tmp/bk_test/test_mine.py`) แล้วรันด้วย `PYTHONPATH=<โฟลเดอร์งาน> python3 -m unittest -q test_mine` ก่อนส่ง — ในโฟลเดอร์งานให้เหลือไฟล์ `solve.py` ไฟล์เดียว (ห้ามวาง test_solve.py หรือไฟล์ขยะอื่นไว้ เพราะอาจชนกับเทสต์ของผู้ตรวจ)"
s=s.replace(old,new)
s=s.replace("- [ ] รัน unittest ของตัวเองผ่านทั้งหมดแล้ว","- [ ] รัน unittest ของตัวเองผ่านทั้งหมดแล้ว และโฟลเดอร์งานเหลือ `solve.py` (ไม่มี test_solve.py / __pycache__ / ไฟล์ชั่วคราว)")
open(p,'w').write(s)
E
grep -n "bk_test\|เหลือ" SKILL.md | head; echo "- epoch2: identical scores (0.9), solver == reference on fuzz+CLI. Unexplained 0.1. v3 experiment: move solver tests out of workspace (only solve.py left). If epoch3 score changes -> learn; revert if drops." >> /evo/evolver_workspace/notes.md
```

ผลที่ได้:

```
15:3. เขียน unittest เอง ให้ครบ 4 กลุ่ม **ไว้นอกโฟลเดอร์งาน** (เช่น `/tmp/bk_test/test_mine.py`) แล้วรันด้วย `PYTHONPATH=<โฟลเดอร์งาน> python3 -m unittest -q test_mine` ก่อนส่ง — ในโฟลเดอร์งานให้เหลือไฟล์ `solve.py` ไฟล์เดียว (ห้ามวาง test_solve.py หรือไฟล์ขยะอื่นไว้ เพราะอาจชนกับเทสต์ของผู้ตรวจ) คำนวณค่าคาดหวังด้วยมือ/Fraction แยกจากโค้ด อย่าเอาผลโค้ดมาเป็นคำตอบ
64:- [ ] รัน unittest ของตัวเองผ่านทั้งหมดแล้ว และโฟลเดอร์งานเหลือ `solve.py` (ไม่มี test_solve.py / __pycache__ / ไฟล์ชั่วคราว)
```

**Agent พูด:** ผมแก้สกิลเป็น v3 ใน `/evo/staging/baankafe-solve/SKILL.md` แล้ว แต่ยังหาสาเหตุที่คะแนนค้างที่ 0.9 ไม่เจอ การแก้รอบนี้จึงเป็นการทดลอง

**ผล epoch 2:** คะแนนเท่า epoch 1 ทุกโจทย์ (t3 ได้ 0.9091 ส่วนที่เหลือได้ 0.9) แม้ Solver เลิกรับ float สำหรับ `distance_km` แล้วก็ตาม

**สิ่งที่ตรวจ:**
- **เทสต์ในเฉลย:** `solve.py` ทั้ง 12 ครั้งผ่านหมด
- **อินพุตสุ่มและอินพุตผิดชนิด:** ผลตรงกับเฉลยทุกกรณีที่ลอง
- **CLI:** ผลของ `main()` ตรงกับเฉลยในอินพุตผิดรูปแบบทุกแบบที่ลอง ทั้งรหัสออกและ JSON
- **สรุป:** ในส่วนที่ผมตรวจได้ Solver ทำงานเหมือนเฉลยทุกอย่าง การที่ t3 เสียคะแนนเพราะ float `distance_km` จึงเป็นข้อสันนิษฐานที่ผิด และสาเหตุของ 0.1 ที่เหลือยังไม่ทราบ เพราะผมไม่เห็นเทสต์ซ่อน

**สิ่งที่เปลี่ยน (ทดลอง):** ข้อสันนิษฐานเดียวที่เหลือคือ `test_solve.py` ของ Solver เองที่วางไว้ในโฟลเดอร์งานอาจชนกับเทสต์ของผู้ตรวจ ใน epoch 0 ที่ไม่มีไฟล์นี้ ก็ยังบอกไม่ได้ว่า 0.1 มาจากตรงนี้หรือไม่ จึงให้ Solver เขียนเทสต์ไว้นอกโฟลเดอร์งาน (เช่น `/tmp/bk_test/`) และให้เหลือแค่ `solve.py` ในโฟลเดอร์งาน ส่วนอื่นของสกิลไม่ได้แตะ

**วิธีอ่านผลรอบหน้า:** ถ้าคะแนนขึ้นเป็น 1.0 แปลว่าไฟล์เทสต์เป็นสาเหตุ ถ้าลดลงหรือเท่าเดิม ผมจะย้อนข้อนี้กลับ เพราะรูปแบบเดิมให้ 0.9 อยู่แล้ว บันทึกอยู่ใน `evolver_workspace/notes.md`
