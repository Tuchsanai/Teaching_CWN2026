---
name: cyolo
description: เรียกใช้ Codex CLI บัญชีอื่นบนเครื่องนี้ผ่านคำสั่ง cyolo1..cyolo5 แบบไม่เปิดหน้าจอ ใช้เมื่อผู้ใช้พูดว่า "เรียก cyoloN", "ให้ Codex ตรวจ...", "บัญชี Codex ไหนล็อกอินอยู่", หรือต้องการส่งผลลัพธ์ต่อไปยังบัญชี Codex/Claude อื่น
---

# cyolo — เรียก Codex CLI หลายบัญชี

ตัวแปรตั้งค่า (แก้ที่เดียว): `BASE_PATH="$HOME/ai-accounts"` (ค่าจริงบนเครื่องนี้ = `/root/ai-accounts`)

คำสั่ง `cyoloN` คือ wrapper ที่ `/usr/local/bin/cyoloN` ซึ่งรัน
`CODEX_HOME=$BASE_PATH/.Codex/cyoloN codex --dangerously-bypass-approvals-and-sandbox "$@"`
(เวอร์ชันที่ติดตั้ง: codex-cli 0.153.4)

## ตารางบัญชี (ตรวจเมื่อ 2026-09-09 ด้วย `cyoloN login status`)

| คำสั่ง | CLI | config root | สถานะล็อกอิน |
|---|---|---|---|
| cyolo1 | Codex CLI | $BASE_PATH/.Codex/cyolo1 | ล็อกอินแล้ว |
| cyolo2 | Codex CLI | $BASE_PATH/.Codex/cyolo2 | ยังไม่ล็อกอิน |
| cyolo3 | Codex CLI | $BASE_PATH/.Codex/cyolo3 | ยังไม่ล็อกอิน |
| cyolo4 | Codex CLI | $BASE_PATH/.Codex/cyolo4 | ยังไม่ล็อกอิน |
| cyolo5 | Codex CLI | $BASE_PATH/.Codex/cyolo5 | ยังไม่ล็อกอิน |

สถานะอาจเปลี่ยนได้ ก่อนใช้งานให้ตรวจสดเสมอ:

```bash
cyoloN login status < /dev/null   # exit 0 + "Logged in ..." = ล็อกอินแล้ว, exit 1 + "Not logged in" = ยังไม่ล็อกอิน
```

## วิธีเรียกแบบไม่เปิดหน้าจอ (ทดสอบแล้วกับ 0.153.4)

```bash
cyoloN exec --skip-git-repo-check -m <model> -c model_reasoning_effort=<effort> -o <ไฟล์ผลลัพธ์> "<prompt>" < /dev/null
```

- `exec` = โหมด non-interactive
- `--skip-git-repo-check` = ให้รันได้แม้โฟลเดอร์ปัจจุบันไม่ใช่ git repo
- `-m, --model` = ชื่อโมเดล
- `-c model_reasoning_effort=<effort>` = ระดับ reasoning (`low | medium | high`)
- `-o, --output-last-message <FILE>` = เขียนเฉพาะข้อความตอบสุดท้ายลงไฟล์ (stdout จะมี log ปนอยู่ จึงควรอ่านคำตอบจากไฟล์นี้)
- `< /dev/null` ป้องกันการรอ stdin
- อ่านคำตอบ: `cat <ไฟล์ผลลัพธ์>`

## ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ

- บัญชี: `cyolo1`
- model: `gpt-6-astra`
- effort: `medium`
- ไฟล์ผลลัพธ์: สร้างชั่วคราวเช่น `/tmp/cyolo-<N>-$$.txt`
- ผู้ใช้ระบุบัญชี / model / effort เองได้เสมอ และให้ใช้ค่าที่ผู้ใช้ระบุก่อน

## กฎที่ต้องปฏิบัติ

1. ถ้าผู้ใช้ระบุบัญชีที่ "ยังไม่ล็อกอิน" → แจ้งผู้ใช้ว่าบัญชีนั้นยังไม่ล็อกอิน แล้วหยุด
   ห้ามสลับไปใช้บัญชีอื่นเอง ห้ามล็อกอินแทนผู้ใช้ (ห้ามรัน `cyoloN login` หรือ `codex login`)
2. ห้ามอ่าน คัดลอก แสดง หรือส่งต่อไฟล์ credential ใด ๆ ใน `$BASE_PATH/.Codex/cyoloN/`
   (เช่น `auth.json`, `config.toml` ที่มี key) ให้ใช้เฉพาะ `cyoloN login status` ในการตรวจสถานะ
3. ห้ามแก้ไขไฟล์ใน config root ของบัญชีอื่น

## วิธีส่งค่าต่อ (relay)

อ่านผลจากคำสั่งแรก (จากไฟล์ `-o` หรือ stdout ของ Claude) แล้วใส่ลงใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

ตัวอย่าง Codex → Codex (ต่างบัญชี):

```bash
Q="ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12"
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/a.txt "$Q" < /dev/null
A="$(cat /tmp/a.txt)"
cyolo2 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/b.txt "โจทย์: $Q
คำตอบจาก cyolo1: $A
ตรวจว่าถูกหรือไม่ ตอบ CORRECT หรือ WRONG" < /dev/null
cat /tmp/b.txt
```

ตัวอย่าง Claude → Codex (ข้าม CLI ทดสอบแล้วได้ CORRECT):

```bash
A="$(yolo1 -p --model fable --effort medium "$Q" < /dev/null)"
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/out.txt "โจทย์: $Q
คำตอบจาก Claude (yolo1): $A
ตรวจว่าถูกหรือไม่ ตอบ CORRECT หรือ WRONG" < /dev/null
cat /tmp/out.txt
```

ตัวอย่าง Codex → Claude:

```bash
A="$(cat /tmp/a.txt)"
yolo1 -p --model fable --effort medium "โจทย์: $Q
คำตอบจาก Codex (cyolo1): $A
ตรวจว่าถูกหรือไม่ ตอบ CORRECT หรือ WRONG" < /dev/null
```

รายละเอียดฝั่ง Claude ดูสกิล `yolo`
