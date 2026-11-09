---
name: agent-team
description: ให้หลายบัญชี yolo/cyolo ทำงานร่วมกันแบบ multi-agent ข้าม CLI ได้ — relay, fan-out, DAG, review loop, debate, best-of-N, router, failover ตามโควตา, human gate, สลับหัวหน้าทีม ใช้เมื่อ "แบ่งงานหลายบัญชี", "ส่งต่องานระหว่าง agent", "ให้หลายบัญชีช่วยกัน", "สลับหัวหน้า", "สถิติโทเค็นแต่ละบัญชี". Orchestrate many Claude and Codex accounts as a team: relay, fan-out, DAG, review loops, debate, best-of-N, routing, quota failover, human gates and leader handoff. Use for "split work across accounts", "hand off between agents", "agent team", "token stats per account".
---

# agent-team — ทีมหลายบัญชี

สคริปต์: `/root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py` (เรียกว่า `T`) ใช้สกิลข้างเคียง `yolo` และ `cyolo`

| ต้องการ | คำสั่ง |
|---|---|
| รันกราฟงาน + ตารางสรุป + โควตา | `python3 T run graph.json` หรือ `… run -` (stdin) · `--json` สำหรับโปรแกรม |
| รันต่อเฉพาะงานที่ล้ม/บล็อก | `python3 T run --resume <run_id> [--set node.expect=number] [--set node.prompt=...]` |
| ภาพรวมบัญชีและงาน | `python3 T status` (`--run <id>`) |
| ตรวจความพร้อมทุกบัญชี | `python3 T check` |
| โควตาทุกบัญชี | `python3 T quota` |
| สถิติ ledger | `python3 T stats` (`--run <id>`) |
| อนุมัติ human gate | `python3 T approve <run_id> <node>` |
| หัวหน้าทีมสลับตัวได้ | `python3 T lead --goal "..."` |
| สาธิตสลับหัวหน้า + ย้ายงาน | `python3 T lead --demo` (ใส่ `--goal "..."` ได้) |

รายละเอียดฟิลด์และรูปแบบอื่น (ไม่จำเป็นสำหรับงานทั่วไป): `references/patterns.md`

## กราฟตัวอย่าง: ทำขนาน → ตรวจ → แก้และทดสอบ

คัดลอกแล้วเปลี่ยน `prompt` และ `cwd` (เขียนไฟล์นี้ก่อน แล้ว `run`):

```json
{
  "goal": "สร้างโมดูลแล้วตรวจไขว้",
  "nodes": [
    {"id": "impl_a", "account": "any", "difficulty": 2, "cwd": "/workspace/proj",
     "prompt": "สร้างไฟล์ /workspace/proj/a.py ฟังก์ชัน add(a,b) แล้วตอบ path"},
    {"id": "impl_b", "account": "any", "difficulty": 2, "cwd": "/workspace/proj",
     "prompt": "สร้างไฟล์ /workspace/proj/b.py ฟังก์ชัน mul(a,b) แล้วตอบ path"},
    {"id": "review", "account": "cyolo", "kind": "code_review", "difficulty": 2, "cwd": "/workspace/proj",
     "depends_on": ["impl_a", "impl_b"],
     "prompt": "ตรวจโค้ด /workspace/proj/a.py และ b.py รายงานจุดที่ควรแก้เป็นข้อ ๆ"},
    {"id": "fix", "account": "yolo", "difficulty": 2, "cwd": "/workspace/proj",
     "depends_on": ["review"],
     "prompt": "อ่านผลตรวจที่ {{file:review}} แก้โค้ด เขียน test แล้วรัน ตอบผลทดสอบ"}
  ]
}
```

ฟิลด์ node ที่ใช้บ่อย:

| ฟิลด์ | ความหมาย |
|---|---|
| `id` | a-z A-Z 0-9 _ . - |
| `account` | `yolo2` (ผูกบัญชี ไม่ย้ายให้) · `yolo`/`cyolo` (ฝั่ง) · `any` (router เลือก: ภาพ/ตรวจโค้ด → Codex, เอกสารยาว → Claude) |
| `difficulty` | 1–6 กำหนดรุ่นและ effort ใช้ `1` กับงานง่ายเสมอ |
| `depends_on` | งานที่ต้องจบก่อน (ใส่ `{{x}}` แล้วเพิ่มให้เอง) |
| `{{x}}` / `{{file:x}}` | แทรกค่าสั้น / ส่ง path ผลงาน (ข้อมูลยาวใช้แบบนี้) |
| `expect` | `number`, `integer`, `json`, `nonempty`, `regex:<re>`, `contains:<ข้อความ>` ไม่ผ่าน = ล้ม แต่เก็บคำตอบใน `out/` |
| `cwd` | โฟลเดอร์ทำงานของงานนั้น (absolute) |
| `approve` | `true` = รอ `approve` ก่อนเริ่ม |
| `prefer` | บัญชีที่อยากให้ลองก่อน แต่ย้ายได้ |
| `kind` | `image`, `code_review`, `long_doc`, `general` (ไม่ใส่ = เดาจาก prompt) |
| `board` | `true` = บอก agent ให้แชร์ข้อค้นพบผ่านบรรทัด `BOARD: ...` |

งานสร้างภาพในกราฟ: `{"id":"pic","kind":"image","out":"/workspace/pic.png","prompt":"วงกลมสีแดง"}` · debate: `{"id":"d","type":"debate","prompt":"โจทย์","judge":"yolo","difficulty":1}` (อ่านผล `{{d}}`) · รูปแบบอื่นดู `references/patterns.md`

ตัวเลือก `run`: `--max-total` (8) `--max-per-account` (3) `--timeout` (600) `--worker-token-budget N` `--quota-stop 80` `--simulate-limit yolo1` `--fresh-check`

exit code: `0` สำเร็จ · `1` มีงานล้ม · `2` กราฟผิด · `3` รอ human gate · `check`/`quota`/`status`/`stats` คืน 0 แม้บางบัญชีไม่พร้อม

กฎ: งานที่ต้องการคนละบัญชี (เช่น ผู้ตรวจต้องไม่ใช่ผู้เขียน) ให้ระบุบัญชีเจาะจง เพราะ `any` อาจเลือกซ้ำ · `{{x}}` ส่งเฉพาะค่าสั้น · งานที่ล้มจาก non-quota **ไม่ retry อัตโนมัติ** ให้แก้แล้ว `--resume` · งานที่ระบุบัญชีเองไม่ย้าย หยุดแล้วรายงาน · agent เขียนบรรทัด `BOARD: ...` แล้วระบบจะบันทึกลง `board.md` (พร้อมผู้เขียนและเวลา) ให้ agent ถัดไปเห็น

## หัวหน้าทีมสลับตัวได้

`T lead` รันหัวหน้าเป็นรอบสั้น ผู้ควบคุมเป็นสคริปต์ ไม่ใช้โทเค็น ลูกทีมเป็น process แยก หัวหน้าเปลี่ยนตัวแล้วงานยังเดินต่อ สถานะอยู่ใน `state.json` + `handoff.md`

สาธิตครบในคำสั่งเดียว (หัวหน้าล้มกลางคัน → สลับเชิงรับ, หัวหน้าคนถัดไปชนงบ → สลับเชิงรุก, ลูกทีมชนโควตา → ย้ายงาน ใช้รุ่นถูก):

```
python3 T lead --demo
python3 T lead --demo --goal "แบ่งงานให้ลูกทีม 3 ชิ้น เขียนประโยคเรื่อง A B C แล้วรวมเป็นไฟล์เดียว"
```

งานจริง: `python3 T lead --goal "..." --lead yolo1 --succession yolo1,yolo2,cyolo1 --lead-token-budget 200000 --worker-token-budget 500000` · ตัวจำลอง `--simulate-crash <บัญชี>` `--simulate-limit <บัญชี>` · หัวหน้าทำงานต่อ: `--resume <run_id>` · จบด้วยตาราง การสลับหัวหน้า/การย้ายงาน/ผลงาน/สถิติ ผลรวมอยู่ที่ `out/final.md`

## เรียกจาก host

อ่านสกิลก่อนเริ่ม แล้วเรียกผ่าน `docker exec` (ใช้ path แบบ `../root/...` ได้ทั้ง PowerShell และ Git Bash โดยไม่ต้องแก้):

```
docker exec multi-account cat ../root/ai-accounts/.Claude/shared/skills/agent-team/SKILL.md
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py check
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py quota
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py status
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py stats
```

ส่งกราฟเข้า stdin โดยไม่ใช้ heredoc: เขียนไฟล์ JSON บน host (เช่น `graph.json`) แล้วรัน (ใช้ได้ทั้งสอง shell และซ่อม encoding ภาษาไทยให้เอง):

```
cat graph.json | docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py run -
```

ส่ง `--json` ถ้าต้องการให้โปรแกรมอ่านผล ไม่ต้องรันใน background เพราะ `run` พิมพ์ความคืบหน้าทีละบรรทัดจนจบ
