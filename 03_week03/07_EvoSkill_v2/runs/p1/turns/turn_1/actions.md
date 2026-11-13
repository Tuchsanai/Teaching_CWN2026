# ตาที่ 1 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 02:04 UTC คุณมีเวลาถึง 2026-11-13 02:34 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 1 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v1` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; ls; cat evolver_workspace/* 2>/dev/null | head -50; ls reference staging skills/* scores traces/*| head -80; cat scores/epoch_0.json | head -50
```

ผลที่ได้:

```
evolver_workspace
reference
scores
skills
solver_workspaces
staging
traces
reference:
baankafe

scores:
epoch_0.json

skills/epoch_0:

staging:

traces/epoch_0:
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
{
 "t1-cafe-bill_s1": 0.5,
 "t1-cafe-bill_s2": 0.5,
 "t1-cafe-bill_s3": 0.5,
 "t2-split-bill_s1": 0.5,
 "t2-split-bill_s2": 0.6,
 "t2-split-bill_s3": 0.4,
 "t3-shipping-fee_s1": 0.6,
 "t3-shipping-fee_s2": 0.5,
 "t3-shipping-fee_s3": 0.6,
 "t4-cashback_s1": 0.3,
 "t4-cashback_s2": 0.3,
 "t4-cashback_s3": 0.3
}
```

### ขั้น 2 · Bash

```
cd /evo; find reference solver_workspaces -maxdepth 3 | head -60; wc -c traces/epoch_0/*
```

ผลที่ได้:

```
reference
solver_workspaces
reference/baankafe
solver_workspaces/epoch_0
reference/baankafe/tasks
solver_workspaces/epoch_0/t4-cashback_s3
solver_workspaces/epoch_0/t2-split-bill_s2
solver_workspaces/epoch_0/t3-shipping-fee_s1
solver_workspaces/epoch_0/t1-cafe-bill_s1
solver_workspaces/epoch_0/t1-cafe-bill_s3
solver_workspaces/epoch_0/t2-split-bill_s1
solver_workspaces/epoch_0/t3-shipping-fee_s3
solver_workspaces/epoch_0/t3-shipping-fee_s2
solver_workspaces/epoch_0/t1-cafe-bill_s2
solver_workspaces/epoch_0/t4-cashback_s2
solver_workspaces/epoch_0/t4-cashback_s1
solver_workspaces/epoch_0/t2-split-bill_s3
reference/baankafe/tasks/t3-shipping-fee.json
reference/baankafe/tasks/t4-cashback.json
reference/baankafe/tasks/t1-cafe-bill.json
reference/baankafe/tasks/t2-split-bill.json
solver_workspaces/epoch_0/t4-cashback_s3/solve.py
solver_workspaces/epoch_0/t2-split-bill_s2/solve.py
solver_workspaces/epoch_0/t3-shipping-fee_s1/solve.py
solver_workspaces/epoch_0/t4-cashback_s2/solve.py
solver_workspaces/epoch_0/t4-cashback_s1/solve.py
solver_workspaces/epoch_0/t2-split-bill_s3/solve.py
solver_workspaces/epoch_0/t1-cafe-bill_s1/solve.py
solver_workspaces/epoch_0/t1-cafe-bill_s3/solve.py
solv
…(ตัด 756 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /evo; cat reference/baankafe/tasks/*.json; for t in t1-cafe-bill t4-cashback; do echo "=== $t"; cat solver_workspaces/epoch_0/${t}_s1/solve.py; done
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 4
…(ตัด 1751 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /evo; python3 -c "
import json
for l in open('traces/epoch_0/t4-cashback_s1.jsonl'):
    d=json.loads(l)
    print(json.dumps(d,ensure_ascii=False)[:3000]); print('---')
"
```

ผลที่ได้:

```
{"type": "system", "subtype": "init", "cwd": "/workspace/evlab/ws/p1/legs/runs/base_train/t4-cashback-r1/sandbox", "session_id": "5950a01d-2278-449e-87a1-dbd4cbced497", "tools": ["Task", "Bash", "CronCreate", "CronDelete", "CronList", "DesignSync", "Edit", "EnterWorktree", "ExitWorktree", "ListAgents", "Monitor", "NotebookEdit", "PushNotification", "Read", "RemoteTrigger", "ReportFindings", "ScheduleWakeup", "SendMessage", "Skill", "TaskStop", "ToolSearch", "WebSearch", "Workflow", "Write", "mcp__playwright__browser_click", "mcp__playwright__browser_close", "mcp__playwright__browser_console_messages", "mcp__playwright__browser_drag", "mcp__playwright__browser_drop", "mcp__playwright__browser_emulate_media", "mcp__playwright__browser_evaluate", "mcp__playwright__browser_file_upload", "mcp__playwright__browser_fill_form", "mcp__playwright__browser_find", "mcp__playwright__browser_handle_dialog", "mcp__playwright__browser_hover", "mcp__playwright__browser_navigate", "mcp__playwright__browser_navigate_back", "mcp__playwright__browser_network_request", "mcp__playwright__browser_network_requests", "mcp__playwright__browser_press_key", "mcp__playwright__browser_resize", "mcp__playwright__
…(ตัด 14994 ตัวอักษร)
```

### ขั้น 5 · Bash

```
cd /evo/solver_workspaces/epoch_0; for t in t1-cafe-bill t2-split-bill t3-shipping-fee; do for s in 1 2 3; do echo "=== $t $s"; cat ${t}_s$s/solve.py; done; done; for s in 2 3; do echo == t4 $s; cat t4-cashback_s$s/solve.py; done
```

ผลที่ได้:

```
=== t1-cafe-bill 1
def cafe_bill(items, member):
    """Return amount due in integer satang (exact arithmetic, rounded half-up once at the end)."""
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%
    return (2 * num + den) // (2 * den)
=== t1-cafe-bill 2
def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, จำนวนเต็ม) ใช้เลขจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    num, den = subtotal, 1
    if subtotal >= 50000:      # 500 บาท = 50000 สตางค์
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100   # VAT 7%
    return (2 * num + den) // (2 * den)
=== t1-cafe-bill 3
def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (จำนวนเต็มสตางค์) คำนวณด้วยจำนวนเต็มล้วน ปัดเศษครั้งเดียวตอนท้าย"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den =
…(ตัด 4547 ตัวอักษร)
```

### ขั้น 6 · Bash

```
mkdir -p /evo/staging/money-spec-functions && cd /evo/staging/money-spec-functions && cat > SKILL.md <<'EOF'
---
name: money-spec-functions
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชันคิดเงิน/ส่วนลด/VAT/ค่าส่ง/เงินคืน/หารบิล ในไฟล์ solve.py จาก brief สั้น ๆ (หน่วยสตางค์ คืนจำนวนเต็ม) — เป็นเช็กลิสต์เรื่องการปัดเศษ การตรวจ input การเก็บเคสขอบ และการทดสอบก่อนส่ง
---

# เขียนฟังก์ชันคิดเงินจาก brief ให้ผ่านตัวตรวจแบบซ่อนเคส

จาก epoch 0: Solver เขียนสูตรถูกตามตัวอักษรแต่ได้ไม่เต็ม (0.3–0.6) เพราะ
(1) ไม่เคยรันทดสอบเลย (2) เลือกวิธีปัดเศษเอาเอง บางแบบเสียคะแนน (3) ตัวตรวจน่าจะลองค่านอกโดเมน
ตัวอย่างหลักฐาน: เวอร์ชันที่ตรวจ input แล้ว `raise ValueError` ได้คะแนนสูงกว่าเวอร์ชันที่ไม่ตรวจเล็กน้อย
และเวอร์ชันที่ปัดทิป "ลง" ได้ต่ำกว่าเวอร์ชันที่ปัด "ครึ่งขึ้น"

## ขั้นตอน

1. **อ่าน brief ทีละบรรทัด แล้วทำตารางกฎ** ทุกตัวเลข/เงื่อนไข = 1 กฎ ระบุให้ชัดว่า
   - หน่วย (บาท vs สตางค์ — แปลงให้ครบ เช่น 500 บาท = 50000 สตางค์, 15 บาท/กก. = 1.5 สตางค์/กรัม)
   - เงื่อนไขขอบ: "ตั้งแต่ X" = `>=`, "เกิน X" = `>`, "ไม่เกิน X" = `<=`, "ต่ำกว่า X" = `<`
   - ลำดับการคิด: "บวก VAT เป็นขั้นสุดท้าย", "คูณต่อจากข้อก่อน" → คูณทบกันตามลำดับ
   - เกณฑ์ (threshold) ใช้กับค่าอะไร (เช่น ยอดรวมก่อนลด) — ถ้า brief ไม่บอก ให้ใช้ค่าดิบก่อนปรับใด ๆ
   - ลำดับ cap/เพดานเทียบกับตัวคูณ (เช่น คูณ 2 ตอนเดือนเกิด *ก่อน* แล้วค่อย cap)
2. **ใช้เลขจำนวนเต็ม/`Fraction` ล้วน ห้าม float** (`0.07`, `1.5` ให้เขียนเป็นอัตราส่วนจำนวนเต็ม)
   ถ้า input เป็น float (เช่น ระยะทาง) ให้เทียบเกณฑ์ตรง ๆ ได้ แต่ถ้าต้องคูณให้แปลงด้วย `Fraction(str(x))`
3. **การปัดเศษ — ค่าเริ่มต้นเมื่อ brief ไม่ระบุ**
   - ปัดแบบ "ครึ่งขึ้น" (round half up → `(2*num + den)//(2*den)` สำหรับค่าไม่ติดลบ) **ครั้งเดียวที่ค่าเงินสุดท้าย**
     ห้ามปัดกลางทางทุกขั้น ห้ามใช้ `round()` ของ Python (เป็น banker's rounding) ห้ามใช้ `//` ตรง ๆ (ปัดลง)
     ยกเว้น brief บอกชัดว่าปัดลง/ปัดขึ้น/ปัดทุกขั้น ให้ทำตาม brief
   - เคสหารบิล: ปัดทิปครึ่งขึ้นเป็นสตางค์ก่อน แล้ว `divmod(grand, people)` แจก 1 สตางค์ให้คนแรก ๆ
     ผลรวมของ list ต้องเท่ากับยอดรวมเสมอ (ตรวจด้วย assert ในเทสต์)
   - ผลลัพธ์ต้องเป็น `int` ของ Python เท่านั้น (ไม่ใช่ float/Fraction/bool)
4. **ตรวจ input ตามโดเมนที่ brief ประกาศไว้** (ตัวตรวจน่าจะลองค่านอกช่วง)
   - ทุกครั้งที่ brief เขียนช่วง/ขั้นต่ำ เช่น "ตั้งแต่ 1", "ตั้งแต่ 0", "0–100", "1–30,000", ค่าที่เป็นได้เพียงไม่กี่ค่า (tier)
     ให้ `raise ValueError(...)` เมื่อหลุดช่วง/ไม่รู้จักค่า — ทำให้ครบทุกพารามิเตอร์ ไม่ใช่แค่ตัวเดียว
     (เช่น cashback: amount < 0 ก็ต้อง ValueError ไม่ใช่เฉพาะ tier แปลก)
   - ปฏิเสธ `bool` ในช่อง
…(ตัด 1444 ตัวอักษร)
```

ผลที่ได้:

```
SKILL.md
```

### ขั้น 7 · Bash

```
cat > helpers.py <<'EOF'
"""ตัวอย่างเครื่องมือ (อ่านอย่างเดียว) — คัดลอกไปใช้ใน solve.py ได้
"""
from fractions import Fraction


def round_half_up(x):
    """ปัดครึ่งขึ้นสำหรับค่าไม่ติดลบ (รับ int/Fraction) คืน int"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def check_int(name, v, lo=None, hi=None):
    """ตรวจจำนวนเต็ม (ไม่รับ bool) และช่วงค่า ไม่ผ่านให้ ValueError"""
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an int, got {v!r}")
    if lo is not None and v < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return v
EOF
echo "epoch1: wrote money-spec-functions skill (validation+half-up+run tests). Hypothesis: validation +0.1, floor tip -0.1. Check epoch1 scores to confirm." > /evo/evolver_workspace/notes.txt
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `skills_v1` ลงใน `/evo/staging/` แล้ว มีสกิลเดียวคือ `money-spec-functions` (`SKILL.md` กับ `helpers.py` ตัวช่วยที่ Solver คัดลอกไปใช้ได้) ตอนนี้ยังไม่มีคะแนนของ epoch 1 มาเทียบ จึงยังไม่รู้ว่าได้ผลหรือไม่

**สิ่งที่เห็นใน epoch 0**
- คะแนนอยู่ระหว่าง 0.3 ถึง 0.6 ในทุกโจทย์ ทั้งที่สูตรที่ Solver เขียนตรงกับ brief
- Solver ไม่เคยรันทดสอบเลย ทุก rollout เขียน `solve.py` แล้วจบทันที
- ผมสันนิษฐานว่าตัวตรวจลองค่านอกโดเมน แต่ยังไม่แน่ใจ หลักฐานคือเวอร์ชันที่ตรวจ input แล้ว raise `ValueError` ได้คะแนนสูงกว่าเล็กน้อย
  - split-bill: ตรวจ input ได้ 0.6 ไม่ตรวจได้ 0.5
  - shipping-fee: ตรวจ input ได้ 0.6 ไม่ตรวจได้ 0.5
- การปัดเศษส่งผลเหมือนกัน เวอร์ชัน split-bill ที่ปัดทิปลงได้ 0.4 ส่วนที่ปัดครึ่งขึ้นได้ 0.5–0.6
- cashback ได้ 0.3 ทั้งสามครั้ง และ Solver ปัดเศษลงทุกครั้ง ผมยังไม่รู้สาเหตุแน่ชัด จึงเดาว่าเป็นเรื่องการปัดเศษหรือการตรวจ input

**สิ่งที่สกิลสอน**
- ให้ทำตารางกฎจาก brief ก่อน แปลงหน่วยให้ครบ และระวังคำว่า "ตั้งแต่", "เกิน", "ไม่เกิน"
- ใช้ `Fraction` หรือจำนวนเต็มล้วน แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย เมื่อ brief ไม่ระบุวิธีปัด
- ตรวจ input ทุกพารามิเตอร์ตามช่วงที่ brief ประกาศ แต่ไม่ตรวจเกินจนปฏิเสธค่าที่ถูกต้อง
- เทียบกับ reference แบบ `Fraction` บนเคสสุ่มและเคสขอบ ก่อนส่งงาน
- สรุปปิดงานโดยบอกว่าตีความจุดกำกวมอย่างไร และอ้างเฉพาะการทดสอบที่รันจริง

สกิลนี้เขียนเป็นเช็กลิสต์ทั่วไปสำหรับโจทย์ประเภทเดียวกัน ไม่ได้ผูกกับโจทย์ train ทั้งสี่ข้อ ผมจดสมมติฐานไว้ที่ `/evo/evolver_workspace/notes.txt` เพื่อเทียบกับคะแนน epoch 1
