# missing-cli-entrypoint: solve.py ไม่มีโหมดสั่งรันจาก stdin จึงไม่มี output และ exit 0 เสมอ

## อาการ
- `cli_ok` ตก: `stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)`
- `cli_error` ตก: `stdin {... "tier": "bronze" ...} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)`
- ตกทั้ง 5 งาน รูปแบบอาการเหมือนกันหมด (stdout ว่าง exit 0)

## สาเหตุ
- โจทย์พูดถึงแค่ฟังก์ชัน Python ในไฟล์ `solve.py` ไม่ได้บอกว่าต้องรันเป็นสคริปต์ได้ แต่ตัวตรวจรัน `python solve.py` โดยส่ง JSON ทาง stdin และอ่าน JSON จาก stdout ตามสัญญาที่ไม่ได้เขียนไว้ในโจทย์
- Agent เขียนแต่ `def` อย่างเดียว ไม่มี `if __name__ == "__main__":` เมื่อไฟล์ถูกรันเฉย ๆ จึงไม่ทำอะไรและจบด้วย exit 0
- รูปแบบอินพุตที่ตัวตรวจส่งมาคือ JSON object ที่ key ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน (เช่น `{"items": [...], "member": false}`) ผลลัพธ์ที่คาดคือ `{"ok": true, "result": <ค่าที่ฟังก์ชันคืน>}` (result อาจเป็นจำนวนเต็มหรือ list เช่น `[3334, 3333, 3333]`)

## หลักฐาน
งานที่ล้ม (ทุกงาน ไม่มีงานผ่านให้เทียบ):
- t4-cashback-r1, t4-cashback-r3, t3-shipping-fee-r3, t1-cafe-bill-r1, t2-split-bill-r1: ไฟล์ `solve.py` ที่เขียนมีเฉพาะนิยามฟังก์ชัน (และค่าคงที่) ไม่มีโค้ดอ่าน stdin หรือ print ใด ๆ
- ทั้งหมดได้ `exit 0 stdout (ว่าง)` ตรงกับไฟล์ที่ไม่มี entrypoint

## วิธีแก้
เพิ่ม entrypoint ท้ายไฟล์ `solve.py` ทุกครั้ง แม้โจทย์ไม่ได้พูดถึง:
1. อ่าน stdin ทั้งก้อนด้วย `json.loads(sys.stdin.read())` ได้ dict แล้วเรียกฟังก์ชันด้วย key ตามชื่อพารามิเตอร์ เช่น `result = cashback(**data)`
2. สำเร็จ: `print(json.dumps({"ok": True, "result": result}))` แล้ว exit 0
3. ล้มเหลว: จับ `ValueError` และข้อผิดพลาดจากอินพุตที่พังรูปแบบ (JSON เสีย, key ขาด/เกิน → `json.JSONDecodeError`, `KeyError`, `TypeError`) แล้ว `print(json.dumps({"ok": False, "error": str(e)}))` และ `sys.exit(2)` ห้ามปล่อยให้เกิด traceback ออก stderr/stdout
4. ครอบด้วย `if __name__ == "__main__":` เพื่อให้ `from solve import ...` ยังใช้เป็นโมดูลได้โดยไม่รันอะไร
5. ทดสอบเอง: `echo '{...}' | python solve.py; echo $?` อย่างน้อยหนึ่งกรณีสำเร็จ (ต้องได้ exit 0 และ JSON ถูกรูปแบบ) และหนึ่งกรณีผิด (ต้องได้ exit 2 และ `{"ok": false, ...}` ไม่มี traceback)
6. ทำควบคู่กับหน้า missing-input-validation เพราะกรณีผิดของ CLI ส่วนใหญ่มาจาก `ValueError` ที่ฟังก์ชัน raise
