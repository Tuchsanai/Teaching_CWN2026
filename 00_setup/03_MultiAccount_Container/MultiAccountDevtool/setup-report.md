# setup-report — MultiAccountDevtool (`tuchsanai/multi-account-devtool:2569_1`)

วันที่ build/ทดสอบ: 2026-09-29 (เวลาไทย UTC+7) · image ID `sha256:1ef1dd87076e…` · ขนาด ≈ 3.0 GB
push `tuchsanai/multi-account-devtool:2569_1` ขึ้น Docker Hub แล้ว (digest `sha256:36e63a66…`) · ยังไม่มีบัญชีใดล็อกอิน (ผู้ใช้ล็อกอินเอง ดู `login-guide.md`)

## 1. เวอร์ชันที่ติดตั้งจริงใน image

| ส่วนประกอบ | เวอร์ชัน | ติดตั้งด้วย | ตำแหน่ง |
|---|---|---|---|
| Claude Code | 2.1.284 | `curl -fsSL https://claude.ai/install.sh \| bash` (native) | `/root/.local/share/claude/versions/2.1.284` ← `/root/.local/bin/claude` ← `/usr/local/bin/claude` |
| Codex CLI | codex-cli 0.159.0 | `npm install -g @openai/codex` | `/usr/lib/node_modules/@openai/codex` ← `/usr/local/bin/codex` |
| Playwright MCP | `@playwright/mcp@0.0.83` (pin) | `npm install -g` | `/usr/bin/playwright-mcp` |
| Playwright (ในแพ็กเกจ MCP) | 1.64.0-alpha-1790635538000 | มากับ `@playwright/mcp` | `…/@playwright/mcp/node_modules/playwright` |
| Chromium | Chrome for Testing 155.0.8059.12 (chromium-1247 + headless shell) | `node <playwright ใน @playwright/mcp>/cli.js install --with-deps chromium` ครั้งเดียวตอน build | `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` |
| ของเดิมจาก 00_Devtool_Container | Ubuntu 24.04, git 2.55.0, Docker 29.8.1 (DinD), Node 22, JupyterLab 4.x + extensions, sshd (password + key `devtoolSSH`) | สำเนา Dockerfile เดิมทั้งส่วน | — |

`claude`, `codex`, `yolo1..5`, `cyolo1..5` อยู่ใน `/usr/local/bin` ซึ่งอยู่ใน PATH มาตรฐานอยู่แล้ว → ใช้ได้ทั้ง JupyterLab Terminal (`bash -l`), SSH และ `docker exec` โดยไม่แก้ `.bashrc` (ทดสอบแล้วทั้งสามทาง)

## 2. โครงสร้างไฟล์ในเครื่อง

```
/etc/ai-accounts.conf                 BASE_PATH="$HOME/ai-accounts"   ← แก้ที่นี่ที่เดียว
/usr/local/bin/ai-accounts-setup      installer (start.sh เรียกทุกครั้งที่ container start, รันซ้ำได้)
/usr/local/bin/ai-account             wrapper กลาง; yolo1..5 / cyolo1..5 เป็น symlink มาที่ไฟล์นี้
/usr/local/lib/ai-accounts/mcp_json_to_codex.py   แปลง mcp.json → -c mcp_servers.<name>={...}
/usr/local/lib/ai-accounts/mcp_stdio_probe.py     ทดสอบ MCP ผ่าน stdio โดยไม่ต้องล็อกอิน

$BASE_PATH = /root/ai-accounts   (named volume `ai-accounts` — อยู่รอดเมื่อสร้าง container ใหม่)
├── .Claude/
│   ├── shared/skills/shared-check/SKILL.md   รหัส SHARED_SKILL_OK-claude-<สุ่ม>
│   ├── shared/mcp/mcp.json                    {"mcpServers":{"playwright":{...}}}
│   └── yolo1..yolo5/                          = CLAUDE_CONFIG_DIR (credential/config/session ของบัญชี)
│       └── skills -> ../shared/skills         symlink ทั้งโฟลเดอร์
├── .Codex/
│   ├── shared/skills/shared-check/SKILL.md   รหัส SHARED_SKILL_OK-codex-<สุ่ม>
│   ├── shared/mcp/mcp.json
│   └── cyolo1..cyolo5/                        = CODEX_HOME
│       ├── config.toml                        cli_auth_credentials_store = "file"
│       └── skills/                            โฟลเดอร์จริง (Codex เขียน .system เอง)
│           └── shared-check -> ../../shared/skills/shared-check   ลิงก์รายตัว
└── playwright-output/                         --output-dir ของ Playwright MCP (นอก /workspace)
```

## 3. config root และตำแหน่ง credential

| บัญชี | คำสั่งจริงที่ wrapper รัน | config root | credential (หลังล็อกอิน) |
|---|---|---|---|
| yoloN | `IS_SANDBOX=1 CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN claude --dangerously-skip-permissions --mcp-config=$BASE_PATH/.Claude/shared/mcp/mcp.json "$@"` | `$BASE_PATH/.Claude/yoloN` | `yoloN/.credentials.json` + สถานะบัญชีใน `yoloN/.claude.json` (ไม่ symlink) |
| cyoloN | `IS_SANDBOX=1 CODEX_HOME=$BASE_PATH/.Codex/cyoloN codex --dangerously-bypass-approvals-and-sandbox -c cli_auth_credentials_store="file" -c mcp_servers.playwright={...} "$@"` | `$BASE_PATH/.Codex/cyoloN` | `cyoloN/auth.json` (ไฟล์ ไม่ใช้ keyring) |

ดูคำสั่งเต็มที่ wrapper จะรันได้โดยไม่เปิด CLI: `AI_ACCOUNTS_DRY_RUN=1 cyolo1` (พิมพ์เฉพาะ path/argument ไม่มี secret)

## 4. แต่ละ CLI อ่าน skill / MCP จากไหน และเชื่อม shared อย่างไร

| | Claude Code (yoloN) | Codex CLI (cyoloN) |
|---|---|---|
| skill อ่านจาก | `$CLAUDE_CONFIG_DIR/skills` | `$CODEX_HOME/skills` (+ `skills/.system` ที่ Codex เขียนเอง) |
| เชื่อม shared | `yoloN/skills` เป็น symlink → `../shared/skills` (ทั้งโฟลเดอร์) → skill ใหม่ใน shared เห็นทันที | `skills/` เป็นโฟลเดอร์จริง; ลิงก์ต่อ skill; **wrapper sync ลิงก์ที่ขาดทุกครั้งที่เปิด** และลบลิงก์ค้างที่ชี้เข้า shared เมื่อ skill ถูกลบ |
| MCP อ่านจาก | `--mcp-config=<shared/mcp/mcp.json>` ส่งทุกครั้งที่เปิด (ต้องมี `=`) | wrapper อ่าน `shared/mcp/mcp.json` ทุกครั้งที่เปิด แล้วแปลงเป็น `-c mcp_servers.<name>={command=…, args=[…], env={…}}` |
| ตรวจ MCP | `/mcp` ในเซสชัน (หลังล็อกอิน) — `claude mcp list` **ไม่แสดง** | `cyoloN mcp list` (ไม่ต้องล็อกอิน) |
| ตรวจ skill | ถาม `shared-check` ในเซสชัน (หลังล็อกอิน) | `cyoloN debug prompt-input hi` แสดงรายการ skill ที่โมเดลเห็น (ไม่ต้องล็อกอิน) หรือถาม `shared-check` |

แก้ `shared/` ครั้งเดียว (เพิ่ม skill, เพิ่ม server ใน mcp.json) → ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป **ไม่ต้องรัน installer ซ้ำ** (ทดสอบแล้ว ดู checklist ข้อ 7)

MCP ส่วนกลางตัวแรก (เหมือนกันทั้งสอง CLI):
```json
{"mcpServers":{"playwright":{"command":"/usr/bin/playwright-mcp",
  "args":["--browser","chromium","--headless","--isolated","--no-sandbox","--output-dir","/root/ai-accounts/playwright-output"],
  "env":{"PLAYWRIGHT_BROWSERS_PATH":"/ms-playwright"}}}}
```

## 5. ตรวจ "ข้อเท็จจริงจากการทดลอง" กับเวอร์ชันที่ติดตั้งจริง

| ข้อเท็จจริงในสเปก | ผลกับ Claude 2.1.284 / Codex 0.159.0 / MCP 0.0.83 | หลักฐาน |
|---|---|---|
| root ต้องตั้ง `IS_SANDBOX=1` | จริง — ไม่ตั้ง: `--dangerously-skip-permissions cannot be used with root/sudo privileges`; ตั้งแล้วผ่านไปถึง `Not logged in` | `_agent_logs/t-claude-facts.log` |
| `CODEX_HOME` ต้อง `mkdir -p` ก่อน | จริง — `Error loading configuration: CODEX_HOME points to "…", but that path does not exist` | `t-claude-facts.log` |
| Claude อ่าน skill จาก `$CLAUDE_CONFIG_DIR/skills` | ตรวจโดยตรงไม่ได้หากไม่ล็อกอิน (SKIP) — ตั้งโครงตามสเปก | — |
| `--mcp-config=<ไฟล์>` ต้องมี `=` | จริง — `--help` แสดง `--mcp-config <configs...>` (รับหลายค่า); ไม่มี `=` แล้ววาง prompt ตามหลัง → `MCP config file not found: /workspace/say hi` | `t-claude-facts.log` |
| `claude mcp list` ไม่แสดง MCP นี้ | จริง — ทั้ง `claude mcp list` และ `yolo1 mcp list` ตอบ `No MCP servers configured` | `t-claude-facts.log` |
| Codex อ่าน `$CODEX_HOME/skills` และเขียน `skills/.system` เอง | จริง — หลังเปิด `cyolo1 debug prompt-input` มี `skills/.system/{imagegen,openai-docs,…}` และเห็น `shared-check` | `t7b-codex-prompt-input.log` |
| MCP ส่งด้วย `-c mcp_servers.<name>={...}` ใช้กับ `codex mcp list` ได้ | จริง — `cyolo1..5 mcp list` แสดง playwright `enabled` | `t2-t6.log` |
| key `cli_auth_credentials_store = "file"` | จริง — ใส่ค่าผิดได้ `unknown variant 'bogus', expected one of 'file','keyring','auto','ephemeral' in 'cli_auth_credentials_store'` | `t-verify-facts.log` |
| Playwright ใน root container ใช้ `--browser chromium --headless --isolated --no-sandbox` + `--output-dir` นอกโฟลเดอร์งาน | ใช้ได้จริง — MCP ผ่าน stdio: initialize → tools/list (25 tools) → navigate example.com → screenshot สำเร็จ | `mcp-probe-transcript.jsonl`, `mcp-probe-example.png` |
| ติดตั้ง Chromium ด้วย playwright ในแพ็กเกจ @playwright/mcp | ทำแล้ว — CLI ที่ใช้คือ `…/@playwright/mcp/node_modules/playwright/cli.js` (1.64.0-alpha) → chromium-1247 ตรงกับ MCP | `_agent_logs/docker-build.log` |
| Codex ใน container ล็อกอินด้วย `codex login --device-auth`; `login status` ไม่ยืนยัน token | มี flag `--device-auth` ใน binary; การยืนยัน token ต้องล็อกอิน (SKIP) | `t-verify-facts.log` |

ข้อสังเกตเพิ่มเติมที่พบจริง (ไม่ขัดสเปก):
- Codex 0.159.0 พิมพ์ `WARNING: … could not create PATH aliases` เมื่อ `CODEX_HOME` อยู่ใต้ `/tmp` เท่านั้น (เจอตอน smoke test ใน build) — ใน `/root/ai-accounts` ไม่มีคำเตือนนี้ และ Codex สร้าง `CODEX_HOME/tmp/` เอง
- `@playwright/mcp` `browser_take_screenshot` ต้องให้ `filename` เป็น absolute path (relative จะบันทึกเทียบกับ cwd) — probe จึงส่ง absolute path
- wrapper ของ Claude ตั้ง `DISABLE_AUTOUPDATER=1` เพราะ CLI อยู่ใน image; อัปเดตโดย build ใหม่ (`--build-arg CLAUDE_CODE_VERSION=…`)

## 6. การทำงานตอน container start (start.sh)

sshd (password `passwd` + key `devtoolSSH`) → dockerd → `ai-accounts-setup` (log `/var/log/ai-accounts-setup.log`) → JupyterLab :8888
- volume ใหม่ → สร้างโครงทั้งหมด + สุ่มรหัส shared-check ใหม่ (volume ต่างกันได้รหัสต่างกัน ทดสอบแล้ว)
- volume เดิม → `created=0` ไม่แตะ credential/config/รหัสเดิม (ทดสอบ `--force-recreate` แล้ว)

## 7. ข้อจำกัด / สิ่งที่ยังร่วมกัน (ไม่ใช่ OS isolation)

- ทุกบัญชีรันเป็น **ผู้ใช้ Linux เดียวกัน (root)** ใน container เดียวกัน → บัญชีหนึ่งอ่านไฟล์ credential ของอีกบัญชีได้ในทางเทคนิค การแยกเป็นแค่ "แยกโฟลเดอร์ config" ไม่ใช่ sandbox
- ร่วมกัน: `$HOME=/root` (เช่น `~/.gitconfig`, `~/.ssh`, `~/.cache`), `/workspace`, ไฟล์ config ระดับโปรเจกต์ในโฟลเดอร์งาน (`.claude/`, `CLAUDE.md`, `AGENTS.md`, `.codex/`), Docker daemon ใน container, Chromium ใน `/ms-playwright`, โฟลเดอร์ `playwright-output`
- MCP/skill ใน shared เห็นทุกบัญชีของ CLI นั้น — **ห้ามใส่ token/credential ใน `shared/`** (ถ้า MCP ต้องใช้ key ให้ส่งผ่าน env ตอนรัน ไม่เขียนลง mcp.json)
- Claude: `claude mcp list` ไม่เห็น MCP จาก `--mcp-config` ให้ตรวจด้วย `/mcp`
- `docker compose down -v` ลบ volume `ai-accounts` = ล็อกอินหายทุกบัญชี
- env_file (`DEVTOOLS_ENV_FILE`, ค่าเริ่ม `/root/workspace/DGX_2024/.env`) เข้า environment ของ container/JupyterLab แต่ SSH session ไม่สืบทอด (เหมือน container เดิม)
- การทดสอบของ agent ใช้ compose override (`_agent_logs/compose.test-override.yaml`) เพราะ agent อยู่ใน container: bind mount ต้องใช้ path ฝั่ง Docker host (`/run/desktop/mnt/host/c/Users/…/MultiAccountDevtool/{workspace,Devtool_SSH}`) และ mount `Devtool_SSH` แบบ `:ro` — นักศึกษาที่รัน `docker compose up -d` บนเครื่องตัวเองไม่ต้องใช้ override นี้
