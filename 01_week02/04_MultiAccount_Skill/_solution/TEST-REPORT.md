# TEST-REPORT — สกิล yolo · cyolo · agent-team

> รายงานจริงจากขั้นที่ 1 (สร้างจากศูนย์ด้วย `prompt_skill_spec.md` + `prompt_skill_hints.md` ไม่มี `reference/`) ตัดรายชื่อบัญชีที่ล็อกอินบนเครื่องผู้สอนออก ผลเทียบกับสกิลชุดเดิมอยู่ใน [BENCHMARK.md](BENCHMARK.md)

- วันที่ 2026-11-08 · 11:20–12:03 (≈ 43 นาที รวมสร้างและทดสอบ)
- container `multi-account` (Claude Code 2.1.319 · codex-cli 0.167.0 · Python 3.12.3)
- ติดตั้ง: `docker cp` โฟลเดอร์ `skills/yolo`, `skills/cyolo`, `skills/agent-team` ลง `/root/ai-accounts/.Claude/shared/skills/` และ `/root/ai-accounts/.Codex/shared/skills/` (สำเนาทั้งสองฝั่งตรงกัน `diff -r` = same) ไม่ได้สร้าง/หยุด/ลบ container หรือ volume ไม่ได้อ่าน credential ไม่ได้ล็อกอินแทน
- บัญชีที่ตรวจด้วยการเรียกจริง: แยกได้ครบ 3 สถานะ (พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน) · ตัดรายชื่อบัญชีที่ล็อกอินบนเครื่องผู้สอนออก
- งานทดสอบทั้งหมดใช้ `haiku/low` (Claude) และ `gpt-6.1-sol/low` (Codex) · ตัวทดสอบแบบผู้ใช้จริงใช้ `yolo2 sonnet/low` ตามสเปก
- ledger ช่วงทดสอบ: 197 การเรียกผ่านสกิล (haiku 118 · gpt-6.1-sol 79) · input 7.44 M (ส่วนใหญ่เป็น cache) · output 47.8 k · $0.29 ราคาตามรายการ · โควตาหลังทดสอบ: yolo1 week 23% · yolo2 session 1% / week 3% · cyolo1/2 primary 2% (ข้อมูล ณ 10:12 เพราะงานทดสอบเป็น ephemeral)

## ผลทดสอบตามหัวข้อ "ทดสอบใน container" ของสเปก

| รายการ | ผล | หลักฐาน | เวลา |
|---|---|---|---|
| คัดลอกแล้วเปิดแต่ละบัญชีหนึ่งครั้ง ทุกบัญชีเห็นสกิลทั้ง 3 | PASS | เปิด `yoloN/cyoloN --version` ทั้ง 10 บัญชี (wrapper รัน `link_shared_skills`) แล้ว `skills/<สกิล>/SKILL.md` อ่านได้ 30/30 · cyolo3 มี symlink `agent-team`, `cyolo`, `yolo` → `../../shared/skills/…` | 2 s |
| ตรวจความพร้อมด้วยการเรียกจริง แยก 3 สถานะ | PASS | `team.py check`: แยก พร้อม / "ล็อกอินแล้วแต่หมดอายุ" (`OAuth session expired`) / ไม่ได้ล็อกอิน · exit 0 | 6 s |
| งานเดียว Claude + Codex ผลถูก และ ledger ครบฟิลด์ | PASS | `yolo.py ask yolo1 "7*6…"` → 42 · `cyolo.py ask cyolo1 …` → 42 · แถว ledger มีครบ 19 ฟิลด์ของสเปก + `event` ไม่มีข้อความ prompt | 8 s |
| relay ข้าม CLI 3 ทอด | PASS | run `t-relay`: yolo1 → **42**, cyolo1 → **142**, yolo2 → **426** (ตรวจอิสระ 7×6=42, 42+100=142, 142×3=426) · regression `t-relay2` ได้เท่าเดิม | 12 s |
| fan-out 3 บัญชี + fan-in | PASS | run `t-multi`: yolo1 144, yolo2 225, cyolo2 441 → cyolo1 รวม **810** (= 144+225+441) | 27 s (ทั้งกราฟ 18 งาน) |
| graph ส่งข้อมูลยาวผ่าน `{{file:node}}` | PASS | `longdata` (seq 1..400, 1,492 ตัวอักษร) → `sumfile` อ่านไฟล์เองได้ **80200** (= 400·401/2) | ใน t-multi |
| review loop จบด้วย APPROVED ภายใน max_rounds | PASS | `rv`: yolo2 เขียน, cyolo2 ตรวจ → `APPROVED` รอบที่ 1 จาก max 3 (`out/rv.review.md`) | ใน t-multi |
| board: งานที่สองใช้ข้อเท็จจริงของงานแรก | PASS | `fact` (yolo1) เขียน `BOARD: รหัสลับโปรเจกต์ = ORCHID-7731` → `board.md` · `usefact` (cyolo1) ตอบ **ORCHID-7731** (expect regex ผ่าน) | ใน t-multi |
| สรุปสถิติแล้วผลรวมตรงกับ ledger | PASS | `team.py stats --run t-multi`: 19 ครั้ง · in 532,767 · out 3,607 · $0.0322 · 102.6 s = ผลรวมคำนวณอิสระจาก ledger ตรงทุกค่า | 1 s |
| debate (Claude vs Codex + ผู้ตัดสิน) และ best-of-N | PASS | debate `deb`: yolo1 & cyolo2 ตอบ 15 → ผู้ตัดสิน `{"final":"15 ตัว","winner":"tie","reason":…}` (จำนวนเฉพาะ < 50 = 15 ถูก) · best_of `bo` 3 บัญชี → `{"best":"A","scores":{"A":9,"B":7,"C":6},"reason":…}` + `out/bo.best.md` | ใน t-multi |
| router เลือกฝั่งถูก + failover เมื่อจำลองบัญชีล้ม | PASS | router: `kind:image`→cyolo1, `code_review`→cyolo2, `doc`→yolo2 · `MA_SIMULATE_LIMIT=yolo1` (t-failover2): y2, y4 ย้าย yolo1→yolo2 (`worker_switch` ใน state/board/ledger) งาน `pin` ที่ระบุ yolo1 เอง **ไม่ย้าย** หยุดและรายงาน, exit 1 | 15 s |
| human gate หยุดรอจนมีไฟล์อนุมัติแล้วรันต่อ | PASS | t-gate: g2 "รออนุมัติ" run จบ exit 0 พร้อมคำสั่ง → `approve --run t-gate g2` → `run --resume` g2 = 10 · g1 ไม่มีแถว ledger ใหม่ (1 แถว) | 15 s |
| บริหารโทเค็นลูกทีม (งบต่ำ → งานถัดไปย้าย, status "หยุดรับงาน") | PASS | t-budget `--worker-token-budget yolo1=1 --per-account 1`: w2 ของ yolo1 ทำจนจบ → `yolo1 หยุดรับงานใหม่` → w4 ย้าย yolo1→yolo2 · `status`: yolo1 "หยุดรับงาน (เกินงบโทเค็นลูกทีม 58019 > 1)" | 21 s |
| สลับหัวหน้าเชิงรุก | PASS | t-demo1: yolo1 งบ 1 token → คำสั่งแรกตอบ "งบหัวหน้าหมด" → checkpoint (มี) → cyolo1 (ข้ามฝั่ง) ทำต่อจาก handoff.md จนจบ | ใน demo |
| สลับหัวหน้าเชิงรับ | PASS | t-demo1: yolo2 ถูก kill หลัง dispatch 8 งาน → yolo1 รับช่วงจาก state.json · งาน t1–t8 ที่สั่งไปแล้ว **สำเร็จครบ 8/8** ไม่มีงานหาย/แจกซ้ำ | ใน demo |
| สาธิตครบในคำสั่งเดียว (งานตัวอย่าง + `--goal` ใหม่) | PASS | `lead --demo --lead-model haiku` (t-demo1): เชิงรับ + เชิงรุก + ย้ายงาน t7 cyolo2→cyolo1 · ตรวจผลอิสระสูตรคูณ **96/96** · 59 s · `--goal` "คำอธิบาย Python/Go/Rust/JavaScript" (t-demo2): ครบ 3 เหตุการณ์ ไฟล์ Markdown 4 หัวข้อ · 69 s | 59 s / 69 s |
| เรียกจาก host ผ่าน docker exec ทุกบรรทัดใน SKILL.md (Git Bash) | PASS | Git Bash (ไม่ตั้ง `MSYS_NO_PATHCONV`) รันทุกบรรทัดของ 3 SKILL.md: cat ×3, check ×3, ask ×2, quota ×2, image, docker cp + run, status, stats, lead --demo (96/96, 61 s), ls out · ทุกคำสั่ง exit 0 · stdin `run - < graph.json` ผ่าน · PowerShell: ask (ภาษาไทย), docker cp + run, status ผ่าน | ~3 นาที |
| `run` จบด้วยตาราง + โควตา และ `--resume` รันเฉพาะงานที่ล้ม | PASS | t-resume2: r2 `expect contains:…` ไม่ผ่าน (คำตอบเก็บใน out/r2.md) r3 ถูกบล็อก → `--resume --set r2.expect=text` ตรวจคำตอบเดิมผ่านโดยไม่เรียกซ้ำ รันเฉพาะ r3 · ledger นับต่องาน r1:1 r2:1 r3:1 (งานที่สำเร็จไม่มีแถวใหม่) | 16 s |
| ทดสอบแบบผู้ใช้จริง (ก)(ข)(ค) | PASS (หลังปรับ) | ดูหัวข้อถัดไป · รอบสุดท้าย 0 คำสั่งล้ม ไม่เปิดโค้ดสกิล | 55–88 s ต่อโจทย์ |
| สร้างภาพเล็ก 1 ภาพผ่าน cyolo ตรวจว่าเป็น PNG จริง | PASS | `cyolo.py image cyolo1 … /workspace/pic.png` → 8 ไบต์แรก `89 50 4e 47 0d 0a 1a 0a` (1.05 MB) · ในกราฟ `t-failover/out/pic.png` ก็เป็น PNG | 27 s |
| ข้อที่ต้องใช้บัญชีที่ไม่พร้อม | SKIP (บางส่วน) | ไม่มีบัญชีที่ `auth status` = loggedIn true แต่ token หมดอายุ จึงทดสอบกรณีนี้ตรง ๆ ไม่ได้ (yolo3 หมดอายุแต่ auth status = false — สคริปต์จัดเป็น "ล็อกอินแล้วแต่หมดอายุ" จากข้อความ `OAuth session expired`) · ทุกข้ออื่นใช้เฉพาะบัญชีที่พร้อม | – |

## ทดสอบแบบผู้ใช้จริง (yolo2 · sonnet/low · stream-json · อ่านเฉพาะ agent-team/SKILL.md)

| รอบ | โจทย์ | คำสั่ง (ทั้งหมด / Bash) | ล้ม | เวลา | ผล | สาเหตุที่มาจากสกิล |
|---|---|---|---|---|---|---|
| 1 | (ก) ขนาน 2 บัญชี → ตรวจ → แก้ + unittest → ตาราง + โควตา | 4 / 2 | 1 | 79 s | สำเร็จหลัง resume | agent ระบุ reviewer = yolo3 (ไม่พร้อม) → run ทำ 2 งานแรกแล้วล้มกลางทาง |
| 1 | (ข) สาธิตสลับหัวหน้า + ย้ายงาน กับเป้าหมายใหม่ (คำศัพท์ 4 หมวด) | 3 / 2 | 0 | 69 s | ครบ 3 เหตุการณ์ | – |
| 1 | (ค) fan-out + debate + ภาพ ในกราฟเดียว | 3 / 2 | 0 | 72 s | สำเร็จหลัง resume | worker ตอบเป็นบรรทัด `BOARD:` อย่างเดียว → สคริปต์ตัดทิ้งแล้วนับว่า "คำตอบว่าง" |
| 2 | (ก) ซ้ำ | 4 / 3 | 0 | 74 s | 4/4 PASS (unittest 8 tests) | – |
| 2 | (ข) ซ้ำ | 3 / 2 | 0 | 88 s | สลับครบ แต่ t1–t4 ล้ม | หัวหน้า haiku ใส่ `"difficulty": "easy"` → `int()` error ในสคริปต์ |
| 2 | (ค) ซ้ำ | 4 / 3 | 0 | 55 s | 8/8 · debate 735 (ถูก) · ภาพ PNG | – |
| 3 | (ข) ซ้ำหลังแก้ | 3 / 2 | 0 | 62 s | ครบ 3 เหตุการณ์ 4/4 งานสำเร็จ | – |

ไม่มี agent ตัวใดเปิด `scripts/` หรือ `references/` (Read มีแค่ SKILL.md) · ทุกโจทย์จบใน 2–3 คำสั่ง Bash

สิ่งที่ปรับตามผลทดสอบ:
1. `run` ตรวจบัญชีที่ผู้ใช้ระบุเอง (`account`/`reviewer`) ก่อนเริ่ม ถ้าไม่พร้อมจะไม่เริ่ม (ยังไม่เสียโทเค็น) และบอกบัญชีที่พร้อม · SKILL.md แนะนำ `yolo`/`cyolo`/`any` เป็นหลัก
2. คำตอบที่มีแต่บรรทัด `BOARD:` ใช้เป็นคำตอบด้วย (ไม่ทิ้ง) และเปลี่ยนคำสั่งใน prompt เป็น "เพิ่มต่อท้ายคำตอบ ไม่ใช่แทนคำตอบ"
3. แปลงค่าที่ชนิดผิด (`difficulty: "easy"`/`"2"`, `timeout`, `depends_on` เป็น string) ให้ใช้ได้ ทั้งใน `run` และ `dispatch` และ prompt ของหัวหน้าระบุว่า difficulty เป็นตัวเลข
4. ตารางสรุปแทน `|` และขึ้นบรรทัดใหม่ในช่องค่า (ผู้ทดสอบรายงานว่าตารางถูกตัด)
5. ระหว่างพัฒนา: แยกฟิลด์บัญชีที่ระบุ (`account`) ออกจากบัญชีที่ได้รับ (`assigned`) — เดิม failover ย้ายงานกลับไปบัญชีเดิม · `--demo` ให้ลูกทีมงบต่ำรับ 2 งานแรก จึงเกิดการย้ายงานแน่นอนแม้เป้าหมายมีงานน้อย · `MA_SIMULATE_LIMIT` ไม่ปลอมโควตา (บัญชีดูปกติจนเรียกจริงแล้วล้ม จึงทดสอบ failover เชิงรับได้)

## ข้อเท็จจริงที่ต่างจาก hints / หมายเหตุ

- yolo3: `auth status` = `loggedIn: false` แต่เรียกจริงได้ `OAuth session expired and could not be refreshed` (hints บอกว่ากรณีหมดอายุ auth status = true) → สคริปต์จัดเป็น "ล็อกอินแล้วแต่หมดอายุ" เมื่อข้อความมีคำว่า expired
- yolo1 `/usage` ไม่มีบรรทัด `Current session` (ตรงกับ hints) → ใช้ `Current week (all models)` ตัดสินแทน
- `-c model_reasoning_effort=ultra` กับ `gpt-6.1-sol` CLI รับได้ (exit 0) → ส่ง ultra เฉพาะรุ่นที่ `models_cache.json` ประกาศว่ารองรับ ไม่งั้นลดเป็น max พร้อม `effort_note`
- ข้อมูลโควตา Codex ค้างที่ 10:12 เพราะทุกการเรียกเป็น `--ephemeral` — รายงานพร้อมเวลาของข้อมูลเสมอ และมี `cyolo.py quota --refresh`
- `agent-team/SKILL.md` = 13.0 KB (≈ 7.9 k ตัวอักษร; ภาษาไทยใช้ 3 ไบต์/ตัวอักษร) จากร่างแรก 16.9 KB รายละเอียดย้ายไป `references/`
- ใน PowerShell `| Select-Object -First N` ตัด pipe ทำให้ docker exec คืน 255 — เป็นผลจากคำสั่งตัดผลของผู้ทดสอบ ไม่ใช่สกิล

## ไฟล์ที่สร้าง

| ที่ | ไฟล์ |
|---|---|
| `./skills/yolo/` | `SKILL.md` · `scripts/yolo.py` · `references/claude-cli.md` |
| `./skills/cyolo/` | `SKILL.md` · `scripts/cyolo.py` · `references/codex-cli.md` |
| `./skills/agent-team/` | `SKILL.md` · `scripts/team.py` · `references/graph.md` · `references/leader.md` · `references/files.md` |
| `./tests/` | กราฟที่ใช้ทดสอบ (`relay.json`, `multi.json`, `failover*.json`, `gate.json`, `budget.json`, `resume.json`, `pinbad.json`, `boardonly.json`, `graph.json`, `host-demo.txt`) — นอกโฟลเดอร์ skills |
| `./TEST-REPORT.md` | ไฟล์นี้ |
| ใน container | สำเนาสกิลใน shared ทั้งสองฝั่ง · run ทดสอบใน `/workspace/.agent-team/` (t-relay, t-multi, t-failover, t-gate, t-budget, t-resume2, t-demo1, t-demo2 …) · `/workspace/pic.png`, `/workspace/ut-a/` (ผลของผู้ทดสอบ) · `/tmp/tg/`, `/tmp/ut-*` |
