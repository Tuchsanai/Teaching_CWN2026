# ไม่มี CLI สำหรับ stdin JSON ใน solve.py (cli_ok / cli_error)

## อาการ
- `cli_ok` และ `cli_error` พลาดทุกรอบ ตัวตรวจรัน `python solve.py` โดยส่ง JSON ทาง stdin
  - stdin `{"amount":20000,"tier":"gold","birthday":false}` ต้องได้ stdout `{"ok": true, "result": 500}` exit 0
  - อินพุตผิด ต้องได้ `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback
- สิ่งที่ได้จริงคือ stdout เป็นผลของตัวอย่างทดสอบใน `__main__` (เช่น `0\n150\n300...`) หรือว่างเปล่า และ exit 0 เสมอ แม้อินพุตผิด

## สาเหตุ
- โจทย์ไม่ได้พูดถึง CLI เลย (ข้อตรวจ `contract` ตรวจเฉพาะฟังก์ชัน) Agent จึงใส่ demo ใน `if __name__ == "__main__"`
- ไม่มีสกิลบอกสัญญานี้ ทั้ง 5 trace ไม่มีใครทำ CLI

## หลักฐาน
- iteration 1: t1-cafe-bill-r2 (stdout 47572), t2-split-bill-r1 (stdout `[3667, 3667, 3666]...`), t3-shipping-fee-r3 (stdout ว่าง), t4-cashback-r1 และ r3 (stdout เป็น demo) พลาดทั้ง `cli_ok` และ `cli_error`

## วิธีแก้
- ใส่ `main()` ท้าย solve.py อ่าน JSON จาก stdin โดยชื่อ key เท่ากับชื่อพารามิเตอร์ แล้วเรียกฟังก์ชันด้วย `**data`
- ```python
  import sys, json
  def main():
      try:
          data = json.load(sys.stdin)
          result = FUNC(**data)
      except (ValueError, TypeError, KeyError) as e:
          print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
          return 2
      print(json.dumps({"ok": True, "result": result}))
      return 0
  if __name__ == "__main__":
      sys.exit(main())
  ```
- ห้ามมี `print` demo อื่นใน `__main__` เพราะ stdout ต้องมี JSON บรรทัดเดียว
- ต้องไม่เกิด traceback ให้จับ exception ที่เป็นไปได้ทั้งหมด (JSON เสีย, key หายหรือเกิน, ValueError) แล้วออก exit 2
- ทดสอบเอง: `echo '{"amount":20000,"tier":"gold","birthday":false}' | python3 solve.py; echo $?` และอินพุตผิด 1 ตัว ต้องได้ exit 2
