---
name: deliverable-format
description: ใช้ทุกครั้งที่ต้องส่งงานเป็นไฟล์ solve.py (และไฟล์ประกอบ) ของโจทย์ฟังก์ชันร้าน BaanKafe — รูปแบบไฟล์ที่ควรส่งให้ครบ ได้แก่ ฟังก์ชัน, main() อ่าน JSON จาก stdin, และ test_solve.py
---

# รูปแบบการส่งงานให้ครบ

หลัง epoch 1 สูตรและการตรวจอินพุตถูกต้องแล้ว แต่ยังได้ ~0.7 ทุกข้อ แม้โค้ดเหมือนเฉลยทุกบรรทัด แปลว่ามีเกณฑ์ส่วนหนึ่ง (~30%) ที่ Solver ยังไม่ได้ทำ จากโครงของเฉลยอ้างอิง สิ่งที่ขาดอยู่ที่น่าจะเป็นไปได้ที่สุดคือ **ส่วนห่อรอบฟังก์ชัน** และ **ไฟล์เทสต์** ทำให้ครบทั้งคู่ (ไม่มีโทษ ถ้าไม่ได้ใช้):

## 1. `solve.py` ต้องมี
- ฟังก์ชันตามชื่อในโจทย์ (import ได้โดยไม่มี side effect)
- `main()` สำหรับรันจาก CLI: อ่าน JSON object จาก stdin เป็น keyword arguments แล้วพิมพ์ JSON หนึ่งบรรทัด
  - สำเร็จ: `{"ok": true, "result": <ค่า>}` exit code 0
  - ValueError/TypeError: `{"ok": false, "error": "<ข้อความ>"}` exit code 2
  - input ที่ไม่ใช่ JSON object → ถือเป็น error แบบเดียวกัน
- `if __name__ == "__main__": sys.exit(main())`

```python
import json, sys

def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = FUNC(**args)          # FUNC = ชื่อฟังก์ชันของโจทย์
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0
```
(json.JSONDecodeError เป็น subclass ของ ValueError อยู่แล้ว) ทดสอบด้วย `echo '{"items":[{"price":4500,"qty":2}],"member":false}' | python3 solve.py`

## 2. `test_solve.py` (unittest) ข้างกัน
เขียนเทสต์ 4 กลุ่ม: Normal (3), Boundary (ทั้งสองฝั่งของทุกเกณฑ์), NoDrift (ค่าที่ปัดเศษครึ่งพอดีหรือใกล้ — คำนวณมือแบบ Fraction เทียบ), Reject (ติดลบ, 0 ที่ไม่อนุญาต, float, str, bool, enum ผิด → `assertRaises(ValueError)`) รันด้วย `PYTHONPATH=. python3 -m unittest -q test_solve` ให้ผ่านก่อนจบ

## 3. สรุปตอนจบ
บอกสมมติฐานที่ใช้ตอน brief เงียบ (เช่น ทิศการปัด, กฎแฝง) สั้น ๆ — ตัดสินใจเองตามสกิล `baankafe-money-rules` ไม่ต้องถามผู้ใช้กลับ
