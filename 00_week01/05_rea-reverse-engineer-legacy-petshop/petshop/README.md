# PawPantry — หน้าร้านออนไลน์

Next.js (App Router) + TypeScript · ข้อมูลร้านอยู่ในหน่วยความจำของ server (รีสตาร์ต container = ข้อมูลกลับค่าเริ่มต้น)

## เปิดเว็บ
```powershell
docker compose up -d --build     # http://localhost:4000
docker compose down              # ปิด
```

## ล้างข้อมูลทดสอบ
```powershell
Invoke-RestMethod -Method Post http://localhost:4000/api/test/reset
```
ใช้ได้เพราะ `ALLOW_TEST_RESET=1` ใน `docker-compose.yml`

## บัญชีและคูปองทดสอบ
ดู [`../TEST-DATA.md`](../TEST-DATA.md) · ชุดเทสต์ regression: `../e2e-legacy/README-LEGACY.md`
