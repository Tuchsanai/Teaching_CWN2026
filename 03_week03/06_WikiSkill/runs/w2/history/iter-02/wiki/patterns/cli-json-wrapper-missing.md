# cli-json-wrapper-missing

## อาการ
- `cli_ok` และ `cli_error` ล้มทุก trace: ส่ง JSON ทาง stdin แล้วได้ exit 0 และ stdout ว่าง
- `solve.py` มีแต่ฟังก์ชัน ไม่มีโค้ดที่อ่าน stdin เลย

## สาเหตุ
- โจทย์เขียนแค่ "ฟังก์ชัน `xxx(...)` ในไฟล์ `solve.py`" ไม่ได้บอกว่าต้องรันเป็น CLI ได้ด้วย ข้อกำหนดนี้อยู่ในตัวตรวจเท่านั้น
- Agent ทำตามตัวอักษรของโจทย์และไม่ได้คิดถึงวิธีที่ตัวตรวจจะเรียกใช้
- ไม่มีสกิลบอกข้อกำหนดนี้ (รอบ 1 ไม่มีสกิล และ `./skills` ไม่มีอยู่)

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2, t3-shipping-fee-r2, t2-split-bill-r4, t1-cafe-bill-r1: ล้มครบ 5/5
- ตัวอย่างข้อความตัวตรวจ: stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ต้องได้ `{"ok": true, "result": 500}` exit 0
- error: stdin มี `tier` เป็น `bronze` หรือ `people: 0` ต้องได้ `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

## วิธีแก้
ต่อท้าย `solve.py` ทุกครั้ง โดยใช้ชื่อพารามิเตอร์เดียวกับ key ของ JSON ในโจทย์
```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))

if __name__ == "__main__":
    _main()
```
- แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์ (JSON ที่พังก็ต้องได้ exit 2 ไม่ใช่ traceback)
- ทดสอบเอง: `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติ (ต้อง exit 0) และกรณีผิด (ต้อง exit 2 และ stdout เป็น JSON)
## อัปเดต iter 2: แก้ได้แล้ว
- `cli_ok` และ `cli_error` ผ่าน 8/8 trace หลังสกิลใส่โค้ด `_main()` ให้คัดลอก Agent ทุกตัววางต่อท้าย solve.py และรันทดสอบทั้ง exit 0 และ exit 2 ก่อนจบ
