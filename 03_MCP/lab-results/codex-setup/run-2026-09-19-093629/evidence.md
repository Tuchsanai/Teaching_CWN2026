# ผลการเริ่มทดสอบ MCP ผ่าน Codex CLI

สถานะ: ยังไม่ได้ทดสอบ tool เนื่องจาก Codex CLI บน Remote ไม่มีข้อมูลล็อกอิน และการเรียกโมเดลถูกปฏิเสธด้วย HTTP 401 (missing authentication)

## สิ่งที่ตรวจได้ก่อนเริ่ม

- Excalidraw canvas ตอบ HTTP 200
- Chrome CDP ตอบข้อมูลเบราว์เซอร์
- Kokoro health ตอบ ok=true, device=cpu, model_loaded=true
- Python environment เดิม import mcp ได้

ผลเหล่านี้เป็นการตรวจบริการโดยตรง ไม่ใช่หลักฐานว่า Codex เรียก MCP tool สำเร็จ

## งานที่ยังรอ

- ให้ Codex เปิดเว็บไซต์สาธารณะจริงผ่าน Playwright MCP พร้อม snapshot และ screenshot
- ให้ Codex วาดและส่งออกภาพผ่าน Excalidraw MCP
- ให้ Codex เรียก add และสร้างเสียง Kokoro ผ่าน MCP
- ฝังภาพและลิงก์เสียงจริงใน readme.md หลังตรวจไฟล์สำเร็จ

ต้องล็อกอิน Codex CLI บน Remote ก่อน จากนั้นรันการทดสอบซ้ำ ไม่ต้องติดตั้งแพ็กเกจใหม่หรือเปลี่ยนบริการเดิม
