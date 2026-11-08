# TEST-REPORT — yolo · cyolo · agent-team

- วันที่ 2026-11-08 06:38–07:10 (+07) · container `multi-account` · Claude Code 2.1.319 · codex-cli 0.167.0 · Python 3.12.3
- ติดตั้งจาก `/tmp/skills` (สำเนาของ `./skills`) ด้วย `install.sh` ลง `/root/ai-accounts/.{Claude,Codex}/shared/skills`
- งานทดสอบใช้ `difficulty 1` ทั้งหมด (Claude `haiku`/`low`, Codex `gpt-6.1-sol`/`low`) รวมหัวหน้าทีม
- หลักฐานทุก run อยู่ที่ `/workspace/.agent-team/<run>/` (= `C:\t\s04\workspace\.agent-team\` บน host) · ภาพที่ `workspace/matest-out/`
- ไม่มี secret ในรายงานนี้: ไม่ได้อ่าน `.credentials.json` / `.claude.json` / `auth.json` ไม่ได้ล็อกอินแทน ไม่ได้สร้าง/หยุด/ลบ container หรือ volume

## สถานะบัญชี (ตรวจด้วยการเรียกจริง)

| บัญชี | สถานะ | หมายเหตุ |
|---|---|---|
| yolo1, yolo2 | พร้อม | `max` / `team` · haiku "ตอบ OK" 4–5 s |
| cyolo1, cyolo2 | พร้อม | Logged in using ChatGPT · 4–5 s |
| yolo3–5, cyolo3–5 | ไม่ได้ล็อกอิน | ผู้ใช้ต้องล็อกอินเอง (`yoloN auth login` / `cyoloN login`) |

## ผลทดสอบ (หัวข้อ "ทดสอบ" ของสเปก)

| # | รายการ | ผล | หลักฐาน | เวลา |
|---|---|---|---|---|
| 1 | `install.sh` 2 รอบ ผลเหมือนเดิม ทุกบัญชีเห็นทั้ง 3 สกิล | PASS | รอบ 1 เขียน 6 (Claude/Codex × 3) + สร้าง symlink รายสกิลให้ cyolo1–5 · รอบ 2 "เขียนใหม่: ไม่มี / ไม่ต้องสำรอง" · 10/10 บัญชี × 3 `SKILL.md` อ่านได้ · เนื้อหาเปลี่ยน → สำรองไป `.skill-backup-20261108-065737/` ก่อนเขียนทับ · ไม่มี `__pycache__` · ทดสอบเพิ่ม: agent yolo2 และ cyolo1 ตอบว่าเห็นสกิล yolo, cyolo, agent-team | 0.2 s |
| 2 | ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริง แยก 3 สถานะ | PASS (บางส่วน) | `team.py check --recheck`: พร้อม 4 · ไม่ได้ล็อกอิน 6 · สถานะ "ล็อกอินแล้วแต่หมดอายุ" **ไม่มีบัญชีใดอยู่ในสถานะนี้** จึงตรวจได้แค่ตัวจำแนก: ข้อความจริงจาก yolo3 (`Failed to authenticate: OAuth session expired…`, 45 ms, 0 tokens) และ 401 ของ Codex → `auth` → "หมดอายุ" เมื่อ `loggedIn=true` | 6.1 s |
| 3 | งานเดียว Claude + Codex ผลถูก ledger ครบฟิลด์ | PASS | `17*23`: yolo2 → 391 (4.0 s, $0.0028 list) · cyolo2 → 391 (4.0 s) · `--schema` yolo1 → `{"answer": 391}` · 19 ฟิลด์ตามสเปกครบทุกแถว ไม่มีข้อความ prompt ใน ledger (มีแค่ `prompt_chars`) | 4–6 s |
| 4 | relay ข้าม CLI 3 ทอด 42 → 142 → 426 | PASS | `t1-relay`: cyolo1 42 → yolo2 142 → cyolo2 426 · ตรวจอิสระ `a==7*6`, `b==a+100`, `c==b*3` จริงทั้ง 3 · `msgs/a__b.md`, `msgs/b__c.md` · ซ้ำจาก host (`t6-host`) ได้เท่าเดิม | 10.8 s |
| 5 | fan-out 3 บัญชี + fan-in | PASS | `t1-fanout`, `t7-fanout`: f1 yolo1 = 55, f2 yolo2 = 120, f3 cyolo1 = 1024 เริ่มวินาทีเดียวกัน (06:58:52) → sum cyolo2 = 1199 = 55+120+1024 | 8.4 s |
| 6 | graph ส่งข้อมูลยาวผ่าน `{{file:node}}` | PASS | `t2-graph`, `t7-graph`: data (3,892 ตัวอักษร) → total cyolo1 = 500500 และ evens yolo1 = 500 (ขนานกัน) → final = 500000 ตรงกับการคำนวณอิสระ · node `bad` ที่แทรก `{{data}}` ตรง ๆ ถูกปฏิเสธ "ยาว 3892 ตัวอักษร ใช้ {{file:data}}" (ตั้งใจให้ล้ม) | 20.6–21.4 s |
| 7 | review loop จบด้วย APPROVED ภายใน max_rounds | PASS | `t1-review`: ผู้ทำ yolo2 ผู้ตรวจ cyolo1 · รอบ 1 ถูกตีกลับ (ขาด type hints / docstring ไทย / doctest) · รอบ 2 `APPROVED` (max 3) · `out/fn.r1.md`, `fn.r2.md`, `msgs/fn.worker__fn.reviewer.md` | 27.4 s |
| 8 | board: งานที่สองใช้ข้อเท็จจริงจากงานแรก | PASS | `t1-board`, `t7-board`: scout (cyolo1) เขียน `BOARD: รหัสลับของภารกิจคือ ZEBRA-7314` → `board.md` · user (yolo2) ไม่ได้รับค่าใน prompt ตอบ `ZEBRA-7314` จากกระดาน | 8.1–9.3 s |
| 9 | สรุปสถิติแล้วผลรวมตรงกับ ledger | PASS | `team.py stats --json` เทียบกับสคริปต์รวมแยก (ไม่ import team.py): ledger รวม 79 calls และ ledger ของ `t2-graph` — total ทุกชนิดโทเค็น, cost, by_account, ผลรวม by_run ตรงทั้งหมด | <1 s |
| 10 | debate (Claude vs Codex + ผู้ตัดสิน) และ best-of-N พร้อมเหตุผล | PASS | `t2-judge` debate: yolo2 vs cyolo1 ผู้ตัดสิน yolo1 → `answer` 25, `agree: true`, เหตุผล "ตัวประกอบเฉพาะไม่เกิน 7…" (ตรวจอิสระ: จำนวนเฉพาะ < 100 = 25) · best-of: yolo1, yolo2, cyolo1 ผู้ตัดสิน cyolo2 (Codex `--output-schema`) ให้คะแนน 6 / 7 / 6.5 เลือก c2 พร้อมเหตุผล | 25.6 s |
| 11 | router เลือกฝั่งถูก + failover เมื่อจำลองบัญชีล้ม | PASS | `t2-router`: ภาพ → cyolo1 · ตรวจโค้ด → cyolo2 · สรุปเอกสาร 30 KB → yolo2 · งานทั่วไป → ฝั่งโควตาเหลือมาก · `t3-failover4` (`MA_SIMULATE_LIMIT=yolo1`): fo2 yolo1 `limit` → ย้ายไป yolo2 (`worker_switch` ใน state.json, board.md, ledger) · `pin` ที่ระบุ yolo1 เอง **ไม่ย้าย** หยุดพร้อมรายงาน (ล้มตามที่ออกแบบ) · ค่า 42/42 ตรวจอิสระถูก | 31.4 s / 4.6 s |
| 12 | human gate หยุดรอไฟล์อนุมัติแล้วรันต่อ | PASS | `t4-gate` (`--detach`): gate เป็น `waiting_approval` ที่ 6 s, รอต่อ 20 s ไม่มีแถว ledger ของ gate ขณะที่ `side` รันจบ · `team.py approve gate` → gate รันได้ 26 (= 25+1) | 32 s |
| 13 | บริหารโทเค็นลูกทีม (งบต่ำ → ย้ายงานถัดไป, status "หยุดรับงาน") | PASS | `t3-budget --worker-token-budget yolo2=1000`: w1 รันบน yolo2 จบปกติ (27,867 tokens) → `worker_pause` → w3 ย้าย yolo2 → yolo1 (`worker_switch`) · `team.py status`: yolo2 = "หยุดรับงาน (ใช้โทเค็นใน run นี้ 27867 ≥ งบ 1000)" | 10.4 s |
| 14 | สลับหัวหน้าเชิงรุก (งบหัวหน้าต่ำ) | PASS | `t5-lead-pro --lead-token-budget 1`: รอบ 1 yolo2 add a, b + dispatch + checkpoint → สลับ yolo2 → yolo1 (88,990 ≥ 1) · รอบ 2 yolo1 อ่าน handoff.md, wait, finish **142** | 19 s |
| 15 | สลับหัวหน้าเชิงรับ (หัวหน้าล้มกลางคัน) | PASS | `MA_SIMULATE_CRASH=lead_after_dispatch`: `t5-lead-re` yolo1 ถูกฆ่าหลัง dispatch → cyolo1 (หัวหน้า Codex) จบ 142 · `t5-lead-re2` → yolo2 (เลือกอัตโนมัติ ฝั่งเดียวกันก่อน) จบ 142 · งาน a, b ถูกเพิ่มครั้งเดียวและรันจบ **หลัง** หัวหน้าตาย (07:05:16, 07:05:21 > 07:05:13) | 19–23 s |
| 16 | เรียกสคริปต์จาก host ผ่าน `docker exec` | PASS | จาก Git Bash บน host: `head SKILL.md` · `yolo.py run` → "pong" (3.4 s) · `team.py run - < relay.json` → 42/142/426 · `cyolo.py image` | 3–27 s |
| 17 | สร้างภาพเล็ก 1 ภาพผ่าน cyolo ตรวจว่าเป็น PNG จริง | PASS | `robot.png` (router, cyolo1) signature `\211 P N G \r \n 032 \n` 1199×1312 · `host-cat.png` (cyolo2 จาก host) ผ่านการตรวจ signature ในสคริปต์ และเปิดดูแล้วเป็นแมวสีส้มบนพื้นขาวตามสั่ง | 27 s |
| 18 | ข้อที่ต้องใช้บัญชีที่ไม่พร้อม | SKIP | ไม่มีข้อทดสอบใดบังคับใช้ yolo3–5 / cyolo3–5 · สถานะ "ล็อกอินแล้วแต่หมดอายุ" ทดสอบกับบัญชีจริงไม่ได้ (ดูข้อ 2) | – |

สรุป: **PASS 17 · SKIP 1** (ข้อ 2 ผ่านเฉพาะส่วนที่มีบัญชีให้ทดสอบ)

## ข้อค้นพบระหว่างทดสอบ (และสิ่งที่แก้)

| เรื่อง | รายละเอียด |
|---|---|
| Codex ไม่ล็อกอิน | 0.167.0 retry 401 ราว 15 s แล้ว `turn.failed` **exit 1** (สเปกเดิมบอกอาจ exit 0) — สคริปต์ไม่ใช้ exit code ตัดสินอยู่แล้ว |
| โควตา Claude | yolo1 ไม่มีบรรทัด `Current session` มีแค่ `Current week` → รายงานเท่าที่มี ไม่เดา · โควตา Codex มาจาก rollout เวลา 06:24/06:35 (งาน ephemeral ไม่อัปเดต) รายงานพร้อมเวลาของข้อมูล |
| haiku/low จัดรูปแบบ | ตอบ "50 − 8 = 42" แทนค่าล้วน → validator `int`/`number` รับเฉพาะรูปสมการบรรทัดเดียวที่ลงท้าย `= N` (ข้อความอื่นยังปฏิเสธ) |
| haiku/low คำนวณผิด 1 ครั้ง | "12+30" ตอบ 30 เมื่อลองเปลี่ยนคำสั่งรูปแบบเป็น "จำนวนเต็มตัวเดียว ห้ามมีสมการ" → ย้อนกลับเป็นคำสั่งเดิม (ถูกทุกครั้งหลังจากนั้น) · ยืนยันกฎ "ตรวจผลด้วยการคำนวณอิสระเสมอ" |
| งบลูกทีม | การตรวจความพร้อมไม่นับเป็นงานของลูกทีม (ไม่งั้นบัญชีถูกหยุดก่อนเริ่มงาน) |
| Git Bash บน host | แปลง `/root/...` และ `/tmp/...` ใน argument เป็น path Windows → ใช้ `//root/...` หรือ PowerShell (เพิ่มในหัวข้อ "เรียกจาก host" ของทุก SKILL.md) |
| JupyterLab | สร้าง `.ipynb_checkpoints` ในโฟลเดอร์สกิลที่ติดตั้งแล้ว → install.sh ถือว่าต่างและสำรองก่อนเขียนทับ (ปลอดภัย) |

## การใช้บัญชี (ledger รวม ณ 07:08)

| บัญชี | ครั้ง | input (รวม cache) | output | $ list |
|---|---|---|---|---|
| yolo1 | 26 | 711,960 | 3,263 | 0.071 |
| yolo2 | 35 | 1,280,695 | 10,922 | 0.127 |
| cyolo1 | 26 | 662,521 | 1,314 | – |
| cyolo2 | 16 | 376,324 | 851 | – |
| **รวม** | **103** (สำเร็จ 93 · ล้ม 10 = จำลองโควตาหมด 8 + หัวหน้าถูกฆ่าโดยตั้งใจ 2) | 3,031,500 (cache read 1,899,364) | 16,350 | **0.198** |

ค่าใช้จ่ายเป็นราคาตามรายการของ Claude ไม่ใช่ยอดจ่ายจริงของ subscription · Codex ไม่มีข้อมูลค่าใช้จ่าย · โควตาหลังทดสอบ: yolo1 week 22%, yolo2 session 0% / week 2%, cyolo1–2 primary 1%

## สิ่งที่ค้างอยู่ใน container / volume

- `/tmp/skills` (ต้นทางติดตั้งตามสเปก) · `/workspace/.agent-team/` (run ทดสอบ t1–t7 + ledger, quota, readiness cache) · `/workspace/matest-out/` (ภาพทดสอบ 2 ภาพ)
- `/root/ai-accounts/.skill-backup-20261108-065737 … 070954` (8 โฟลเดอร์) = สำรองจากการติดตั้งซ้ำระหว่างพัฒนา (เวอร์ชันเก่าของ 3 สกิลนี้ + `.ipynb_checkpoints`) ลบได้ถ้าไม่ต้องการ · `.skill-backup-20261108` เดิม (yolo/cyolo ชุดเก่า) ไม่ได้แตะ
