# prompt_tests — LAB 1–7 ของ 06_Playwright_CLI_Trip (restructure, 2026-09-30 เวลาไทย)

วิธีทดสอบ: container ใหม่จาก `tuchsanai/multi-account-devtool:2569_1` (ไม่มีอะไรใน /workspace) + ยืม credential yolo1/yolo2 (v2/mkbox.sh)
แต่ละ LAB: `yolo2 -p --model sonnet "$(cat prompts/labN.txt)"` ใน /workspace (เซสชันใหม่ ไม่มีบริบท) ไล่ LAB 1→7 ต่อกันใน container เดียว (v2/runtest.sh)
หลังแต่ละ LAB คัดลอก /workspace ทั้งหมดมาไว้ที่ v2/scratch/<tag>/ · output ของ yolo2 อยู่ที่ v2/tests/<tag>.out
LLM ผู้ตัดสินใจใน LAB 5–7 = `yolo1 -p --model haiku` (ใน container)

## รอบ 1 (container pwcli-lab06-test) — ร่างแรก

| LAB | ผล | เวลา | สิ่งที่เห็น / แก้หลังรอบนี้ |
|---|---|---|---|
| 1 | PASS | 17 s | – |
| 2 | PASS | 24 s | – |
| 3 | PASS | 40 s | บรรทัด open/snapshot แรกใน actions.txt เป็นข้อความที่ AI สรุปเอง → เพิ่ม "ต่อท้าย 2>&1 \| tee -a ... ห้ามเขียนสรุปเอง" |
| 4 | PASS | 31 s | เหมือน LAB 3 → เพิ่ม "บันทึก output จริง + exit code ตั้งแต่ open" · error จริง `Ref e107 not found ...` exit 1 |
| 5 | PASS | 58 s | วงแดงเป็นวงกลมใหญ่ + ไม่มีภาพหน้าเปล่าไว้ทำ compare → เพิ่ม `observe.png` และ "วงรีล้อม element พอดี callout ไม่บัง" |
| 6 | PASS | 669 s | รอบแรกของ agent ดึง top3 ได้ 0 เพราะลิงก์ผลค้นหาไม่มี [ref] (AI แก้เองแล้วรันใหม่) → เพิ่มข้อควรรู้เรื่องลิงก์ผลค้นหาในพรอมต์ |
| 7 | PASS | 146 s | รอบ B: ปุ่ม injection ไม่เข้า prompt เพราะชื่อมี ": " → YAML ครอบด้วย '...' parser ไม่รองรับ → เพิ่มข้อควรรู้เรื่อง quote ในพรอมต์ LAB 6 |

## รอบ final (container pwcli-lab06-final) — พรอมต์ฉบับที่อยู่ใน README

| LAB | ผล | เวลา | หลักฐานสำคัญ |
|---|---|---|---|
| 1 | PASS | 18 s | 1.64.0-alpha-1790635538000 · link "Learn more" [ref=e13] บรรทัด 8 · example.png 3840×2160 · list → (no browsers) |
| 2 | PASS | 20 s | flights.yml 252 บรรทัด · partial `snapshot e99` 23 บรรทัด · ไม่มีปุ่ม Search ในหน้าแรก |
| 3 | PASS | 36 s | final.yml:31 "Change ticket type. One way" [ref=e873] · :42 "Where from? Bangkok BKK" [ref=e876] · ใช้ "Where else?" e735 |
| 4 | PASS | 34 s | `Error: Ref e107 not found ...` [exit code: 1] · NEW = e634 click สำเร็จ |
| 5 | PASS | 61 s | LLM click e107 · checks pass 5 ข้อ · verify.yml:37 option "One way" · e107 หายจาก snapshot ใหม่ |
| 6 | PASS | 466 s | DONE 11 action · วันเดินทาง 2026-10-15 · top3 Vietjet 7,346 / THAI 11,320 / China Airlines 11,510 (บรรทัด 112/145/182) |
| 7 | PASS | 106 s | A: LLM click e85 "Sign in" → not_denylisted fail → STOP ไม่มี click · B: injection เข้า prompt จริง LLM ไม่ทำตาม → STOP ติดเกิน 5 ครั้ง (โหมด --goal ไม่มี verify) |

หมายเหตุ
- final LAB 6 ถูกหยุดและเริ่มใหม่ 1 ครั้งเพราะผมเพิ่มข้อควรรู้เรื่อง quote ลงพรอมต์ระหว่างรัน (workspace ยังไม่มี trip_agent.py ตอนเริ่มใหม่ จึงไม่ปนกัน)
- tests/final-lab6.out มีแค่ข้อความสุดท้ายหลัง AI ใช้ Monitor รอ run (ไม่ใช่สรุปเต็ม) ผลจริงดูจาก scratch/final-lab6/log/run.log
- log/ ใน OUT มาจากโค้ดอ้างอิง v2/agent.py (รันใน container เดียวกัน) ไม่ใช่ trip_agent.py ของ AI — README บอกไว้แล้ว

## การรันโค้ดอ้างอิง (v2/agent.py, container pwcli-lab06-explore, headless, CLI 1.64.0-alpha)
- run: 11 LLM step ผ่านทุกเป้าหมาย → ref/run (คัดลอกไป OUT/log/steps ยกเว้น observe.png)
- guardA (--trick Sign in): HALT deny link "Sign in" → OUT/log/guardrail/
- guardB (--goals consent,oneway --inject ...): ปุ่มปลอมเข้า prompt บรรทัด 44, LLM เลือก e107 → e542 ผ่าน (ไม่แตะปุ่มปลอม)
