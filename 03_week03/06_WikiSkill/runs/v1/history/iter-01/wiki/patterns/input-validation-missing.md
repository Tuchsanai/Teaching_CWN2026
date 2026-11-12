# input-validation-missing: ไม่ตรวจ input ทำให้ไม่ raise ValueError

## อาการ
- ข้อตรวจ `reject_value` และ `reject_type` ตกเกือบทุกกรณีในทุก Trace (5 จาก 5 Trace)
- ค่าที่ผิดช่วงถูกคำนวณต่อจนได้ตัวเลข เช่น `cafe_bill` qty=0 คืน 0, `shipping_fee(0,...)` คืน 4000, `cashback(-1,...)` คืน 0
- ค่าที่ชนิดผิดผ่านไปได้ เช่น 20000.0 ได้ 500.0 กลับมาเป็น float
- หารด้วยศูนย์ ทำให้เกิด `ZeroDivisionError` แทน `ValueError` (`split_bill` people=0)

## สาเหตุ
- โจทย์บอกแค่ช่วงค่าที่ถูกต้อง (เช่น "น้ำหนัก 1–30,000", "จำนวนคนตั้งแต่ 1") แต่ไม่ได้สั่งให้ reject ตัวตรวจจึงคาดหวังเองว่าค่านอกช่วงต้อง raise `ValueError`
- Agent ทำเฉพาะ happy path และตรวจแค่ tier ที่ไม่รู้จัก (t4) ไม่ตรวจ amount ที่ติดลบหรือชนิดข้อมูล
- ใน t4 การ early-return `amount < MIN_AMOUNT -> 0` มาก่อนการตรวจช่วงค่า จึงกลืนค่า -1

## หลักฐาน
- iteration 1: t1-cafe-bill-r1 (qty=0 คืน 0, price 4500.0 คืน 4815.0), t2-split-bill-r1 (people=0 ได้ ZeroDivisionError), t3-shipping-fee-r3 (weight 0 คืน 4000, 1000.0 คืน 4000), t4-cashback-r1 และ r2 (-1 คืน 0, 20000.0 คืน 500.0)
- ข้อความตัวตรวจ: "ต้อง raise ValueError แต่คืนค่า ..."

## วิธีแก้
1. ตรวจ input ที่ต้นฟังก์ชัน ก่อนคำนวณและก่อน early-return ใด ๆ
2. ชนิด: ใช้ `type(x) is int` สำหรับค่าจำนวนเต็ม (ปฏิเสธ float และ bool ซึ่งเป็น subclass ของ int) ใช้ `type(x) is bool` กับ flag เช่น `member` `express` `birthday`
3. ช่วงค่า: ตรวจตามที่โจทย์ระบุทุกตัว (เช่น weight 1–30000, tip 0–100, people >= 1, amount >= 0, qty >= 1)
4. ค่าเลือก (enum) เช่น tier ต้องอยู่ในชุดที่กำหนด
5. โครงสร้าง: ถ้ารับ list ของ dict ต้องตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ แล้วตรวจแต่ละฟิลด์เหมือนข้อ 2–3
6. ทุกกรณีผิดต้อง `raise ValueError("...")` ไม่ปล่อยให้เป็น `TypeError` `ZeroDivisionError` หรือ `KeyError`
