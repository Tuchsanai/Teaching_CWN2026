# แชทบอทร้าน "สบายใจ นวดแผนไทย"

หน้าแชท + หน้ารายการจอง (Next.js) กับฐานข้อมูล PostgreSQL รันด้วย `docker compose`
บอทอ่านข้อมูลร้านจากฐานข้อมูล แล้วส่งไปถาม LLM แบบ OpenAI-compatible (ตั้งค่าใน `.env`)

## เริ่มใช้งานกับ LLM จริง

```bash
cp .env.example .env
# แก้ 3 บรรทัดใน .env: LLM_BASE_URL, LLM_MODEL, LLM_API_KEY (ไม่ใส่เครื่องหมายคำพูด ไม่เขียน comment ต่อท้ายค่า)
docker compose up -d --build
```

เปิด http://localhost:3300 (หน้าแชท) และ http://localhost:3300/bookings (รายการจอง)

## เริ่มใช้งานแบบ mock (ไม่ต้องมี LLM)

```bash
docker compose --profile mock up -d --build
```

ไม่ต้องมี `.env` — ค่าเริ่มต้นชี้ไปที่ `mock-llm` ซึ่งตอบตามคำสำคัญและไม่มีความจำ ใช้ตรวจว่าระบบทำงานครบเท่านั้น

## ทดสอบ

```bash
bash ../e2e/run-all.sh
```

รัน 26 เคส ได้ GIF ทุกเคสและรายงานที่ `../e2e/out/TEST_REPORT.md` (รายละเอียดใน `../e2e/README.md`)

## ปิด

```bash
docker compose --profile mock down        # ปิด (ข้อมูลยังอยู่)
docker compose --profile mock down -v     # ปิดและลบข้อมูล (จำเป็นเมื่อแก้ db/init.sql)
```

แก้ `.env` แล้วให้รัน `docker compose up -d` อีกครั้งเพื่อให้เว็บอ่านค่าใหม่
