# สกิลระบบหลายบัญชี (yolo · cyolo · agent-team)

ชุดสกิลสำหรับ container `multi-account` ที่ทำให้ AI ใช้ Claude Code หลายบัญชี (`yolo1…yoloN`) และ Codex CLI หลายบัญชี (`cyolo1…cyoloN`) ได้ถูกวิธี ประหยัด และทำงานร่วมกันเป็นทีม

| สกิล | ใช้ทำอะไร | สคริปต์ |
|---|---|---|
| `yolo` | เรียก Claude Code บัญชีใดก็ได้แบบไม่โต้ตอบ เลือกรุ่น/effort ตามความยาก ตรวจความพร้อมด้วยการเรียกจริง ดูโควตา `/usage` สถิติต่อครั้ง | `yolo/scripts/yolo.py` |
| `cyolo` | เรียก Codex บัญชีใดก็ได้ เลือกรุ่น/effort จาก `models_cache.json` **สร้างภาพ** ตรวจความพร้อม โควตาจาก rollout สถิติต่อครั้ง | `cyolo/scripts/cyolo.py` |
| `agent-team` | หลายบัญชีทำงานร่วมกัน: relay, fan-out/fan-in, DAG, review loop, board, debate, best-of-N, router, failover, human gate, งบโทเค็นลูกทีม, สลับหัวหน้าทีม, สถิติทั้งทีม | `agent-team/scripts/team.py` |

ทั้งหมดเป็น Python 3.8+ ไลบรารีมาตรฐาน ไม่ต้องติดตั้งแพ็กเกจเพิ่ม · `macore.py` (แกนกลางร่วม) มีสำเนาเหมือนกันใน `yolo/scripts` และ `cyolo/scripts` เพื่อให้แต่ละสกิลใช้เดี่ยว ๆ ได้ — แก้แล้วต้องคัดลอกให้ตรงกัน (install.sh ตรวจให้)

## ติดตั้ง

โฟลเดอร์นี้บน host คือต้นฉบับสำรอง ติดตั้งลง container ด้วยการคัดลอกโฟลเดอร์แล้วรัน `install.sh`:

```bash
docker cp ./skills multi-account:/tmp/skills
docker exec multi-account bash /tmp/skills/install.sh
```

`install.sh`:

- คัดลอกทุกโฟลเดอร์ที่มี `SKILL.md` ไปที่ `/root/ai-accounts/.Claude/shared/skills/` และ `/root/ai-accounts/.Codex/shared/skills/` (อยู่ใน volume `ai-accounts` จึงคงอยู่แม้ลบ container)
- สกิลชื่อเดิมที่เนื้อหาต่างกันสำรองไป `/root/ai-accounts/.skill-backup-<วันเวลา>/` ก่อนเขียนทับ · เนื้อหาเหมือนเดิมข้าม (รันซ้ำได้ ผลเหมือนเดิม)
- ไม่แตะสกิลอื่นและไม่แตะไฟล์ credential
- ตรวจว่าทุกบัญชีเห็น `SKILL.md` ของทุกสกิล: บัญชีที่ `skills` เป็น symlink ทั้งโฟลเดอร์ (`yoloN/skills → ../shared/skills` ใน volume เก่า) เห็นเองอยู่แล้ว · นอกนั้น (ทุกบัญชีใน volume ใหม่ ทั้ง yolo และ cyolo) สร้าง symlink รายสกิลให้ แบบเดียวกับ wrapper

## ใช้งาน

ใน container (`yoloN`/`cyoloN` โหลดสกิลจาก shared อัตโนมัติ) แค่ขอเป็นภาษาธรรมชาติ เช่น "ให้ cyolo2 ตรวจโค้ดนี้", "แบ่งงานนี้ให้หลายบัญชี", "สถิติโทเค็นแต่ละบัญชี"

จาก host ผ่าน `docker exec`:

```bash
docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/agent-team/SKILL.md       # อ่านสกิลก่อน
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py check
docker exec -i multi-account python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py run - < graph.json
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py stats
```

ผลงานของทีมอยู่ที่ `/workspace/.agent-team/<run_id>/` = `workspace/.agent-team/` บน host

## โครงสร้าง

```
skills/
├── install.sh            ติดตั้งลง shared ของทั้งสอง CLI
├── README.md             ไฟล์นี้
├── TEST-REPORT.md        ผลทดสอบใน container จริง
├── yolo/        SKILL.md · scripts/{yolo.py, macore.py} · references/claude-cli.md
├── cyolo/       SKILL.md · scripts/{cyolo.py, macore.py} · references/codex-cli.md
└── agent-team/  SKILL.md · scripts/team.py · references/{graph.md, leader.md, tokens.md}
```

## ความปลอดภัย

บัญชีทุกตัวรันแบบข้าม permission/sandbox เป็น root ใช้กับงานที่ได้รับอนุญาตเท่านั้น · สคริปต์ไม่อ่าน `.credentials.json`, `.claude.json`, `auth.json` และไม่แสดงอีเมล/orgId · ledger เก็บแค่จำนวนตัวอักษรของ prompt · ไม่มีการล็อกอินแทนผู้ใช้: บัญชีที่ไม่พร้อมถูกรายงานให้ผู้ใช้ล็อกอินเอง
