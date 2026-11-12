# รับ float/bool/str เป็นอินพุต หรือ raise TypeError แทน ValueError (reject_type)

## อาการ
- ข้อตรวจ `reject_type` พลาดเกือบทุกกรณี มีสองแบบ
  - ฟังก์ชันรับค่าผิดชนิดแล้วคำนวณต่อ: `cafe_bill([{"price":4500.0,"qty":1}], false)` คืน 4815, `split_bill(10000.0,2,0)` คืน [5000.0, 5000.0], `shipping_fee(1000.0,10,false)` คืน 4000, `cashback(20000,"gold","yes")` คืน 1000
  - ฟังก์ชัน raise `TypeError` แต่ตัวตรวจต้องการ `ValueError` (`cashback(20000.0,"gold",false)`)

## สาเหตุ
- โจทย์ไม่ได้เขียนว่า "ต้อง reject ชนิดผิด" Agent จึงไม่ validate หรือ validate แค่บางตัวแปร (ตรวจ `amount` แต่ไม่ตรวจ `birthday`)
- `Fraction(str(x))` หรือ `int(x)` แปลงค่าแปลก ๆ ให้ใช้ได้เงียบ ๆ
- `bool` เป็น subclass ของ `int` ดังนั้น `isinstance(True, int)` เป็น True
- Agent เลือก `TypeError` ตามความเคยชินของ Python ทั้งที่ตัวตรวจต้องการ `ValueError`

## หลักฐาน
- iteration 1: t1-cafe-bill-r2 พลาด 5/5, t2-split-bill-r1 พลาด 4/4, t3-shipping-fee-r3 พลาด 3/5, t4-cashback-r1 พลาด 4/5 (TypeError), t4-cashback-r3 พลาด 1/5 (birthday="yes")

## วิธีแก้
- ตรวจ **ทุก** พารามิเตอร์ก่อนคำนวณ และ raise `ValueError` อย่างเดียวสำหรับทุกกรณีผิด (ชนิดผิด, ค่านอกช่วง, tier ไม่รู้จัก)
- ```python
  def _int(v, name):
      if isinstance(v, bool) or not isinstance(v, int):
          raise ValueError(f"{name} must be an integer")
      return v
  ```
- flag ต้องเป็น `bool` จริง: `if not isinstance(flag, bool): raise ValueError(...)`
- `tier` ต้องเป็น `str` และอยู่ในชุดที่โจทย์ระบุ (ไม่ต้อง normalize ตัวพิมพ์)
- list/dict: ตรวจว่า `items` เป็น list, แต่ละตัวเป็น dict, มี key ครบ และ `price`/`qty` เป็น int จริง
- ปฏิเสธ float แม้ค่าเป็นจำนวนเต็ม (4500.0), None และ str
- ถ้าโจทย์ไม่ระบุว่าพารามิเตอร์ต้องเป็นจำนวนเต็ม ให้อ่านหน่วยในโจทย์ก่อน ค่าที่เป็นสตางค์หรือจำนวนชิ้นต้องเป็น int
