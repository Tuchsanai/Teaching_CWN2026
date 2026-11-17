# สมุดรายจ่ายจากใบเสร็จ (Next.js + PostgreSQL)

- เปิดทั้งเว็บและฐานข้อมูลด้วยคำสั่งเดียวในโฟลเดอร์นี้: `docker compose up -d --build` แล้วเข้า `http://localhost:3404`
- เว็บต่อ AI server ผ่านไฟล์ `receipt.env` ในโฟลเดอร์นี้ (4 บรรทัด: `RECEIPT_BASE_URL` `RECEIPT_API_KEY` `RECEIPT_MODEL_BASE` `RECEIPT_MODEL_FT` · ดูตัวอย่างใน `receipt.env.example`) ขั้นเปิด AI server ใน `../RECIPE.md` เป็นผู้เขียนไฟล์นี้
- เปลี่ยน AI server: แก้ `receipt.env` แล้วสั่ง `docker compose up -d` อีกครั้ง · แถบสถานะใต้ปุ่ม “อ่านใบเสร็จ” ต้องขึ้น `AI server พร้อม`
- ปิดและลบข้อมูล: `docker compose down -v`
- ไฟล์ `receipt.env` มี API key จึงไม่อยู่ใน Git (ดู `.gitignore`)
