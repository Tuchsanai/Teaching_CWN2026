# ทดสอบแชทบอทอัตโนมัติด้วย Playwright (E2E)

ต้องเปิดเว็บแชทบอทไว้ก่อน (http://localhost:3300 จากโฟลเดอร์ `frontend`) แล้วเปิด Git Bash ในโฟลเดอร์ `e2e` นี้

## 1) ติดตั้ง (ครั้งแรกครั้งเดียว)

```bash
npm install
npx playwright install chromium
```

## 2) รันเทสต์ทั้ง 7 เคส

```bash
npx playwright test
```

อยากเห็นเบราว์เซอร์ทำงานจริง ๆ ใส่ `--headed` · ดูรายงาน: `npx playwright show-report`
ถ้าเว็บอยู่ที่อื่น: `BASE_URL=http://localhost:3300 npx playwright test`

| เคส | สิ่งที่ทดสอบ |
|---|---|
| 1 | ทักทาย + ถามเวลาเปิดปิด |
| 2 | กดปุ่ม "ดูราคา" |
| 3 | ขอคำแนะนำนวดแก้ปวดหลัง (ออฟฟิศซินโดรม) |
| 4 | ถามโปรโมชั่น / ส่วนลดนักศึกษา |
| 5 | จองคิวทีละขั้น → การ์ดจองสำเร็จ → หน้า `/bookings` มีแถวใหม่ (จาก PostgreSQL) |
| 6 | ถามนอกเรื่อง (สูตรอาหาร) → บอทตอบสุภาพแล้ววกกลับเรื่องร้าน |
| 7 | ลูกค้าพิมพ์ภาษาอังกฤษ |

## 3) แปลงวิดีโอเป็น GIF + MP4

```bash
node make-media.mjs
```

ไฟล์จะไปอยู่ที่ `01_VastAi_Skill/image/ex2/` (ต้องมี ffmpeg — ถ้ายังไม่มี: `winget install Gyan.FFmpeg` แล้วเปิด Git Bash ใหม่)

## 4) (ถ้าต้องการ) ล้างข้อมูลก่อนรันใหม่ — รันในโฟลเดอร์ `frontend`

```bash
docker compose exec db psql -U massage -d massage_shop -c "TRUNCATE bookings, chat_messages RESTART IDENTITY;"
```
