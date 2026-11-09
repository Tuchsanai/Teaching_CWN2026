---
name: agent-team
description: ให้หลายบัญชี Claude Code และ Codex ทำงานร่วมกันแบบ multi-agent ทั้งภายใน CLI เดียวกันและข้าม CLI แบ่งงานขนาน ส่งต่องาน review loop debate best-of-N router failover ตามโควตา หัวหน้าทีมสลับตัวได้ ใช้เมื่อ "แบ่งงานหลายบัญชี", "ส่งต่องานระหว่าง agent", "ให้หลาย agent ตรวจไขว้", "หัวหน้าทีม", "สถิติโทเค็นแต่ละบัญชี", "สรุปทีม" · Use for multi-account agent teams: fan-out, relay, DAG, review loops, debate, routing, quota failover, leader handoff, team token stats.
---

# agent-team — ทีมหลายบัญชี

`T=/root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py` (จาก Codex ใช้ `.Codex` แทน `.Claude`) ทุกคำสั่งมี `--help`

**ถ้าอ่านไฟล์นี้อยู่ใน container (เป็น yoloN/cyoloN) ให้รัน `python3 $T ...` ตรง ๆ ใน container ไม่มีคำสั่ง docker** · ถ้าอยู่บน host ดูหัวข้อ "เรียกจาก host"

| ต้องการ | คำสั่ง |
|---|---|
| ตรวจความพร้อมทุกบัญชี | `python3 $T check` |
| รันกราฟงาน จบด้วยตาราง + โควตา | `python3 $T run g.json` (`-` = stdin · `--json`) |
| รันต่อจาก run เดิม | `python3 $T run --resume <id> --set t1.expect=text` |
| โควตาทุกบัญชี | `python3 $T quota` |
| ภาพรวมบัญชีของ run | `python3 $T status [run]` |
| สถิติทีม (ledger) | `python3 $T stats [--run <id>]` |
| อนุมัติ human gate | `python3 $T approve <run> <node>` |
| กระดานความรู้ | `python3 $T board <run> [--by me --text "..."]` |
| ดู router โดยไม่เรียกโมเดล | `python3 $T route "ตรวจโค้ดนี้"` |
| หัวหน้าทีมทำเป้าหมายให้ | `python3 $T lead --goal "..."` |
| สาธิตสลับหัวหน้า | `python3 $T lead --demo` |

## กราฟตัวอย่าง: ทำขนาน → ตรวจ → แก้และทดสอบ

```json
{"goal":"เขียน add.py และ sub.py แล้วตรวจ",
 "defaults":{"difficulty":1,"cwd":"work"},
 "nodes":[
  {"id":"a","account":"yolo1","prompt":"เขียนไฟล์ add.py ฟังก์ชัน add(a,b) ในโฟลเดอร์ทำงาน ตอบชื่อไฟล์อย่างเดียว"},
  {"id":"b","account":"cyolo1","prompt":"เขียนไฟล์ sub.py ฟังก์ชัน sub(a,b) ในโฟลเดอร์ทำงาน ตอบชื่อไฟล์อย่างเดียว"},
  {"id":"review","account":"cyolo","depends_on":["a","b"],"prompt":"ตรวจ add.py และ sub.py ในโฟลเดอร์ทำงาน บอกปัญหาเป็นข้อ ๆ ถ้าไม่มีตอบ ไม่มีปัญหา"},
  {"id":"fix","account":"yolo","depends_on":["review"],"prompt":"ข้อตรวจ: {{review}}\nแก้ไฟล์ตามข้อตรวจถ้ามี แล้วรันทดสอบ add(2,3) และ sub(5,3) ตอบผลลัพธ์"}
 ]}
```

ค่า `cwd` แบบ relative จะอยู่ใต้ run directory (ทุกงานในกราฟนี้ใช้โฟลเดอร์เดียวกัน) · งานแก้ไฟล์เดียวกันพร้อมกันให้แยก `cwd`

## ฟิลด์ของงาน (node)

| ฟิลด์ | ความหมาย |
|---|---|
| `id` `prompt` | จำเป็น (`A-Za-z0-9_.-`) |
| `account` | `yolo2` (ระบุเอง ไม่ย้ายอัตโนมัติ) · `yolo` / `cyolo` (ฝั่ง) · `any` (router ค่าเริ่มต้น) |
| `difficulty` / `model` / `effort` | 1 ง่าย … 6 งานใหญ่ หรือระบุเอง (กราฟทดสอบใช้ 1 = haiku/low) |
| `depends_on` | งานก่อนหน้า (`{{x}}` เพิ่มให้เอง) |
| `{{node}}` / `{{file:node}}` | แทรกค่าสั้น / path ไฟล์ของข้อมูลยาว (`{{run_dir}}` `{{out_dir}}`) |
| `expect` | `text` · `int` · `number` · `json` · `regex:…` · `contains:…` คำตอบที่ไม่ผ่านเก็บใน `out/` และบอกเหตุผล |
| `kind` | `task` (ค่าเริ่มต้น) · `image` (+`path`) · `review` · `debate` · `best_of` |
| `cwd` `timeout` `task_type` | โฟลเดอร์ทำงาน · วินาที · `image`/`code_review`/`long_doc` ให้ router |
| `board` | `true` ให้ agent เขียนข้อค้นพบ (บรรทัด `BOARD: ...`) ลงกระดาน · งานถัดไปเห็นอัตโนมัติ |
| `approve` | `true` หยุดรอไฟล์อนุมัติก่อนรัน |

## รูปแบบที่ใช้บ่อย

```json
{"id":"rv","kind":"review","worker":"yolo","reviewer":"cyolo","prompt":"เขียนฟังก์ชัน ...","review_prompt":"เกณฑ์การตรวจ","max_rounds":3}
{"id":"db","kind":"debate","accounts":["yolo","cyolo"],"judge":"any","prompt":"คำถาม"}
{"id":"best","kind":"best_of","accounts":["yolo1","yolo2","cyolo1"],"judge":"any","criteria":"ชัดเจน สั้น","prompt":"เขียนคำโปรย"}
{"id":"img","kind":"image","account":"cyolo","path":"/workspace/out.png","prompt":"วงกลมสีแดง 1 วง พื้นขาว"}
```

relay: ต่อ `depends_on` เป็นทอด ๆ และ `{{a}}` · fan-out/fan-in: หลายงานไม่มี deps แล้วงานรวมอ้าง `{{file:x}}` ทุกตัว · งานล้ม งานที่ขึ้นกับมันถูก `blocked` ไม่ retry อัตโนมัติ

## สาธิตสลับหัวหน้าทีมและย้ายงานลูกทีม

คำสั่งเดียวเกิดครบทั้ง สลับหัวหน้าเชิงรับ, เชิงรุก และย้ายงานลูกทีม โดยไม่ต้องตั้งค่าเอง จบด้วยตารางประวัติ:

```bash
python3 $T lead --demo
python3 $T lead --demo --goal "เขียนบทความ 4 หัวข้อเรื่อง X แบ่งให้ลูกทีมหัวข้อละงาน แล้วรวมเป็นไฟล์เดียว"
```

`--demo` ใช้รุ่นต่ำ ตั้งให้เองว่า หัวหน้าคนแรกล้มหลังสั่งงาน (`--simulate-crash`), หัวหน้าคนที่สองงบ 1 โทเค็น (`--lead-token-budget บัญชี=1`), ลูกทีมคนแรกงบ 1 โทเค็น (`--worker-token-budget บัญชี=1`) และบังคับทำครั้งละ 1 งานต่อบัญชีจึงมีงานในคิวให้ย้าย งานที่กำลังรันจะทำจนจบ ไม่ถูกย้าย ต้องการบัญชีพร้อมอย่างน้อย 2 บัญชี

ปรับเอง: `--succession yolo1,yolo2,cyolo1` · `--exclude yolo2` · `--simulate-limit yolo1` (เหมือน `MA_SIMULATE_LIMIT`) · `--lead-difficulty 1` · `--quota-stop 80` · ไฟล์รวมอยู่ใน `out/final.md`

งบโทเค็นนับ input ใหม่ + cache write + output ไม่นับ cache read และไม่นับการตรวจความพร้อม

## เรียกจาก host

container คือ `multi-account` ห่อคำสั่งด้วย `sh -c "..."` เสมอ (Git Bash จะแปลง `/root/...` ถ้าไม่ห่อ) อ่านสกิล แล้วเรียก:

```text
docker exec multi-account sh -c "cat /root/ai-accounts/.Claude/shared/skills/agent-team/SKILL.md"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py check"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py status"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py lead --demo"
```

ส่งกราฟจาก host (ห้ามใช้ heredoc): เขียนไฟล์ด้วย Write เช่น `g.json` แล้ว

```text
docker cp g.json multi-account:/tmp/g.json
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py run /tmp/g.json"
```

สองบรรทัดนี้ใช้ได้ทั้ง PowerShell และ Git Bash และรักษาภาษาไทย ส่วน `run -` รับกราฟทาง stdin ก็ได้: Git Bash ใช้ `docker exec -i multi-account sh -c "python3 …/team.py run -" < g.json` ได้เลย แต่ PowerShell 5.1 ไม่มี `<` และ pipe ทำภาษาไทยเพี้ยน (สคริปต์ตรวจแล้วปฏิเสธให้) จึงควรใช้ `docker cp`

ไฟล์ผลลัพธ์อยู่ที่ `/workspace/.agent-team/<run_id>/` (`graph.json` `board.md` `msgs/` `out/` `ledger.jsonl` `state.json` `handoff.md`) รายละเอียดเพิ่มดู `references/reference.md`
