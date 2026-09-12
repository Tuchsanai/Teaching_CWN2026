---
name: yolo
description: เรียกใช้ Claude Code บัญชีอื่นบนเครื่องนี้ผ่านคำสั่ง yolo1..yolo5 แบบไม่เปิดหน้าจอ ใช้เมื่อผู้ใช้พูดว่า "เรียก yoloN", "ให้ Claude อีกบัญชีทำ...", "บัญชี Claude ไหนล็อกอินอยู่", หรือต้องการส่งผลลัพธ์ต่อไปยังบัญชี Claude/Codex อื่น
---

# yolo — เรียก Claude Code หลายบัญชี

ตัวแปรตั้งค่า (แก้ที่เดียว): `BASE_PATH="$HOME/ai-accounts"` (ค่าจริงบนเครื่องนี้ = `/root/ai-accounts`)

คำสั่ง `yoloN` คือ wrapper ที่ `/usr/local/bin/yoloN` ซึ่งรัน
`CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN claude --dangerously-skip-permissions "$@"`
(เวอร์ชันที่ติดตั้ง: Claude Code 2.1.266)

## ตารางบัญชี (ตรวจเมื่อ 2026-09-09 ด้วย `yoloN auth status`)

| คำสั่ง | CLI | config root | สถานะล็อกอิน |
|---|---|---|---|
| yolo1 | Claude Code | $BASE_PATH/.Claude/yolo1 | ล็อกอินแล้ว |
| yolo2 | Claude Code | $BASE_PATH/.Claude/yolo2 | ล็อกอินแล้ว |
| yolo3 | Claude Code | $BASE_PATH/.Claude/yolo3 | ยังไม่ล็อกอิน |
| yolo4 | Claude Code | $BASE_PATH/.Claude/yolo4 | ยังไม่ล็อกอิน |
| yolo5 | Claude Code | $BASE_PATH/.Claude/yolo5 | ยังไม่ล็อกอิน |

สถานะอาจเปลี่ยนได้ ก่อนใช้งานให้ตรวจสดเสมอ:

```bash
yoloN auth status < /dev/null   # exit 0 + "loggedIn": true = ล็อกอินแล้ว, exit 1 = ยังไม่ล็อกอิน
```

## วิธีเรียกแบบไม่เปิดหน้าจอ (ทดสอบแล้วกับ 2.1.266)

```bash
yoloN -p --model <model> --effort <effort> "<prompt>" < /dev/null
```

- `-p, --print` = ตอบแล้วออกทันที (non-interactive)
- `--model` รับ alias เช่น `fable`, `opus`, `sonnet` หรือชื่อเต็ม
- `--effort` รับ `low | medium | high | xhigh | max`
- `< /dev/null` ป้องกันการรอ stdin
- ผลลัพธ์ออกทาง stdout เก็บได้ด้วย `OUT="$(yoloN -p ... < /dev/null)"`

## ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ

- บัญชี: `yolo1`
- model: `fable`
- effort: `medium`
- ผู้ใช้ระบุบัญชี / model / effort เองได้เสมอ และให้ใช้ค่าที่ผู้ใช้ระบุก่อน

## กฎที่ต้องปฏิบัติ

1. ถ้าผู้ใช้ระบุบัญชีที่ "ยังไม่ล็อกอิน" → แจ้งผู้ใช้ว่าบัญชีนั้นยังไม่ล็อกอิน แล้วหยุด
   ห้ามสลับไปใช้บัญชีอื่นเอง ห้ามล็อกอินแทนผู้ใช้ (ห้ามรัน `yoloN auth login` / `claude login`)
2. ห้ามอ่าน คัดลอก แสดง หรือส่งต่อไฟล์ credential ใด ๆ ใน `$BASE_PATH/.Claude/yoloN/`
   (เช่น `.credentials.json`, `auth.json`, `settings.json` ที่มี key) ให้ใช้เฉพาะ `yoloN auth status` ในการตรวจสถานะ
3. ห้ามแก้ไขไฟล์ใน config root ของบัญชีอื่น

## วิธีส่งค่าต่อ (relay)

อ่านผลจากคำสั่งแรกเก็บในตัวแปร แล้วใส่ลงใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

ตัวอย่าง Claude → Claude (ต่างบัญชี):

```bash
Q="ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12"
A="$(yolo1 -p --model fable --effort medium "$Q" < /dev/null)"
yolo2 -p --model fable --effort medium "โจทย์: $Q
คำตอบจาก yolo1: $A
ตรวจว่าถูกหรือไม่ ตอบ CORRECT หรือ WRONG" < /dev/null
```

ตัวอย่าง Claude → Codex (ข้าม CLI ทดสอบแล้วได้ CORRECT):

```bash
A="$(yolo1 -p --model fable --effort medium "$Q" < /dev/null)"
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/out.txt "โจทย์: $Q
คำตอบจาก Claude (yolo1): $A
ตรวจว่าถูกหรือไม่ ตอบ CORRECT หรือ WRONG" < /dev/null
cat /tmp/out.txt
```

รายละเอียดฝั่ง Codex ดูสกิล `cyolo`
