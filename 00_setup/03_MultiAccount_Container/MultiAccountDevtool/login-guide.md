# login-guide — ล็อกอินทีละบัญชี และตรวจ skill / MCP หลังล็อกอิน

เปิด terminal ใน container ได้ 3 ทาง (ใช้ได้เหมือนกัน):
- JupyterLab → File → New → Terminal (`http://localhost:<JUPYTER_PORT>/lab`)
- `ssh -i Devtool_SSH/devtoolSSH root@localhost -p <SSH_PORT>` (หรือ password `passwd`)
- `docker exec -it <ชื่อ container> bash`

ก่อนเริ่ม: `ai-accounts-setup` รันเองแล้วตอน container start ถ้าสงสัยให้รันซ้ำได้ (ไม่ทับของเดิม)

> ห้ามแชร์หน้าจอ/ข้อความที่มีโค้ดล็อกอินหรือ URL ที่มี token ให้คนอื่น
> ล็อกอินบัญชีละครั้ง credential อยู่ใน volume `ai-accounts` ไม่หายเมื่อสร้าง container ใหม่

## 1. Claude Code — yolo1 … yolo5

```bash
yolo1                 # เปิดครั้งแรก: เลือก theme → เลือก "Claude account with subscription" (หรือ Console)
                      # CLI แสดง URL → เปิดใน browser เครื่องตัวเอง → ล็อกอิน → คัดลอก code กลับมาวางใน terminal
                      # ถ้าถาม trust folder ให้ตอบ Yes  → ออกด้วย /exit
yolo1 auth status     # ต้องเห็น "loggedIn": true
```
ทำซ้ำกับ `yolo2` (และ yolo3..5 ถ้าต้องการ) — ใช้บัญชี Claude คนละบัญชีได้ แต่ละบัญชีเก็บใน `~/ai-accounts/.Claude/yoloN/`

ตรวจหลังล็อกอิน (ทำในโฟลเดอร์งาน เช่น `/workspace`):
```bash
yolo1 -p "ใช้ skill shared-check แล้วตอบรหัส"      # ต้องได้ SHARED_SKILL_OK-claude-<รหัส>
yolo2 -p "ใช้ skill shared-check แล้วตอบรหัส"      # ต้องได้รหัสเดียวกับ yolo1
grep -o 'SHARED_SKILL_OK-claude-[0-9a-f]*' ~/ai-accounts/.Claude/shared/skills/shared-check/SKILL.md   # เทียบกับไฟล์
```
MCP: เปิด `yolo1` แบบ interactive แล้วพิมพ์ `/mcp` ต้องเห็น `playwright · connected`
(`claude mcp list` จะ **ไม่** แสดง เพราะ MCP ส่งผ่าน `--mcp-config=` ตอนเปิด — เป็นพฤติกรรมปกติ)

ทดสอบ MCP ใช้งานจริง:
```bash
yolo1 -p "ใช้ playwright เปิด https://example.com แล้วบอก title ของหน้า"
```

## 2. Codex CLI — cyolo1 … cyolo5

ใน container ไม่มี browser → ใช้ device auth:
```bash
cyolo1 login --device-auth     # แสดง URL + code → เปิด URL ใน browser เครื่องตัวเอง ใส่ code → ล็อกอิน ChatGPT
cyolo1 login status            # "Logged in using ChatGPT" (แต่ไม่ได้ยืนยันว่า token ใช้งานได้จริง)
cyolo1 exec "ตอบคำว่า OK"      # ยืนยัน token ใช้ได้จริง ต้องได้คำตอบกลับ
ls -l ~/ai-accounts/.Codex/cyolo1/auth.json   # credential เป็นไฟล์ของบัญชีนี้ (ห้าม cat/แชร์ไฟล์นี้)
```
ทำซ้ำกับ `cyolo2` (และ cyolo3..5 ถ้าต้องการ)

ตรวจหลังล็อกอิน:
```bash
cyolo1 mcp list                                        # เห็น playwright  enabled (ตรวจได้ก่อนล็อกอินด้วย)
cyolo1 exec "ใช้ skill shared-check แล้วตอบรหัส"       # SHARED_SKILL_OK-codex-<รหัส>
cyolo2 exec "ใช้ skill shared-check แล้วตอบรหัส"       # รหัสเดียวกับ cyolo1
cyolo1 exec "ใช้ playwright เปิด https://example.com แล้วบอก title ของหน้า"
```
ในโหมด interactive (`cyolo1`) พิมพ์ `/mcp` เพื่อดูสถานะ MCP และ `/skills` เพื่อดูรายการ skill

## 3. ตรวจว่าบัญชีแยกกันจริง

```bash
yolo1 auth status | grep -E 'loggedIn|email' ; yolo2 auth status | grep -E 'loggedIn|email'   # คนละบัญชี
find ~/ai-accounts -maxdepth 2 -name '.credentials.json' -o -maxdepth 2 -name 'auth.json'      # 1 ไฟล์ต่อบัญชีที่ล็อกอิน ไม่มีใน shared
```
เปิด `yolo1` กับ `yolo2` (หรือ `cyolo1` กับ `cyolo2`) พร้อมกันคนละ terminal ได้ เพราะใช้ config root คนละโฟลเดอร์

## 4. เพิ่ม skill / MCP ส่วนกลางภายหลัง (ไม่ต้องรัน installer ซ้ำ)

```bash
# skill ใหม่ให้ทุกบัญชี Claude
mkdir -p ~/ai-accounts/.Claude/shared/skills/my-skill && $EDITOR ~/ai-accounts/.Claude/shared/skills/my-skill/SKILL.md
# skill ใหม่ให้ทุกบัญชี Codex (wrapper ลิงก์ให้เองตอนเปิด cyoloN ครั้งถัดไป)
mkdir -p ~/ai-accounts/.Codex/shared/skills/my-skill && $EDITOR ~/ai-accounts/.Codex/shared/skills/my-skill/SKILL.md
# MCP ใหม่: เพิ่ม entry ใน "mcpServers" ของ ~/ai-accounts/.Claude/shared/mcp/mcp.json และ/หรือ .Codex/shared/mcp/mcp.json
```
ห้ามใส่ token/API key ลงในไฟล์ใต้ `shared/`

## 5. ออกจากระบบ / ล้างบัญชี

```bash
yolo1 auth logout      # หรือ /logout ในเซสชัน
cyolo1 logout
```
`docker compose down` ไม่ลบล็อกอิน · `docker compose down -v` ลบ volume = ต้องล็อกอินใหม่ทุกบัญชี (และได้รหัส shared-check ใหม่)
