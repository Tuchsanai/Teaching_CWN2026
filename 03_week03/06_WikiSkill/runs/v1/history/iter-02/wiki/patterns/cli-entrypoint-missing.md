# cli-entrypoint-missing: solve.py ไม่มี CLI อ่าน stdin เป็น JSON

## อาการ
- `cli_ok` และ `cli_error` ตกใน 5 จาก 5 Trace
- ข้อความตัวตรวจ: "ได้ exit 0 stdout (ว่าง)" ทั้งกรณีปกติและกรณี input ผิด

## สาเหตุ
- ตัวตรวจรัน `python solve.py` โดยส่ง JSON ทาง stdin แต่โจทย์พูดถึงแค่ฟังก์ชัน ไม่ได้บอกว่าต้องมี CLI
- Agent เขียนแต่ฟังก์ชัน ไม่มี `if __name__ == "__main__"` สคริปต์จึงจบเงียบ ๆ ด้วย exit 0
- รูปแบบที่ตัวตรวจคาดหวังรู้ได้จากข้อความของตัวตรวจเท่านั้น ไม่ใช่จากโจทย์

## หลักฐาน
- iteration 1: ทุก Trace (t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r2)
- ตัวอย่างที่คาด: stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ได้ stdout `{"ok": true, "result": 500}` exit 0
- กรณีผิด: stdin `{"amount": 20000, "tier": "bronze", ...}` ได้ `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

## วิธีแก้
ต่อท้าย solve.py ทุกครั้ง (key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน):

```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = FUNC(**data)  # แทน FUNC ด้วยชื่อฟังก์ชันของโจทย์
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0

if __name__ == "__main__":
    sys.exit(_main())
```

แล้วรันเองทั้งกรณีปกติและกรณีผิด: `echo '{...}' | python3 solve.py; echo $?` ตรวจว่า exit code เป็น 0 และ 2 ตามลำดับ และไม่มี traceback
## สถานะรอบ 2: แก้ได้แล้ว
- `cli_ok` และ `cli_error` ผ่านทั้ง 8 Trace ที่สุ่ม ทุก Trace คัดลอกโค้ด `_main()` จากสกิล และรันทดสอบ exit=0 / exit=2 จริง
