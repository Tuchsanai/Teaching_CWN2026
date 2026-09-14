# ตรวจฟีเจอร์ UI v2 ผ่านเบราว์เซอร์

ตรวจ US-09/14/21 และผลต่อ snapshot/การจ่ายด้วยข้อมูลจำลอง แยก context ทุกกรณี รัน N=5 สามรอบตามแผน ไม่ใช่หลักฐาน LAN หรือการคืนเงินจริง เวลาในภาพเป็นนาฬิกาจำลอง ส่วนเวลารันจริงอยู่ meta.json

Selectors อ้างจาก DOM ที่เปิดตรวจและ ui-contract-v2.md; ใช้ helper เดิมของ LAB 004

คำสั่งที่รัน:

    /opt/venv/bin/python3 AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-browser/ui-scenarios-v2.py --shots AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/img
