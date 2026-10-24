---
name: maccount
description: เตรียม container `multi-account-devtool` จาก image `tuchsanai/multi-account-devtool:2569_1` ตามขั้นที่ 1 ของ LAB 03 — เช็ก image/container/port/env/local skill → rm -f ตัวเดิม → docker run → รอ JupyterLab 200 → sync local skill + ตรวจ skill → ตรวจล็อกอิน yolo1–5/cyolo1–5 แล้วสรุปภาษาไทย โหลด .env จากโฟลเดอร์ปัจจุบันก่อน ถ้าไม่มีใช้ path env ที่ตั้งไว้ในสกิล ไม่เจอก็ไม่โหลด (path env แยก Windows/macOS ตั้งไว้บนสุดของสกิล ใช้ได้ทั้งสอง OS) ใช้เมื่อผู้ใช้สั่ง /maccount หรือ "เตรียม/เปิด/รัน container multi-account-devtool"
---

# maccount — เตรียม container `multi-account-devtool`

## ⚙️ ตั้งค่า environment (แก้ตรงนี้ที่เดียว)
path ไฟล์ env ที่ใช้เมื่อ **ไม่พบ `.env` ในโฟลเดอร์ปัจจุบัน** — แยกตาม OS · ไฟล์ไม่มีอยู่จริง = ไม่โหลด (มี WARN) · เว้นว่าง = ไม่โหลด
(แก้แค่ค่าหลัง `=` · ไม่ต้องใส่ quote · ใช้ `/` ได้ทั้งสอง OS · ขึ้นต้นด้วย `~` ได้ · `maccount.sh` อ่านบรรทัดเหล่านี้ตรง ๆ)

```
ENV_FILE_WINDOWS=C:/Users/oishi/Documents/GitHub/DGX_2024/.env
ENV_FILE_MACOS=~/Documents/GitHub/DGX_2024/.env
ENV_FILE_LINUX=~/Documents/GitHub/DGX_2024/.env
```

- `maccount.sh` เลือกบรรทัดตาม OS เอง (`uname -s`: MINGW/MSYS/CYGWIN → Windows · Darwin → macOS · อื่น ๆ → Linux)
- override ชั่วคราวไม่ต้องแก้ไฟล์: `MACCOUNT_ENV_FILE=<path> bash ~/.claude/skills/maccount/maccount.sh`
- `LOCAL_SKILLS_DIR` ใน env file ต้องเป็น path ของเครื่องที่รันอยู่ (path Windows ใช้บน Mac ไม่ได้ → WARN ไม่พบ แล้วไม่ mount)

Image: `tuchsanai/multi-account-devtool:2569_1` · container: `multi-account-devtool` · Jupyter เริ่มที่ port 8886

## กติกา (ห้ามละเมิด)
- ห้ามลบ volume `ai-accounts` (เก็บล็อกอินทุกบัญชี): ห้าม `docker volume rm`, `prune --volumes`, `compose down -v`
- ห้ามแสดงค่าในไฟล์ env (แสดงได้แค่ชื่อตัวแปร ยกเว้น `LOCAL_SKILLS_DIR`) และห้ามแสดงเนื้อหา SKILL.md ห้าม `cat` ไฟล์ env
- ห้ามติดตั้ง Claude/Codex/skill เอง (ยกเว้นการ sync local skill ในข้อ 3 ซึ่งสคริปต์ทำให้)
- ห้ามล็อกอินแทนผู้ใช้
- คำเตือน ⚠️ ทุกข้ออยู่บนสุดของสรุป
- ให้เร็ว: เรียกสคริปต์แค่ 2 ครั้งตามด้านล่าง ห้ามแยกเช็กเอง ห้าม sleep รอเป็นหลายรอบ

## ไฟล์ env ที่โหลด (ลำดับ)
1. `.env` ในโฟลเดอร์ปัจจุบัน
2. path ที่ตั้งไว้ในสกิล: `ENV_FILE_WINDOWS` / `ENV_FILE_MACOS` / `ENV_FILE_LINUX` (ตาม OS) ในหัวข้อ "⚙️ ตั้งค่า environment" ด้านบน
   หรือ override ชั่วคราวด้วย `MACCOUNT_ENV_FILE=<path>`
3. `.env_example` / `.env.example` ในโฟลเดอร์ปัจจุบัน (มีคำเตือน)
4. ไม่เจอเลย → ไม่ใส่ `--env-file`

`LOCAL_SKILLS_DIR` ในไฟล์ env: path แบบ relative นับจากโฟลเดอร์ของไฟล์ env · ว่างหรือเป็นค่าตัวอย่าง → ไม่ mount ·
มี `SKILL.md` ตรงตัว → mount เป็น `/opt/local-skills/<ชื่อ>:ro` · เป็นโฟลเดอร์รวม skill → mount `/opt/local-skills:ro`

## OS ที่รองรับ
- **Windows**: Docker Desktop + Git Bash (Bash tool ของ Claude Code ใช้ Git Bash อยู่แล้ว) · ห้ามเรียกสคริปต์ด้วย PowerShell
- **macOS**: Docker Desktop (หรือ OrbStack/Colima) + bash ที่ติดเครื่อง (3.2 ก็ได้)
- บน host ใช้แค่ `docker`, `bash`, `curl`, `netstat`/`ss` · การตรวจ skill/ล็อกอินรันใน container จึงได้ผลเหมือนกันทุก OS

## ขั้นตอน (Bash tool · Windows ใช้ Git Bash, macOS/Linux ใช้ bash · สคริปต์ตั้ง `MSYS_NO_PATHCONV=1` เอง)

รันจากโฟลเดอร์ปัจจุบันของผู้ใช้ (ให้หา `.env` ถูกที่)

**ข้อ 1–4 · คำสั่งเดียวจบ** (ใช้ตัวเดิม ~1.6 วิ · สร้างใหม่ ~3.5 วิ · timeout 600000 ms)
```bash
bash ~/.claude/skills/maccount/maccount.sh
```
ทำ: เช็ก image/container/port/env → **ใช้ container ตัวเดิมถ้าค่าไม่เปลี่ยน** ไม่งั้น `rm -f` ตัวเดิม (volume อยู่ครบ) → `docker run` → `docker exec` ครั้งเดียว
(รอ installer → ตรวจล็อกอิน 10 บัญชีขนานกัน + sync/ตรวจ skill) → เช็ก Jupyter 200 ตอนท้ายสุด
- ใช้ตัวเดิม: container มีป้าย `maccount.fp` = ลายนิ้วมือของ image ID + path/เนื้อหาไฟล์ env + mount local skill
  ตรงกับรอบนี้ → `REUSE` (หยุดอยู่ → `docker start` → `STARTED`) · ไม่ตรง/ไม่มีป้าย → `rm -f` แล้ว `CREATED`
  · ยัง sync skill และตรวจล็อกอินทุกครั้ง · **ผู้ใช้สั่ง "สร้างใหม่ / recreate / รีสตาร์ท"** → เพิ่ม `--recreate`
- ตรวจล็อกอินขนาน: จำนวน worker = จำนวน core ของ CPU แต่อยู่ในช่วง **2–4** เสมอ แสดงเป็น `LOGIN_WORKERS`
  · กำหนดเองได้ด้วย `MACCOUNT_JOBS=<n> bash ~/.claude/skills/maccount/maccount.sh`
- **exit 10 + บรรทัด `NOTICE ...`** (ยังไม่มี image, เริ่ม pull เบื้องหลังแล้ว) → แจ้งผู้ใช้ข้อความนั้นทันที
  แล้วรัน `bash ~/.claude/skills/maccount/maccount.sh --wait-pull` (run_in_background) ซึ่งรอ pull เสร็จแล้วทำต่อจนจบ
- `FAIL ...` → หยุดแล้วรายงาน error ตามจริง ห้ามวนรอต่อ
- port ชนหรือ OS สงวนไว้ → สคริปต์ `rm -f` แล้วลอง port ว่างถัดไปเอง (`RETRY`)
- บรรทัด `TIME ...` = เวลาสะสมแต่ละช่วง ไว้ดูคอขวด ไม่ต้องใส่ในสรุป
- ดูข้อ 1 อย่างเดียวโดยไม่สร้าง container: `bash ~/.claude/skills/maccount/maccount.sh check`

## ข้อ 5 · สรุปภาษาไทย ตามลำดับนี้
1. **⚠️ คำเตือน** (ไม่มีให้เขียน "ไม่มี") รวมจาก:
   - `WARN ...` จากสคริปต์ (env / `LOCAL_SKILLS_DIR` / Jupyter)
   - `EMPTY` / `PLACEHOLDER` เมื่อใช้ `.env_example` → บอกชื่อตัวแปรที่ว่างหรือเป็นค่าตัวอย่าง
   - `LOCAL_SKILLS_MOUNTED yes` แต่ `TOTAL 0` → "LOCAL_SKILLS_DIR ไม่มีโฟลเดอร์ skill ที่มี SKILL.md"
   - มี `MISSING` → "ยังไม่ได้ติดตั้ง skill — กรุณาติดตั้ง: <รายชื่อที่ขาด>"
   - ไม่มี `LOGGED_IN` เลย → "ยังไม่มีบัญชีไหนล็อกอิน — กรุณาล็อกอินอย่างน้อย 1 บัญชีใน Terminal ของ JupyterLab:
     yolo1 (เลือก Claude account with subscription แล้ว /exit) หรือ cyolo1 login --device-auth"
2. **Environment variable — เจอหรือไม่** (สำคัญ)
   - เจอ ✅ / ไม่เจอ ❌ + ไฟล์ที่ใช้ และมาจากไหน (`.env` ในโฟลเดอร์ปัจจุบัน / path ที่ตั้งในสกิล / ไฟล์ตัวอย่าง / ไม่มี)
   - จำนวนตัวแปร + ชื่อตัวแปร (`VARS`) ห้ามแสดงค่า
3. **Skill — เจอหรือไม่** (สำคัญ)
   - local skill: path ที่ mount หรือ "ไม่ได้กำหนด" + รายการ `SYNCED` / `SKIP`
   - ตาราง `skill | .Claude | .Codex` (✅ OK / ❌ MISSING) ทุก skill ที่ตรวจ
4. **บัญชีที่ล็อกอิน** (สำคัญ) — บรรทัดสรุป "ล็อกอินแล้ว N/10: <รายชื่อ>" แล้วตาราง `บัญชี | ล็อกอินแล้ว?` ของ yolo1–5 และ cyolo1–5
5. เข้า shell: `docker exec -it multi-account-devtool bash` (เริ่มที่ /workspace)

ไม่ต้องแสดง URL ของ JupyterLab — สคริปต์ไม่รอ Jupyter ก่อน แต่ทำข้อ 3–4 ทันทีหลัง installer เสร็จ
แล้วค่อยเช็ก Jupyter 200 ตอนท้ายสุด (ถ้าไม่ตอบจะเป็น `WARN` อยู่ในคำเตือน)
