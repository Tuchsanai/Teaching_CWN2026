# หลักฐานจริงของการ authoring

| ไฟล์ | สิ่งที่พิสูจน์ | สิ่งที่ไม่ได้พิสูจน์ |
|---|---|---|
| [runtime-tests.txt](runtime-tests.txt) | HTTP/การแก้ผิด/การกู้/reset/แยก instance/cleanup พร้อมคำสั่งและเวลา | ความสามารถของ AI หรือผู้เรียน |
| [package-checks.txt](package-checks.txt) | ลิงก์ local, body ตรงกัน, dataset/CSV, เตรียม P/S และร้านใน workspace | native Skill ถูกใช้จริงโดยโมเดล |
| [skill-validation.txt](skill-validation.txt) | validator ตรวจส่วนหัวและรูปแบบ Skill ทั้งสามผ่าน | คำตอบเชิงพฤติกรรมถูกทุกโจทย์ |
| [cli-help.txt](cli-help.txt) | รุ่น0.154.0, flags และการรับ prompt ทาง stdin | สิทธิ์โมเดล/โควตาของผู้เรียนทุกคน |
| [cli-local.txt](cli-local.txt) | syntax $skill-name ในข้อความที่มากับ binary ที่ติดตั้ง | ความสำเร็จของการค้นพบ Skill ที่เพิ่งสร้าง |
| [final-audit.txt](final-audit.txt) | inventory/link check และไม่มี process ร้านของแพ็กเกจเหลือ | ผลการนำร่องกับคน |

คำสั่งรันทดสอบจากรากแพ็กเกจ:

```bash
python3 instructor/runtime/test_runtime.py
python3 instructor/runtime/check_package.py
```

อาศัย Python3.12.3 บน Linux ไม่มี pip/Docker และไม่ส่งคำขอโมเดล Raw logs เป็นผลรันจริง; ข้อความตัวอย่างที่สร้างขึ้นโดยผู้สอนอยู่ instructor/*-key.md และ *-exemplar.md แยกจากหลักฐานชุดนี้ การทดสอบรอบท้ายไม่นับ checkpoint ที่ editor สร้างขึ้นเป็นเอกสารแจกเรียน
