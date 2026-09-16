# สถานะการตรวจสอบ — 2026-09-12

ชุดสื่อเป็นไฟล์จริง การแสดงตัวอย่างผู้สอนและผลทดสอบโปรแกรมเป็นคนละประเภทกัน ไม่มีการรัน AI experiments ในรอบ authoring ตามคำสั่ง parent

| รายการ | สถานะ | หลักฐาน/ข้อจำกัด |
|---|---|---|
| Python stdlib shop บน Linux/Python3.12 | PASS | [stdout จริง](evidence/runtime-tests.txt) พร้อม UTC/เวอร์ชัน/คำสั่ง |
| STOPPED → start → HTTP ร้าน/สินค้า/order | PASS | runtime-tests.txt ตรวจ HTTP200 และเนื้อหาทุกจุด |
| bad release503 → rollback → HTTPดี | PASS | ทดสอบ rollback-A/B และ transfer-C |
| แก้ผิดยังเสีย | PASS | rollback ใน basic ไม่เริ่มบริการ; start ใน bad release ไม่ซ่อม503 |
| setup ซ้ำ/reset ซ้ำ/สอง instance แยกกัน | PASS | พอร์ตที่ครองพร้อมกันต่างกัน หยุดอันหนึ่งอีกอันยังผ่าน |
| ไม่มีธุรกรรมจริง/cleanup | PASS | order smoke ไม่ persist; ทุก test instance หยุดใน finally |
| สร้าง experiment bundles/ใช้งานร้านใน workspace | PASS | [package audit](evidence/package-checks.txt) ตรวจไฟล์จริงและ copied runtime |
| canonical body/Skillส่วนหัว/แปดส่วน/links | PASS | [package audit](evidence/package-checks.txt), [Skill validator](evidence/skill-validation.txt) |
| CLI flags และ syntax Skill | ตรวจ help/bundled material แล้ว | evidence/cli-local.txt, cli-help.txt; 0.154.0 |
| path project discovery | ยืนยันเอกสาร | [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills), ตรวจ 2026-09-12 หลังตรวจ local package แล้ว |
| native discovery และการโหลดสาม Skill ของแพ็กเกจจริง | PENDING | parent ต้องทำ gate ใน experiments/README.md; การมีไฟล์ยังไม่พิสูจน์ |
| ผล P/S ผ่าน cyolo1/gpt-6-astra/high | PENDING | ไม่รัน nested AI ตาม task; score sheets ว่าง |
| ใช้ AI สร้าง/ปรับ Skill ตาม Prompt ใน workshop | PENDING | มีต้นฉบับและขั้นพร้อมใช้ ยังไม่อ้างว่ารัน Prompt แล้ว |
| Browser UI โดยคน/การอ่านภาษาไทยบนจอ | PENDING | มีคู่มือตรวจ; HTTP tests ไม่ใช่การเปิดเบราว์เซอร์ |
| การนำร่องกับมือใหม่/เวลาสอนจริง | PENDING | เวลาที่ระบุเป็นแผนผู้สอน ไม่ใช่เวลาที่สังเกตจากคน |
| Windows/macOS/remote browser | ไม่ทดสอบ | runtime อาศัย Linux /proc, pidfd, flock; เตรียม Linux ให้ก่อนคาบ |

## รันทดสอบซ้ำเฉพาะแพ็กเกจ (ผู้สอน)

```bash
python3 instructor/runtime/test_runtime.py
python3 instructor/runtime/check_package.py
```

ตัวตรวจ package สร้างพื้นที่ audit ใหม่ใน experiments/workspaces ไม่เรียกโมเดล และหยุดร้านของตนหลังจบ หลักฐานเวลาเครื่องไม่ใช้แทนคะแนนเวลาผู้เรียน หากแก้ runtime ให้รัน functional test ใหม่ เก็บ raw stdout/UTC/version/คำสั่งก่อนปรับ PASS

ข้อจำกัด: ร้านนี้จำลองบริการเพียงส่วนเล็กของ DevOps ไม่มี production deployment หรือข้อมูลลูกค้าจริง การแยก workspace ไม่ใช่การบังคับสิทธิ์ระดับระบบ; wrapper ต้องใช้ในขอบเขตที่ผู้สอนเตรียม เหตุการณ์ที่ไม่ตรงคู่มือให้ส่งผู้สอน ไม่ขยายงานแก้ระบบนอก Lab
