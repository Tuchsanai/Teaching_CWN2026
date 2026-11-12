# input-validation-missing

## อาการ
- `reject_value`: ส่งค่านอกช่วง (`weight_g=0`, `qty=0`, `people=0`, `amount=-1`) แล้วฟังก์ชันคืนค่าปกติ (0, 4000) หรือ raise `ZeroDivisionError` แทน `ValueError`
- `reject_type`: ส่ง float ที่ค่าเป็นจำนวนเต็ม (`20000.0`, `1000.0`, `4500.0`) แล้วฟังก์ชันคืนค่าปกติ เช่น `4815.0` หรือ `[5000.0, 5000.0]`
- ตัวตรวจทั้งสองข้อนี้ล้มทั้ง 5 trace

## สาเหตุ
- โจทย์บอกแค่ช่วงค่าที่ถูกต้อง ("ตั้งแต่ 1", "1–30,000", "จำนวนเต็ม 0–100") ไม่ได้เขียนว่าต้อง `raise ValueError` Agent จึงถือว่าอินพุตถูกเสมอ
- ตัวตรวจคาดว่าอินพุตที่ผิดช่วงหรือผิดชนิดทุกแบบต้องได้ `ValueError` ไม่ใช่ `TypeError` หรือ `ZeroDivisionError`
- ใน cashback Agent ตรวจแค่ `tier` ที่ไม่รู้จัก ไม่ตรวจ `amount` กับ `birthday`
- ลำดับผิด: เช็ค `amount < 10000 → return 0` ก่อนตรวจ `amount < 0` ทำให้ `-1` ได้ 0

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2: `cashback(-1, "gold", false)` ต้อง raise แต่คืน 0 · `cashback(20000.0, ...)` คืน 500 หรือ 500.0
- iter 1 · t3-shipping-fee-r2: `shipping_fee(0, 10, false)` คืน 4000 · พลาด 4/4 กรณี และ reject_type พลาด 5/5
- iter 1 · t2-split-bill-r4: `split_bill(10000, 0, 0)` raise `ZeroDivisionError` · `split_bill(10000.0, 2, 0)` คืน `[5000.0, 5000.0]`
- iter 1 · t1-cafe-bill-r1: `qty: 0` คืน 0 · `price: 4500.0` คืน 4815.0

## วิธีแก้
ตรวจอินพุตทุกตัวเป็นอย่างแรกของฟังก์ชัน ก่อนกติกาธุรกิจใด ๆ (รวมทั้งทางลัดที่ return 0)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข โดยเอาช่วงจากโจทย์ ("ตั้งแต่ 0" → `lo=0`, "ตั้งแต่ 1" → `lo=1`)
- ปฏิเสธ `bool` ในช่องตัวเลข (เพราะ `True` เป็น `int`) และปฏิเสธค่าที่ไม่ใช่ `bool` ในช่อง flag เช่น `birthday`, `member`, `express` (ข้อนี้ยังไม่ยืนยันจากตัวตรวจ ทำไว้กันพลาด)
- ตรวจ enum (`tier`) และโครงสร้าง list/dict (ต้องมี key `price`, `qty`) ด้วย โดยให้ raise `ValueError` ทั้งหมด
- กรณีหารด้วยตัวแปร ตรวจช่วงก่อนหาร จะได้ไม่เจอ `ZeroDivisionError`
## อัปเดต iter 2: แก้ได้แล้ว
- `reject_value` และ `reject_type` ผ่าน 8/8 trace (t1-r1, t1-r3, t1-r5, t2-r4, t3-r2, t4-r4, t4-r5, t4-r6) ทุกตัวใช้ `_int` / `_flag` ตามสกิล และตรวจอินพุตก่อนทางลัด return 0
- ช่วงที่โจทย์ไม่ได้ระบุ (เช่น `price` ตั้ง `lo=0`, list ว่างคืน 0) ไม่ทำให้ตัวตรวจล้ม
