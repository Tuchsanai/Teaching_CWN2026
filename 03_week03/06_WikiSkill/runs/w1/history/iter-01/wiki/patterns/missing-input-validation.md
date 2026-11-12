# missing-input-validation

## อาการ
- `reject_value` และ `reject_type` ล้มทุก trace
- ค่าที่ไม่ถูกต้องผ่านเข้าไปคำนวณ: `cashback(-1,...)` คืน 0, `shipping_fee(0,...)` คืน 4000, `cafe_bill` qty=0 คืน 0
- float ผ่านเงียบ ๆ: `cashback(20000.0,...)` คืน `500.0`, `split_bill(10000.0,2,0)` คืน `[5000.0, 5000.0]`
- บางกรณี raise ผิดชนิด: `split_bill(10000, 0, 0)` ได้ `ZeroDivisionError` แต่ต้องเป็น `ValueError`

## สาเหตุ
- โจทย์ระบุช่วงค่าที่ถูกต้อง (เช่น people ตั้งแต่ 1, weight 1–30,000, qty ตั้งแต่ 1, tip 0–100, tier 3 ค่า) แต่ไม่ได้สั่งให้ปฏิเสธค่านอกช่วง
- Agent ถือว่าช่วงค่าเป็นแค่คำอธิบาย ไม่ใช่เงื่อนไขที่ต้อง raise
- ตัวตรวจถือว่า ช่วงค่า + ชนิดข้อมูลที่โจทย์ระบุ = สิ่งที่ต้องบังคับด้วย `ValueError`

## หลักฐาน
- t4-cashback-r1 / r3: reject_value พลาด 3/3, reject_type พลาด 5/5
- t2-split-bill-r1: reject_value พลาด 5/5 (ZeroDivisionError), reject_type พลาด 4/4
- t3-shipping-fee-r3: reject_value พลาด 4/4, reject_type พลาด 5/5 (`1000.0` ผ่านเข้าไป)
- t1-cafe-bill-r1: reject_value พลาด 3/3 (qty 0), reject_type พลาด 5/5 (price `4500.0`)

## วิธีแก้
ตรวจทุกพารามิเตอร์ก่อนคำนวณและก่อนหารใด ๆ แล้ว raise `ValueError` เสมอ:

```python
def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be an int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x
```
- ทุกช่วงที่โจทย์เขียนไว้ต้องมีเงื่อนไขตรวจ (ขอบล่าง ขอบบน และ enum เช่น tier)
- ชนิด: ปฏิเสธ float, str, None และ `bool` ในช่องที่เป็นจำนวนเต็ม
- ช่อง flag (`birthday`, `express`, `member`) ตรวจให้เป็น `bool` ไว้ก่อนเพื่อความปลอดภัย (หลักฐานยังไม่ยืนยันว่าตัวตรวจทดสอบข้อนี้)
- list ซ้อน dict (`items`): ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และตรวจชนิด/ช่วงของ `price`/`qty` ทุกตัว
- ห้ามให้ `KeyError`/`ZeroDivisionError` หลุด ต้องตรวจก่อนถึงบรรทัดนั้น
