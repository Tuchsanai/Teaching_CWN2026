# CLAUDE.md · PawPantry (ระบบเดิมที่รับช่วงมา)

ร้านขายของสัตว์เลี้ยง Next.js 16 (App Router) ใน `petshop/` · ข้อมูล server อยู่ใน RAM · ตะกร้า/โปรด/คูปองอยู่ใน localStorage `pp-*`
แผนที่ระบบ (หน้า · API · กฎธุรกิจ · state · เทสต์เดิม · เอกสารที่ไม่ตรงโค้ด) อยู่ในไฟล์ CODEBASE-MAP.md — เปิดอ่านเมื่อต้องใช้ ไม่ต้องโหลดทุกครั้ง

## รันคำสั่ง (PowerShell เสมอ · รันจากรากบท)

```powershell
# เว็บ → http://localhost:4000 (ในคอนเทนเนอร์คือ 3000 · REA ในคอนเทนเนอร์ใช้ http://petshop:3000 ผ่าน network pawpantry05_default)
cd petshop; docker compose up -d --build; cd ..
# reset ข้อมูลทดสอบ (ผู้ใช้ ออเดอร์ สต็อก · ไม่ล้าง localStorage)
Invoke-RestMethod -Method Post http://localhost:4000/api/test/reset
# เทสต์ chromium
cd e2e-legacy; npx playwright test; cd ..
# เทสต์ 3 เบราว์เซอร์ (นาน)
cd e2e-legacy; npm run test:all; cd ..
# REA
powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 <คำสั่ง> ...
```

- สคริปต์ชั่วคราว (Playwright ฯลฯ) ไว้ใน `rea\scratch\` เท่านั้น
- ผล REA ใน `out\` ใหญ่ ห้ามเปิดตรง ๆ ใช้ `node rea\rea-summarize.mjs <ไฟล์>`
- PowerShell 5.1: อย่าใช้ `Get-Content | Set-Content` / `>` กับไฟล์ JSON/ภาษาไทย (encoding พัง)

## ห้ามแตะ

- ไฟล์เดิมทุกไฟล์ใน `e2e-legacy/` (config · global-setup · package.json · `tests/*.ts` ชั้นบนสุด) และ `TEST-DATA.md`
- ห้ามทั้งด้วยเครื่องมือแก้ไฟล์ **และ** ด้วยคำสั่ง shell (`Set-Content` `Out-File` `>` `sed -i` `Move-Item` `Remove-Item` ฯลฯ)
  — `.claude/settings.json` กันได้แค่เครื่องมือแก้ไฟล์ ไม่กัน shell กติกานี้จึงต้องทำเอง
- test ใหม่วางใน `e2e-legacy/tests/new/` เท่านั้น
- ห้ามเปิด `README.md` ที่รากโฟลเดอร์บท `fast_track/` และ `_solution/` (มีเฉลย · `petshop/README.md` อ่านได้) · `.claude/settings.json` กันด้วย `Read(...)` แล้ว

## กติกาการแก้โค้ด

1. อธิบายก่อนแก้: ต้นเหตุอยู่ไฟล์:บรรทัดไหน จะแก้อะไร ทำไม
2. ทำตาราง impact ก่อนแก้: ไฟล์/หน้า/API/test ที่กระทบ (กฎหลายข้อถูกเขียนซ้ำหลายที่ ดูส่วน D ใน CODEBASE-MAP.md)
3. แก้ให้เล็กที่สุด ที่ต้นเหตุ · ไม่ refactor/จัดรูปแบบไฟล์ที่ไม่เกี่ยว
4. ห้ามแก้เทสต์เดิมให้ผ่าน · ถ้าเทสต์เดิมแดงหลังแก้ ให้หยุดแล้วรายงาน
5. เขียน test ใหม่ที่แดงก่อนแก้ แล้วเขียวหลังแก้ (ใน `e2e-legacy/tests/new/`)
6. หลังแก้: rebuild container แล้วรัน regression · ตรวจ `git diff --stat -- e2e-legacy TEST-DATA.md` ต้องว่าง

## ระวัง

- เอกสารเก่า (`petshop/HANDOVER-NOTES.md` `petshop/README.md` คอมเมนต์ในโค้ด) อาจไม่ตรงโค้ด — เชื่อโค้ดและการรันจริง แล้วถามเจ้าของร้านเมื่อขัดกัน
- ไม่แน่ใจกฎธุรกิจ ให้ถาม อย่าเดา
- ไฟล์ `.har` มีรหัสผ่าน/cookie ห้าม commit หรือส่งต่อ
