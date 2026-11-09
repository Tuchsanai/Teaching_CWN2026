# TEST-REPORT: สกิล yolo · cyolo · agent-team

ทดสอบเมื่อ 2026-11-09 (21:54–22:23 น. รวมการสร้างสกิล) · container `multi-account` · Claude Code 2.1.319 · codex-cli 0.167.0 · Python 3.12.3
งานทดสอบใช้ `haiku/low` และ Codex `low` ทั้งหมด (ตามคำสั่งผู้ใช้) · ไม่ได้ลบ หยุด หรือสร้าง container/volume · ไม่อ่านไฟล์ credential · ไม่ล็อกอินแทน

## บัญชีที่ตรวจด้วยการเรียกจริง

| บัญชี | สถานะ |
|---|---|
| yolo1, yolo2, cyolo1, cyolo2 | พร้อม |
| yolo3 | ล็อกอินแล้วแต่หมดอายุ (`OAuth session expired`) |
| yolo4, yolo5, cyolo3, cyolo4, cyolo5 | ไม่ได้ล็อกอิน |

## ผลทดสอบ

| รายการ | ผล | หลักฐาน | เวลา |
|---|---|---|---|
| คัดลอกแล้วทุกบัญชีเห็นสกิลทั้ง 3 | PASS | เปิดทุกบัญชี 1 ครั้ง · `skills/{yolo,cyolo,agent-team}/SKILL.md` มีครบ 10/10 บัญชี | <10 s |
| ตรวจความพร้อม แยก 3 สถานะ | PASS | ตารางด้านบน (`team.py check`, exit 0) | 8 s |
| งานเดียว Claude + Codex + ledger ครบฟิลด์ | PASS | ตอบ `PONG` ทั้งสองฝั่ง · ฟิลด์ขาด = ไม่มี | 8.1 s |
| relay ข้าม CLI | PASS | `42 → 142 → 426` ตรวจแต่ละทอดด้วย Python | 20.5 s |
| fan-out 3 บัญชี + fan-in | PASS (รอบ 2) | บัญชี yolo1, yolo2, cyolo1 · รวมได้ `red green blue` · รอบแรก FAIL เพราะตัวทดสอบบังคับให้มี `-` ตรงตัว | 20.2 s |
| graph ส่งข้อมูลยาว `{{file:node}}` | PASS | ไฟล์ 300 บรรทัด ผู้รับนับเองด้วยเชลล์ได้ 299 (`wc -l` ไม่นับบรรทัดสุดท้ายที่ไม่มี newline) | 23.4 s |
| review loop จบด้วย APPROVED | PASS | APPROVED ในรอบ 1 จาก `max_rounds` 3 | 20.6 s |
| board งานที่สองใช้ข้อค้นพบงานแรก | PASS | งานสองตอบ `ZX9` · `board.md` มีผู้เขียนและเวลา | 19.2 s |
| สถิติตรงกับ ledger | PASS | ผลรวมทุกประเภท tokens และจำนวนครั้งตรงกัน 9 แถว | 11.7 s |
| debate + best-of-N | PASS | `144` พร้อมเหตุผลผู้ตัดสิน · best-of เลือกผู้ชนะพร้อมเหตุผล | 21.5 s |
| router + failover (`MA_SIMULATE_LIMIT`) | PASS | ภาพ→cyolo ตรวจโค้ด→cyolo เอกสาร→yolo · ย้ายงาน `b` yolo1→yolo2 | 15.4 s |
| human gate | PASS | ก่อนอนุมัติ 0 แถวของงาน · หลังอนุมัติ rc=0 | 16.3 s |
| บริหารโทเค็นลูกทีม | PASS | ย้ายงาน yolo2→yolo1 · `status` แสดง "หยุดรับงาน" | 17.4 s |
| สลับหัวหน้าเชิงรุก | PASS | yolo1→yolo2 (proactive) · ไฟล์รวมมีครบ | 33.0 s |
| สลับหัวหน้าเชิงรับ | PASS | yolo2→yolo1 (reactive) · งานลูกทีมไม่หาย | 31.5 s |
| สาธิตคำสั่งเดียว (งานตัวอย่าง) | PASS | reactive + proactive + ย้ายงาน `t3` · สูตรคูณ 2–5 ตรวจครบ 48 บรรทัด · ครบ 4 ตาราง | 38.3 s |
| สาธิตคำสั่งเดียว (`--goal` ใหม่) | PASS | เกิดครบ 3 เหตุการณ์ · กำลังสอง 11–14 ถูกทุกค่า รวมไฟล์เดียว | 35.3 s |
| เรียกจาก host ตาม `SKILL.md` ทุกบรรทัด (Git Bash) | PASS | อ่านสกิล 3 ไฟล์, check 3 สกิล, ask 2 ฝั่ง, status, `docker cp` + `run` กราฟภาษาไทย, `lead --demo` | 2 นาที |
| `run` จบด้วยตาราง+โควตา และ `--resume` | PASS (รอบ 2) | รอบแรก rc=1 เก็บคำตอบ `hello` · resume rc=0 · แถวของงานที่สำเร็จ 1→1 · รอบแรกของการทดสอบ FAIL เพราะ `expect:int` ทำให้ haiku ตอบ `1` งานไม่ล้มตามที่ตั้งใจ จึงเปลี่ยนเป็น `contains:NOPE` | 30.9 s |
| สร้างภาพผ่าน cyolo | PASS | PNG signature ถูกต้อง · 999,650 B | 29.3 s |
| ทดสอบแบบผู้ใช้จริง 3 โจทย์ | PASS (รอบ 2) | ดูหัวข้อถัดไป | ~4 นาที |

SKIP: ไม่มี (ทุกข้อทำได้ด้วยบัญชีที่พร้อม 4 บัญชี)

## ทดสอบแบบผู้ใช้จริง

agent ใหม่บน `yolo2` อ่านเฉพาะ `agent-team/SKILL.md` (`--output-format stream-json`) รุ่น **haiku/low** ตามคำสั่งประหยัดของผู้ใช้ (สเปกยกตัวอย่าง sonnet) ทำงานพร้อมกัน 3 โจทย์

| โจทย์ | รอบ | คำสั่ง | ล้ม | ล้มเพราะสกิล | เวลา | ผล |
|---|---|---|---|---|---|---|
| ก. ขนาน → ตรวจ → แก้+ทดสอบ แล้วตาราง+โควตา | 1 | 7 | 1 | 1 | 78 s | ตารางครบ · การทดสอบ palindrome ไม่ผ่านเพราะ agent ไม่ได้ระบุเรื่องเครื่องหมายวรรคตอนในโจทย์ของงาน |
| | 2 | 6 | 1 | 0 | 90 s | สำเร็จ · รันทดสอบซ้ำเองผ่าน |
| ข. สาธิตสลับหัวหน้า + ย้ายงาน `--goal` ใหม่ | 1 | 6 | 1 | 1 | 59 s | สำเร็จ |
| | 2 | 4 | 0 | 0 | 59 s | สำเร็จ · reactive + proactive + ย้าย `t3` · ไฟล์รวมถูก |
| ค. fan-out + debate + สร้างภาพ ในกราฟเดียว | 1 | 6 | 1 | 0 | 65 s | สำเร็จ |
| | 2 | 5 | 1 | 0 | 69 s | สำเร็จ · 391 ถูก · agent เปิดดูภาพแล้วเป็นวงกลมสีน้ำเงิน |

สิ่งที่ปรับ: agent ใน container ลองใช้ `docker exec` จากตัวอย่างฝั่ง host (โจทย์ ก, ข รอบ 1) จึงเพิ่มข้อความใน `SKILL.md` ทั้ง 3 ไฟล์ว่า "ใน container รัน `python3` ตรง ๆ ไม่มีคำสั่ง docker"

คำสั่งที่ล้มในรอบ 2 ไม่ใช่คำสั่งของสกิล: โจทย์ ค เรียก `file` ซึ่งไม่มีใน container · โจทย์ ก เป็นคำสั่งเชลล์ต่อกันหลายขั้นที่ agent เขียนเองเพื่อตรวจไฟล์ผล · ไม่มี agent ตัวใดเปิดโค้ดของสกิล (ตัวตรวจจับอัตโนมัติขึ้นเตือน 2 ครั้ง แต่ดูคำสั่งแล้วเป็น `team.py status` และ heredoc เขียนกราฟ ไม่ใช่การอ่านโค้ด)

## ข้อจำกัดที่ควรทราบ

- คำสั่ง host ทดสอบจาก Git Bash ตามที่สเปกกำหนด ส่วน PowerShell ทดสอบเฉพาะ `docker cp`, การอ่านข้อความไทย และการ pipe (ซึ่งทำภาษาไทยเพี้ยน)
- ไม่พบบัญชี Codex ที่ "ล็อกอินแล้วแต่หมดอายุ" จริง จึงยังไม่เห็นกรณีนี้ฝั่ง Codex
- ไม่ได้ทดสอบ `ultra` ผ่านสคริปต์ และ `--refresh` ของโควตา Codex
- โควตา Codex มาจาก rollout เก่าเมื่อใช้ ephemeral ตารางจึงแสดงเวลาของข้อมูลกำกับ

## ความต่างจาก `prompt_skill_hints.md`

| เรื่อง | ใน hints | ที่วัดได้ |
|---|---|---|
| `yolo3` ที่หมดอายุ | `auth status` = `loggedIn: true` | บัญชีนี้ `loggedIn: false` แต่เรียกจริงได้ `OAuth session expired` → สกิลจัดประเภทจากการเรียกจริง |
| `/usage` บรรทัด session | บางบัญชีไม่มี | ยืนยัน: yolo1 ไม่มี `Current session` |
| `ultra` | ห้ามส่งเป็น `reasoning.effort` | ผ่าน CLI ด้วย `-c model_reasoning_effort=ultra` ได้ (รุ่นที่รองรับ, ทดลองตรงด้วย `reply OK` 1 ครั้ง) |
| ส่งกราฟทาง stdin จาก host | `< ไฟล์` | ใช้ไม่ได้ใน PowerShell 5.1 → `SKILL.md` ใช้ `docker cp` + `run <ไฟล์>` เป็นหลัก ส่วน `run -` ใช้ได้ใน Git Bash |

## ไฟล์ที่สร้าง

`skills/` มี 3 โฟลเดอร์สกิลเท่านั้น (ไฟล์ด้านล่าง) · ขนาด `agent-team/SKILL.md` 10.3 KB

- `yolo/`: `SKILL.md`, `scripts/yolo.py`, `scripts/ma_ledger.py`
- `cyolo/`: `SKILL.md`, `scripts/cyolo.py`, `scripts/ma_ledger.py`
- `agent-team/`: `SKILL.md`, `scripts/team.py`, `references/reference.md`
- `TEST-REPORT.md` (นอก skills)

ไฟล์ผลทดสอบที่ยังอยู่ใน `/workspace/.agent-team/` (run `t-*` และ run วันนี้, `t-image.png`, `ut_c.png`) และ `/tmp/ut_*` `/tmp/g*.json` ใน container ลบได้ตามสะดวก
