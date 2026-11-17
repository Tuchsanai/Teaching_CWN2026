# เว็บตรวจความปลอดภัยหน้างาน (LAB 1)

Next.js + PostgreSQL รันบน Docker ของเครื่องนี้ เปิดที่ http://localhost:3401

| หน้า | ทำอะไร |
|---|---|
| `/` ตรวจรูป | อัปโหลดรูปหรือกดรูปตัวอย่าง → ส่งไป AI server → วาดกรอบ + สรุป "พบคนไม่สวมหมวก N คน" (ผ่าน/ไม่ผ่าน) + เวลาที่โมเดลใช้ |
| `/history` ประวัติ | ผลตรวจทุกครั้งจากตาราง `inspections` ใน PostgreSQL |
| `/api/detect` | POST รูป (`file`) → ส่งต่อไป `YOLO_BASE_URL/v1/detect` พร้อม key → บันทึกผล → คืน JSON |

## ต่อกับ AI server บน Vast.ai

1. คัดลอกไฟล์ค่าเชื่อมต่อ `yolo.env` (ขั้นเปิด AI server เขียนไว้) มาเป็นไฟล์ `.env` ในโฟลเดอร์นี้
   ```bash
   docker cp multi-account:/workspace/vastapp_lab/lab1_yolo/yolo.env .env
   ```
2. เปิดเว็บ
   ```bash
   docker compose up -d --build
   ```
3. ทดสอบจาก command line
   ```bash
   curl -s http://localhost:3401/api/health
   curl -s -F file=@public/samples/sample-1.jpg http://localhost:3401/api/detect
   ```

ไฟล์ `.env` มี 3 ค่า (ดูตัวอย่างใน `.env.example`): `YOLO_BASE_URL` `YOLO_API_KEY` `YOLO_MODEL`

## ทดสอบโดยไม่มี GPU

```bash
docker compose --profile mock up -d --build
```
ถ้าไม่มีไฟล์ `.env` เว็บจะเรียก AI server จำลอง (`mock-yolo`) ที่ตอบกรอบตัวอย่างชุดเดิมทุกรูป

## ปิดเว็บ

```bash
docker compose down        # เก็บประวัติไว้
docker compose down -v     # ลบประวัติทิ้งด้วย
```

รูปตัวอย่างใน `public/samples/` มาจาก Test Set ของ [Construction Site Safety](https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety/dataset/28) (Roboflow Universe, CC BY 4.0)
