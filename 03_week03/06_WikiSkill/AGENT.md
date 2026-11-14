# กติกาของ LAB (ไฟล์นี้เขียนให้ Claude อ่าน)

โฟลเดอร์นี้ = **ต้นฉบับบนเครื่อง** · container `multi-account` = **ที่รันเท่านั้น** (`/workspace/wklab`)

| อะไร | บนเครื่อง (โฟลเดอร์นี้) | ใน container |
|---|---|---|
| ตัวรัน WikiSkill และ prompt | `wikiskill/` | `/workspace/wklab/wikiskill` |
| ชุดโจทย์และ Grader (ชุดเดียวกับบท 05 + Test Set 3 ข้อ) | `suite/` | `/workspace/wklab/suite` |
| ตัวรัน Trial ของบท 05 | `../../00_resource/skills/skill-optimizer` | `/workspace/wklab/skill-optimizer` |
| สกิลของบท 05 ที่ใช้เทียบ | `../05_Skill_Optimizer/runs/v3/skills/money-coder` | `/workspace/wklab/baselines/v3/skills` |
| workspace ของ WikiSkill (raw/ wiki/ skills/) | `runs/<ชื่อ>/` | `/workspace/wklab/ws/<ชื่อ>` |
| ผลของทุก Trial | `results/` | `/workspace/wklab/suite/runs` |

## ทำตามนี้ทุกครั้ง

0. คำสั่ง `bash tools/…` และ path `results/` `runs/` ในไฟล์นี้เทียบกับโฟลเดอร์ของบท: `cd 03_week03/06_WikiSkill` ก่อน
1. ส่งไฟล์เข้า container: `bash tools/push.sh` (รันซ้ำได้)
2. คำสั่งทั้งหมดรันใน container ด้วยรูปแบบนี้ (แทน `<คำสั่ง>`):
   `docker exec multi-account bash -lc 'cd /workspace/wklab && python3 wikiskill/wikiskill.py <คำสั่ง>'`
3. สร้าง workspace (ครั้งเดียวต่อ 1 ชื่อ · ถ้าชื่อนั้นมีอยู่แล้ว `init` จะไม่ทำอะไร ให้ถามผู้ใช้ว่าจะใช้ชื่อใหม่หรือไม่ ห้ามลบของเดิมเอง):
   `init ws/<ชื่อ> --suite suite --skillopt skill-optimizer/scripts/skillopt.py --accounts <บัญชี yolo ที่ล็อกอินแล้ว คั่นด้วย ,> --iters 8 --task-desc "เขียนฟังก์ชัน Python สำหรับคิดเงินของร้านกาแฟ BaanKafe (ตัวตรวจอัตโนมัติให้คะแนนผลงาน 10 ข้อ)"`
   ค่าอื่นใช้ค่าเริ่มต้น (`--reps 3 --par 6 --model sonnet --effort medium --opt-model sonnet --opt-effort high`) ซึ่งเท่ากับบท 05
4. ลำดับของ 1 รอบ: `rollout ws/<ชื่อ>` → `maintain ws/<ชื่อ>` → `propose ws/<ชื่อ>` → `gate ws/<ชื่อ>` · ก่อนรอบแรกต้อง `baseline ws/<ชื่อ>` · ทำทุกรอบจนจบด้วย `loop ws/<ชื่อ>` (ทำต่อจากขั้นที่ค้าง ไม่เริ่มใหม่) · ดูตารางสรุปและเหตุผลที่วงรอบหยุดด้วย `status ws/<ชื่อ>`

   | ขั้น | ชั้นที่เปลี่ยน | ไฟล์ที่เกิดหรือเปลี่ยน |
   |---|---|---|
   | `baseline` | ไม่มี | `state.json` (R_best) |
   | `rollout` | raw | `raw/iter-NN/traces/*.md` · `raw/iter-NN/summary.md` |
   | `maintain` | wiki | `wiki/patterns/*.md` · `wiki/index.md` · `wiki/log.md` |
   | `propose` | ยังไม่มี (ข้อเสนอยังไม่ใช่สกิลที่ใช้งาน) | `history/iter-NN/proposal.json` |
   | `gate` | skills (เมื่อรับ) + wiki | `skills/*/SKILL.md` `PURPOSE.md` · `wiki/skill-impact.md` |
5. วัดชุดสกิลใดก็ได้: `eval ws/<ชื่อ> --label <ป้าย> --skills <active | none | โฟลเดอร์ skills> --split <train|val|test|all>` · ตารางเทียบ: `python3 skill-optimizer/scripts/skillopt.py report suite --labels <ป้าย,ป้าย>`
6. เก็บผลลงเครื่องทุกครั้งหลังรัน: `bash tools/pull.sh` แล้วบันทึกผลของ `status ws/<ชื่อ>` ลง `results/status-<ชื่อ>.txt` ด้วย `docker exec … > results/status-<ชื่อ>.txt` · ผลของ `report` ลง `results/report.md` เฉพาะเมื่อพรอมต์สั่งให้รัน `report`
7. คำสั่ง `loop` และ `eval` ใช้เวลาหลายนาที ให้รันแบบเบื้องหลังแล้วรอจนจบ ไม่ต้องรันซ้ำ (รันซ้ำได้: Trial ที่เสร็จแล้วจะไม่ถูกรันใหม่) · ขั้นเดี่ยว (`baseline` `rollout` `maintain` `propose` `gate`) ใช้ 20–80 วินาที รันแบบปกติได้

ตรวจบัญชีที่ล็อกอินแล้ว: `docker exec multi-account bash -lc 'for a in yolo1 yolo2 yolo3 yolo4 yolo5; do $a auth status 2>/dev/null | grep -q "loggedIn.: *true" && echo "$a ok" || echo "$a ยังไม่ล็อกอิน"; done'`
ตรวจ Grader: `docker exec multi-account bash -lc 'cd /workspace/wklab && python3 suite/check_grader.py'` (รันได้ แต่ไม่ต้องเปิดอ่านไฟล์)
ไฟล์ที่เปิดอ่านได้หลังแต่ละขั้น (ใน container ใต้ `ws/<ชื่อ>/` หรือบนเครื่องใต้ `runs/<ชื่อ>/` หลัง pull):
`raw/iter-NN/summary.md` · `raw/iter-NN/traces/*.md` · `wiki/index.md` · `wiki/log.md` · `wiki/skill-impact.md` · `wiki/patterns/*.md` · `skills/*/SKILL.md` · `skills/*/PURPOSE.md` · `history/iter-NN/proposal.json` · `state.json`

บน Windows (Git Bash) ตั้ง `export MSYS_NO_PATHCONV=1` ก่อน `docker exec` ทุกครั้ง

## ข้อห้าม

- ห้ามแก้ไฟล์ใน `wiki/` `skills/` `raw/` ด้วยมือ · ทั้งสามชั้นเปลี่ยนได้โดย `wikiskill.py` เท่านั้น (นี่คือสิ่งที่บทนี้ต้องการวัด)
- ห้ามเปิด `suite/grade.py` `suite/check_grader.py` `suite/ref/` และโจทย์ ผลรายข้อ หรือโค้ดของ Validation Set (โจทย์ที่ขึ้นต้นด้วย `v`) · คะแนนราย Trial ที่คำสั่งพิมพ์ออกมาเองดูได้ · Test Set (ขึ้นต้นด้วย `x`) เปิดผลรายข้อได้หลังวัดครบทุกชุดสกิลแล้วเท่านั้น
- ห้ามแก้ Grader โจทย์ หรือ prompt ใน `wikiskill/prompts/` ระหว่าง LAB · ห้ามวัดซ้ำเพื่อให้ได้คะแนนที่ต้องการ
- ห้ามติดตั้งหรือแก้สกิล global ใน `/root/ai-accounts` · ห้ามล็อกอินแทนผู้ใช้ · ห้ามรันคำสั่ง git
- ตัวเลขในคำตอบต้องมาจากผลของคำสั่ง หรือไฟล์ใน workspace เท่านั้น · ตอบสั้น เป็นตาราง
