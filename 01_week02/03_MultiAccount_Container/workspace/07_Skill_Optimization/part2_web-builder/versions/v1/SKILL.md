---
name: web-builder
description: สร้างเว็บไซต์ static หน้าเดียวจาก brief ของผู้ใช้ ไว้ที่ ./site/index.html (HTML/CSS/JavaScript ล้วน ไม่มี server ไม่มี build step ไม่มี framework) แล้วเปิดด้วย Playwright (Chromium headless --no-sandbox) เพื่อตรวจว่าโหลดได้ ไม่มี JS error ไม่ล้นจอมือถือ ลิงก์/ปุ่มทำงาน ก่อนส่งงาน ใช้เมื่อผู้ใช้ให้ brief/รายละเอียดเว็บ เช่น "ทำเว็บ landing page ให้ร้าน...", "สร้างหน้าเว็บแนะนำ...", "build a one-page site for ..."
---

# web-builder

เปลี่ยน brief ของผู้ใช้ให้เป็นเว็บ static หน้าเดียวที่ **ตรวจแล้วว่าทำงานจริง**

- ผลลัพธ์: `./site/index.html` (relative กับ working directory ปัจจุบันของผู้ใช้ ไม่ใช่โฟลเดอร์ของสกิล)
- ตัวตรวจ: `scripts/verify.cjs` (อยู่ในโฟลเดอร์เดียวกับไฟล์ SKILL.md นี้)

`SKILL_DIR` ด้านล่างหมายถึงโฟลเดอร์ที่ SKILL.md นี้อยู่ — ใช้ path จริงที่อ่านไฟล์นี้มา สกิลย้ายไปวางที่ไหนก็ได้

## ขั้นตอน

### 1. อ่าน brief
สรุปให้ได้: ชื่อ/แบรนด์, เป้าหมายของเว็บ, กลุ่มผู้ใช้, section ที่ต้องมี, call-to-action, โทนสี/อารมณ์, ภาษา
ถ้า brief ขาดบางอย่าง ให้ตัดสินใจเองอย่างสมเหตุสมผลแล้วบอกผู้ใช้ตอนส่งงาน — ถามกลับเฉพาะเมื่อขาดข้อมูลที่เดาไม่ได้จริง ๆ (เช่น เบอร์โทร/ราคาจริงที่ต้องถูกต้อง → ใส่ placeholder ที่เห็นชัดว่าเป็น placeholder)

### 2. เขียน `./site/index.html`
กฎบังคับ:
- **ไฟล์เดียว**: CSS ใน `<style>`, JS ใน `<script>` ท้าย body ห้ามมี server, npm, bundler, framework, CDN ที่จำเป็นต่อการทำงาน
  (เปิดด้วยการดับเบิลคลิกไฟล์ผ่าน `file://` ต้องใช้ได้ — ห้ามใช้ `fetch()` ไฟล์ local หรือ ES module import)
- ฟอนต์จากภายนอก (เช่น Google Fonts) ใช้ได้เฉพาะเมื่อมี fallback ใน `font-family` เว็บต้องดูดีแม้ออฟไลน์
- รูปภาพ: ใช้ inline SVG, CSS gradient, emoji หรือ data URI — ห้ามอ้างไฟล์รูปที่ไม่มีอยู่จริง ถ้าผู้ใช้ให้รูปมา ให้วางไว้ใน `./site/` และอ้างแบบ relative
- โครงสร้าง: `<!DOCTYPE html>`, `<html lang="...">`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`, `<title>`, `<h1>` หนึ่งตัว, semantic tags (`header/nav/main/section/footer`)
- Responsive: mobile-first, ไม่มี scroll แนวนอนที่ 375px (ระวัง `100vw`, รูป/ตารางกว้างเกิน, ข้อความยาวไม่ตัดบรรทัด)
- ลิงก์ `href="#x"` ต้องมี element `id="x"` จริง; ปุ่มทุกปุ่มต้องทำอะไรบางอย่าง
- Accessibility: `alt` ทุกรูป, label ทุก input, contrast อ่านง่าย, focus มองเห็นได้
- ฟอร์ม: ไม่มี backend จึงให้ JS ตรวจค่า + แสดงข้อความยืนยันในหน้า (ไม่ submit ออกไปจริง)
- ใส่ `id` ให้ element ที่โต้ตอบได้ เพื่อให้ steps อ้างถึงได้
- กล่องที่แสดงข้อความของผู้ใช้: ใช้ `textContent` (ห้าม `innerHTML`) และ `overflow-wrap:anywhere`
- ข้อมูลใน `localStorage`: อ่านใน `try/catch` และตรวจชนิดก่อนใช้ ถ้าเสียให้เริ่มจากค่าว่าง

### 3. เขียน steps จาก brief แล้วตรวจด้วย Playwright (ห้ามข้าม)

**ทุกข้อของ brief ต้องมี step ที่ตรวจ** ไล่ brief ทีละบรรทัด แล้วเขียน `./.verify/steps.json` (นอก `./site/`) ให้ครบ รวมถึง 4 กรณีนี้ที่มักพลาด

| กรณี | step ที่ต้องมี |
|---|---|
| ค่าที่ขอบเกณฑ์ (เท่ากับขั้นต่ำ/เพดานพอดี และเลยไป 1 ขั้น) | ทำให้ถึงค่านั้น แล้ว `expectBodyText` ด้วยตัวเลขที่คำนวณเองจาก brief |
| ข้อมูลต้องอยู่หลังรีเฟรช | `reload` แล้ว `expectBodyText` ซ้ำ |
| ข้อความที่ผู้ใช้พิมพ์แล้วแสดงบนหน้า | `fillLong` ที่ช่องนั้น แล้วส่งฟอร์ม (สคริปต์ตรวจว่าจอมือถือไม่ล้น) |
| ข้อความเตือนเก่าต้องหาย | ทำกรณีผิดแล้วทำกรณีถูกต่อ แล้ว `expectNoBodyText` ข้อความเตือนเดิม |

```json
[
  {"action": "click", "selector": "#add-latte"},
  {"action": "expectBodyText", "value": "ยอดสุทธิ ฿105.00"},
  {"action": "fillLong", "selector": "#name"},
  {"action": "click", "selector": "form button[type=submit]"},
  {"action": "reload"},
  {"action": "expectBodyText", "value": "ตะกร้า (1)"},
  {"action": "expectNoBodyText", "value": "กรุณากรอกชื่อ"}
]
```
```bash
node "$SKILL_DIR/scripts/verify.cjs" site/index.html --steps .verify/steps.json
```
- action: `click` `fill` `fillLong` `press` `select` `wait` `reload` `expectVisible` `expectHidden` `expectText` `expectCount` `expectBodyText` `expectNoBodyText` `eval` (JS ที่ต้องได้ค่า truthy)
- steps ชุดเดียวกันถูกรัน 2 รอบ: desktop 1280×800 และ mobile 375×740 แต่ละรอบเริ่มจากข้อมูลว่าง
- **FAIL** เมื่อ: step ไม่ผ่าน · console error · ไฟล์ local โหลดไม่ได้ · หน้าว่าง · จอล้นแนวนอน (ก่อนหรือหลัง steps) · anchor ไม่มีปลายทาง · รูปเสีย · ไม่มี meta viewport
- **WARN** ต้องอ่านทุกบรรทัดแล้วแก้ (เช่น steps ยังไม่มี `reload` หรือ `fillLong`)
- exit code: `0` PASS · `1` FAIL · `2` หาไฟล์หรือ playwright ไม่เจอ
- เงินให้คำนวณเป็น**สตางค์ (จำนวนเต็ม)** แล้วค่อยแปลงเป็นข้อความตอนแสดง ห้ามคูณทศนิยมแล้ว `toFixed`
- **ห้ามเขียนสคริปต์ Playwright เอง และห้ามใช้เครื่องมือเบราว์เซอร์อื่น** ถ้า action ไม่พอให้ใช้ `eval`

### 4. แก้จนผ่าน
อ่าน `FAIL` และ `WARN` ทีละบรรทัด → แก้ `site/index.html` (หรือเพิ่ม step ที่ขาด) → รัน verify ซ้ำจนได้ `PASS` และไม่เหลือ `WARN`
เปิดดู screenshot (`.verify/mobile-after-steps.png`) เฉพาะเมื่อ brief พูดถึงหน้าตา หรือสงสัยว่า layout พัง ไม่ต้องเปิดทุกครั้ง

### 5. ส่งงาน
รายงานสั้น ๆ: path ของไฟล์ · ผล verify (PASS + จำนวน step) · สิ่งที่ตัดสินใจเองจาก brief
อย่าอ้างว่าผ่านถ้ายังไม่ได้รัน verify หรือผลยังเป็น FAIL

## แก้ปัญหา
- `หา playwright ไม่เจอ` → `export PLAYWRIGHT_PATH="$(npm root -g)/@playwright/mcp/node_modules/playwright"` หรือ path ของ playwright ที่มีในเครื่อง
- `Executable doesn't exist` → ยังไม่ได้ติดตั้ง Chromium ของ playwright เวอร์ชันนั้น: `node <playwright-path>/cli.js install chromium`
- error เรื่อง sandbox → สคริปต์ใส่ `--no-sandbox` ให้แล้ว ถ้าเขียนสคริปต์ทดสอบเองต้องใส่ `chromium.launch({ args: ['--no-sandbox'] })` ด้วย
