# สร้าง CLI ภายใน Linux  สำหรับรัน Claude Code และ Codex CLI หลายบัญชี

กำหนดให้สภาพแวดล้อมนี้ต้องติดตั้งเครื่องมือ AI coding CLI  ดังนี้:

1. Claude Code (Anthropic)
   - ติดตั้งผ่าน: curl -fsSL https://claude.ai/install.sh | bash
   - เรียกใช้ด้วยคำสั่ง: claude

2. Codex CLI (OpenAI)
   - ติดตั้งผ่าน: npm install -g @openai/codex
   - เรียกใช้ด้วยคำสั่ง: codex

ตรวจสอบ Claude Code และ Codex CLI ติดตั้งไว้แล้วไม่ต้องติดตั้งซ้ำ ตรวจ claude --version และ codex --version 
เพื่อยืนยันความพร้อมก่อนตั้งค่าหลายบัญชี


BASE_PATH="$HOME/ai-accounts"   # แก้ที่นี่ที่เดียว

## เป้าหมาย
- yolo1..yolo5   → claude --dangerously-skip-permissions  (CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN)
- cyolo1..cyolo5 → codex --dangerously-bypass-approvals-and-sandbox  (CODEX_HOME=$BASE_PATH/.Codex/cyoloN)
- $BASE_PATH/.Claude/shared และ .Codex/shared มี skills/ และ mcp/mcp.json ({"mcpServers":{...}}) แก้ครั้งเดียว ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป โดยไม่ต้องรัน installer ซ้ำ
- wrapper ส่งต่อ "$@" ครบ แจ้งชัดถ้าโฟลเดอร์บัญชีไม่มี ไม่พิมพ์ secret

## กติกา
- แยก credential/config/session ต่อบัญชี เปิดพร้อมกันได้ ใช้ CLAUDE_CONFIG_DIR/CODEX_HOME เท่านั้น ห้ามเปลี่ยน $HOME
- Codex ใช้ file-based credential ต่อ CODEX_HOME ระบุสิ่งที่ยังร่วมกัน (project config, ผู้ใช้ Linux) ห้ามอ้างว่าเป็น OS isolation
- ห้ามแก้ .bashrc/Git/SSH ถ้าต้องเพิ่ม PATH ให้ขอยืนยันก่อน
- installer รันซ้ำได้ ไม่เขียนทับ credential/config เดิม ห้ามแชร์ credential ใน shared
- MCP ส่วนกลางตัวแรก: Playwright (@playwright/mcp) + Chromium ติดตั้งครั้งเดียว
- skill ตัวอย่าง shared-check: ตอบ SHARED_SKILL_OK-<tool>-<ค่าสุ่มตอนติดตั้ง> ซึ่งมีในไฟล์นี้เท่านั้น

## ข้อเท็จจริงจากการทดลอง (ตรวจว่ายังจริงกับเวอร์ชันนี้)
- root ต้องตั้ง IS_SANDBOX=1; CODEX_HOME ต้อง mkdir -p ก่อน
- Claude: skill อ่านจาก $CLAUDE_CONFIG_DIR/skills; MCP ส่งผ่าน --mcp-config=<ไฟล์> (ต้องมี =)
  ห้าม symlink .claude.json (มีสถานะล็อกอิน); claude mcp list ไม่แสดง MCP นี้ ให้ตรวจด้วย /mcp
- Codex: skill อ่านจาก $CODEX_HOME/skills และเขียน skills/.system เอง ห้าม symlink ทั้งโฟลเดอร์
  ห้ามใช้ ~/.agents/skills เป็นทางลัด; MCP ส่งด้วย -c mcp_servers.<name>={...} (ใช้กับ codex mcp list ได้)
- Playwright ใน root container: --browser chromium --headless --isolated --no-sandbox และ --output-dir นอกโฟลเดอร์งาน
  ติดตั้ง Chromium ด้วย playwright ในแพ็กเกจ @playwright/mcp ให้เวอร์ชันตรงกัน
- Codex ใน container ล็อกอินด้วย codex login --device-auth; login status ไม่ยืนยัน token ให้ทดสอบด้วย codex exec

## ทดสอบ (PASS/FAIL/SKIP ตามจริง)
- 10 คำสั่ง --version ครบ, config root คนละโฟลเดอร์ (find), installer รอบ 2 ไม่ทำลายของเดิม, Git/SSH ปกติ
- cyoloN mcp list เห็น playwright, skill shared-check ทุกบัญชี readlink -f ไปไฟล์เดียวกันใน shared
- อะไรที่ต้องล็อกอิน = SKIP

## รายงาน (ห้ามมี secret) ในโฟลเดอร์ปัจจุบัน
- setup-report.md: config root, ตำแหน่ง credential, แต่ละ CLI อ่าน skill/MCP จากไหน และเชื่อม shared อย่างไร, ข้อจำกัด
- login-guide.md: ล็อกอินทีละบัญชี และวิธีตรวจ skill/MCP หลังล็อกอิน
- checklist.md: รายการ | หลักฐาน | PASS/FAIL/SKIP | เหตุผล
เสร็จแล้วแสดงสาระสำคัญเป็นตาราง แล้วหยุดรอ ห้ามล็อกอินแทนฉัน ห้ามทำขั้นถัดไปเอง