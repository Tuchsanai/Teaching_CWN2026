# FT-IMAGES · ภาพของ `fast_track/` บท 06 (สเปก · ยังไม่สร้าง)

> สำหรับผู้ผลิตบท · เขียน 12 ต.ค. 2026 (งาน FT6) · **ยังไม่ได้สร้างภาพ** · ปลายทาง `06_sabai-spa-legacy-change-request/fast_track/img/`
> `fast_track/README.md` อ้างภาพใหม่ 3 ไฟล์ข้างล่าง + ใช้ภาพของบทซ้ำ 2 ไฟล์ (`../img/concept-18-claude-md-fence.jpg` · `../img/concept-12-intended-vs-unintended.jpg`) จึงไม่ต้องสร้าง `ft-03-*`
> วิธีสร้างตาม STYLE-GUIDE §4.2: jpg = Codex (`cyolo exec - < prompt.txt` · ระบุ path ปลายทางในพรอมต์ · 1280×853 · ~200–350 KB · เปิดดูทุกรูปว่าข้อความไทยถูก) · png = HTML → PNG (Noto Sans Thai · 1280 CSS px DSF 2 · < 600 KB · ใช้ `05_…/_solution/_design/diagrams/house.css` + `tools/render-png.mjs` แบบเดียวกับภาพไดอะแกรมของบท)
> **กันเฉลยรั่ว:** ข้อความในภาพห้ามมีชื่อบั๊กหรือพฤติกรรมผิดของระบบเดิม ตัวเลขผลลัพธ์ของ CR หรือเนื้อหาข้อสอบ · ใช้แค่ชื่อไฟล์ ชื่อขั้น และหัวข้อ CR ตามหนังสือ

## 1. ตารางภาพ

| # | ไฟล์ | ใช้ที่ | ประเภท | alt ที่ README ใช้ (ภาพต้องตรงกับ alt นี้) |
|---|---|---|---|---|
| 1 | `ft-01-one-prompt.jpg` | ใต้ย่อหน้าแรก | jpg gen | เด็กชายหย่อนซองหนังสือ CR-01 ถึง CR-05 กับกล่อง ระบบเดิม ลงเครื่องจักร AI WORKFLOW … หัวเรื่อง พรอมต์เดียว จบครบ 13 ขั้น |
| 2 | `ft-02-steps.png` | 🧭 พรอมต์ทำอะไรบ้าง | png diagram | 13 ขั้นต่อกัน รับมอบ 0 … 12 ซ้อมถอยกลับและเอกสาร · แถบล่าง ทุก CR ถาม อธิบายของเดิม impact แดงก่อน แก้ regression โยงกลับ |
| 3 | `ft-04-hint-vs-blackbox.jpg` | 🔀 เลือกพรอมต์ | jpg gen | ภาพแบ่งครึ่ง หัวเรื่อง บอกใบ้ หรือ ไม่บอกใบ้ … เด็กชายกับน้องบัวแอบดูอยู่ข้างล่าง |

## 2. พรอมต์ภาพ jpg

นำหน้าทุกพรอมต์ด้วย style prefix ของบท 06 (`LESSON-PLAN.md` §12.1) ตรงตัว แล้วต่อด้วยข้อความในกรอบ

### 2.1 `ft-01-one-prompt.jpg`

```text
Save the final image to 06_sabai-spa-legacy-change-request/fast_track/img/ft-01-one-prompt.jpg (1280x853, JPEG ~250 KB).
Spa garden with a long conveyor belt. On the left the boy drops a stack of five envelopes labeled "CR-01", "CR-02", "CR-03", "CR-04", "CR-05" together with a dusty cardboard box labeled "ระบบเดิม" into the hopper of a big friendly machine labeled "AI WORKFLOW". The robot stands on a small platform beside the machine holding a magnifying glass over a document. Out of the machine, the conveyor carries neat documents and items in a row, each with a small label: "HANDOVER-CHECK", "REA-INVENTORY", "SYSTEM-MAP", "CLAUDE.md", "golden", "impact", a small traffic light showing red then green labeled "แดง → เขียว", a database cylinder labeled "migration", "REGRESSION-REPORT", "RELEASE-NOTES" with a green check stamp. At the end of the belt Khun Chan waits behind a wooden counter holding a rubber stamp. Nong Bua waves from a lotus pot. Title sign "พรอมต์เดียว จบครบ 13 ขั้น". No other text.
```

### 2.2 `ft-04-hint-vs-blackbox.jpg`

```text
Save the final image to 06_sabai-spa-legacy-change-request/fast_track/img/ft-04-hint-vs-blackbox.jpg (1280x853, JPEG ~250 KB).
Split-screen illustration with a thin golden divider. Title sign across the top "บอกใบ้ หรือ ไม่บอกใบ้".
Left half labeled with a round badge "A บอกใบ้": office scene, Khun Chan leans in and whispers into the robot's ear while pointing at a system map pinned on the wall with three colored pins tagged "วันหยุด", "กดซ้ำ", "ข้ามเที่ยงคืน"; the robot holds an open notebook labeled "บทเรียนหลัก".
Right half labeled with a round badge "B ไม่บอกใบ้": dim storeroom, the robot shines a flashlight on a closed wooden box labeled "ระบบเดิม" surrounded by floating question marks; in its other hand only one envelope labeled "หนังสือ CR".
At the bottom center the boy and Nong Bua peek over the divider curiously. Speech bubbles none. No other text.
```

## 3. เลย์เอาต์ HTML · `ft-02-steps.png`

- หัวเรื่องกรมท่า "Fast Track บท 06: 13 ขั้นในพรอมต์เดียว" · subtitle เทา "ขั้นที่ N = LAB N · อ่านไฟล์ของขั้นก่อนจากดิสก์ทุกครั้ง"
- 5 แถบแนวนอนสีตามช่วง (🟢🟡🔵🟠🟣 แบบ `overview-5-phases.png`) แต่ละแถบมีวงกลมเลขขั้น + ชื่อขั้น + pill ชื่อไฟล์ (mono):
  - 🟢 **รับมอบ** · ⓪ เช็กเครื่อง (ตารางในแชท) · ① รับมอบ `HANDOVER-CHECK.md` `commit baseline` · ② REA `docs/REA-INVENTORY.md` `rea-out/`
  - 🟡 **เข้าใจ** · ③ แผนที่ระบบ `SYSTEM-MAP.md` `docs/SPEC-GAPS.md` · ④ CLAUDE.md และรั้ว `CLAUDE.md` `.claude/settings.json` `docs/IMPACT-TEMPLATE.md`
  - 🔵 **ตาข่าย** · ⑤ seam golden known issue mutant `tests/golden/` `e2e-cr/` `KNOWN-ISSUES.md`
  - 🟠 **Change Request** · ⑥ CR-02 · ⑦ CR-03 · ⑧ CR-04 migration `db/migrations/` · ⑨ CR-01 · ⑩ CR-05 · ใต้แถบมี pill ร่วม `docs/impact/CR-0N.md` `tests/cr0N.mjs` `TRACEABILITY.md` และวงจรเล็ก 6 ช่อง "ถาม → อธิบายของเดิม → impact → แดงก่อน → แก้ → regression"
  - 🟣 **ส่งมอบ** · ⑪ regression และ REA เทียบเวอร์ชัน `REGRESSION-REPORT.md` · ⑫ ซ้อมถอยกลับและเอกสาร `tests/smoke.mjs` `RELEASE-NOTES.md` `UAT-CHECKLIST.md`
- หมายเหตุเล็กมุมขวาของแถบ 🟠: "🅱️ เรียงลำดับ CR เอง"
- แถบล่างสีฟ้าอ่อน 🎯 "ทุก CR: ถาม · อธิบายของเดิม · impact · แดงก่อน · แก้ · regression · โยงกลับ"

## 4. ตรวจหลังสร้าง

| ☐ | ตรวจ |
|---|---|
| ☐ | เปิดดูทุกรูป ข้อความไทยสะกดตรงตามพรอมต์ · หุ่นยนต์ไม่มีโลโก้ |
| ☐ | ภาพตรงกับ alt ใน `fast_track/README.md` ทุกคำ (ถ้าภาพต่าง ให้แก้ alt ให้ตรงภาพ) |
| ☐ | ไม่มีข้อความเฉลย (ชื่อบั๊ก ตัวเลขผลลัพธ์ CR เนื้อหาข้อสอบ) |
| ☐ | jpg ~200–350 KB · png < 600 KB · ไม่มีไฟล์ > 3 MB |
| ☐ | link check `fast_track/README.md` 0 broken (รวม `../img/concept-18-claude-md-fence.jpg` `../img/concept-12-intended-vs-unintended.jpg`) |
