# แหล่งอ้างอิงและขอบเขตข้อเท็จจริง

ตรวจเมื่อ 2026-09-12 UTC เวลาการเปิด/รันจริงละเอียดอยู่ใน metadata และรายงาน build ไม่ถือว่าสเปกผลิตภัณฑ์จะคงเดิมตลอด

| แหล่งทางการ | ใช้ยืนยัน | ขอบเขต |
|---|---|---|
| [OpenAI Docs: Build skills](https://learn.chatgpt.com/docs/build-skills) (จาก developers.openai.com/codex/skills) | SKILL.md, name/description, progressive disclosure, .agents/skills, $ และ /skills, skill-creator | ตรวจประกอบ CLI ที่ติดตั้งจริง ไม่เทียบ syntax กับ UI อื่นโดยอัตโนมัติ |
| [OpenAI: GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) | ชื่อโมเดลและ effort high | การเข้าถึงบัญชีจริงตรวจด้วย login และผลรัน ไม่เอาราคา API ไปอ้างต้นทุน subscription |
| [Playwright: Test CLI](https://playwright.dev/docs/test-cli) | วิธีรัน test และตัวเลือก CLI | เวอร์ชัน local 1.58.2 ตรวจด้วย --version และ --help |
| [Excalidraw](https://docs.excalidraw.com/) | รูปแบบเครื่องมือวาดและส่งออก | แพ็กเกจใช้ CLI mcp-excalidraw-server 2.0.0 ที่ติดตั้งจริง; คำสั่งและผลงานเก็บใน diagrams และ build |

โครงเรื่องและภาพรวมการจัดหน้าใช้ Week1/ai-agent-routing.html เป็นแบบ: เริ่มจากเหตุผล → คำศัพท์/ตั้งเครื่อง → กระบวนการเลือกใช้ → ตัวอย่าง → กิจกรรม → ตรวจผล อ่านเอกสาร Week1/005_LAB_AI_Work_Prompt_vs_Skill เพื่อคงแนวทางผู้เรียนใช้ภาษาคน แต่สร้างข้อมูลและหลักฐานทดลองใหม่ทั้งหมด

นโยบายร้านและข้อความลูกค้าใน Lab1/3 เป็นตัวอย่างสมมติ ไม่ใช่นโยบายธุรกิจจริงหรือคำแนะนำทางกฎหมาย Lab2 เป็นบริการจำลองที่ทำงานจริงในเครื่อง ไม่มีชำระเงินจริง คะแนนทดลองและข้อจำกัดอ้างจากไฟล์หลักฐานในแพ็กเกจ ไม่ใช่แหล่งอ้างอิงภายนอก
