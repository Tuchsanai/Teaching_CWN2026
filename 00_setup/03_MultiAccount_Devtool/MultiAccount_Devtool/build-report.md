# build-report — MultiAccount_Devtool (multiaccount_devtool:2569_1)

วันที่ทดสอบ: 2026-09-29 (เวลาไทย UTC+7) · Docker host 29.5.2 · image ID `20e4718c089e` (~3 GB)
ไม่มี secret ในรายงานนี้ รหัส `shared-check` แสดงเป็น sha256 แบบย่อเท่านั้น และไม่มีการล็อกอินบัญชีใด

## ไฟล์ที่สร้าง (`03_MultiAccount_Devtool/MultiAccount_Devtool/`)

| ไฟล์ | หน้าที่ |
|---|---|
| `Dockerfile` | `FROM ubuntu:24.04` — ส่วนที่ 1 คัดจาก base ครบทุกคำสั่ง, ส่วนที่ 2 ระบบหลายบัญชี |
| `start.sh` | คัดจาก base + เรียก `ai-accounts-init` (แก้ header, เพิ่ม 8 บรรทัด, บรรทัดสรุป log) |
| `jupyter_overrides.json` | คัดจาก base ไม่แก้ |
| `scripts/ai-accounts.conf` | `BASE_PATH=/root/ai-accounts` (แก้ที่เดียว), รายชื่อบัญชี, path Chromium/output |
| `scripts/ai-account` | wrapper กลาง; `yolo1..5`, `cyolo1..5` เป็น symlink ใน `/usr/local/bin` |
| `scripts/ai-accounts-init` | สร้างโฟลเดอร์บัญชี + shared + skill (ค่าสุ่ม) + mcp.json ใน volume, รันซ้ำได้ |
| `scripts/ai-accounts-check` | ตรวจแบบไม่ต้องล็อกอิน ตาราง PASS/FAIL/SKIP |
| `scripts/mcp_json_to_codex.py` | แปลง `mcp.json` → `-c mcp_servers.<name>={...}` (TOML inline) |
| `scripts/mcp_stdio_probe.py` | JSON-RPC ผ่าน stdio: initialize → tools/list → browser_navigate → screenshot |
| `docker-compose.yml` | build+run คำสั่งเดียว, volume ชื่อ `ai-accounts` ตรงกับ `docker run` |
| `.dockerignore`, `.gitignore` | ไม่ส่ง readme/report/workspace/Devtool_SSH เข้า image |
| `readme.md` | build, run, ล็อกอินทีละบัญชี, โครงสร้าง, ต่างจาก base |
| `verify-prompt.txt` | พรอมต์ตรวจหลังล็อกอิน (config root, `shared-check`, Playwright MCP + screenshot 3 ภาพ, ตาราง) — ค้นเที่ยวบิน Google Flights อย่างเดียว ไม่จอง |
| `build-report.md` | ไฟล์นี้ |

## สิ่งที่ต่างจาก base

* เพิ่ม Claude Code `2.1.284`, Codex CLI `0.159.0`, `@playwright/mcp@0.0.83` (npm -g, pin ด้วย `ARG`)
* Chromium 155 (`chromium-1247` + `chromium_headless_shell-1247`) ติดตั้งด้วย playwright ที่อยู่ในแพ็กเกจ @playwright/mcp (`--with-deps`) พร้อม `fonts-thai-tlwg` ไว้ที่ `/opt/ms-playwright`
* wrapper 10 คำสั่งใน `/usr/local/bin` (ไม่แก้ `.bashrc`), `ai-accounts-init`, `ai-accounts-check`
* `VOLUME /root/ai-accounts` — credential/config/session/shared อยู่ใน volume ไม่อยู่ใน image
* `start.sh` เรียก `ai-accounts-init` ทุกครั้งที่ start ส่วน sshd/dockerd/jupyter เหมือนเดิม
* compose: ไม่โหลด `env_file` ของ base เพราะ API key ในไฟล์จะทับการล็อกอินรายบัญชี

## ปัญหาที่เจอระหว่าง build และวิธีแก้

| ปัญหา | สาเหตุ | แก้ |
|---|---|---|
| `Error: claude native binary not installed.` | npm 12 บล็อก install script โดย default → postinstall ของ Claude Code ไม่รัน | `npm install -g --allow-scripts=@anthropic-ai/claude-code …` |
| `ERR_PACKAGE_PATH_NOT_EXPORTED ./cli.js` | `playwright` ไม่ export `cli.js` | หา path จาก `dirname(require.resolve("playwright"))` |
| screenshot ไปอยู่ใน `/workspace` | `browser_take_screenshot` ที่ได้ `filename` แบบ relative จะบันทึกเทียบกับ cwd ไม่ใช่ `--output-dir` (ทดลองจริง: ไม่ระบุชื่อ → output-dir, path เต็ม → บันทึกตาม path นั้น) | probe ส่ง path เต็มใต้ output-dir; `verify-prompt.txt` สั่งให้ใช้ path เต็ม; ลบไฟล์ทดสอบใน `/workspace` แล้ว |

## ผลทดสอบ

### ai-accounts-check

รันจริงใน container สุดท้ายด้วย `docker exec MultiAccount_Devtool ai-accounts-check` → exit 0, **PASS=44 FAIL=0 SKIP=3**

| รายการ | หลักฐาน | ผล |
|---|---|---|
| claude ติดตั้งใน image | /usr/bin/claude: 2.1.284 (Claude Code) | PASS |
| codex ติดตั้งใน image | /usr/bin/codex: codex-cli 0.159.0 | PASS |
| playwright-mcp ติดตั้งใน image | /usr/bin/playwright-mcp: Version 0.0.83 | PASS |
| yolo1 … yolo5 --version (5 แถว) | /usr/local/bin/ai-account → 2.1.284 (Claude Code) | PASS ×5 |
| cyolo1 … cyolo5 --version (5 แถว) | /usr/local/bin/ai-account → codex-cli 0.159.0 | PASS ×5 |
| config root แยกกัน 10 โฟลเดอร์ | find: 10 โฟลเดอร์ ไม่ซ้ำ 10 (.Claude/yolo1..5, .Codex/cyolo1..5) | PASS |
| wrapper ตั้ง CLAUDE_CONFIG_DIR / CODEX_HOME | dry-run yolo1 → /root/ai-accounts/.Claude/yolo1, cyolo1 → /root/ai-accounts/.Codex/cyolo1 (HOME=/root ไม่เปลี่ยน) | PASS |
| Claude skill shared-check → ไฟล์เดียวกัน | readlink -f ทุกบัญชี = /root/ai-accounts/.Claude/shared/skills/shared-check/SKILL.md | PASS |
| Codex skill shared-check → ไฟล์เดียวกัน | readlink -f ทุกบัญชี = /root/ai-accounts/.Codex/shared/skills/shared-check/SKILL.md | PASS |
| Claude yoloN/skills เป็นลิงก์ไป shared | yoloN/skills -> ../shared/skills | PASS |
| Codex cyoloN/skills เป็นโฟลเดอร์จริง (ลิงก์รายตัว) | Codex เขียน skills/.system เองได้ | PASS |
| รหัส shared-check (claude) มีในไฟล์ | SHARED_SKILL_OK-claude-…  sha256(รหัส)=e6733941c200 | PASS |
| รหัส shared-check (codex) มีในไฟล์ | SHARED_SKILL_OK-codex-…  sha256(รหัส)=b4ce225c2492 | PASS |
| Claude shared/mcp/mcp.json มี playwright | /root/ai-accounts/.Claude/shared/mcp/mcp.json | PASS |
| Codex shared/mcp/mcp.json มี playwright | /root/ai-accounts/.Codex/shared/mcp/mcp.json | PASS |
| cyolo1 … cyolo5 mcp list เห็น playwright (5 แถว) | playwright /usr/bin/playwright-mcp --browser chromium --headless --isolated --no-sandbox … | PASS ×5 |
| yoloN ส่ง --mcp-config=<shared mcp.json> | dry-run ทั้ง 5 บัญชี (claude mcp list ไม่แสดง MCP นี้ ต้องดูด้วย /mcp) | PASS |
| ไม่มีไฟล์ credential ใน shared | find .credentials.json/auth.json/.claude.json ใน shared = 0 | PASS |
| .claude.json ไม่เป็น symlink | แต่ละ yoloN มีสถานะล็อกอินของตัวเอง | PASS |
| Codex credential แบบไฟล์ต่อ CODEX_HOME | config.toml + wrapper -c cli_auth_credentials_store="file" | PASS |
| ai-accounts-init รอบซ้ำไม่เขียนทับ | snapshot ก่อน=หลัง (7890747b5e82c31f); created=0 kept=42 warnings=0 | PASS |
| wrapper แจ้งเมื่อไม่มีโฟลเดอร์บัญชี | exit 2: yolo1: ไม่พบโฟลเดอร์บัญชี /nonexistent-ai-accounts/.Claude/yolo1 | PASS |
| .bashrc ไม่ถูกแก้ | wrapper อยู่ใน /usr/local/bin (PATH ของ image) | PASS |
| Git ปกติ | git version 2.55.0 | PASS |
| SSH (sshd) ปกติ | sshd ทำงาน, sshd -t ผ่าน | PASS |
| Chromium ตรงกับ playwright ใน @playwright/mcp | playwright-core 1.64.0-alpha-1790635538000 ต้องการ chromium-1247, มี: 1247 (/opt/ms-playwright) | PASS |
| Claude MCP stdio: initialize | Playwright 1.64.0-alpha-1790635538000 protocol 2025-06-18 | PASS |
| Claude MCP stdio: tools/list | 25 tools, มี browser_navigate, browser_take_screenshot, browser_snapshot | PASS |
| Claude MCP stdio: browser_navigate | https://example.com/ → title="Example Domain"; screenshot /root/ai-accounts/playwright-output/claude/ai-accounts-check-claude.png (21016 bytes) | PASS |
| Codex MCP stdio: initialize | Playwright 1.64.0-alpha-1790635538000 protocol 2025-06-18 | PASS |
| Codex MCP stdio: tools/list | 25 tools, มี browser_navigate, browser_take_screenshot, browser_snapshot | PASS |
| Codex MCP stdio: browser_navigate | https://example.com/ → title="Example Domain"; screenshot /root/ai-accounts/playwright-output/codex/ai-accounts-check-codex.png (21016 bytes) | PASS |
| ล็อกอิน yoloN / cyoloN | ต้องให้ผู้ใช้ล็อกอินเอง (ห้ามล็อกอินแทน) | SKIP |
| เรียก skill shared-check ผ่าน AI | ต้องล็อกอิน — ใช้ verify-prompt.txt หลังล็อกอิน | SKIP |
| Claude /mcp เห็น playwright, AI เรียก tool playwright | ต้องล็อกอิน | SKIP |

### ทดสอบเพิ่มเติมด้วย docker exec

| รายการ | หลักฐาน | ผล |
|---|---|---|
| ค่าสุ่ม shared-check คงเดิมหลัง `docker restart` | sha256(SKILL.md) ของ Claude `3954992b0389402f` และ Codex `f90dad106e0effe8` เท่ากันทั้ง T0 (start แรก) และ T1 (หลัง restart); init: `created=0 kept=42` | PASS |
| ลบ container แล้วสร้างใหม่ด้วย volume เดิม ค่าสุ่มไม่เปลี่ยน | `docker rm -f` → `docker run … -v ai-accounts:…` (image ที่ build ใหม่ `20e4718c089e`): hash เท่าเดิมทั้งสองไฟล์, `created=0 kept=42`; restart ซ้ำอีกรอบ (T3) ก็ยังเท่าเดิม | PASS |
| wrapper ส่งต่อ `"$@"` ครบ | `AI_ACCOUNTS_DRY_RUN=1 yolo2 -p "hello world" --model x` → `… --mcp-config=… -p hello\ world --model x` | PASS |
| skill ใหม่ใน shared เห็นโดยไม่รัน installer ซ้ำ (Codex) | เพิ่ม `shared/skills/zz-tmp-test` → `cyolo4 --version` → เกิดลิงก์ `cyolo4/skills/zz-tmp-test` (ลบทิ้งหลังทดสอบ) | PASS |
| subcommand ผ่าน wrapper | `yolo1 auth status` → `"loggedIn": false`; `cyolo1 login status` → `Not logged in` | PASS |
| `.claude.json` แยกต่อบัญชี | หลังรัน `yolo1` มี `.Claude/yolo1/.claude.json` เป็นไฟล์จริงของบัญชีนั้น | PASS |
| sshd (base) | SSH ด้วย key `devtoolSSH` ที่ `host.docker.internal:2223` → `multiaccount-devtool via SSH: 2.1.284 (Claude Code) \| codex-cli 0.159.0` และ `yolo1` อยู่ใน PATH ของ SSH session | PASS |
| dockerd (base) | `docker run --rm hello-world` ใน container → `Hello from Docker!` (server 29.8.1) | PASS |
| JupyterLab (base) | ใน container `curl localhost:8888/api/status` → 200; จากภายนอก `host.docker.internal:8886/lab` → 200 | PASS |
| Playwright screenshot เป็นภาพจริง | เปิดดู `ai-accounts-check-claude.png` (21 KB) แล้วเห็นหน้า Example Domain | PASS |
| ล็อกอิน 10 บัญชี, เรียก skill ผ่าน AI, `/mcp` ใน Claude, AI เรียก tool playwright | ต้องล็อกอิน — ใช้ `verify-prompt.txt` หลังผู้ใช้ล็อกอินเอง | SKIP |

## Port ที่ใช้จริง

| บริการ | container | host |
|---|---|---|
| SSH | 22 | **2223** (ว่าง ใช้ได้ตั้งแต่ครั้งแรก) |
| JupyterLab | 8888 | **8886** (ว่าง ใช้ได้ตั้งแต่ครั้งแรก) |

คำสั่งที่รันจริง:
`docker run -dit --name MultiAccount_Devtool --hostname multiaccount-devtool --privileged -p 2223:22 -p 8886:8888 -v ai-accounts:/root/ai-accounts multiaccount_devtool:2569_1`

## ข้อจำกัด

* **ยังไม่ได้ล็อกอินบัญชีใด** — ส่วนที่ต้องล็อกอินเป็น SKIP ทั้งหมด (ตามคำสั่ง ห้ามล็อกอินแทน)
* เซสชันที่ใช้ทดสอบรันอยู่ใน container อื่น: port ที่ publish เข้าถึงผ่าน `host.docker.internal` ได้ แต่ `localhost:2223/8886` จากเซสชันนี้เข้าไม่ได้ (บนเครื่องผู้ใช้ปกติใช้ `localhost` ได้)
* การแยกบัญชีเป็นการแยก config/credential/session ภายใต้ `root` คนเดียว ไม่ใช่ OS isolation และ project config ในโฟลเดอร์งานยังใช้ร่วมกัน
* `skills/.system` ของ Codex จะถูกสร้างเมื่อ Codex เริ่ม session จริงหลังล็อกอิน จึงยังไม่เห็นในการทดสอบนี้ (โครงสร้างรองรับแล้ว เพราะ `skills/` เป็นโฟลเดอร์จริง)
* Claude ไม่แสดง MCP จาก `--mcp-config` ใน `claude mcp list` — การทดสอบนี้จึงตรวจด้วย wrapper dry-run + stdio probe แทน ส่วน `/mcp` ต้องล็อกอินก่อน
* `ai-accounts-check` ต้องใช้ internet เพื่อเปิด `https://example.com/` (เปลี่ยนได้ด้วย `AI_CHECK_URL`, ข้ามได้ด้วย `--no-browser`)
* `ai-accounts-init` ไม่แก้ `config.toml` ที่มีอยู่แล้ว — wrapper จึงบังคับ `cli_auth_credentials_store="file"` ด้วย `-c` ทุกครั้งแทน
* ถ้าแก้ `ai-accounts.conf` (BASE_PATH) หลังสร้าง `mcp.json` แล้ว path `--output-dir` ใน mcp.json เดิมจะไม่เปลี่ยนตาม (init ไม่เขียนทับ)
* image ~3 GB (base ~1.3 GB + Chromium/deps + CLI)
