# 04_Skill_Setup — แนวทางสำหรับ Claude

## บริบท
- `00_Setup_Skill/readme.md` = LAB 04: ลากโฟลเดอร์ skill (`yolo` `cyolo` `vastai`) จาก Windows (`Teaching_CWN2026\00_resource\skills`) ไปวางใน JupyterLab ของ container `multi-account-devtool` (LAB 03) 2 ที่:
  - `/root/ai-accounts/.Claude/shared/skills` → ให้ `yolo1`–`yolo5` (Claude Code)
  - `/root/ai-accounts/.Codex/shared/skills` → ให้ `cyolo1`–`cyolo5` (Codex)
  - ทดสอบด้วย `/skills` และ skill `shared-check` → `SHARED_SKILL_OK-claude-…` / `SHARED_SKILL_OK-codex-…`
- JupyterLab: http://localhost:8886/lab (port จาก LAB 03)
- รูปใน `image/`: "ภาพจริง" = screenshot จริง, "ภาพแนวคิด" = Imagegen ด้วย cyolo — ให้ระบุแบบนี้ใน caption ทุกครั้ง

## กฎ: สร้างรูป → ใช้ cyolo CLI เท่านั้น
- ภาพแนวคิด/ภาพประกอบทุกภาพ สร้างด้วย `cyolo` (Codex CLI wrapper: `C:\Users\oishi\bin\cyolo.cmd`)
- วิธีที่ใช้ได้: เขียน prompt ลงไฟล์ (ใช้ Python สร้างไฟล์ prompt, path แบบ `/`) แล้วรันใน background จาก Bash:
  `/c/Users/oishi/bin/cyolo.cmd exec - < prompt.txt`
  (ส่ง prompt ยาว/ภาษาไทยเป็น argument จะพังผ่าน .cmd) ใช้เวลา ~3 นาที/ภาพ
- ระบุ output path ชัดเจนใน prompt (เช่น `00_Setup_Skill/image/<name>.png`) และ**เปิดดูผลทุกครั้ง** — Codex อาจรายงานว่าสำเร็จทั้งที่ภาพไม่เปลี่ยน
- ห้ามสร้างรูปด้วยวิธีอื่น (PIL วาดภาพ, SVG ฯลฯ) แทน cyolo

## กฎ: เข้าเว็บ → ใช้ Playwright
- เปิด/อ่าน/คลิก/ถ่าย screenshot หน้าเว็บ (JupyterLab, GitHub, เอกสาร ฯลฯ) ให้ใช้ Playwright MCP (`mcp__playwright__browser_*`: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_take_screenshot` …)
- ไม่ใช้ built-in browser pane, Claude in Chrome หรือ WebFetch แทน เว้นแต่ผู้ใช้สั่ง หรือ Playwright เชื่อมต่อไม่ได้ (ให้แจ้งผู้ใช้ก่อน)
- screenshot "ภาพจริง" ของ JupyterLab ให้ถ่ายด้วย `browser_take_screenshot` แล้วบันทึกลง `00_Setup_Skill/image/`
