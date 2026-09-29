# MultiAccount_Devtool — DevTools container + ระบบหลายบัญชี Claude Code / Codex CLI

image `multiaccount_devtool:2569_1` = ทุกอย่างของ base `00_Devtool_Container` (Ubuntu 24.04, Docker-in-Docker, Python, Node.js 22, JupyterLab, SSH)
**บวก** Claude Code, Codex CLI, คำสั่ง `yolo1`–`yolo5` / `cyolo1`–`cyolo5`, Playwright MCP + Chromium ส่วนกลาง และ skill `shared-check`
ติดตั้งมาใน image เลย ไม่ต้องให้ AI ตั้งค่าหลายบัญชีเองแบบในแลป `02_Setup_Multi_Account`

| หมวด | รายละเอียด |
|------|------------|
| **Base** | เหมือน `00_Devtool_Container` ทุกอย่าง (Dockerfile เขียนใหม่จาก `ubuntu:24.04` ไม่ FROM image ของ base) |
| **AI CLI** | Claude Code `2.1.284`, Codex CLI `0.159.0` (ปรับได้ด้วย `--build-arg`) |
| **บัญชี** | `yolo1`–`yolo5` → Claude Code, `cyolo1`–`cyolo5` → Codex CLI (wrapper อยู่ใน `/usr/local/bin`) |
| **MCP ส่วนกลาง** | `@playwright/mcp@0.0.83` + Chromium (chromium-1247) ใน `/opt/ms-playwright` |
| **Skill ส่วนกลาง** | `shared-check` ตอบรหัส `SHARED_SKILL_OK-<claude\|codex>-<ค่าสุ่ม>` |
| **ข้อมูลบัญชี** | `/root/ai-accounts` เป็น **volume** — credential/config/session ไม่อยู่ใน image |
| **คำสั่งตรวจ** | `ai-accounts-check` — ตรวจแบบไม่ต้องล็อกอิน พิมพ์ตาราง PASS/FAIL/SKIP |
| **Ports** | `22` SSH, `8888` JupyterLab (ตัวอย่างนี้ map เป็น `2223` / `8886` ให้ไม่ชนกับ `devtools`) |

> ⚠️ รหัสผ่าน `passwd` และ key SSH เป็นค่าสำหรับเรียนบนเครื่องตัวเองเท่านั้น และ `yoloN`/`cyoloN` รันโหมดข้ามการยืนยัน
> (`--dangerously-skip-permissions` / `--dangerously-bypass-approvals-and-sandbox`) — ใช้ใน container นี้เท่านั้น

## โครงสร้างโฟลเดอร์

```text
MultiAccount_Devtool/
├── Dockerfile               ← ส่วนที่ 1 = base ทั้งหมด, ส่วนที่ 2 = ระบบหลายบัญชี
├── start.sh                 ← entrypoint: sshd + dockerd + ai-accounts-init + jupyter lab
├── jupyter_overrides.json   ← ค่า default ของ JupyterLab UI (เหมือน base)
├── docker-compose.yml       ← ทางเลือก: build + run คำสั่งเดียว
├── .dockerignore / .gitignore
├── scripts/                 ← COPY เข้า image
│   ├── ai-accounts.conf     → /etc/ai-accounts/ai-accounts.conf   (BASE_PATH แก้ที่นี่ที่เดียว)
│   ├── ai-account           → /usr/local/bin/ai-account  (+ symlink yolo1..5, cyolo1..5)
│   ├── ai-accounts-init     → /usr/local/bin/  สร้างโฟลเดอร์บัญชี + shared ใน volume (รันซ้ำได้)
│   ├── ai-accounts-check    → /usr/local/bin/  ตรวจแบบไม่ต้องล็อกอิน
│   ├── mcp_json_to_codex.py → /usr/local/lib/ai-accounts/  แปลง mcp.json เป็น -c mcp_servers.<name>={...}
│   └── mcp_stdio_probe.py   → /usr/local/lib/ai-accounts/  คุยกับ Playwright MCP ผ่าน stdio จริง
├── verify-prompt.txt        ← พรอมต์ตรวจหลังล็อกอิน (skill + Playwright MCP + screenshot)
├── build-report.md          ← ผล build/test จริง
└── readme.md
```

ใน container — **ใน image** (เหมือนกันทุกเครื่อง ไม่มีข้อมูลบัญชี):

```text
/usr/bin/claude, /usr/bin/codex, /usr/bin/playwright-mcp     ← npm -g
/opt/ms-playwright/chromium-1247, chromium_headless_shell-1247
/usr/local/bin/yolo1..5, cyolo1..5 -> ai-account
```

ใน **volume `ai-accounts`** → `/root/ai-accounts` (สร้างตอน container start ครั้งแรก ไม่เขียนทับของเดิม):

```text
/root/ai-accounts/
├── .Claude/
│   ├── shared/
│   │   ├── skills/shared-check/SKILL.md     ← รหัสสุ่มของ Claude (สุ่มครั้งเดียว)
│   │   └── mcp/mcp.json                     ← {"mcpServers":{"playwright":{...}}}
│   ├── yolo1/                               ← CLAUDE_CONFIG_DIR ของ yolo1 (.claude.json, .credentials.json หลังล็อกอิน)
│   │   └── skills -> ../shared/skills       ← ลิงก์ทั้งโฟลเดอร์
│   └── yolo2 … yolo5/
├── .Codex/
│   ├── shared/
│   │   ├── skills/shared-check/SKILL.md     ← รหัสสุ่มของ Codex
│   │   └── mcp/mcp.json
│   ├── cyolo1/                              ← CODEX_HOME ของ cyolo1 (auth.json หลังล็อกอิน)
│   │   ├── config.toml                      ← cli_auth_credentials_store = "file"
│   │   └── skills/shared-check -> /root/ai-accounts/.Codex/shared/skills/shared-check   ← ลิงก์รายตัว
│   └── cyolo2 … cyolo5/
└── playwright-output/{claude,codex}/         ← ภาพ/ไฟล์ที่ Playwright MCP บันทึก (นอก /workspace)
```

### คำสั่งสั้นทำงานอย่างไร

| คำสั่ง | ตั้ง env | รันจริง |
|---|---|---|
| `yoloN …` | `IS_SANDBOX=1`, `CLAUDE_CONFIG_DIR=/root/ai-accounts/.Claude/yoloN` | `claude --dangerously-skip-permissions --mcp-config=/root/ai-accounts/.Claude/shared/mcp/mcp.json …` |
| `cyoloN …` | `IS_SANDBOX=1`, `CODEX_HOME=/root/ai-accounts/.Codex/cyoloN` | `codex --dangerously-bypass-approvals-and-sandbox -c cli_auth_credentials_store="file" -c mcp_servers.playwright={…} …` |

* ส่งต่อ argument ทั้งหมด (`"$@"`) — เช่น `yolo1 -p "สวัสดี"`, `cyolo1 exec --skip-git-repo-check "…"`, `cyolo1 mcp list`
* ดูคำสั่งที่จะรันจริงโดยไม่เปิด CLI: `AI_ACCOUNTS_DRY_RUN=1 yolo1`
* ไม่มีโฟลเดอร์บัญชี → แจ้งข้อความชัดและออกด้วย exit 2 (แก้ด้วย `ai-accounts-init`)
* แก้ `shared/mcp/mcp.json` หรือ `shared/skills/…` ครั้งเดียว ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป
  (skill ใหม่ของ Codex: wrapper สร้างลิงก์รายตัวที่ยังไม่มีให้ตอนเปิด)
* แยกกันเฉพาะ config/credential/session ภายใต้ user `root` เดียวกัน — **ไม่ใช่การแยกสิทธิ์ของ OS**;
  ไฟล์โครงการและ config ระดับโครงการ (เช่น `.claude/`, `AGENTS.md` ในโฟลเดอร์งาน) ยังใช้ร่วมกันทุกบัญชี

---

# ขั้นที่ 1 — Build image

เปิด terminal ในโฟลเดอร์นี้ (ที่มี `Dockerfile`):

```bash
docker build -t multiaccount_devtool:2569_1 .
```

ครั้งแรกใช้เวลาหลายนาที (ดาวน์โหลด Ubuntu, Docker, Node.js, JupyterLab, Claude Code, Codex, Chromium) image ประมาณ 3 GB

เปลี่ยนเวอร์ชัน CLI ได้ด้วย `--build-arg` (ค่า default คือเวอร์ชันที่ทดสอบแล้ว):

```bash
docker build -t multiaccount_devtool:2569_1 \
  --build-arg CLAUDE_CODE_VERSION=latest \
  --build-arg CODEX_VERSION=latest \
  --build-arg PLAYWRIGHT_MCP_VERSION=0.0.83 .
```

> ถ้า npm ตอบ `404` เพราะเวอร์ชันเพิ่งออก Dockerfile จะลองใหม่ 3 ครั้ง ถ้ายังไม่ได้ให้ pin เวอร์ชันก่อนหน้า (`npm view @openai/codex versions`)

---

# ขั้นที่ 2 — Run container

```bash
docker run -dit --name MultiAccount_Devtool --hostname multiaccount-devtool --privileged -p 2223:22 -p 8886:8888 -v ai-accounts:/root/ai-accounts multiaccount_devtool:2569_1
```

| Flag | ความหมาย |
|------|----------|
| `--name MultiAccount_Devtool` | ชื่อ container |
| `--hostname multiaccount-devtool` | prompt เป็น `root@multiaccount-devtool:~#` |
| `--privileged` | จำเป็นสำหรับ Docker-in-Docker |
| `-p 2223:22` / `-p 8886:8888` | SSH / JupyterLab (ถ้าพอร์ตชน ให้เปลี่ยนเลขฝั่งซ้าย) |
| `-v ai-accounts:/root/ai-accounts` | **สำคัญ** — named volume เก็บการล็อกอินทุกบัญชี ลบ container แล้วสร้างใหม่ด้วย volume เดิม ไม่ต้องล็อกอินใหม่ และรหัส `shared-check` ไม่เปลี่ยน |

เพิ่มได้ตามต้องการ (เหมือน base): `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` สำหรับ SSH ด้วย key, `-v "${PWD}/workspace:/workspace"` เก็บงานบน host

ตรวจว่า start ครบ:

```bash
docker logs MultiAccount_Devtool
# [start.sh] [ai-accounts-init] done: base=/root/ai-accounts created=41 kept=1 warnings=0   ← ครั้งแรก
# [start.sh] sshd :22 | dockerd | ai-accounts | jupyter lab :8888 (password: <none>) ...
docker exec MultiAccount_Devtool ai-accounts-check          # ตาราง PASS/FAIL/SKIP (ไม่ต้องล็อกอิน)
```

ครั้งถัดไป (restart หรือสร้าง container ใหม่ด้วย volume เดิม) จะเห็น `created=0 kept=42`

---

# ขั้นที่ 3 — ล็อกอินทีละบัญชี (ผู้ใช้ทำเอง)

เข้า container ทางใดทางหนึ่ง: JupyterLab <http://localhost:8886> → **Terminal**, หรือ `ssh root@localhost -p 2223` (password `passwd`), หรือ `docker exec -it MultiAccount_Devtool bash`
ยืนยันตัวตนในเบราว์เซอร์ด้วยตัวเอง ไม่ส่งรหัสหรือข้อมูลบัญชีให้ AI

### Claude Code — `yolo1` … `yolo5`

```bash
yolo1            # เปิดครั้งแรก: เลือกธีม → "Claude account with subscription" → เปิดลิงก์ในเบราว์เซอร์ → วาง code กลับใน Terminal
yolo1 auth status   # ตรวจ: "loggedIn": true
```

ทำซ้ำกับ `yolo2`–`yolo5` เฉพาะบัญชีที่มี — แต่ละบัญชีเก็บสถานะไว้ใน `.Claude/yoloN/` ของตัวเอง

### Codex CLI — `cyolo1` … `cyolo5`

ใน container ให้ใช้ device code (เบราว์เซอร์ส่ง callback กลับเข้า container ไม่ได้):

```bash
cyolo1 login --device-auth    # เปิด URL ที่แสดงในเบราว์เซอร์ ใส่ code แล้วยืนยัน
cyolo1 login status           # "Logged in using ChatGPT" — แต่ยังไม่ยืนยันว่า token ใช้ได้
cyolo1 exec --skip-git-repo-check "ตอบคำว่า OK"   # ทดสอบว่า token ใช้งานได้จริง
```

credential ของ Codex เป็นไฟล์ `.Codex/cyoloN/auth.json` (ไม่ใช้ keyring ของ OS) — ทำซ้ำกับ `cyolo2`–`cyolo5`

### เปิดหลายบัญชีพร้อมกัน

เปิด Terminal หลายแท็บ แท็บละบัญชี หรือออกจาก CLI (`/exit`) แล้วเรียกบัญชีถัดไป
การพิมพ์ `yolo2` ในช่องสนทนาของ AI **ไม่ใช่** การสลับบัญชี

---

# ขั้นที่ 4 — ตรวจหลังล็อกอิน

### 4.1 ตรวจแบบไม่ต้องล็อกอิน (ทำได้ทุกเมื่อ)

```bash
ai-accounts-check
```

ตรวจ: CLI ใน image, `--version` ทั้ง 10 คำสั่ง, config root แยก 10 โฟลเดอร์, skill `shared-check` ทุกบัญชี `readlink -f` ไปไฟล์เดียวกัน,
`cyoloN mcp list` เห็น `playwright`, `yoloN` ส่ง `--mcp-config`, ไม่มี credential ใน shared, `ai-accounts-init` รอบซ้ำไม่เขียนทับ,
Git/SSH, Chromium ตรงเวอร์ชัน และ **เปิด Playwright MCP ผ่าน stdio จริง** (`initialize` → `tools/list` → `browser_navigate` + screenshot) โดยไม่ผ่าน AI
ส่วนที่ต้องล็อกอินจะเป็น `SKIP`

### 4.2 ตรวจผ่าน AI (ต้องล็อกอินแล้ว)

```bash
for a in yolo1 yolo2 cyolo1 cyolo2; do printf "%-7s " $a; $a --version; done
ls -l /root/ai-accounts/.Claude/yolo1/skills /root/ai-accounts/.Codex/cyolo1/skills/
cyolo1 mcp list
```

ใน Claude ให้พิมพ์ `/mcp` ในหน้าสนทนาเพื่อดู `playwright` (`claude mcp list` ไม่แสดง MCP ที่ส่งผ่าน `--mcp-config`)

จากนั้นใช้ `verify-prompt.txt` (อยู่ในโฟลเดอร์นี้ — copy เข้า container หรือเปิดใน JupyterLab):
คัดลอกข้อความใต้เส้น `====` ไปวางในช่องสนทนาของแต่ละบัญชี หรือรันจาก shell ตามวิธีในหัวไฟล์
ผลที่คาด: บัญชีต่างกันของ CLI เดียวกันได้ **รหัสเดียวกัน**, เรียก tool ของ MCP `playwright` ได้ และได้ภาพ 3 ภาพใน `/root/ai-accounts/playwright-output/`
(พรอมต์นี้ค้นหา/อ่านเว็บอย่างเดียว ไม่ล็อกอินเว็บ ไม่กรอกข้อมูลส่วนตัว ไม่จอง)

---

# ต่างจาก base (`00_Devtool_Container`) ตรงไหน

| เรื่อง | base `devtools:2569_1` | `multiaccount_devtool:2569_1` |
|---|---|---|
| Dockerfile | ส่วนที่ 1 | ส่วนที่ 1 เหมือนเดิมทุกคำสั่ง (แก้แค่ตัวเลข port ในคอมเมนต์) + ส่วนที่ 2 |
| Claude Code / Codex CLI | ไม่มี | ติดตั้งด้วย npm `-g` (pin ด้วย `ARG`) — npm 12 ต้อง `--allow-scripts=@anthropic-ai/claude-code` ให้ postinstall วาง native binary |
| หลายบัญชี | ไม่มี | wrapper `yolo1..5` / `cyolo1..5` ใน `/usr/local/bin` (ไม่แก้ `.bashrc`) |
| Playwright | ไม่มี | `@playwright/mcp` + Chromium + system library + `fonts-thai-tlwg` ใน image |
| Volume | `/var/lib/docker` | เพิ่ม `/root/ai-accounts` (credential/config/session + shared) |
| start.sh | sshd, dockerd, jupyter | เพิ่ม `ai-accounts-init` ก่อน jupyter (log: `/var/log/ai-accounts-init.log`) — ที่เหลือเหมือนเดิม |
| compose | `devtools`, 2222/8888, โหลด `env_file` | `MultiAccount_Devtool`, 2223/8886, volume `ai-accounts`; **ไม่โหลด env_file** เพราะ `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` ในไฟล์จะทับการล็อกอินรายบัญชี |
| คำสั่งเพิ่ม | — | `ai-accounts-init`, `ai-accounts-check` |

# ต่างจากแลป 02 (ให้ AI ตั้งค่าเอง) ตรงไหน

| 2.4.3.1 | ที่นี่ |
|---|---|
| "ห้ามติดตั้งซ้ำ" | Dockerfile ติดตั้ง Claude Code/Codex เอง |
| `BASE_PATH="$HOME/ai-accounts"` | `/root/ai-accounts` (= `$HOME/ai-accounts` ของ root) เป็น volume; แก้ที่ `/etc/ai-accounts/ai-accounts.conf` |
| installer รันซ้ำได้ | `ai-accounts-init` รันทุกครั้งที่ start — สร้างเฉพาะที่ยังไม่มี |
| ขอยืนยันก่อนเพิ่ม PATH | ไม่ต้อง — wrapper อยู่ใน `/usr/local/bin` ซึ่งอยู่ใน PATH อยู่แล้ว |
| `playwright install-deps` ตอนตั้งค่า | ติดตั้ง Chromium + library ไว้ใน image แล้ว |

# ข้อควรรู้

* screenshot ของ Playwright MCP: ถ้าไม่ระบุ `filename` จะไปที่ `--output-dir` (`/root/ai-accounts/playwright-output/<cli>/`);
  ถ้าระบุชื่อแบบ relative จะไปอยู่ในโฟลเดอร์ที่เปิด CLI (เช่น `/workspace`) — ใช้ path เต็มถ้าต้องการให้อยู่นอกโฟลเดอร์งาน
* SSH session ไม่สืบทอด `ENV` ของ Dockerfile — wrapper อ่านค่าจาก `/etc/ai-accounts/ai-accounts.conf` เอง จึงใช้ได้เหมือนกันทั้ง SSH / JupyterLab / `docker exec`
* Claude ตั้ง `DISABLE_AUTOUPDATER=1` ใน wrapper — อัปเดตด้วยการ build image ใหม่
* `docker volume rm ai-accounts` = ลบการล็อกอินทุกบัญชีและรหัสสุ่ม `shared-check` (สร้างใหม่ตอน start ครั้งถัดไป)

# คำสั่งที่ใช้บ่อย

```bash
docker logs MultiAccount_Devtool                       # log ตอน start
docker exec -it MultiAccount_Devtool bash              # เข้า shell
docker exec MultiAccount_Devtool ai-accounts-check     # ตรวจระบบหลายบัญชี
docker restart MultiAccount_Devtool                    # เริ่มใหม่ (บัญชียังอยู่)
docker rm -f MultiAccount_Devtool                      # ลบ container (volume ai-accounts ยังอยู่)
docker build -t multiaccount_devtool:2569_1 .          # build ใหม่ แล้ว rm -f + run ใหม่ด้วย -v ai-accounts:/root/ai-accounts
```
