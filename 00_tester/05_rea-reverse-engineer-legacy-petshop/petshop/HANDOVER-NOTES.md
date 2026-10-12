# บันทึกส่งมอบ PawPantry (ทีมเดิม)

- Stack: Next.js App Router + TypeScript · ไม่มีฐานข้อมูล ข้อมูลอยู่ใน memory ของ server · ตะกร้าและรายการโปรดเก็บใน localStorage
- รัน: `docker compose up -d --build` ในโฟลเดอร์ `petshop` แล้วเปิด http://localhost:4000
- ทุกหน้าดึงรายการสินค้าผ่าน `GET /api/products` ถ้าจะแก้ข้อมูลสินค้าให้ดูที่ API ก่อน
- คูปองที่ใช้อยู่: PAW10 ลด 10% · FREESHIP · NEWCAT50 · SUMMER20 ลด 20% ใช้ได้ถึงสิ้นปี
- บัญชีทดสอบและข้อมูลร้าน: `../TEST-DATA.md`
- ชุดเทสต์ regression อยู่ `../e2e-legacy` ผ่านครบทุกข้อก่อน deploy รอบล่าสุด
- งานค้าง: ไม่มี (tracker เดิมปิดไปแล้ว)
