# Teaching CWN 2026

## เปิด container `multi-account-devtool`

💬 วางพรอมต์นี้ใน **Claude Code ใน VS Code บนเครื่องตัวเอง** (Docker Desktop ต้อง Engine running) → กดส่ง → อนุญาตคำสั่ง `docker` เมื่อถูกถาม

```text

เตรียม container `multi-account-devtool`:

1. ถ้ามี container `multi-account-devtool` อยู่แล้ว ให้ลบด้วย `docker rm -f multi-account-devtool`
   (ห้ามลบ volume `ai-accounts` เพราะเก็บการล็อกอินของทุกบัญชีไว้)

2. ตรวจ port <SSH_PORT>=2223 และ <JUPYTER_PORT>=8886 ถ้าชน ให้ใช้ port ว่างถัดไป

3. หาไฟล์ env ในโฟลเดอร์ปัจจุบัน: ใช้ `.env` ก่อน ถ้าไม่มีใช้ `.env_example` (หรือ `.env.example`)
   แล้วเติม `--env-file <path เต็ม>` ในข้อ 4 (ห้ามแสดงค่าในไฟล์ แสดงได้เฉพาะชื่อตัวแปร)
   - ถ้าใช้ไฟล์ example ให้เตือนว่า "⚠️ ไม่พบ .env — ใช้ <ชื่อไฟล์> แทน ค่าอาจเป็นค่าตัวอย่าง
     กรุณา copy เป็น .env แล้วใส่ค่าจริง" พร้อมบอกชื่อตัวแปรที่ค่าว่างหรือดูเป็นค่าตัวอย่าง
   - ถ้าไม่พบทั้งสองไฟล์ ให้ตัด `--env-file` ออกแล้วรันต่อ และเตือนว่า
     "⚠️ ไม่พบ .env หรือ .env_example — container จะไม่มี environment variable กรุณาสร้าง .env แล้วรันใหม่"

4. หาโฟลเดอร์ key SSH `Devtool_SSH/` (key สำเร็จรูปของ lab) ในโฟลเดอร์ปัจจุบันเท่านั้น
   (ไม่ต้องค้นในโฟลเดอร์ย่อย) และต้องมีครบทั้ง 2 ไฟล์
     Devtool_SSH/
     ├── devtoolSSH       ← private key (ใช้กับ ssh -i)
     └── devtoolSSH.pub   ← public key (container ใส่ใน authorized_keys ให้อัตโนมัติตอน start)
   - ถ้าเจอ ให้แทน <SSH_KEY_DIR> ในข้อ 5 และ 7 ด้วย path เต็มของโฟลเดอร์นั้น
     (ห้ามแสดงเนื้อหา private key)
   - ถ้าไม่เจอ (หรือไฟล์ไม่ครบ) = ไม่ใช้ key ให้ตัดบรรทัด `-v ...:/etc/devtools/ssh:ro` ออกแล้วรันต่อ และเตือนว่า
     "⚠️ ไม่พบโฟลเดอร์ Devtool_SSH — SSH ใช้ได้เฉพาะ password (passwd) ยังใช้ key ไม่ได้"

5. รัน:

docker run -dit --name multi-account-devtool --hostname multi-account-devtool --privileged \
  -p <SSH_PORT>:22 -p <JUPYTER_PORT>:8888 \
  --env-file <ENV_FILE> \
  -v "<SSH_KEY_DIR>:/etc/devtools/ssh:ro" \
  -v ai-accounts:/root/ai-accounts \
  tuchsanai/multi-account-devtool:2569_1

6. รอจน `docker logs multi-account-devtool` มีบรรทัดที่มีข้อความ `jupyter lab :8888`

7. ถ้า mount `Devtool_SSH` ในข้อ 4 ให้ตรวจ key (ข้ามได้ถ้าไม่เจอโฟลเดอร์):
   - `docker logs multi-account-devtool` ต้องมีบรรทัด `SSH key login enabled`
   - ทดสอบ login ด้วย key จริง (ไม่ใช้ password):

ssh -i "<SSH_KEY_DIR>/devtoolSSH" -p <SSH_PORT> -o BatchMode=yes \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost "echo SSH_KEY_OK"

     (บน Windows PowerShell ใช้ `UserKnownHostsFile=NUL`)
   - ถ้าได้ `SSH_KEY_OK` = ใช้ key ได้ ถ้าไม่ได้ ให้เตือนว่า
     "⚠️ SSH ด้วย key ไม่สำเร็จ — ใช้ password (passwd) ไปก่อน" พร้อมสาเหตุสั้น ๆ
     ถ้าสาเหตุคือ permission ของไฟล์ private key กว้างเกินไป (UNPROTECTED PRIVATE KEY FILE)
     ให้บอกคำสั่งแก้ให้ฉัน (Windows: `icacls`, macOS/Linux: `chmod 600`) โดยไม่ต้องรันเอง

8. ตรวจ skill `vastai` `yolo` `cyolo` (สำคัญ ห้ามข้าม):

docker exec multi-account-devtool bash -lc \
'B=$HOME/ai-accounts; for t in .Claude .Codex; do for s in vastai yolo cyolo; do [ -d $B/$t/shared/skills/$s ] && echo "$t/$s OK" || echo "$t/$s MISSING"; done; done'

   ถ้ามี MISSING แม้แต่ตัวเดียว ให้แจ้งเตือนฉันเป็นภาษาไทยอย่างชัดเจนว่า
   "⚠️ ยังไม่ได้ติดตั้ง skill — กรุณาติดตั้ง skill ต่อไปนี้ก่อนใช้งาน: <รายชื่อที่ขาด>"
   ห้ามแสดงรหัสหรือเนื้อหาใน SKILL.md
   และห้ามติดตั้ง skill เอง ให้แจ้งเตือนอย่างเดียว

9. ไม่ต้องติดตั้ง Claude Code / Codex เพิ่ม (มีใน image แล้ว) ห้ามล็อกอินแทนฉัน
   สรุปผลเป็นภาษาไทย โดยเรียงดังนี้:
   - ถ้ามีคำเตือน (ใช้ไฟล์ example / ไม่พบไฟล์ env / ไม่พบ Devtool_SSH / SSH key ไม่สำเร็จ / skill ขาด)
     ให้แสดงคำเตือนไว้บนสุดของสรุป ก่อนข้อมูลอื่น
   - port ที่ใช้ (SSH / Jupyter)
   - URL ของ JupyterLab
   - สถานะ SSH key (ใช้ได้ / ไม่พบ Devtool_SSH / ไม่สำเร็จ) พร้อมคำสั่ง
     `ssh -i "<SSH_KEY_DIR>/devtoolSSH" -p <SSH_PORT> root@localhost`
   - สถานะไฟล์ env (ใช้ .env / ใช้ .env_example แทน / ไม่พบ) พร้อมรายชื่อตัวแปรที่โหลด (เฉพาะชื่อ)
   - ผลตรวจ skill (มีครบ / ขาดอะไร)

```

| ตัวแปร | ค่าเริ่มต้น | ใช้ทำอะไร |
|---|---|---|
| `<SSH_PORT>` | `2223` | `ssh -i Devtool_SSH/devtoolSSH root@localhost -p <SSH_PORT>` (key) หรือ `ssh root@localhost -p <SSH_PORT>` (password `passwd`) |
| `<SSH_KEY_DIR>` | `./Devtool_SSH` | โฟลเดอร์ key สำเร็จรูปของ lab → mount เป็น `/etc/devtools/ssh` (อ่านอย่างเดียว) ให้ container ใส่ public key ใน `authorized_keys` |
| `<JUPYTER_PORT>` | `8886` | http://localhost:<JUPYTER_PORT>/lab (ไม่มีรหัสผ่าน) |

