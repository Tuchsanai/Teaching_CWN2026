---
name: mdevtool
description: เตรียม (สร้างใหม่) container `multi-account-devtool` จาก image `tuchsanai/multi-account-devtool:2569_1` — ลบตัวเก่า, เลือก port, ตรวจ .env, รัน, sync local skill, ตรวจ skill/docker/Vast/บัญชีที่ล็อกอิน แล้วสรุปภาษาไทย ใช้เมื่อผู้ใช้สั่ง "เตรียม/สร้าง/รีสตาร์ท container multi-account-devtool" หรือ /mdevtool
---

# เตรียม container `multi-account-devtool`

Image: `tuchsanai/multi-account-devtool:2569_1`

## กฎ (ห้ามละเมิด)
- **ห้ามโชว์ค่าใน .env** — บอกได้แค่ชื่อตัวแปร (อ่านไฟล์ด้วยสคริปต์ที่พิมพ์เฉพาะชื่อ/สถานะ ห้าม `cat`)
- **ห้ามลบ volume `ai-accounts`** (เก็บการล็อกอินทุกบัญชี) — ห้าม `docker volume rm`, `prune --volumes`
- **ห้ามล็อกอินแทนผู้ใช้** และไม่ต้องติดตั้งอะไรเพิ่ม

## ขั้นตอน

### 1. ลบตัวเก่า + เลือก port
- `docker rm -f multi-account-devtool`
- SSH_PORT = 2223, JUPYTER_PORT = 8886 — ถ้าชน ใช้ port ว่างถัดไป

### 2. เลือก ENV_FILE (ตามลำดับ เจอตัวแรกใช้เลย)
1. `C:/Users/oishi/Documents/GitHub/DGX_2024/.env`
2. `.env` ในโฟลเดอร์ปัจจุบัน
3. `.env_example` ในโฟลเดอร์ปัจจุบัน + ⚠️ ให้ copy เป็น `.env`
- ไม่มีเลย → ตัด `--env-file` ออก + ⚠️

แล้ว ⚠️ บอก **ชื่อตัวแปร** ที่:
- ค่าว่าง / ยังเป็นค่าตัวอย่าง
- ค่าครอบด้วย `"` หรือ `'` (docker `--env-file` เก็บ quote ไว้ในค่า)
- ชื่อซ้ำ

### 3. รัน แล้วรอจน `http://localhost:<JUPYTER_PORT>/lab` ตอบ 200
- docker.sock → container ที่ skill สร้างจะอยู่บน Docker ของเครื่องผู้ใช้ · port ผูก `127.0.0.1` เท่านั้น
- บรรทัด `-v LOCAL_SKILLS_DIR` ใส่เฉพาะเมื่อค่า `LOCAL_SKILLS_DIR` ใน ENV_FILE ชี้ไปโฟลเดอร์ที่มีอยู่จริง ไม่งั้นตัดออก (ค่ามีแต่ไม่พบโฟลเดอร์ → ⚠️)
- บรรทัด `-v WORKSPACE_DIR` (map โฟลเดอร์ local → `/workspace`) ใส่เฉพาะเมื่อค่า `WORKSPACE_DIR` ใน ENV_FILE ไม่ว่างและชี้ไปโฟลเดอร์ที่มีอยู่จริง — ไม่มีตัวแปร/ค่าว่าง → ตัดออก ไม่ต้อง map (ค่ามีแต่ไม่พบโฟลเดอร์ → ⚠️)

```bash
docker run -dit --name multi-account-devtool --hostname multi-account-devtool --privileged \
  -p 127.0.0.1:<SSH_PORT>:22 -p 127.0.0.1:<JUPYTER_PORT>:8888 --env-file "<ENV_FILE>" \
  -v ai-accounts:/root/ai-accounts \
  -v //var/run/docker.sock:/var/run/host-docker.sock -e DOCKER_HOST=unix:///var/run/host-docker.sock \
  -v "<LOCAL_SKILLS_DIR>:/opt/local-skills:ro" \
  -v "<WORKSPACE_DIR>:/workspace" \
  tuchsanai/multi-account-devtool:2569_1
```

### 4. sync local skill + ตรวจ (รันเสมอ ห้ามข้าม ห้ามแก้สคริปต์)
สคริปต์อยู่ที่ [check.sh](check.sh) ในโฟลเดอร์ skill นี้ — ส่งเข้า container ทาง stdin ตามเดิม (ใช้ Bash tool):

```bash
docker exec -i multi-account-devtool bash -l < .claude/skills/mdevtool/check.sh
```

⚠️ ถ้าเจอ:
- `WARN` (LOCAL_SKILLS_DIR ไม่มี skill ที่มี SKILL.md)
- `MISSING` → "ยังไม่ได้ติดตั้ง skill: <รายชื่อ>"
- `docker:` ไม่ใช่ Docker ของเครื่องผู้ใช้ (เทียบกับ `docker info -f '{{.Name}}'` บน host)
- `VAST FAIL` (VAST_API_KEY ใช้ไม่ได้)

### 5. สรุปภาษาไทย ตามลำดับนี้
1. ⚠️ ทั้งหมดไว้บนสุด
2. port SSH / Jupyter + URL (`http://localhost:<JUPYTER_PORT>/lab`)
3. env file ที่ใช้ + ชื่อตัวแปร (ไม่มีค่า) + `/workspace` map จากโฟลเดอร์ไหน (หรือ "ไม่ได้ map")
4. local skill ที่ SYNCED / SKIP
5. docker (ชื่อ host ที่ต่ออยู่)
6. ผลตรวจ skill
7. บัญชีที่ LOGIN แล้ว — บัญชีที่เหลือ: บอกให้ผู้ใช้รัน `yoloN` / `cyoloN` ใน terminal ของ container เพื่อล็อกอินเอง
