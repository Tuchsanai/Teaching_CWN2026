# Evolution Log

## Iteration 1 · Training 50.8%

- ทั้ง 5 trace (t1 cafe_bill, t2 split_bill, t3 shipping_fee, t4 cashback x2) ผ่านเฉพาะ contract/basic/boundary ได้ 0.40–0.60 ข้อที่พลาดซ้ำและสาเหตุ:
  - half_up: ปัดด้วย `//` (t4 x2, t2) -> สร้าง floor-instead-of-half-up
  - no_drift: ปัดทีละขั้น/ปัดก่อนคูณ 2 (t1, t4) -> สร้าง intermediate-rounding-drift (t3 ผ่านเพราะใช้ Fraction ปัดครั้งเดียว)
  - reject_type: รับ float/str/bool หรือ raise TypeError (ทั้ง 5) -> สร้าง reject-non-int-inputs-as-valueerror
  - reject_value: ไม่ตรวจ qty >= 1 (t1) -> สร้าง validate-spec-ranges-with-valueerror
  - cli_ok/cli_error: ไม่มี CLI stdin JSON (ทั้ง 5) -> สร้าง hidden-cli-contract-stdin-json
  - tests: ไม่มี test_solve.py (ทั้ง 5) -> สร้าง missing-test-solve-py
  - ทดสอบเองผ่านหมดแต่คะแนนต่ำ -> สร้าง self-check-confirms-own-assumptions
- ยังไม่มีสกิลและ skill-impact ว่าง จึงไม่มีผลรอบก่อนให้เทียบ ปัญหาทั้งหมดยังเกิดอยู่ทุกข้อ
- ข้อสังเกต: Agent เสีย 1 คำสั่งใน 3 trace เพราะใช้ `python3 -I` แล้ว import solve ไม่ได้ (บันทึกใน missing-test-solve-py)
