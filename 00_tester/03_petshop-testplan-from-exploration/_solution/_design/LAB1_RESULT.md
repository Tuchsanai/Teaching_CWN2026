# LAB 1 RESULT · เปิดเว็บด้วย Docker

> ถ่ายทำ 2026-10-10 (agent S1 จำลองผู้เรียน) · เวลาที่ใช้ ≈ 1 นาที (build 15 วินาที เพราะมี cache · healthy หลัง start ≈ 6 วินาที)
> หมายเหตุ: ในเครื่องที่ยังไม่เคย build (ไม่มี cache) คาดว่าใช้ 1–3 นาทีสำหรับ `npm ci` + `next build`

## คำตอบในแชทที่ผู้เรียนจะได้รับ

เปิดเว็บเรียบร้อยแล้วครับ ✅

| ขั้น | คำสั่ง | ผล |
|---|---|---|
| 1. build + run | `docker compose up -d --build` (ในโฟลเดอร์ `petshop`) | Image `pawpantry:latest` Built · Container `petshop` Started |
| 2. รอสถานะ | `docker compose ps` | `Up … (healthy)` · พอร์ต `0.0.0.0:3000->3000/tcp` |
| 3. เช็กสุขภาพ | `curl http://localhost:3000/api/health` | `{"ok":true}` |
| 4. เปิดเว็บ | http://localhost:3000 | หน้าแรก "PawPantry — อาหารแมวและสุนัขคัดพิเศษ" แสดงปกติ |

```text
NAME      IMAGE              COMMAND                  SERVICE   CREATED         STATUS                   PORTS
petshop   pawpantry:latest   "docker-entrypoint.s…"   petshop   7 seconds ago   Up 7 seconds (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp

{"ok":true}
```

📝 จดไว้ใช้ทีหลัง (Entry criteria หัวข้อ 6): **"เว็บพร้อมทดสอบเมื่อ container `petshop` เป็น healthy และ `/api/health` ตอบ `{"ok":true}`"**
ผมไม่ได้เปิดอ่านไฟล์โค้ดในโฟลเดอร์ `petshop` (อ่านแค่ README / docker-compose.yml เพื่อรู้วิธีเปิดเว็บ)

## ไฟล์ที่ได้
- ไม่มีไฟล์ใหม่ในโฟลเดอร์ผู้เรียน (ได้เว็บที่ localhost:3000)
- ภาพ: `_solution/_design/shots/lab1-docker.png` (จำลองหน้าต่าง terminal: compose up → ps healthy → /api/health)

## ข้อสังเกตสำหรับ README
- ✅ ผลจริง: compose สร้าง container ชื่อ `petshop` ทับตัวเดิม (log: `Container petshop Recreate`) · healthy ภายใน ~6 วินาที · `BUG_MODE=0` (เช็กด้วย `docker exec petshop printenv BUG_MODE` → `0`), `ALLOW_TEST_RESET=1`
- 👀 สังเกต: Dockerfile มี `HEALTHCHECK` (wget `/api/health` ทุก 10 วินาที) — นี่คือที่มาของคำว่า healthy · ถ้า `docker compose ps` ยังขึ้น `(health: starting)` ให้รอสักครู่
- 👀 ถ้าเครื่องผู้เรียนเคยรันบท 02 ไว้ (container ชื่อ `petshop` เดียวกัน) compose ของบท 03 จะ recreate แทน — ไม่ต้องลบเอง แต่ถ้าพอร์ต 3000 ถูกโปรแกรมอื่นใช้อยู่จะ error
- 👀 HTML ของเว็บมี `data-bug-mode="0"` ที่ `<html>` — ผู้เรียนอาจเห็นใน DOM ระหว่างสำรวจ (ผู้สอนอาจอยากซ่อนก่อน LAB 8 เพราะเป็นใบ้ว่ามีโหมดบั๊ก)
- ไม่พบปัญหา
