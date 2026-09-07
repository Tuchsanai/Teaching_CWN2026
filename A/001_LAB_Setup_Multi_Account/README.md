# LAB 001 · Setup Multi Account

เวลาโดยประมาณ: 45–60 นาที
สิ่งที่จะได้: ติดตั้งหลายบัญชี แยก “ติดตั้ง” “ตอบได้” “คนละบัญชี”
บทเรียนที่เชื่อมโยง: [AI Agent Routing](../ai-agent-routing.html) หัวข้อ 1.0 และ 4.1–4.3
วิธีทำ: อ่านโจทย์ → คัดลอกพรอมท์ → วางใน AI → ดูผล → เทียบ Expected → ขั้นถัดไป

![ผังขั้นตอน](img/flow.png)

## ก่อนเริ่ม

| หน้าต่าง | wrapper (คำสั่งเปิด) | บทบาท |
|---|---|---|
| เริ่มต้น | AI ที่ผู้สอนเปิดให้ | ติดตั้งและตรวจ |
| A/B · Claude | `yolo1` / `yolo2` | เจ้าของ login และทดสอบ |
| A/B · Codex | `cyolo1` / `cyolo2` | เจ้าของ login และทดสอบ |
| A/B · Qwen | `qyolo1` / `qyolo2` | เจ้าของ login และทดสอบ |

ถ้าเห็น `$`/`#` ท้ายบรรทัดคือ shell ไม่ใช่ AI ให้ผู้สอนเปิด wrapper

ที่เก็บงานคือ `/root/workspace/sa-work/001/` ห้ามส่งข้อมูล login ให้ AI

ถ้ามีโปรแกรม AI (CLI) ค่ายเดียว ให้ใช้ตัวเดิมและติดป้าย `SIMULATION` ในผลส่งงาน

### รหัสบัญชีและตำแหน่ง config

`N` คือเลขลำดับบัญชี ไม่ใช่ชื่อโมเดล

| รหัสบัญชี 1.0 | คำสั่ง | CLI | config root |
|---|---|---|---|
| Yellow N (`N`=1–5) | `yoloN` | Claude Code | `/root/workspace/.Claude/yoloN` |
| C-Yellow N (`N` = 1–5) | `cyoloN` | Codex CLI | `/root/workspace/.Codex/cyoloN` |
| Q-Yellow N (`N` = 1–3) | `qyoloN` | Qwen Code | `/root/workspace/.Qwen/qyoloN` |

## ขั้นที่ 1 · ติดตั้ง (หน้าต่าง: AI ตัวเริ่มต้น | เวลา ~20 นาที)

### 🎯 เป้าหมายของขั้นนี้
ผู้เรียนจะได้ CLI 3 ตัวและ wrapper 13 ตัวแยกบัญชี เพื่อใช้ในขั้นต่อไป

### 📥 ข้อมูลตั้งต้นที่ต้องใช้
- **คำสั่ง:** `yolo1..5`, `cyolo1..5`, `qyolo1..3` รวม 13 wrapper
- **กฎ 1–8:** config แยก, HOME เดิม, เจ้าของใส่ข้อมูลลับ, มี shared
- **กฎ 9–11/ทดสอบ:** ติดตั้งซ้ำ, ตรวจ `--help`; ไม่มี credential=`SKIP`

### 📋 พรอมท์สำหรับคัดลอก  (คัดลอกทั้งกรอบ วางในช่องสนทนา AI แล้ว Enter)
```text
โฟลเดอร์งานคือ /root/workspace/sa-work/001/ (สร้างถ้ายังไม่มี) เก็บทุกไฟล์ที่นี่ ห้ามแก้ไฟล์ใน /root/workspace/sa-labs/
ลงมือติดตั้งใน container นี้ ผู้เรียนใช้พรอมท์เท่านั้น
ห้ามอ่านหรือค้นหาไฟล์ README ของ LAB เพื่อหาเฉลย

สร้าง CLI บน Ubuntu สำหรับรัน Claude Code, Codex CLI และ Qwen Code หลาย account
แยก credential/config กัน 100%

## ตัวแปรตั้งค่า (แก้ที่นี่ที่เดียว ที่อื่นต้องอ้างอิงตัวแปรนี้)
BASE_PATH="/root/workspace"

## คำสั่ง
- yolo1..yolo5   → Claude Code + Anthropic account
- cyolo1..cyolo5 → Codex CLI + OpenAI account
- qyolo1..qyolo3 → Qwen Code + QwenCloud account (ใช้ Qwen Code โดยตรง ห้ามผ่าน Claude Code/Codex)

## โครงสร้าง
$BASE_PATH/
├── .Claude/                      # Claude Code
│   ├── yolo1/ … yolo5/           # config root ต่อ account (CLAUDE_CONFIG_DIR) — credential/session/history/cache แยกกัน
│   └── shared/
│       ├── skills/               # skill ใช้ร่วมทุก yoloN (symlink / discovery)
│       └── mcp/                  # MCP config ใช้ร่วมทุก yoloN
├── .Codex/                       # Codex CLI
│   ├── cyolo1/ … cyolo5/         # config root ต่อ account (CODEX_HOME)
│   └── shared/
│       ├── skills/
│       └── mcp/
├── .Qwen/                        # Qwen Code
│   ├── qyolo1/ … qyolo3/         # config root ต่อ account (ตาม docs) + API key permission 600
│   └── shared/
│       ├── skills/
│       └── mcp/
└── .mcp/                         # (สร้างโฟลเดอร์ว่างไว้) state ของ MCP server ที่ทุก CLI ทุก account จะใช้ร่วมกัน — ติดตั้งภายหลัง

หลักการ: <tool>/<account>/ = ของใครของมัน, <tool>/shared/ = แก้ครั้งเดียวทุก account ของ CLI นั้นเห็น,
.mcp/ = ที่เก็บ MCP ตัวเดียวกันแชร์ข้ามทุก CLI

## Isolation
1. ทุก account แยก credential/config/session/history/cache สมบูรณ์ เปิดพร้อมกันได้ไม่ชน
2. ห้ามเปลี่ยน $HOME — ใช้กลไก official กำหนด config root ต่อ CLI
   (Claude: CLAUDE_CONFIG_DIR, Codex: CODEX_HOME, Qwen: ตาม docs ล่าสุด)
   ถ้า CLI ใดไม่มีกลไก official ให้ระบุข้อจำกัดชัดและใช้เฉพาะวิธีที่รองรับจริง
3. ห้ามแก้ .bashrc, Git config, SSH config หรือ project environment เดิมโดยไม่จำเป็น

## Wrapper
4. ทุกคำสั่งส่งต่อ "$@" และรันแบบ skip permissions ด้วย flag ล่าสุดของแต่ละ CLI
   - yoloN  → claude --dangerously-skip-permissions
   - cyoloN → codex + bypass approval/sandbox
   - qyoloN → qwen + permission/approval flag ที่รองรับ

## Qwen credential
5. qyoloN ครั้งแรก: ให้ผู้ใช้เลือก plan (Token Plan Personal / Token Plan Team / Coding Plan /
   Pay-as-you-go) และกรอก API key แบบซ่อนตัวอักษร
   endpoint, credential variable, default model ต้องตรงกับ plan ตาม docs ห้ามเดาหรือใช้ข้าม plan
6. เก็บ key แยกใน .Qwen/qyoloN permission 600 — ห้ามฝังใน source/template/ไฟล์แจกจ่าย,
   ห้ามส่งผ่าน argument, ห้ามโชว์ใน terminal / process list / log
7. ห้ามใช้ key เดียวข้ามหลาย account โดยไม่แจ้งเจ้าของ credential (ห้ามเปิดเผย credential)

## Skills / MCP
8. แต่ละ CLI ใช้ <tool>/shared เป็น source เดียว — แก้ครั้งเดียวทุก account ของ CLI นั้นเห็น
   - Skills: symlink หรือ official discovery mechanism
   - MCP: ถ้า CLI ไม่มี config include ให้ sync ด้วยคำสั่ง official ของ CLI นั้น
   - CLI ใดไม่รองรับส่วนใด ให้ระบุชัดและทำเท่าที่รองรับ

## Installer
9. รันได้โดยไม่ลบ/เขียนทับ credential-config เดิม
10. วิธีติดตั้งและจัดวางไฟล์ให้เลือกเอง พร้อมอธิบายเหตุผลสั้นๆ

## Docs
11. ตรวจสอบ official docs และ --help ของเวอร์ชันที่ติดตั้งจริงก่อน implement
    ห้ามเดา env/path/endpoint/model/flag — ถ้า docs กับ CLI ไม่ตรงกัน ให้รายงานและใช้ค่าที่ยืนยันจากเวอร์ชันจริง
    - https://code.claude.com/docs/
    - https://github.com/openai/codex
    - https://docs.qwencloud.com/developer-guides/clients-and-developer-tools/qwen-code

## ทดสอบ (รายงานตามจริง PASS / FAIL / SKIP)
- yolo1/yolo2, cyolo1/cyolo2 login คนละ account + qyolo1/qyolo2 ใส่ key ต่างกัน → เปิดพร้อมกัน ไม่ชน
- Qwen key ไม่ปรากฏใน argument / process list / log
- เพิ่ม Skill และ MCP อย่างละ 1 ใน shared ของแต่ละ CLI → ทุก account ที่เกี่ยวข้องเห็น
- installer รอบ 2 ไม่ทำลายของเดิม
- Git/SSH ทำงานปกติ
- test ที่ต้องใช้ credential จริง ให้เจ้าของ credential เป็นผู้รัน (มิฉะนั้นรายงาน SKIP)

## รายงาน
- config root ของแต่ละ CLI, credential location, shared source และข้อจำกัดของแต่ละ CLI

รอบนี้ห้ามใช้ credential; login เป็น SKIP เขียน setup-report.md, login-guide.md, checklist.md และรายงานข้อจำกัดตามจริง
ให้สร้างรายงานและสรุปภายใน 12 นาที หากการตรวจเสริมยังไม่จบให้บันทึก SKIP/PARTIAL แทนการทำต่อจนเกินเวลา

ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหาสำคัญของไฟล์ที่สร้าง (ไม่ใช่แค่ชื่อไฟล์) บนหน้าจอเป็นตาราง/รายการที่ฉันอ่านตรวจได้ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
```

ถ้าผู้สอนวางโฟลเดอร์ LAB ไว้ใน container แล้ว วางข้อความสั้นนี้แทนได้
ขั้นที่ 1 ใช้ทางลัดได้เมื่อ AI ตัวเริ่มต้นอ่านไฟล์ได้และมีโฟลเดอร์ LAB แล้วเท่านั้น

```text
อ่านไฟล์ /root/workspace/sa-labs/001_LAB_Setup_Multi_Account/prompts/step-01.md แล้วทำตามคำสั่งในไฟล์นั้นทั้งหมด ทำเฉพาะขั้นนี้ แสดงผลบนหน้าจอ แล้วหยุดรอฉันตรวจ
```

### ✅ Expected Output (ตัวอย่างสำหรับเทียบ — ไม่ใช่ผลการรันจริง)
| CHECK | ACTUAL EXAMPLE |
|---|---|
| CLI | 3 PASS: `2.1.263 / 0.153.4 / 0.23.0` |
| yolo | 5/5 PASS |
| cyolo | 5/5 PASS |
| qyolo | 3/3 PASS |
| config A/B | 3 families PASS |
| reports | 3/3 created |
| real login | SKIP |
- **ต้องตรง:** (1) CLI=3 (2) wrapper=13 (3) ไฟล์ `setup-report.md`/`login-guide.md`/`checklist.md` และ login=`SKIP`
- **ต่างได้:** (1) version (2) ถ้อยคำ/ลำดับ

### 🔍 จุดที่ผู้เรียนต้องตรวจ
- [ ] หน้าจอมี `yolo` 5, `cyolo` 5, `qyolo` 3 ตัว รวม 13 ตัว
- [ ] หน้าจอมีไฟล์รายงาน 3 ไฟล์
- [ ] งานที่ใช้บัญชีจริงเป็น `SKIP` พร้อมเหตุผล
- [ ] หน้าจอไม่มีข้อมูล login

### 🔁 ถ้าผลไม่ตรง
| อาการ | ข้อความที่วางต่อ |
|---|---|
| ใกล้ 12 นาทีแล้วยังไม่จบ | งานค้างเป็น SKIP/PARTIAL; สร้าง 3 รายงาน แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |
| wrapper ไม่ครบ | สร้างให้ครบ 13 ตัว แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |
| ไม่ login แต่เป็น PASS | เปลี่ยนเป็น SKIP แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |

## ขั้นที่ 2 · ตรวจผลติดตั้ง (หน้าต่าง: AI ตัวเริ่มต้น | เวลา ~10 นาที)

### 🎯 เป้าหมายของขั้นนี้
ผู้เรียนจะแยก “เปิดได้” “ตอบได้” และ “คนละบัญชี” เพื่อไม่สรุปเกินหลักฐาน

### 📥 ข้อมูลตั้งต้นที่ต้องใช้
- ไฟล์จากขั้น 1: `/root/workspace/sa-work/001/setup-report.md`; ถ้าขาดให้บอก path แล้วหยุด
- **กฎคำสั่ง/1–9:** ตรวจ CLI 3, wrapper 13, config A/B, shared, รอบสอง, Git/SSH
- **กฎทดสอบ:** ยังไม่ login = `SKIP`

### 📋 พรอมท์สำหรับคัดลอก  (คัดลอกทั้งกรอบ วางในช่องสนทนา AI แล้ว Enter)
```text
โฟลเดอร์งานคือ /root/workspace/sa-work/001/ (สร้างถ้ายังไม่มี) เก็บทุกไฟล์ที่นี่ ห้ามแก้ไฟล์ใน /root/workspace/sa-labs/
ห้ามอ่าน README ของ LAB เพื่อหาเฉลย
อ่าน setup-report.md จากขั้นก่อน ถ้าไม่มีให้บอก path เต็มแล้วหยุด ห้ามแต่งขึ้นเอง
ตรวจ CLI 3 ตัว, wrapper 13 ตัว, config คู่ A/B, shared Skills/MCP, installer รอบสอง และ Git/SSH จากของจริง ห้ามเปลี่ยน HOME หรือแสดงข้อมูลลับ
เขียน checklist.md ตาราง “รายการ | หลักฐาน | PASS/FAIL/SKIP | เหตุผล” แยกติดตั้ง/ตอบได้/คนละบัญชี เรื่องที่ต้อง login ให้ SKIP
ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหาสำคัญของไฟล์ที่สร้าง (ไม่ใช่แค่ชื่อไฟล์) บนหน้าจอเป็นตาราง/รายการที่ฉันอ่านตรวจได้ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
```

ถ้าผู้สอนวางโฟลเดอร์ LAB ไว้ใน container แล้ว วางข้อความสั้นนี้แทนได้

```text
อ่านไฟล์ /root/workspace/sa-labs/001_LAB_Setup_Multi_Account/prompts/step-02.md แล้วทำตามคำสั่งในไฟล์นั้นทั้งหมด ทำเฉพาะขั้นนี้ แสดงผลบนหน้าจอ แล้วหยุดรอฉันตรวจ
```

### ✅ Expected Output (ตัวอย่างสำหรับเทียบ — ไม่ใช่ผลการรันจริง)
| CATEGORY | PASS | FAIL | SKIP |
|---|---:|---:|---:|
| installed | 14 | 0 | 0 |
| responsive | 2 | 0 | 5 |
| separate root | 3 | 0 | 3 |
| TOTAL | 19 | 0 | 8 |
| wrapper | 13/13 | 0 | 0 |
| model login | 0 | 0 | 3 |
- **ต้องตรง:** (1) 5+5+3=13 (2) version ≠ login (3) config A/B ต่าง path
- **ต่างได้:** (1) จำนวนสถานะตามผลจริง (2) version/รูปตาราง

### 🔍 จุดที่ผู้เรียนต้องตรวจ
- [ ] หน้าจอมี wrapper 5+5+3 = 13 ตัว
- [ ] หน้าจอมี config A/B ต่าง path ครบ 3 ค่าย
- [ ] version `PASS` แยกจาก model login `SKIP`
- [ ] ทุกแถวมีหลักฐานและเหตุผลของสถานะ

### 🔁 ถ้าผลไม่ตรง
| อาการ | ข้อความที่วางต่อ |
|---|---|
| ไม่มีหลักฐาน | เติมหลักฐานจริง แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |
| version ถูกนับเป็น login | แยกผล local; login เป็น SKIP แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |

## ขั้นที่ 3 · Login สองหน้าต่าง (หน้าต่าง: A/B ทีละคู่ | เวลา ~15 นาที)

### 🎯 เป้าหมายของขั้นนี้
ผู้เรียนจะตรวจสอง login พร้อมกัน เพราะ config แยกยังพิสูจน์บัญชีไม่ได้

### 📥 ข้อมูลตั้งต้นที่ต้องใช้
- ไฟล์: `/root/workspace/sa-work/001/login-guide.md` และ `/root/workspace/sa-work/001/checklist.md`
- คู่: `yolo1+yolo2`, `cyolo1+cyolo2`, `qyolo1+qyolo2`
- หลักฐาน: เจ้าของยืนยัน, config, model/`UNKNOWN`, `20`/`16` และช่วงเปิดพร้อมกัน

ลำดับที่เจ้าของบัญชีทำ:

1. เปิด SSH สองหน้าต่างเข้า container เดียวกัน
2. ที่ shell พิมพ์ wrapper คู่แรก เช่น A=`yolo1`, B=`yolo2`
3. เจ้าของ login ตามหน้าจอและ `login-guide.md`; ไม่ส่งข้อมูลให้ AI
4. วาง A=`ตอบบรรทัดเดียว: <NONCE_A> | 12 + 8 = 20` และ B=`ตอบบรรทัดเดียว: <NONCE_B> | 25 - 9 = 16`; เมื่อ B ตอบให้ถาม A ซ้ำ
5. ทำอีกสองคู่ ปกปิดข้อมูล แล้วแทน placeholder ด้วยผลจริง
6. ไม่มี credential หรือ login ไม่สำเร็จ = `SKIP` ไม่ใช่ `PASS`

### 📋 พรอมท์สำหรับคัดลอก  (คัดลอกทั้งกรอบ วางในช่องสนทนา AI แล้ว Enter)
```text
โฟลเดอร์งานคือ /root/workspace/sa-work/001/ (สร้างถ้ายังไม่มี) เก็บทุกไฟล์ที่นี่ ห้ามแก้ไฟล์ใน /root/workspace/sa-labs/
ห้ามอ่าน README ของ LAB เพื่อหาเฉลย
อ่าน login-guide.md และ checklist.md จากขั้นก่อน ถ้าขาดให้บอก path เต็มแล้วหยุด ห้ามแต่ง
เจ้าของ login เองทีละคู่ yolo1+yolo2, cyolo1+cyolo2, qyolo1+qyolo2 ใช้ผลปกปิดแล้ว: <PASTE_REDACTED_OBSERVATIONS>
เขียน login-results.md ตาราง “คู่ | ยืนยันต่างบัญชี | config | model/UNKNOWN | nonce A/B | A ตอบหลัง B | พร้อมกัน | PASS/FAIL/SKIP | เหตุผล”
PASS ต้องมีหลักฐานครบ; nonce ไม่พิสูจน์บัญชี; placeholder ยังอยู่ให้ SKIP; ห้ามขอหรือแสดงข้อมูล login

ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหาสำคัญของไฟล์ที่สร้าง (ไม่ใช่แค่ชื่อไฟล์) บนหน้าจอเป็นตาราง/รายการที่ฉันอ่านตรวจได้ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
```

ถ้าผู้สอนวางโฟลเดอร์ LAB ไว้ใน container แล้ว วางข้อความสั้นนี้แทนได้

```text
อ่านไฟล์ /root/workspace/sa-labs/001_LAB_Setup_Multi_Account/prompts/step-03.md แล้วทำตามคำสั่งในไฟล์นั้นทั้งหมด ทำเฉพาะขั้นนี้ แสดงผลบนหน้าจอ แล้วหยุดรอฉันตรวจ
```

### ✅ Expected Output (ตัวอย่างสำหรับเทียบ — ไม่ใช่ผลการรันจริง)
| CHECK | ACTUAL EXAMPLE |
|---|---|
| `yolo1/yolo2` | `SKIP · SIMULATED` |
| `cyolo1/cyolo2` | `SKIP · SIMULATED` |
| `qyolo1/qyolo2` | `SKIP · SIMULATED` |
| nonce A | `<NONCE_A> · 20` |
| nonce B | `<NONCE_B> · 16` |
| model | `UNKNOWN` |
| PASS needs | owner + config + A/B + retry A + concurrent |
- **ต้องตรง:** (1) 20/16 (2) `PASS` มีหลักฐานครบ (3) ไม่มี credential=`SKIP`
- **ต่างได้:** (1) nonce/เวลา (2) model/`UNKNOWN`

### 🔍 จุดที่ผู้เรียนต้องตรวจ
- [ ] หน้าจอมีคู่ `yolo`, `cyolo`, `qyolo` ครบ
- [ ] หน้าจอมี A=`20`, B=`16` และ A ตอบซ้ำ
- [ ] `PASS` มีคำยืนยันเจ้าของและ config ต่าง path
- [ ] ไม่มี credential = `SKIP` และ `login-results.md` ไม่มีข้อมูล login

### 🔁 ถ้าผลไม่ตรง
| อาการ | ข้อความที่วางต่อ |
|---|---|
| หลักฐานไม่ครบแต่ PASS | เปลี่ยนเป็น SKIP/FAIL แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |
| A/B ไม่ตอบหรือคำนวณผิด | บันทึก FAIL ห้ามแต่งผล แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |

## ขั้นที่ 4 · สรุปผล (หน้าต่าง: AI ตัวเริ่มต้น | เวลา ~5 นาที)

### 🎯 เป้าหมายของขั้นนี้
ผู้เรียนจะได้ตารางสรุปที่ไม่ใช้ผลติดตั้งหรือผลจำลองแทน login จริง

### 📥 ข้อมูลตั้งต้นที่ต้องใช้
- ไฟล์: `/root/workspace/sa-work/001/setup-report.md`, `/root/workspace/sa-work/001/checklist.md`, `/root/workspace/sa-work/001/login-results.md`; ขาดไฟล์ให้บอก path แล้วหยุด
- **กฎคำสั่ง/1–9:** CLI 3, wrapper 13, config A/B, shared, รอบสอง, Git/SSH
- **กฎทดสอบ:** login/nonce ตามจริง; ผลจำลองมี `SIMULATED`

### 📋 พรอมท์สำหรับคัดลอก  (คัดลอกทั้งกรอบ วางในช่องสนทนา AI แล้ว Enter)
```text
โฟลเดอร์งานคือ /root/workspace/sa-work/001/ (สร้างถ้ายังไม่มี) เก็บทุกไฟล์ที่นี่ ห้ามแก้ไฟล์ใน /root/workspace/sa-labs/
ห้ามอ่าน README ของ LAB เพื่อหาเฉลย
อ่าน setup-report.md, checklist.md, login-results.md จากขั้นก่อน ถ้าขาดให้บอก path เต็มแล้วหยุด ห้ามแต่ง
เขียน final-results.md ตาราง “หัวข้อ | หลักฐาน | PASS/FAIL/SKIP | งานต่อ” ครบ CLI, wrapper 13 ตัว, config A/B, shared, installer รอบสอง, Git/SSH, login และ nonce
ยึดไฟล์จริง คงป้าย SIMULATED ห้ามใช้ Expected หรือเปลี่ยน SKIP เป็น PASS และสรุปว่าติดตั้ง/ตอบได้/คนละบัญชีเป็นคนละหลักฐาน
ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหาสำคัญของไฟล์ที่สร้าง (ไม่ใช่แค่ชื่อไฟล์) บนหน้าจอเป็นตาราง/รายการที่ฉันอ่านตรวจได้ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
```

ถ้าผู้สอนวางโฟลเดอร์ LAB ไว้ใน container แล้ว วางข้อความสั้นนี้แทนได้

```text
อ่านไฟล์ /root/workspace/sa-labs/001_LAB_Setup_Multi_Account/prompts/step-04.md แล้วทำตามคำสั่งในไฟล์นั้นทั้งหมด ทำเฉพาะขั้นนี้ แสดงผลบนหน้าจอ แล้วหยุดรอฉันตรวจ
```

### ✅ Expected Output (ตัวอย่างสำหรับเทียบ — ไม่ใช่ผลการรันจริง)
| CHECK | EVIDENCE | STATUS |
|---|---|---|
| CLI | 3 versions | PASS |
| wrapper | 5+5+3 = 13 | PASS |
| config A/B | 3 separate roots | PASS |
| shared | Skills 13/13; MCP responds | PASS |
| installer + Git/SSH | unchanged + checks pass | PASS |
| login/nonce | no real result | `SKIP · SIMULATED` |
- **ต้องตรง:** (1) ครบหัวข้อ (2) อ้างไฟล์จริง (3) ผลจำลองมี `SIMULATED`
- **ต่างได้:** (1) จำนวน/ลำดับแถว (2) version/ถ้อยคำ

### 🔍 จุดที่ผู้เรียนต้องตรวจ
- [ ] หน้าจอมีคอลัมน์ “หัวข้อ | หลักฐาน | PASS/FAIL/SKIP | งานต่อ”
- [ ] หน้าจอมี wrapper 13 ตัวและ config A/B ครบ 3 ค่าย
- [ ] login/nonce ตรงไฟล์จริงและผลจำลองมี `SIMULATED`
- [ ] หน้าจอแยก “ติดตั้ง” “ตอบได้” “คนละบัญชี”

### 🔁 ถ้าผลไม่ตรง
| อาการ | ข้อความที่วางต่อ |
|---|---|
| สถานะขัดไฟล์จริง | แก้ตามไฟล์จริง แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |
| ป้าย SIMULATED หาย | คืนป้าย ห้ามยกเป็น PASS แก้เฉพาะขั้นนี้ แสดงผล แล้วหยุด |

## ส่งงาน

ส่งจาก `/root/workspace/sa-work/001/`: `setup-report.md`, `login-guide.md`, `checklist.md`, `login-results.md`, `final-results.md`

- [ ] ผลงานแสดงผลตรวจ CLI 3 ตัวและ wrapper 13 ตัวจริงครบ
- [ ] ผลงานแสดง config A/B ครบสามค่ายและเป็นคนละ path
- [ ] ผลงานไม่ใช้ผล version แทนผลโมเดลหรือ login
- [ ] ทุกสถานะมีเหตุผล และเมื่อไม่มี credential ต้องเป็น `SKIP`
- [ ] งานจำลองมีป้าย และทุกไฟล์ไม่มีข้อมูลลับ

คำถามสะท้อนคิด:

1. ทำไม config สองโฟลเดอร์ยังพิสูจน์ไม่ได้ว่าเป็นคนละบัญชี?
2. ผล 20 และ 16 พิสูจน์อะไรได้และไม่ได้?
3. เมื่อคู่บัญชีเป็น `SKIP` ควรบอกข้อจำกัดและงานต่ออย่างไร?

## หลักฐานผู้จัดทำ

ผู้จัดทำใช้ `cyolo1` รันขั้น 1, 2, 4; ขั้น 1 รอบ 2 ตรวจ 3 CLI/13 wrapper
ขั้น 3 login/nonce=`SKIP`; ขั้น 4=`SIMULATED`; ดู [รายงาน](../evidence/lab001/report.md)
