# Week 03 · เช่า GPU · ทีม AI · ส่งมอบระบบ AI ครบวงจร

สัปดาห์นี้มี 3 บท ทุกบทรันใน container `multi-account-devtool` และใช้พรอมต์ Copy & Paste ใน Claude Code Desktop

| บท | หัวข้อ | สิ่งที่ได้ |
|---|---|---|
| [01_VastAi_Skill](01_VastAi_Skill/readme.md) | เช่า GPU บน Vast.ai ด้วยสกิล `vastai` ของ Vast.ai | ติดตั้งสกิลใน container · เทียบราคาเครื่อง · เช่า RTX 4090 แล้วลบ · แชทบอทที่ใช้ AI บน RTX 5090 ผ่าน 26/26 เคส |
| [02_VastAi_Application](02_VastAi_Application/README.md) | เช่า GPU บน Vast.ai มาเทรนโมเดล ต่อเข้าเว็บ และออกแบบระบบให้รับผู้ใช้พร้อมกัน (9 LAB) | พรอมต์ทีละขั้นที่ AI เขียนโค้ดเอง: YOLO · VLM · QLoRA · Multi-GPU · คลัสเตอร์หลายเครื่อง · วัดความจุ GPU · Load Balancer · RabbitMQ · ปิดท้ายทุก LAB ด้วยสกิลเวอร์ชัน 0 |
| [03_Agent_Team_End_to_End](03_Agent_Team_End_to_End/README.md) | Agent Team ส่งมอบระบบ AI ครบวงจร: จาก User Story ถึง Test Report (2 หัวข้อ) | SiteSafe Inspect (YOLO11s · 10 บล็อก · 16 ขั้น) และ ReceiptDesk (Qwen3-VL-2B + LoRA · 14 บล็อก · 19 ขั้น) · Next.js + RabbitMQ + GPU บน Vast.ai · Playwright Test · สกิล `agent-team-delivery` เวอร์ชัน 1 |
| [04_Homework](04_Homework/README.md) | การบ้านกลุ่ม: เทรนโมเดล สร้าง และทดสอบระบบ AI บน GPU ด้วย Agent Team (โจทย์ 10 ข้อ กลุ่มละ 1 ข้อ) | เว็บใน Docker + RabbitMQ + GPU Worker 2 ตัว · ทุกข้อ Fine-tune โมเดลเองบน GPU ที่เช่า · Dataset สาธารณะ มีภาพตัวอย่างข้อมูลจริงทุกข้อ · เกณฑ์คะแนน 100 คะแนนต่อข้อ |

บทเรื่อง Reverse Engineer ANYTHING และการปรับสกิลอัตโนมัติ (Skill Optimizer · WikiSkill · EvoSkill v2) อยู่ที่ [Week 04](../04_week04/README.md)
