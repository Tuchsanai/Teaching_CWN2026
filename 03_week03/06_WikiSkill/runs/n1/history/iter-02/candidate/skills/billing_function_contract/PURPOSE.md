# PURPOSE

## Origin
สร้างจาก Trace iteration 1 (t1–t4 ทุก rollout) ที่ไม่มีสกิล Agent เขียนฟังก์ชันถูกตรงตามโจทย์ แต่ตัวตรวจต้องการสิ่งที่โจทย์ไม่ได้บอก

## Problems Addressed
- `reject_value` / `reject_type`: ไม่ตรวจอินพุต ปล่อย float, bool, ค่านอกช่วงผ่าน หรือเกิด ZeroDivisionError แทน ValueError
- `cli_ok` / `cli_error`: ไม่มี `__main__` ที่อ่าน stdin JSON และพิมพ์ `{ok,result|error}` พร้อม exit 2
- `tests`: ไม่มี test_solve.py
- `half_up` / `no_drift`: บาง rollout ปัดลงด้วย `//` ทำให้ 250.5 เป็น 250

## Evolution History
- v1: สร้างครั้งแรก

v2: จาก Trace iteration 2 (t1, t2-r3, t3 ทุก rollout) พลาดเฉพาะข้อ `tests` เพราะเขียนเทสต์ 4–5 เมธอด (รวมหลาย assert ไว้ในเมธอดเดียว) ขณะที่ตัวตรวจต้องการอย่างน้อย 6 เมธอด ส่วน rollout ที่ผ่านมี 6 เมธอดพอดี จึงระบุจำนวนขั้นต่ำและรายการเมธอดที่ต้องแยก พร้อมให้เช็ก `Ran N tests` ก่อนจบงาน
