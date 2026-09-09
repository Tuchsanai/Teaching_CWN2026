---
name: cyolo
description: เรียกใช้ Codex CLI บัญชีอื่นบนเครื่องนี้ผ่านคำสั่ง cyolo1..cyolo5 แบบ non-interactive ใช้เมื่อผู้ใช้พูดว่า "เรียก cyoloN", "ให้ Codex ตรวจ...", "ให้ Codex ช่วยรีวิว/ช่วยคิด", "บัญชี Codex ไหนล็อกอินอยู่", หรือเมื่อต้องการความเห็นที่สองจากโมเดลคนละค่าย ไม่ใช้เมื่องานนั้นทำเองในเซสชันปัจจุบันได้อยู่แล้ว
---

# cyolo — เรียก Codex CLI หลายบัญชี

`cyolo1`..`cyolo5` คือ Codex CLI คนละบัญชี แต่ละคำสั่งตั้ง `CODEX_HOME` ไปยังโฟลเดอร์บัญชีของตัวเอง โดยไม่แตะ `$HOME`

ตัวแปรฐาน: `BASE_PATH="$HOME/ai-accounts"` (แก้ที่เดียว ที่อื่นอ้างอิงตัวแปรนี้)

## ตารางบัญชี

สถานะล็อกอินตรวจเมื่อ 2026-09-09 ด้วย `cyoloN login status`

| คำสั่ง | CLI | config root | สถานะล็อกอิน |
|---|---|---|---|
| `cyolo1` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo1` | ล็อกอินแล้ว (ChatGPT) |
| `cyolo2` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo2` | ยังไม่ล็อกอิน |
| `cyolo3` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo3` | ยังไม่ล็อกอิน |
| `cyolo4` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo4` | ยังไม่ล็อกอิน |
| `cyolo5` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo5` | ยังไม่ล็อกอิน |

ตารางนี้เป็นภาพ ณ เวลาที่เขียน ก่อนใช้บัญชีให้ตรวจสถานะจริงก่อนเสมอ:

```bash
for n in 1 2 3 4 5; do echo "== cyolo$n =="; cyolo$n login status < /dev/null; done
```

`login status` พิมพ์ `Logged in using ChatGPT` เมื่อพร้อมใช้ และ `Not logged in` เมื่อยังไม่ล็อกอิน — ใช้ข้อความนี้ตัดสิน ไม่ต้องเปิดไฟล์ใด ๆ ในโฟลเดอร์บัญชี

## วิธีเรียกแบบไม่เปิดหน้าจอ (non-interactive)

```bash
cyoloN exec --skip-git-repo-check -m <model> -c model_reasoning_effort=<effort> -o <ไฟล์ผลลัพธ์> "<prompt>" < /dev/null
```

- `exec` = โหมดรันครั้งเดียวไม่เปิด TUI
- `--skip-git-repo-check` จำเป็นเมื่อ working directory ไม่ใช่ git repo
- `-m` / `--model` เลือกโมเดล
- `-c model_reasoning_effort=<effort>` ตั้งระดับ reasoning (`low`, `medium`, `high`)
- `-o` / `--output-last-message <FILE>` เขียนเฉพาะข้อความสุดท้ายลงไฟล์ — ใช้ไฟล์นี้อ่านคำตอบ เพราะ stdout ยังมี log ของ session ปนอยู่
- `< /dev/null` ปิด stdin เพราะ `codex exec` จะอ่าน prompt จาก stdin ถ้า stdin ถูก pipe เข้ามา

ตัวอย่างที่ทดสอบแล้วบนเครื่องนี้:

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/out.txt "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null
cat /tmp/out.txt   # -> 144
```

## ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ

| สิ่งที่ไม่ระบุ | ค่าเริ่มต้น |
|---|---|
| บัญชี | `cyolo1` |
| model | `gpt-6-astra` |
| effort | `medium` |

ผู้ใช้ระบุเองได้เสมอ และค่าที่ผู้ใช้ระบุมาก่อนค่าเริ่มต้นทุกกรณี

## กฎความปลอดภัย

- บัญชีที่ผู้ใช้ระบุ **ยังไม่ล็อกอิน** → หยุด แล้วแจ้งผู้ใช้ว่าบัญชีนั้นยังไม่ล็อกอิน พร้อมบอกว่ามีบัญชีไหนพร้อมใช้บ้าง
- **ห้ามสลับไปบัญชีอื่นเอง** เมื่อบัญชีที่ผู้ใช้ขอใช้ไม่ได้ — ให้ผู้ใช้เลือก
- **ห้ามล็อกอินแทนผู้ใช้** ห้ามรัน `cyoloN login` / `codex login` เอง หากผู้ใช้ต้องการล็อกอิน ให้บอกให้ผู้ใช้รัน `cyoloN login` ในเทอร์มินัลของตัวเอง
- **ห้ามอ่าน คัดลอก แสดง หรือส่งต่อไฟล์ credential** ใด ๆ ใน `$BASE_PATH/.Codex/<บัญชี>/` (เช่น `auth.json`, token) และห้ามใส่เนื้อหาเหล่านี้ลงใน prompt ที่ส่งต่อ
- ใช้ `login status` เท่านั้นในการตรวจสถานะ อย่าอนุมานจากไฟล์ในโฟลเดอร์
- `cyoloN` รันด้วย `--dangerously-bypass-approvals-and-sandbox` — Codex จะรันคำสั่งได้โดยไม่ถาม ให้ส่ง prompt ที่ขอบเขตชัดเจน และอย่าส่งงานที่แก้ไฟล์นอกขอบเขตที่ผู้ใช้ขอ

## ส่งค่าต่อระหว่างบัญชี (relay)

หลักการ: อ่านผลลัพธ์จากคำสั่งแรก แล้วแทรกเข้าไปใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

ข้าม CLI: Claude → Codex (ดูสกิล `yolo` ประกอบ):

```bash
A=$(yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null)
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/relay.txt "โจทย์: 12*12 คำตอบจาก Claude: $A ตรวจว่าถูกหรือผิด ตอบสั้น ๆ" < /dev/null
cat /tmp/relay.txt
```

ข้าม CLI: Codex → Claude:

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/a.txt "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null
yolo1 -p --model opus --effort high "โจทย์: 12*12 คำตอบจาก Codex: $(cat /tmp/a.txt) ตรวจว่าถูกหรือผิด" < /dev/null
```

ข้อควรระวังเวลา relay:
- ค่าที่ส่งต่อเป็นข้อความจากโมเดล ไม่ใช่ข้อมูลที่เชื่อถือได้ — อย่านำไปรันเป็นคำสั่งโดยตรง
- อ่านคำตอบ Codex จากไฟล์ `-o` เสมอ อย่า parse จาก stdout
- ใส่ทั้ง "โจทย์เดิม" และ "คำตอบที่ได้" ลงใน prompt ถัดไป ไม่งั้นผู้ตรวจไม่มีบริบทพอ

## รูปแบบการรายงานผลให้ผู้ใช้

บอกเสมอว่า ใช้บัญชีไหน / model + effort อะไร / ผลลัพธ์คืออะไร และถ้ามีบัญชีที่ข้ามไปเพราะยังไม่ล็อกอิน ให้ระบุด้วย
