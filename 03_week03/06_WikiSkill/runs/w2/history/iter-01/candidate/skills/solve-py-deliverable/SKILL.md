---
name: solve-py-deliverable
description: เช็กลิสต์และโครง solve.py สำหรับงานเขียนฟังก์ชันคิดเงินร้านกาแฟ BaanKafe ให้ครบ 3 ส่วนที่ตัวตรวจคาดแม้โจทย์ไม่บอก คือตรวจอินพุตแล้ว raise ValueError, มี CLI อ่าน JSON จาก stdin และมี test_solve.py ใช้ทุกครั้งที่ต้องเขียน solve.py
---

# solve.py ที่ส่งงานได้ครบ

ตัวตรวจไม่ได้ดูแค่สูตรคำนวณ โจทย์มักไม่เขียนข้อกำหนดต่อไปนี้ แต่ตัวตรวจคาดเสมอ ต้องทำให้ครบทั้ง 4 ข้อก่อนส่งงาน

## 0. การคำนวณ (คงวิธีนี้ไว้)
- เงินทุกจำนวนเป็นสตางค์ (`int`) หรือ `Fraction` ห้ามใช้ `float`
- ต่อเปอร์เซ็นต์หลายขั้นด้วยการคูณตัวเศษ/ตัวส่วนสะสม แล้วปัดเศษครั้งเดียวตอนท้าย (ยกเว้นโจทย์สั่งให้ปัดทีละขั้น)
- ถ้าโจทย์ไม่ระบุวิธีปัด ให้ปัดครึ่งขึ้นด้วยจำนวนเต็ม: `(2 * num + den) // (2 * den)` (ใช้กับค่าไม่ติดลบ)
- ผลลัพธ์เป็น `int` เสมอ (หรือ list ของ `int`)

## 1. ตรวจอินพุตก่อนคำนวณ (ตัวตรวจจะลองค่านอกช่วงและชนิดผิด)
อ่านโจทย์ทีละตัวแปร ทุกช่วงค่าที่เขียนในวงเล็บ (เช่น "ตั้งแต่ 1", "ตั้งแต่ 0", "1–30,000", "0–100") และทุกชุดค่าที่อนุญาต (เช่น tier ที่มีให้เลือก) คือเงื่อนไขที่ต้องบังคับ ไม่ใช่แค่คำอธิบาย

- ผิดช่วงหรือผิดชนิดทุกกรณี ให้ `raise ValueError("ข้อความ")` ห้ามปล่อยให้เป็น `TypeError`, `KeyError`, `ZeroDivisionError`
- ชนิดต้องเข้ม: ช่องจำนวนเต็มต้องเป็น `int` จริง ไม่รับ `float` (แม้ `20000.0`) และไม่รับ `bool` ช่องที่ควรเป็น bool ต้องเป็น `bool` จริง ช่องข้อความต้องเป็น `str`
- ถ้าอินพุตซ้อน (เช่น list ของ dict) ตรวจว่าเป็น list/dict, มี key ครบ และตรวจชนิดกับช่วงของทุกสมาชิก
- ตรวจที่ต้นฟังก์ชัน **ก่อน** early return หรือการหาร (เช่นก่อน `if amount < 10000: return 0`) ไม่เช่นนั้นค่าติดลบจะหลุดไปเป็น 0
- ค่า "ไม่ถึงเกณฑ์" ที่โจทย์ให้คืนค่าปกติ (เช่นได้เงินคืน 0) ไม่ใช่ค่าผิด แยกให้ออกจาก "อยู่นอกช่วงที่รับได้"

ตัวช่วยตรวจ:

```python
def _int(name, v, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้อง >= {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้อง <= {hi}")
    return v

def _bool(name, v):
    if not isinstance(v, bool):
        raise ValueError(f"{name} ต้องเป็น bool")
    return v
```

## 2. CLI ท้ายไฟล์ solve.py (ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin)
อินพุตเป็น JSON object ที่ key ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน ผลลัพธ์ต้องเป็น JSON บรรทัดเดียวบน stdout

```python
if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = FUNC(**data)   # แทน FUNC ด้วยชื่อฟังก์ชันของโจทย์
    except (ValueError, TypeError, KeyError) as e:   # JSONDecodeError เป็น ValueError อยู่แล้ว
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
```

- สำเร็จ: `{"ok": true, "result": ...}` exit 0 · ล้มเหลว: `{"ok": false, "error": "..."}` exit 2 และห้ามมี traceback
- ครอบด้วย `if __name__ == "__main__":` เพื่อให้ `from solve import ...` ยังใช้เป็นโมดูลได้

## 3. สร้าง test_solve.py ข้าง solve.py (ตัวตรวจเช็กว่ามีไฟล์นี้)
ใช้ `unittest` (ไม่ต้องติดตั้งอะไร) ให้ครอบ:
- ตัวอย่างพื้นฐานตามโจทย์ และค่าที่ขอบเงื่อนไขทุกจุด (พอดี / ต่ำกว่า / สูงกว่าเกณฑ์)
- กรณีปัดเศษ
- กรณี `assertRaises(ValueError)`: ต่ำกว่าช่วง เกินช่วง float ที่ค่าเป็นจำนวนเต็ม bool ในช่องตัวเลข ชนิดผิดในช่อง str/bool
- CLI ผ่าน `subprocess.run([sys.executable, "solve.py"], input=..., capture_output=True, text=True)` อย่างน้อย 1 กรณีสำเร็จ (exit 0) และ 1 กรณีผิด (exit 2, stdout เป็น `{"ok": false, ...}`)
- ค่าคาดหมายในเทสให้คิดด้วยมือจากข้อความโจทย์ ไม่ใช่คัดผลที่โค้ดคืนมา

## 4. ตรวจก่อนส่ง (ต้องรันจริง)
1. `python -m unittest` ในโฟลเดอร์งาน ต้องผ่านทั้งหมด
2. `echo '{...กรณีปกติ...}' | python solve.py; echo $?` ต้องได้ JSON `ok: true` และ 0
3. `echo '{...กรณีผิด เช่น ค่าติดลบ...}' | python solve.py; echo $?` ต้องได้ JSON `ok: false` และ 2 ไม่มี traceback
4. ไล่ทุกข้อกำหนดและทุกช่วงค่าในโจทย์เทียบกับโค้ดทีละข้อ ว่ามีเงื่อนไขตรวจครบ
5. มีไฟล์ `solve.py` และ `test_solve.py` อยู่โฟลเดอร์เดียวกัน
