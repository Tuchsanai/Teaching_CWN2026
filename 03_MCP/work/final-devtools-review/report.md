# รายงานสุดท้าย: ปรับบทเรียน MCP

แก้ readme.md บทที่ 3–4, labs/prompts/setup-*.md จำนวน 8 ไฟล์ และเพิ่ม labs/my-mcp-server/direct_call_kokoro.py

- บท 4: เส้นทางหลักใช้ GitHub ต้นทาง + คำขอภาษาธรรมดา ทั้ง Claude Code และ Codex; ส่วน manual มีคำสั่งติดตั้ง/ตั้งค่าแยกเครื่องมือครบ
- บท 3: แสดง client ฉบับเต็มตรงกับไฟล์จริง อธิบายขั้นตอนและ error พร้อมผล Python MCP client จริงและลิงก์/เครื่องเล่นเสียง
- ทดสอบ client_test.py ผ่าน hello และ tts; ทดสอบ direct_call_kokoro.py ซ้ำ กรณีปกติ exit 0 และชื่อเสียงผิด exit 1
- WAV จริง 2 ไฟล์ในบทเรียนยาวไฟล์ละ 4.45 วินาที 24000 Hz mono; DevTools พบเครื่องเล่นทั้งสอง readyState=4
- Bash บท 4 จำนวน 13 บล็อกผ่าน bash -n; JSON/TOML config parse ผ่าน; ลิงก์ภายในและ code fences ผ่าน
- Chrome DevTools Protocol Runtime.evaluate ตรวจเนื้อหาโค้ด 64 บล็อกตรงต้นฉบับทั้งหมด รูป 14 รูปไม่เสีย ไม่มี horizontal page overflow หรือ page error; Page.captureScreenshot เก็บ ch3.png และ ch4.png
- ตรวจและแก้ PATH placeholder ที่เป็น shell redirection โดยเปลี่ยนเป็นคำอธิบายให้รันจากโฟลเดอร์บทเรียน; จับคู่ Chromium ที่ติดตั้งกับ browser flag; แยกคำสั่งหยุดเว็บออกจากชุดเริ่มเว็บ

## ขอบเขตและข้อจำกัด

yolo2 รอบแรกแก้เอกสารสำเร็จ รอบที่สองเขียนส่วนหลักและผลทดสอบแล้ว แต่จบด้วยข้อผิดพลาดการล็อกอินก่อน QA สุดท้าย ผู้ช่วยหลักจึงอ่าน ตรวจซ้ำ แก้จุดตกหล่น และตรวจ DevTools จนผ่าน ไม่จำเป็นต้องล็อกอินเพื่ออ่านหรือทดสอบ Python client

ไม่ได้ติดตั้งแพ็กเกจใหม่ทั้งชุด ไม่ได้แก้ server/config/credentials ไม่ได้ commit หรือ push การตรวจ installation เป็นการตรวจ syntax/help และทดสอบ runtime เดิม จึงไม่อ้างว่า clean install ผ่านแล้ว

ผลใหม่เป็น Python MCP client ไม่ใช่ผล Codex CLI เป็น Host; การรันผ่าน Codex Host และสร้างภาพ Excalidraw ใหม่ยังไม่สำเร็จในรอบนี้เนื่องจาก auth เดิม จึงไม่ได้แต่งหลักฐาน

## หลักฐาน

- final-static-review.json: ../final-static-review.json
- devtools-report.json, ch3.png, ch4.png, readme.html: โฟลเดอร์รายงานนี้
- direct-call logs/WAV: ../../lab-results/documentation-check/run-2026-09-20-022330/
- independent check logs: ../../lab-results/documentation-check/run-2026-09-20-021614/
