# FT-IMAGES · ภาพของ `fast_track/` บท 05 (ยังไม่สร้าง)

> ภาพที่ `fast_track/README.md` อ้าง · เก็บที่ `fast_track/img/` · **ยังไม่ได้สร้าง** (งาน FT5 เขียนแค่สเปก)
> jpg สร้างด้วย Codex (`/c/Users/oishi/bin/cyolo.cmd exec - < prompt.txt` · ~3 นาที/รูป · 1280×853) · png ทำจาก HTML → PNG ด้วย `tools/render-png.mjs` (Noto Sans Thai · 2560 px · < 600 KB) ตาม `STYLE-GUIDE.md` §4.2
> ภาพที่ใช้ซ้ำจากบท (มีอยู่แล้ว ไม่ต้องสร้าง): `../img/intro-02-understand-lock-change-prove.jpg` (🧭) · `../img/concept-12-evidence-badge-e.jpg` (🏷️)
> **กติกากันเฉลยรั่ว:** ข้อความในภาพห้ามมีชื่อไฟล์โค้ดหรือต้นเหตุของ BUG-01 · ห้ามตัวเลข ฿999 / ฿1,049 · ห้ามรายละเอียดคำตอบร้านของ CR-01 · เปิดดูทุกรูปหลังสร้าง (ข้อความไทยต้องถูก ไม่มีโลโก้หน้ากากละครบนหุ่นยนต์)

## Prefix (ต่อหน้าพรอมต์ jpg ทุกตัว · = `LESSON-PLAN.md` §8)

```text
Cute kawaii flat cartoon illustration, thick clean outlines, soft bright pastel colors, bright PawPantry pet-food shop setting with shelves of cat and dog food, paw-print decorations and sky with fluffy clouds through big windows, a cheerful boy with messy brown hair in a blue hoodie (the tester, often holding a clipboard or magnifying glass), a friendly round white robot with a black screen face, glowing blue eyes and a curved smile, an antenna topped with a small blue ball, the robot has NO logo, NO emblem and NO theater-mask icon anywhere on its body, cute orange cat and brown puppy characters, Thai title text in bold navy rounded font inside a white rounded label, short Thai speech bubbles of at most 5 words, 3:2 landscape, 1280x853, no watermark.
```

## รายการ

| ไฟล์ | ใช้ที่ | ชนิด | พรอมต์ (ต่อท้าย prefix) / เลย์เอาต์ |
|---|---|---|---|
| `ft-01-one-prompt.jpg` | หัว fast_track | jpg gen | The boy drops a single sheet of paper labeled "PROMPT" into the top of a big friendly machine labeled "AI WORKFLOW"; the machine has three input pipes connected to a cardboard box labeled "petshop", an old toolbox labeled "e2e-legacy" and a small container box labeled "REA"; the robot stands on a platform inspecting with a magnifying glass; out of the machine a conveyor belt carries neat documents in a row labeled "CODEBASE-MAP", "SYSTEM-MAP", "API-INVENTORY", "BASELINE", "BUG-01", "CR-01", "CHANGE-PROOF", "CHANGE-REPORT"; the orange cat sits on the petshop box, the puppy runs alongside the belt. Title label "พรอมต์เดียว รับช่วงครบ 10 ขั้น" |
| `ft-02-steps.png` | 🧭 | png diagram | หัว "พรอมต์เดียว 10 ขั้น" subtitle "ขั้นที่ N = LAB N · อ่านไฟล์ก่อนทำขั้นถัดไป" · การ์ด 5 กลุ่มตามสีช่วง: ⚙️ เทา ⓪ เช็กเครื่อง + REA (pill `doctor` `pawpantry05_default`) · 🟢 เข้าใจ ① อ่าน repo (`CODEBASE-MAP` `CLAUDE.md`) ② REA ส่อง build (`SYSTEM-MAP` `out\v1`) ③ HAR + scenario (`API-INVENTORY`) · 🟡 ล็อก ④ characterization (`BASELINE` `char-money`) · 🔵 แก้บั๊ก ⑤ ผู้ช่วยตาใหม่ทำซ้ำ → test แดง → ต้นเหตุ (`BUG-01`) ⑥ แก้ที่ต้นเหตุ · 🟠 ฟีเจอร์ ⑦ ถามร้าน + impact + test แดง (`CR-01`) ⑧ ทำ + regression 3 เบราว์เซอร์ · 🟣 พิสูจน์ ⑨ hash + source-to-bundle 4 ทิศ + obligation (`CHANGE-PROOF` `CHANGE-REPORT`) · แถบล่าง 🎯 "จบแล้วสรุปเป็นตาราง · ⚠️ ที่ต้องดู · เรื่องที่ตัดสินแทนผู้เรียน" · alt ใน README ต้องอัปเดตถ้าข้อความต่างจากนี้ |
| `ft-03-fresh-eyes.jpg` | 🤖 | jpg gen | Three-panel comic strip. Panel 1: the main robot holds a big colorful map labeled "CODEBASE-MAP" and is gently stopped outside a shop door by a small sign "ห้ามเอาแผนที่เข้า". Panel 2: a second, smaller fresh robot (same design, a tiny sparkle above its head to show it is new) holds only a customer note and a sheet labeled "TEST-DATA", looks at the PawPantry website on a laptop through a magnifying glass, finds a small ladybug with a question mark sitting on a receipt (no numbers on the receipt, only "฿ ?"), and raises a red card labeled "test แดง". Panel 3: the main robot receives the red card and opens a code book with a flashlight to look for the root, the boy nods with a clipboard. Title label "ขั้น 5: ผู้ช่วยตาใหม่". Bottom ribbon text "เห็นกับตาก่อน แล้วค่อยเปิดโค้ด" |
| `ft-04-hint-vs-blackbox.jpg` | 🔀 | jpg gen | Split scene with a vertical divider. Left side labeled "A บอกใบ้": a senior developer (friendly young woman with glasses and a lanyard, carrying a box as if leaving the team) whispers into the robot's ear and points at a shop floor plan already marked with pins; the robot holds a notebook labeled "บทเรียนหลัก". Right side labeled "B ไม่บอกใบ้": the robot holds a flashlight and walks into a dim warehouse full of floating question marks, holding only a customer note and a card labeled "CR-01". At the bottom the boy and the orange cat peek from behind a counter. Title label "บอกใบ้ หรือ ไม่บอกใบ้" |

## alt ที่ README ใช้ (ตรวจกับภาพจริงหลังสร้าง แล้วแก้ alt ให้ตรงทุกคำในภาพ)

| ไฟล์ | alt ปัจจุบันใน `fast_track/README.md` (ย่อ) |
|---|---|
| `ft-01-one-prompt.jpg` | เด็กชายหย่อนกระดาษ PROMPT … เครื่องจักร AI WORKFLOW ที่มีกล่อง petshop ชุดเทสต์เก่า และกล่อง REA … หัวเรื่อง พรอมต์เดียว รับช่วงครบ 10 ขั้น |
| `ft-02-steps.png` | 10 ขั้นต่อกัน 0 เช็กเครื่องและ REA · เข้าใจ 1–3 · ล็อก 4 · แก้บั๊ก 5–6 · ฟีเจอร์ 7–8 · พิสูจน์ 9 … แถบล่าง |
| `ft-03-fresh-eyes.jpg` | การ์ตูน 3 ช่อง หัวเรื่อง ขั้น 5 ให้ผู้ช่วยตาใหม่ทำซ้ำบั๊ก … แถบล่าง เห็นกับตาก่อน แล้วค่อยเปิดโค้ด (หมายเหตุ: alt เขียนหัวเรื่องว่า "ขั้น 5 ให้ผู้ช่วยตาใหม่ทำซ้ำบั๊ก" ถ้าภาพจริงได้ "ขั้น 5: ผู้ช่วยตาใหม่" ให้แก้ alt ตามภาพ) |
| `ft-04-hint-vs-blackbox.jpg` | ภาพแบ่งครึ่ง หัวเรื่อง บอกใบ้ หรือ ไม่บอกใบ้ … |
