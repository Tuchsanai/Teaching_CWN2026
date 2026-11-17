# แชทบอทร้าน "สบายใจ นวดแผนไทย" 🌿

Next.js + PostgreSQL ทำงานใน Docker (เปิด Docker Desktop ไว้ก่อน แล้วใช้ Git Bash ในโฟลเดอร์นี้)

## 1) รันแบบทดสอบ (mock ไม่ต้องใช้ GPU)

```bash
cp .env.example .env
docker compose --profile mock up -d --build
```

เปิดเว็บ: http://localhost:3300 → ลองกดปุ่ม "📅 จองคิว" หรือพิมพ์

```
จอง นวดไทย ชื่อสมชาย เบอร์ 081-234-5678 วันที่ 2026-10-20 เวลา 14:00
```

## 2) ดูว่าการจองเข้า Database จริง

เปิด http://localhost:3300/bookings หรือ

```bash
docker compose exec db psql -U massage -d massage_shop -c "SELECT * FROM bookings;"
```

## 3) เปลี่ยนไปใช้ AI จริงบน Vast.ai

แก้ไฟล์ `.env` สองบรรทัดนี้ (ใส่ IP:PORT และชื่อโมเดลของเครื่อง Vast)

```
LLM_BASE_URL=http://<VAST_IP>:<VAST_PORT>
LLM_MODEL=<ชื่อโมเดล>
```

แล้วรัน

```bash
docker compose up -d --build web
```

## 4) ปิด / ล้างข้อมูล

```bash
docker compose --profile mock down        # ปิด (ข้อมูลยังอยู่)
docker compose --profile mock down -v     # ปิดและลบข้อมูลทั้งหมด
```
