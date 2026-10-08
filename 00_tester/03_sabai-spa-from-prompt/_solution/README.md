# เฉลย · LAB 006-2 สบายใจ สปา (สำหรับผู้สอน)

ผลจากการรันพรอมต์ทุก LAB จริงใน [`../README.md`](../README.md) (8 ต.ค. 2569)
นักศึกษาเริ่มจากโฟลเดอร์ที่มีแค่ `README.md`, `img/`, `assets/` แล้วจะได้ไฟล์แบบนี้

| LAB | ไฟล์ / โฟลเดอร์ |
|---|---|
| 1 | `USER-STORIES.md` (34 US) |
| 2 | `REQUIREMENTS.md` (FR 31 · BR 25 · NFR 15) |
| 3 | `BUILD-PROMPT.md` (113 บรรทัด) |
| 4 | `spa/` เว็บ Next.js + PostgreSQL · `spa/SPEC.md` · `spa/BUGS.md` (เฉลยบั๊ก) |
| 5 | `screenshots/` (16 ภาพ) |
| 6 | `TEST-PLAN.md` (33 TC) |
| 7–8 | `e2e/` Playwright + `CLAUDE.md` · ผลโหมดปกติ: `_design/lab8-normal/test-report/` |
| 9 | ผลโหมดบั๊ก: `e2e/test-report/TEST-REPORT-bugmode.md` + `e2e/test-report/bugmode/` |

`_design/` = งานออกแบบของทีม multi-agent (BRIEF, แผนของ yolo1–3, พรอมต์ฉบับจริง `PROMPTS.md`, รีวิว, สคริปต์สร้างรูป)

## เปิดเว็บเฉลย (PowerShell)

```powershell
cd spa
docker compose up -d --build
```

แล้วรัน test ใน `e2e/` ด้วย `npm install` → `npx playwright test` (ดู `CLAUDE.md`)
