# การตรวจ Input สำหรับผลอ้างอิง

ตรวจโดยผู้ช่วยจัดทำผลอ้างอิงตามคำสั่งให้เตรียมและรัน; ไม่ใช่การรับรองของนักศึกษาหรือเจ้าของร้าน

ACCEPTED: input

พร้อมรันกราฟเพื่อวิเคราะห์เอกสาร โดยคงข้อค้างเดิม ไม่ได้อนุมัติกฎที่ยังไม่ยืนยัน

ACCEPTED: customer
ACCEPTED: kitchen-front

ตรวจด้วย input/validate.py --node ของแต่ละบทบาทแล้ว ผ่าน schema, hashes, verbatim FR evidence และ US coverage: customer 12 flows / 8 US, kitchen-front 14 flows / 6 US
ผลสำเร็จจาก CLI มี turn.completed ไม่มี turn.failed และ exit code 0 ทั้งสองบทบาท
ข้อค้าง CUS-C01–CUS-C03 และ C-KF-01–C-KF-02 ยัง unresolved; รับผลเป็นเอกสารเพื่อวิเคราะห์ต่อ ไม่ได้อนุมัติกฎที่ยังขาด ให้ downstream คงข้อค้างและ merge ตัดสิน readiness ตามหลักฐาน

ACCEPTED: manager

manager: ตรวจ input/validate.py --node manager ผ่าน; 10 flows ครบ 4 US, schema / sources SHA-256 / FR evidence ตรงต้นทาง ผลนี้ยังคง DI-04/A-03 unresolved เพื่อให้ merge พิจารณา ไม่อนุมัติการเปลี่ยน FR

ACCEPTED: state-machine

state-machine: ผ่าน input/validate.py --node state-machine, เก็บ flow upstream ครบ 36 flows; คงความไม่ชัดเจนด้าน order mapping / payment timeout / table guard เป็นข้อค้าง ไม่รับรองกฎที่ยังไม่ยืนยัน

ACCEPTED: structure

structure: ผ่าน input/validate.py --node structure, เก็บ upstream 36 flows ครบ; มี module/entity/screen/permission tables และคง Unknown/ข้อเสนอ field/cardinality ตามหลักฐาน ให้ merge เทียบกับ state-machine และคง readiness BLOCKED เมื่อข้อค้างกระทบการส่งต่อ
