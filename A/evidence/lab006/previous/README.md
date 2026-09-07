# บันทึกหลักฐานเดิม

ก่อนเริ่มงาน ได้ย้ายไฟล์เดิมของ `evidence/lab006/` มาไว้ใต้ `previous/` ตามสเปกแล้ว ได้แก่ `cleanup.json`, `desktop-1440.png`, `document-checks.json`, `mobile-375.png`, `playwright-before-fix.txt`, `playwright-cli.txt`, `report.md`, `ssh-checks.json`, `uat-results.json` และ `lab-artifacts/README-checkpoint.md`

ระหว่างรัน live test โฟลเดอร์ `evidence/lab006/` ถูกลบจากภายนอกกระบวนการนี้ทั้งโฟลเดอร์ จึงไม่สามารถกู้ไฟล์เดิมเหล่านั้นกลับมาได้ ไฟล์หลักฐาน live ที่เห็นในโฟลเดอร์ปัจจุบันถูกกู้จาก session log ของ wrapper หรือสร้างซ้ำจากเว็บฉบับสุดท้าย เหตุการณ์นี้ถูกรายงานตามจริงและไม่ได้อ้างว่าไฟล์เดิมยังอยู่

ก่อนส่งงานพบ autosave เก่าถูกสร้างขึ้นใหม่ใต้ LAB จึงย้ายมาเก็บแบบกู้คืนได้ที่ `lab-checkpoints/` เพื่อไม่ให้ปะปนกับ README และพรอมท์ฉบับส่ง โดยไม่ได้แก้เนื้อหาไฟล์ autosave
