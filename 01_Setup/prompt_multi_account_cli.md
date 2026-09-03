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

## หมายเหตุจากการทดลองจริง (2026-09-03, Ubuntu 24.04 container · claude 2.1.258 · codex 0.152.1 · qwen 0.22.3)
ดูหลักฐานเต็มใน labs/labA-fresh-install/report.md และ labs/labB-collision/report.md
- npm ≥ 11/12 บล็อก postinstall → `claude --version` ได้ `Error: claude native binary not installed.`
  ติดตั้งด้วย `npm install -g --allow-scripts=@anthropic-ai/claude-code,@qwen-code/audio-capture <pkg>@<ver> ...`
- รันเป็น root: ต้องตั้ง `IS_SANDBOX=1` ไม่งั้น `--dangerously-skip-permissions cannot be used with root/sudo privileges`
- `CODEX_HOME` ต้อง `mkdir -p` ก่อน (codex ไม่สร้างให้: `CODEX_HOME points to "...", but that path does not exist`)
  และ `codex login status` ไม่ validate token — ยืนยันการ login ด้วย `codex exec` เท่านั้น
- Qwen: `-y/--yolo/--approval-mode` ไม่โชว์ใน `--help` แต่ใช้ได้; sub-command (mcp, extensions, ...) ห้ามใส่ `-y`;
  OAuth ฟรียกเลิกแล้ว (2026-04-15) เหลือ API key ตาม plan + `security.auth.selectedType: "openai"`; CLI เขียน settings.json ทับเป็น 644 → installer บังคับ 600
- Claude เขียน MCP log ลง `~/.cache/claude-cli-nodejs/` แม้ตั้ง `CLAUDE_CONFIG_DIR` → ตั้ง `XDG_CACHE_HOME=<account>/.cache` ถ้าต้องการแยกให้ครบ
- ไม่มี CLI ใด include ไฟล์ MCP ภายนอก → ใช้ `claude mcp add-json -s user` / `codex mcp add` / `qwen mcp add -s user` sync ลงทุก account (เกณฑ์ผ่าน: `mcp list` ทุก account เห็น)
- เชลล์: `VAR=x; claude` (มี ;) ไม่ export → ใช้ default เงียบ ๆ ต้องเขียน `VAR=x claude` หรือ export ก่อน แล้วตรวจด้วย `find <root>`
