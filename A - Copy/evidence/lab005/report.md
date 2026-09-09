# รายงานการสร้างและทดสอบ LAB 005

วันที่ทดสอบ: 2026-09-07 · สถานะ: ทดสอบแล้ว

## 1. สิ่งที่เปลี่ยนจาก README เดิม

- จัดใหม่เป็น 3 ขั้น แต่ละขั้นมี 6 ส่วนตามสเปก
- กำหนดหน้าต่าง A `cyolo1` สำหรับตรวจ และหน้าต่าง B `yolo1` สำหรับแก้
- แยกพรอมท์หลักเป็น `prompts/step-01.md` ถึง `step-03.md`
- คงกรณีคืนสินค้า B-01..B-06, FR-01..FR-05, NFR-01 และเฉลย D-01..D-04
- เพิ่มการตรวจ T-01..T-07 และแยก COUNT_CHECK จาก SEMANTIC_CHECK
- รองรับการทำขั้น 2–3 ซ้ำได้หนึ่งรอบเมื่อ REVISE และหยุดที่ NEEDS_HUMAN หลังรอบสอง

## 2. ผลรันพรอมท์จริงบน host — รอบแรก

cwd ทุกครั้งคือ `/root/workspace/sa-work/005/` ส่งข้อความจากไฟล์พรอมท์ด้วย command substitution ตามตัวอักษร ยกเว้น newline ท้ายไฟล์ที่ shell ตัดตามสเปก และกำหนด timeout 15 นาทีต่อครั้ง

| ขั้น | เวลา UTC | wrapper ที่รันจริง | รุ่น / effort | exit | ตรง Expected |
|---|---|---|---|---:|---|
| 1 | 10:35:33–10:39:15 | `cyolo1` | `gpt-5.6-sol` / medium | 0 | PASS — พบ D-01..D-04 ครบ 4/4, REVISE |
| 2 | 10:39:38–10:41:32 | `yolo2` | UNKNOWN | 0 | PASS — สร้าง v1/changes เท่านั้นและหยุด |
| 3 attempt 1 | 10:41:59–10:45:33 | `cyolo1` | `gpt-5.6-sol` / medium | 0 | REVISE PROMPT — สาระถูก แต่รูปแบบสอง check ยังไม่ชัด |
| 3 attempt 2 | 10:47:10–10:49:34 | `cyolo1` | `gpt-5.6-sol` / medium | 0 | PASS — T-01..T-07 PASS, D ทั้งสี่ CLOSED, v0 COUNT=PASS/SEMANTIC=FAIL |

CLI ที่ตรวจ: Codex CLI 0.153.4 และ Claude Code 2.1.258 บัญชี Claude ของ LAB นี้ใช้ `yolo2` ตามข้อ 9.6 แม้ README แสดง `yolo1` สำหรับผู้เรียน

### SHA-256 ของพรอมท์รอบแรก

| ไฟล์ | SHA-256 |
|---|---|
| step-01.md | `26a8e86bb622199f455a26454f25c915f3a484ba25243abc7d58754dce9fdeee` |
| step-02.md | `e1a2bb59f7e332dc7ccbf909edbd92cf759c79844e690aab1d06a0b0785da004` |
| step-03.md | `416cf01486ee24c75ba84f3eee67ab4edc21b613162d6812c97b5c74798ea48f` |

### รอบตรวจรับหลังขยายข้อมูลตั้งต้น

| ขั้น/attempt | เวลา UTC | wrapper ที่รันจริง | รุ่น / effort | exit | ผลตรวจ |
|---|---|---|---|---:|---|
| 1 / attempt 1 | 11:05–11:09 | `cyolo1` | outer `gpt-5.6-sol` / medium; เรียก `cyolo1` ภายใน | 0 | PASS — พบ D-01..D-04 และ REVISE |
| 2 / attempt 1 | 11:10:30–11:12:33 | `yolo2 -p` | `claude-opus-5` / medium | 0 | PASS — สร้าง v1/changes และคงส่วนถูก |
| 3 / attempt 1 | 11:13:05–11:19:41 | `cyolo1` | outer `gpt-5.6-sol` / medium; เรียก `cyolo1` ภายใน | 0 | PASS — T-01..T-07, checks และ D-ID ถูกต้อง |

### SHA-256 ของพรอมท์รอบตรวจรับ

| ไฟล์ | SHA-256 |
|---|---|
| step-01.md | `2d91ae6ec33a3541fb4f66acd3a720fe5f11aa4acc2982d797d9aa4b70d0fd94` |
| step-02.md | `2b9c86af01fc6b67df672e66b72a762afffda84616c9b17d58364849bd69a593` |
| step-03.md | `14cd83d9a06f6006f02f0197a38f19abcf3064521939ecbcdebd6eb2900fffc2` |

พฤติกรรมเรียก wrapper ภายในรอบนี้เป็นสาเหตุของการแก้รอบ 3 ในหัวข้อ 10

## 3. ผลทดสอบ container

| รายการ | ผล |
|---|---|
| ชื่อ | `devtools-lab005-b34ffb` |
| ID | `d163b2ccf19e4410005d9549c1fe007a1920e52923d8ee823d0c2c15732ad5bf` |
| image / สิทธิ์ | `tuchsanai/devtools:2569_1` / privileged |
| พอร์ต | host 2285 → container 22 |
| การเชื่อมต่อ | ใช้ `docker exec -i` ตาม fallback ที่อนุญาต |
| การคัดลอก/path ทางลัด | PASS — README และ step-01/02/03 มีจริง |
| cleanup | PASS — ไม่เหลือ container ชื่อ LAB 005 |

## 4. การตรวจ README กับ prompts

ใช้สคริปต์อ่านกรอบ `text` ทั้งสามจาก README ตัด fence ออก แล้วเทียบไฟล์ UTF-8 แบบ byte-exact รวม newline ท้ายไฟล์หนึ่งตัว ผลล่าสุดอยู่ใน `live/round3/readme-prompt-diff.txt`

| ไฟล์ | ผล |
|---|---|
| `prompts/step-01.md` | MATCH |
| `prompts/step-02.md` | MATCH |
| `prompts/step-03.md` | MATCH |

## 5. สิ่งที่ SKIP

- SKIP การให้ผู้เรียนจริงเปิดหน้าต่าง SSH สองหน้าต่างและสลับ wrapper ด้วยตนเอง เพราะเป็น build test แบบ non-interactive
- SKIP การรันระบบคืนเงินจริงและการวัดสมรรถนะ 2 วินาที เพราะ LAB นี้ตรวจเอกสาร ไม่เชื่อมระบบธุรกิจ

## 6. การตรวจข้อมูลลับ

ตรวจทุกไฟล์ใน `005_LAB_Review_and_Revise/` และ `evidence/lab005/live/round3/` ด้วยรูปแบบความลับทั้งหมดตามข้อ 9.9 ไม่พบค่าข้อมูลส่วนตัวหรือค่ารับรองตัวตน รายละเอียดผลล่าสุดอยู่ในหัวข้อ 10

## 7. เกณฑ์ตรวจรับข้อ 8

| ข้อ | สถานะ | หลักฐาน |
|---:|---|---|
| 1 | PASS | README มีหัวข้อครบ และ 3 ขั้นมี 6 ส่วนเรียงถูก |
| 2 | PASS | ทุกพรอมท์ครบในตัว ขึ้นต้นด้วย path และลงท้ายข้อความมาตรฐาน |
| 3 | PASS | ขั้น 2/3 อ้างไฟล์ที่ขั้นก่อนสร้างจริง ชื่อตรงกัน |
| 4 | PASS | Expected ทุกขั้นเป็นรูปธรรม มีต้องตรง/ต่างได้ และป้ายไม่ใช่ผลจริง |
| 5 | PASS | byte-exact MATCH ทั้ง 3 ไฟล์ และไม่มีเฉลยจับคู่ D-ID ใน prompts |
| 6 | PASS | ตรวจตามข้อ 9.9 แล้วไม่พบค่าข้อมูลลับ |
| 7 | PASS | รายงานแยกรันจริง/SKIP และยืนยัน cleanup |
| 8 | PASS | ผู้เรียนมีเพียงชื่อ wrapper สำหรับเปิด AI ไม่มีคำสั่งจัดการระบบให้พิมพ์ |

สรุป: ผ่าน 8/8 ข้อ

## 9. การแก้ไขรอบตรวจรับ (Claude review)

- ขยายข้อมูลตั้งต้นเป็น BRIEF ฉบับเต็มทุกขั้น และ V0 ฉบับเต็มในขั้น 1
- ขยาย Expected Output จุดตรวจ และข้อความแก้อาการ โดยไม่เปลี่ยนกฎธุรกิจ ตัวเลข รหัส หรือเกณฑ์ผ่าน
- ผล byte-exact หลังประกอบ README ก่อนรอบ 3 เป็น MATCH 3/3
- รอบตรวจรับรันชั้น B ใหม่ครบสามขั้น ส่วนชั้น A ใช้ผลตรวจเดิมตามข้อยกเว้น LAB 005

## 10. รอบ 3 — แก้การเรียก wrapper ซ้อน

แก้เฉพาะบรรทัดที่ 2 ของ `step-01.md`, `step-02.md`, `step-03.md` และบรรทัดเดียวกันในกรอบ README ให้ระบุว่า AI ถูกเปิดผ่าน wrapper แล้วและห้ามเรียก wrapper/CLI อื่นเอง ส่วนอื่นของพรอมท์ไม่เปลี่ยน

### SHA-256 ของพรอมท์รอบ 3

| ไฟล์ | SHA-256 |
|---|---|
| step-01.md | `f7be855ad026ea123381153eeb210697d88f62d49feefe6b052fa7a1060bc4a2` |
| step-02.md | `3e650b134307efb61155798556d1f5d5931c918d971538024e98ffd361ed93b2` |
| step-03.md | `86af666c2a02b852e4c40808864d55a4d03804bfecfe66e1b683443cd0c2b04d` |

Codex CLI 0.153.4; การรันที่ใช้ตัดสินใช้ `cyolo1 exec --skip-git-repo-check -m gpt-5.6-sol -c model_reasoning_effort="medium" --json` และส่งพรอมท์ด้วย `"$(cat .../step-NN.md)"` จาก cwd `/root/workspace/sa-work/005/`

| ขั้น/attempt | เวลา UTC | exit | usage (input/cached/output/reasoning) | ผล | หลักฐาน |
|---|---|---:|---|---|---|
| 1 / attempt 1 | 11:44:46–11:46:46 | 0 | บันทึกใน session rollout | ไม่นับเป็นผลตัดสิน — รันจาก cwd ผิดและ transcript/stream ถูกลบจากการเปลี่ยน `evidence/` พร้อมกันภายนอก; session ยืนยันว่าไม่เรียกซ้อน | รันใหม่ attempt 2 |
| 1 / attempt 2 | 11:58:18–12:00:18 | 0 | 72,288 / 62,848 / 3,175 / 399 | PASS — D-01..D-04 ครบ จบ REVISE; `NESTED_WRAPPER=NONE` | `live/round3/step-01-cyolo1.md`, `.jsonl`, `.stderr` |
| 2 / staged | หลังขั้น 1 | – | – | คัดลอก `requirements-v1.md` และ `changes-r1.md` จาก `live/round2/work/` แบบ byte-exact; ไม่รัน AI ใหม่ | `live/round3/validation.txt` |
| 3 / attempt 1 | 12:01:48–12:04:06 | 0 | 107,157 / 85,120 / 3,427 / 295 | PASS — T-01..T-07 PASS; v0 COUNT=PASS/SEMANTIC=FAIL; v1 PASS/PASS; D-01..D-04 CLOSED; `NESTED_WRAPPER=NONE` | `live/round3/step-03-cyolo1.md`, `.jsonl`, `.stderr` |

ตรวจการเรียกซ้อนด้วย `jq` เลือกเฉพาะ `command_execution` จาก stream แล้ว grep ชื่อคำสั่ง wrapper ผลเป็น `NESTED_WRAPPER=NONE` ทั้งขั้น 1 และ 3 ดู `live/round3/validation.txt` ไม่ต้องปรับถ้อยคำรอบสอง

สคริปต์ diff ดึงกรอบพรอมท์หลักของแต่ละขั้นจาก README แล้วรัน `diff -u` เทียบกับ `prompts/step-NN.md`: `step-01.md MATCH`, `step-02.md MATCH`, `step-03.md MATCH` รวม **MATCH 3/3** ดู `live/round3/readme-prompt-diff.txt`

snapshot ผลงาน 8 ไฟล์อยู่ใน `live/round3/work/` และตรงกับพื้นที่งานก่อน cleanup; ไม่พบไฟล์ v2 จากนั้นลบ `/root/workspace/sa-work/005/` แล้วและตรวจว่า path ไม่มีอยู่
