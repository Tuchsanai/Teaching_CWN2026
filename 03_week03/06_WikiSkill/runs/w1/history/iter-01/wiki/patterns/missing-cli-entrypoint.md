# missing-cli-entrypoint

## อาการ
- `cli_ok` และ `cli_error` ล้มทุก trace (5 จาก 5) ข้อความตัวตรวจ: `ได้ exit 0 stdout (ว่าง)`
- `solve.py` มีแต่ฟังก์ชัน ไม่มีโค้ดที่อ่าน stdin หรือพิมพ์ผลลัพธ์

## สาเหตุ
- โจทย์พูดถึงแต่ฟังก์ชัน แต่ตัวตรวจเรียก `python solve.py` แล้วส่ง JSON ทาง stdin (key = ชื่อพารามิเตอร์ของฟังก์ชัน)
- Agent ไม่รู้ข้อตกลงนี้และไม่มีสกิลบอก จึงไม่เขียน CLI ส่วนนี้

## หลักฐาน
- iteration 1 ทุก trace: t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r3
- ตัวอย่าง t4: stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ต้องได้ `{"ok": true, "result": 500}` exit 0 แต่ได้ stdout ว่าง
- t4 `cli_error` (tier "bronze") ต้องได้ `{"ok": false, "error": "..."}` exit 2 ไม่มี traceback
- Agent ไม่เคยรัน `python solve.py` เลยจึงไม่เห็นปัญหา

## วิธีแก้
ต่อท้าย `solve.py` เสมอ (ปรับชื่อฟังก์ชันและ key ตามโจทย์):

```python
import json, sys

def main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(data['amount'], data['tier'], data['birthday'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0

if __name__ == '__main__':
    sys.exit(main())
```
- JSON เสีย (`JSONDecodeError`) เป็น subclass ของ ValueError จึงถูกจับด้วย
- ห้ามให้ traceback ออก ต้องจับ error แล้วพิมพ์ JSON บรรทัดเดียว
- ทดสอบเองด้วย `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติและกรณีผิด
