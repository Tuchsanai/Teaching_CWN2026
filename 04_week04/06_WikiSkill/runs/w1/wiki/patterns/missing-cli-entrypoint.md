# missing-cli-entrypoint: solve.py ไม่มีโหมดสั่งรันจาก stdin จึงไม่มี output และ exit 0 เสมอ

## อาการ
- `cli_ok` ตกทุกโจทย์ เช่น stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ต้องได้ `{"ok": true, "result": 500}` exit 0 แต่ได้ exit 0 stdout (ว่าง)
- `cli_error` ตกทุกโจทย์ เช่น stdin `{"amount": 20000, "tier": "bronze", "birthday": false}` ต้องได้ `{"ok": false, "error": "..."}` exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- พบใน `t1-cafe-bill-r1`, `t2-split-bill-r1`, `t3-shipping-fee-r3`, `t4-cashback-r1`, `t4-cashback-r3`

## สาเหตุ
- Agent เขียน `solve.py` เป็นไฟล์ที่มีแต่ฟังก์ชัน ไม่มีบล็อก `if __name__ == "__main__":` เมื่อตัวตรวจรัน `python3 solve.py` โดยส่ง JSON ทาง stdin ไฟล์จึงแค่ประกาศฟังก์ชันแล้วจบ ได้ exit 0 และ stdout ว่าง
- โจทย์ไม่ได้เอ่ยถึงโหมด CLI และไม่มีสกิลบอก Agent จึงไม่รู้ว่าต้องทำ
- ชื่อ key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน (เช่น `amount`, `tier`, `birthday`) ซึ่งเอาไปเรียกฟังก์ชันตรง ๆ ได้

## หลักฐาน
งานที่ล้ม: ทั้ง 5 Trace ใช้ `cat > solve.py` หรือ Write เฉพาะนิยามฟังก์ชัน ไม่มีโค้ดอ่าน stdin

งานที่ผ่าน: ไม่มีใน Trace ที่สุ่มมารอบนี้

หมายเหตุ: `cli_error` ผูกกับ `missing-input-validation.md` ด้วย เพราะต้องมี ValueError ก่อนจึงจะแปลงเป็น JSON error ได้ แต่ต่อให้ validation ถูก ถ้าไม่มี CLI ข้อนี้ก็ยังตก

## วิธีแก้
เพิ่มท้าย `solve.py` ให้ทำงานดังนี้ (เขียนเป็นหลักทั่วไป ใช้ได้กับทุกฟังก์ชันที่รับพารามิเตอร์เป็นชื่อ):
- อ่าน JSON object จาก stdin แล้วเรียกฟังก์ชันด้วย `fn(**data)`
- สำเร็จ: พิมพ์ `{"ok": true, "result": <ค่าที่คืน>}` ทาง stdout แล้ว exit 0 (result เป็น list/int ตามจริง)
- ผิดพลาด: จับ `ValueError` และข้อผิดพลาดจากอินพุตเสียรูปแบบ (JSON เสีย, key ขาดหรือเกิน → `TypeError`/`KeyError`/`json.JSONDecodeError`) พิมพ์ `{"ok": false, "error": "<ข้อความ>"}` แล้ว `sys.exit(2)` โดยห้ามให้ traceback ออกมา
- ห่อทั้งหมดใน `if __name__ == "__main__":` เพื่อให้การ import ฟังก์ชันจากไฟล์ทดสอบไม่ไปรอ stdin
- ลองรันจริงอย่างน้อย 1 กรณีสำเร็จและ 1 กรณีผิดด้วย `echo '{...}' | python3 solve.py; echo $?` ตรวจ stdout และ exit code
## อัปเดตรอบ 2: แก้ได้แล้ว
- `cli_ok` และ `cli_error` ผ่านครบในทั้ง 7 Trace ที่สุ่มมา ทุกงานมีบล็อก `if __name__ == "__main__":` ที่คัดจากสกิล `solve-py-contract` (อ่าน stdin, `FUNC(**data)`, พิมพ์ `{"ok": ...}`, `sys.exit(2)` เมื่อผิด)
- Agent ทุกตัวลองรันจริงทั้งสองกรณีก่อนตอบ เช่น `t4-cashback-r3`: สำเร็จ `{"ok": true, "result": 5000}` exit=0 และ amount เป็น float ได้ `{"ok": false, "error": "amount ต้องเป็นจำนวนเต็ม (สตางค์)"}` exit=2 ไม่มี traceback
- สาเหตุเดิมคือไม่มีสกิลและโจทย์ไม่ได้บอก เมื่อสกิลให้โค้ดบล็อกสำเร็จรูป ปัญหานี้หายหมด ให้คงบล็อกนั้นไว้ในสกิลตามเดิม
