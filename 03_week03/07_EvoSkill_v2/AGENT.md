# กติกาของ LAB (ไฟล์นี้เขียนให้ Claude อ่าน)

โฟลเดอร์นี้ = **ต้นฉบับบนเครื่อง** · container `multi-account` = **ที่รันเท่านั้น** (`/workspace/evlab`)

| อะไร | บนเครื่อง (โฟลเดอร์นี้) | ใน container |
|---|---|---|
| ตัวรัน EvoSkill v2 และ prompt | `evoskill/` | `/workspace/evlab/evoskill` |
| สิ่งที่ผู้ใช้ส่งให้การรัน: คำสั่ง · ข้อมูล · การแบ่งชุด · ตัวตรวจ | `bench/` | `/workspace/evlab/bench` |
| ตัวรัน Trial ของบท 05 (ใช้เป็น Solver) | `../../00_resource/skills/skill-optimizer` | `/workspace/evlab/skill-optimizer` |
| สกิลของบท 05 และ 06 ที่ใช้เทียบ | `../05_…/skills/money-coder/v3` · `../06_WikiSkill/runs/w2/skills` | `/workspace/evlab/baselines/so-v3/skills` · `baselines/wiki-w2/skills` |
| โฟลเดอร์ของแต่ละการรัน | `runs/<ชื่อ>/` | `/workspace/evlab/ws/<ชื่อ>` |

## ทำตามนี้ทุกครั้ง

0. คำสั่ง `bash tools/…` และ path `results/` `runs/` ในไฟล์นี้เทียบกับโฟลเดอร์ของบท: `cd 03_week03/07_EvoSkill_v2` ก่อน
1. ส่งไฟล์เข้า container: `bash tools/push.sh` (รันซ้ำได้)
2. คำสั่งทั้งหมดรันใน container ด้วยรูปแบบนี้ (แทน `<คำสั่ง>`):
   `docker exec multi-account bash -lc 'cd /workspace/evlab && python3 -W ignore evoskill/evoskill.py <คำสั่ง>'`
3. สร้างการรัน (ครั้งเดียวต่อ 1 ชื่อ · ถ้าชื่อนั้นมีอยู่แล้ว `init` จะไม่ทำอะไร ให้ถามผู้ใช้ว่าจะใช้ชื่อใหม่หรือไม่ ห้ามลบของเดิมเอง):
   `init ws/<ชื่อ> --instruction bench/instruction.md --data bench/data/baankafe --split bench/split.json --grader bench/benchmark_grader.py --solver-prompt bench/solver_prompt.txt --skillopt skill-optimizer/scripts/skillopt.py --accounts <บัญชี yolo ที่ล็อกอินแล้ว คั่นด้วย ,>`
   ค่าอื่นใช้ค่าเริ่มต้น (`--solver-model sonnet --solver-effort medium --evolver-model sonnet --evolver-effort high --par 6`) ซึ่ง Solver เท่ากับบท 05 และ 06 · ขนาดของการรัน (`3 epochs · 3 samples per task`) อ่านจากไฟล์คำสั่งของผู้ใช้
4. ลำดับของ 1 การรัน: `adapt` → `base` → (`turn` → `rollout`) × จำนวน epoch → `test` · รันทีละขั้นด้วยชื่อขั้นตามด้วยการรัน เช่น `adapt ws/<ชื่อ>` `base ws/<ชื่อ>` `turn ws/<ชื่อ>` `rollout ws/<ชื่อ>` · ทำทุกขั้นที่เหลือจนจบด้วย `run ws/<ชื่อ>` (ทำต่อจากขั้นที่ค้าง ไม่เริ่มใหม่) · หยุดหลังขั้นใดขั้นหนึ่งด้วย `run ws/<ชื่อ> --stop-after <adapt|base|turn|rollout>` · ตารางสรุป: `status ws/<ชื่อ>` · ความแกว่ง: `noise ws/<ชื่อ>`

   | ขั้น | ใครทำงาน | ไฟล์ที่เกิดหรือเปลี่ยน (ใต้ `ws/<ชื่อ>/`) |
   |---|---|---|
   | `adapt` | Benchmark Adaptor (1 เซสชัน) แล้วโปรแกรมล็อกด้วย hash | `setup/benchmark_plugin.py` `tasks.json` `freeze.json` `audit.md` · `reference/` · `turns/adaptor/` |
   | `base` | Solver ไม่มีสกิล ทุกชุด | `legs/base_train.json` `base_val.json` `base_test.json` |
   | `turn` | Evolver 1 ตา (เซสชันเดิมต่อเนื่อง) | `skills_v<K>/` · `turns/turn_<K>/actions.md` `stats.json` · `evo/evolver_workspace/` |
   | `rollout` | Solver ด้วย `skills_v<K>` | `legs/v<K>_val.json` · `legs/v<K>_train.json` (ไม่มีใน epoch สุดท้าย) |
   | `test` | Solver ด้วยชุดสกิลของ epoch สุดท้าย กับ Test Set | `legs/v<E>_test.json` |

   ตารางนี้ระบุเฉพาะไฟล์หลัก · ไฟล์อื่นที่เกิดด้วย: `inputs/` `adapt/` (หลัง init และ adapt) · `legs/runs/<leg>/<rollout>/` · `turns/*/message.md` · `evo/traces` `scores` `solver_workspaces` `skills` `staging`
5. วัดชุดสกิลใดก็ได้: `eval ws/<ชื่อ> --label <ป้าย> --skills <v1|v2|v3 | none | โฟลเดอร์ skills> --split <train|val|test|all> [--model haiku]`
6. เก็บผลลงเครื่องทุกครั้งหลังรัน: `bash tools/pull.sh` (ดึง **ทุกการรัน** ที่อยู่ใน container ไม่ใช่เฉพาะการรันล่าสุด · บนเครื่องจะมี `evo/` เฉพาะ `evo/evolver_workspace/` และ `evo/scores/`) แล้วบันทึกผลของ `status ws/<ชื่อ>` ลง `results/status-<ชื่อ>.txt` และผลของ `noise ws/<ชื่อ>` ลง `results/noise-<ชื่อ>.txt` ด้วย `docker exec … > results/<ไฟล์>`
7. คำสั่ง `run` `base` `turn` `rollout` `test` `eval` ใช้เวลาหลายนาที ให้รันแบบเบื้องหลังแล้วรอจนจบ ไม่ต้องรันซ้ำ (รันซ้ำได้: rollout ที่เสร็จแล้วจะไม่ถูกรันใหม่) · `adapt` ใช้ราว 20 วินาที · `status` `noise` `audit` ไม่ใช้โทเคน

ตรวจบัญชีที่ล็อกอินแล้ว: `docker exec multi-account bash -lc 'for a in yolo1 yolo2 yolo3 yolo4 yolo5; do $a auth status 2>/dev/null | grep -q "loggedIn.: *true" && echo "$a ok" || echo "$a ยังไม่ล็อกอิน"; done'`
ตรวจ Grader: `docker exec multi-account bash -lc 'cd /workspace/evlab && python3 bench/check_grader.py'` (รันได้ แต่ไม่ต้องเปิดอ่านไฟล์)
ไฟล์ที่เปิดอ่านได้หลังแต่ละขั้น (ใน container ใต้ `ws/<ชื่อ>/` หรือบนเครื่องใต้ `runs/<ชื่อ>/` หลัง pull):
`RUN.json` · `state.json` · `setup/benchmark_plugin.py` · `setup/freeze.json` · `setup/audit.md` · `reference/` · `skills_v*/` · `turns/*/message.md` `actions.md` `stats.json` · `evo/evolver_workspace/` · `evo/scores/` · `legs/*.json`

บน Windows (Git Bash) ตั้ง `export MSYS_NO_PATHCONV=1` ก่อน `docker exec` ทุกครั้ง

## ข้อห้าม

- ห้ามแก้ไฟล์ใน `setup/` `reference/` `skills_v*/` `evo/` ด้วยมือ · ทั้งหมดเปลี่ยนได้โดย `evoskill.py` และ Agent ของมันเท่านั้น (นี่คือสิ่งที่บทนี้ต้องการวัด)
- ห้ามเปิด `bench/benchmark_grader.py` `bench/check_grader.py` `bench/data/baankafe/answers/` และโจทย์ ผลรายข้อ หรือโค้ดของ Validation Set (โจทย์ที่ขึ้นต้นด้วย `v`) · คะแนนที่คำสั่งพิมพ์ออกมาเองดูได้ · Test Set (ขึ้นต้นด้วย `x`) เปิดผลรายข้อได้หลังขั้น `test` จบแล้วเท่านั้น
- ไฟล์ที่ระบุไว้ข้างบนว่าเปิดอ่านได้ เปิดได้ทั้งหมด แม้จะมีชื่อโจทย์ของ Validation และ Test (เช่น `setup/benchmark_plugin.py` `setup/freeze.json`) หรือมีบางส่วนของสิ่งที่ Benchmark Adaptor อ่าน (`turns/adaptor/actions.md`) · สิ่งที่ Benchmark Adaptor ถูกสั่งดูได้จาก `turns/adaptor/message.md`
- ห้ามแก้ตัวตรวจ ข้อมูล คำสั่งของผู้ใช้ใน `bench/` หรือ prompt ใน `evoskill/prompts/` ระหว่าง LAB · ห้ามวัดซ้ำเพื่อให้ได้คะแนนที่ต้องการ
- ห้ามติดตั้งหรือแก้สกิล global ใน `/root/ai-accounts` · ห้ามล็อกอินแทนผู้ใช้ · ห้ามรันคำสั่ง git
- ตัวเลขในคำตอบต้องมาจากผลของคำสั่ง หรือไฟล์ของการรันเท่านั้น · ตอบสั้น เป็นตาราง
