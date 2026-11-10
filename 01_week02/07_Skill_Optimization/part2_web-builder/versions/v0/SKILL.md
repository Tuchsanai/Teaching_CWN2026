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
- ใส่ `id`/`data-testid` ให้ element ที่โต้ตอบได้ เพื่อให้ตรวจด้วย Playwright ได้ง่าย

### 3. ตรวจด้วย Playwright (ห้ามข้าม)
```bash
node "$SKILL_DIR/scripts/verify.cjs" site/index.html
```
สคริปต์จะ:
- หา playwright เอง (ลำดับ: `$PLAYWRIGHT_PATH` → `require('playwright')` → `$(npm root -g)/@playwright/mcp/node_modules/playwright` → `$(npm root -g)/playwright`)
- เปิด Chromium headless ด้วย `--no-sandbox` ที่ desktop 1280×800 และ mobile 375×740
- **FAIL** เมื่อ: console error / uncaught exception, ไฟล์ local โหลดไม่ได้, หน้าว่าง, scroll แนวนอน, anchor `#id` ไม่มีปลายทาง, รูปเสีย, ไม่มี meta viewport, interaction step ไม่ผ่าน
- **WARN** เมื่อ: ไม่มี title/lang, จำนวน h1 ≠ 1, รูปไม่มี alt, resource ภายนอกโหลดไม่ได้ (เครื่องอาจออฟไลน์)
- บันทึก screenshot ไว้ที่ `./.verify/desktop.png`, `mobile.png` (และ `after-steps.png`) — ใช้ `--out DIR` เปลี่ยนที่เก็บได้
- exit code: `0` PASS, `1` FAIL, `2` setup error (หาไฟล์/playwright ไม่เจอ)

**ตรวจ interaction** ของเว็บ (เมนู, tab, ฟอร์ม, ปุ่ม, filter ฯลฯ) ด้วยไฟล์ steps แบบ JSON — เขียนไว้นอก `./site/` เช่น `./.verify/steps.json`:
```json
[
  {"action": "click", "selector": "#menu-toggle"},
  {"action": "expectVisible", "selector": "nav ul"},
  {"action": "fill", "selector": "#email", "value": "a@b.co"},
  {"action": "click", "selector": "form button[type=submit]"},
  {"action": "expectText", "selector": "#form-status", "value": "ขอบคุณ"},
  {"action": "eval", "value": "document.querySelectorAll('.card').length >= 3"}
]
```
```bash
node "$SKILL_DIR/scripts/verify.cjs" site/index.html --steps .verify/steps.json
```
action ที่รองรับ: `click`, `fill`, `press` (value = ชื่อคีย์ เช่น `Enter`; ไม่ใส่ selector = กดที่หน้า), `select`, `wait` (ms), `expectVisible`, `expectHidden`, `expectText`, `expectCount`, `eval` (JS expression ต้องได้ค่า truthy)
steps รันที่ viewport desktop; ถ้ามีเมนูมือถือ (hamburger) ให้ทดสอบด้วยการตรวจ CSS/JS ใน `eval` หรือออกแบบให้ทำงานได้ทั้งสองขนาด

### 4. แก้จนผ่าน
อ่าน `FAIL` แต่ละบรรทัด → แก้ `site/index.html` → รัน verify ซ้ำจนได้ `PASS`
จากนั้น **ดู screenshot** (`.verify/desktop.png`, `.verify/mobile.png`) ด้วยเครื่องมืออ่านรูป เพื่อตรวจด้วยตาว่า layout ไม่พัง ข้อความไม่ทับกัน สีอ่านได้ ตรงกับ brief — ถ้าไม่ดีให้แก้และรันใหม่
ถ้ามีเครื่องมือ Playwright MCP (`browser_navigate` ฯลฯ) จะใช้ลองเล่นเพิ่มก็ได้ แต่ต้องรัน `verify.cjs` ให้ผ่านเสมอ

### 5. ส่งงาน
รายงานสั้น ๆ:
- path ไฟล์ (`site/index.html`) และวิธีเปิด (ดับเบิลคลิก หรือ `xdg-open`/`open site/index.html`)
- section/ฟีเจอร์ที่ทำ และสมมติฐานที่ตัดสินใจเองจาก brief, placeholder ที่ผู้ใช้ต้องแก้
- ผลการตรวจ: PASS + WARN ที่เหลือ (ถ้ามี) และ interaction ที่ทดสอบ
- อย่าอ้างว่าผ่านถ้ายังไม่ได้รัน verify หรือผลยังเป็น FAIL

## แก้ปัญหา
- `หา playwright ไม่เจอ` → `export PLAYWRIGHT_PATH="$(npm root -g)/@playwright/mcp/node_modules/playwright"` หรือ path ของ playwright ที่มีในเครื่อง
- `Executable doesn't exist` → ยังไม่ได้ติดตั้ง Chromium ของ playwright เวอร์ชันนั้น: `node <playwright-path>/cli.js install chromium`
- error เรื่อง sandbox → สคริปต์ใส่ `--no-sandbox` ให้แล้ว ถ้าเขียนสคริปต์ทดสอบเองต้องใส่ `chromium.launch({ args: ['--no-sandbox'] })` ด้วย
