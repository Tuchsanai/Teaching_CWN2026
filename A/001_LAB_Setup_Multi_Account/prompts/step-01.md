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
