# กติกาของ LAB (ไฟล์นี้เขียนให้ Claude อ่าน)

โฟลเดอร์นี้ = **ต้นฉบับบนเครื่อง** · container `multi-account` = **ที่รันเท่านั้น** (`/workspace/sklab`)

| อะไร | บนเครื่อง (โฟลเดอร์นี้) | ใน container |
|---|---|---|
| เครื่องมือ `skill-optimizer` | `../../00_resource/skills/skill-optimizer` | `/workspace/sklab/skill-optimizer` |
| ชุดโจทย์และ Grader | `suite/` | `/workspace/sklab/suite` |
| สกิลที่ถูกปรับ ทุกรุ่น | `skills/money-coder/v0` `v1` … และ `ISSUES.md` | `/workspace/sklab/skills/money-coder` |
| ผลการวัด | `results/` | `/workspace/sklab/suite/runs` |

## ทำตามนี้ทุกครั้ง

1. ส่งไฟล์เข้า container: `bash tools/push.sh` (รันซ้ำได้ ทุกครั้งที่สร้างหรือแก้ไฟล์บนเครื่อง)
2. อ่าน `/workspace/sklab/skill-optimizer/SKILL.md` ใน container แล้วทำตามขั้นตอนของสกิลนั้น · คำสั่งรันใน container: `docker exec multi-account bash -lc 'cd /workspace/sklab && python3 skill-optimizer/scripts/skillopt.py <คำสั่ง>'`
3. สกิลรุ่นใหม่สร้าง **บนเครื่อง**: คัดลอก `skills/money-coder/<รุ่นฐาน>` เป็น `skills/money-coder/<รุ่นใหม่>` แล้วแก้ในโฟลเดอร์ใหม่ · ห้ามแก้รุ่นเดิม · รุ่นฐาน = รุ่นล่าสุดที่ Gate ให้ ACCEPT · Issue Log อยู่ที่ `skills/money-coder/ISSUES.md`
4. **1 จุด** = กติกา 1 ข้อ หรือสคริปต์ 1 ไฟล์ ที่เพิ่ม ลบ หรือแทน · แต่ละรุ่นแก้ไม่เกิน 3 จุด
5. วัดทุกรุ่นด้วยค่าเดียวกัน: `run suite --skill skills/money-coder/<รุ่น> --label <รุ่น> --reps 3 --model sonnet --effort medium --accounts <บัญชี yolo ที่ล็อกอินแล้ว คั่นด้วย ,> --par 6` (ไม่มีสกิล: `--skill none --label noskill`)
6. `gate` ใช้ `--cost-metric context_tokens` เสมอ
7. เก็บผลลงเครื่องทุกครั้งหลังวัดหรือตัดสิน: `bash tools/pull.sh` แล้วบันทึกผลของคำสั่งลง `results/` ด้วย `docker exec … > results/<ไฟล์>`
   - `report.md` = `report suite --labels <ทุกรุ่นที่วัดแล้ว เรียงตามลำดับ>`
   - `gate-<ฐาน>-<ใหม่>.txt` · `failures-<รุ่น>.txt` · `null-<รุ่น>.txt` · `lint-<รุ่น>.json`

ตรวจบัญชีที่ล็อกอินแล้ว: `docker exec multi-account bash -lc 'for a in yolo1 yolo2 yolo3 yolo4 yolo5; do $a auth status 2>/dev/null | grep -q "loggedIn.: *true" && echo "$a ok" || echo "$a ยังไม่ล็อกอิน"; done'`
ตรวจ Grader: `docker exec multi-account bash -lc 'cd /workspace/sklab && python3 suite/check_grader.py'` (รันได้ แต่ไม่ต้องเปิดอ่านไฟล์)
ค่าในไฟล์นี้ใช้แทนค่าเริ่มต้นใน `SKILL.md` ของ `skill-optimizer` (เช่น `--reps 3`) · Grader ตรวจแล้วใน LAB 0 รุ่นถัดไปไม่ต้องตรวจซ้ำ
โจทย์ของ Training Set อ่านจาก `suite/runs/<รุ่น>/t*-r1/task.json` ใน container (ไม่พิมพ์ `suite/suite.json` ทั้งไฟล์ เพราะมีโจทย์ของ Validation Set)
รายการคำสั่ง จำนวนรอบ และโทเคนของแต่ละ Trial ดูได้จาก `results/runs/<รุ่น>/<โจทย์>-r<รอบ>/metrics.json` บนเครื่อง
Trace ของแต่ละ Trial อยู่ใน container: `suite/runs/<รุ่น>/<โจทย์>-r<รอบ>/transcript.jsonl` (อ่านผ่าน `docker exec`) · ใน `failures` รายการที่ score 1.00 คือ Trial ที่มีแค่คำสั่งล้ม ไม่ใช่ข้อที่พลาดของสกิล

บน Windows (Git Bash) ตั้ง `export MSYS_NO_PATHCONV=1` ก่อน `docker exec` ทุกครั้ง · ไฟล์ที่มีหลายบรรทัดให้สร้างด้วยเครื่องมือเขียนไฟล์ ไม่ใช้ heredoc

## ข้อห้าม

- ห้ามเปิด `suite/grade.py` `suite/check_grader.py` `suite/ref/` และโจทย์ ผลรายข้อ หรือโค้ดของ Validation Set (โจทย์ที่ขึ้นต้นด้วย `v`) · ของ Validation Set ใช้ได้เฉพาะคะแนนจาก `report` และ `gate` · `failures` ใช้ค่าเริ่มต้น = Training Set เท่านั้น
- ห้ามแก้ Grader หรือโจทย์
- ห้ามใส่ชื่อฟังก์ชัน ตัวเลขของโจทย์ หรือคำตอบของ Training Set ลงในสกิล · ใส่ได้เฉพาะมาตรฐานของร้านที่ใช้กับทุกโจทย์ (เช่น รูปแบบ CLI ชนิดของ error จำนวนเทสต์ขั้นต่ำ) ซึ่งเห็นได้จากข้อความของ `failures`
- ห้ามติดตั้งหรือแก้สกิล global ใน `/root/ai-accounts` · ห้ามล็อกอินแทนผู้ใช้ · ห้ามรันคำสั่ง git
- ตัวเลขในคำตอบต้องมาจากคำสั่งของ `skill-optimizer` เท่านั้น · ตอบสั้น เป็นตาราง
