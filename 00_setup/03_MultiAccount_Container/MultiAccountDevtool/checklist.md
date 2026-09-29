# checklist — ผลทดสอบจริง (2026-09-29, เวลาไทย)

container ทดสอบ: `devtools-multiacct-cb5b94` (compose project เดียวกัน) · SSH `2224` · JupyterLab `8892`
image `tuchsanai/multi-account-devtool:2569_1` = `sha256:1ef1dd87076e…` · volume `devtools-multiacct-cb5b94_ai-accounts`, `devtools-multiacct-cb5b94_multi-account-dind`
env_file ชี้ไปไฟล์ว่าง (`_agent_logs/empty.env`) — ไม่ได้โหลด .env ส่วนตัว · log ทั้งหมดอยู่ใน `../_agent_logs/`

| # | รายการ | หลักฐาน | ผล | เหตุผล |
|---|---|---|---|---|
| 1 | build image | `docker-build.log` จบด้วย `EXIT 0`, `naming to …multi-account-devtool:2569_1`; tag `:latest` ชี้ ID เดียวกัน | PASS | push `2569_1` แล้ว (digest `sha256:36e63a66…`) |
| 2 | `claude`/`codex` ติดตั้งตามวิธีในสเปก | build log: install.sh → `Version: 2.1.284`; npm → `codex-cli 0.159.0` | PASS | |
| 3 | 10 คำสั่ง `--version` (yolo1..5, cyolo1..5) | `t1-versions.log`: yolo1..5 = `2.1.284 (Claude Code)`, cyolo1..5 = `codex-cli 0.159.0` | PASS | |
| 4 | อยู่ใน PATH ทั้ง `bash -l`, `sh -c` (docker exec), SSH, JupyterLab Terminal | `t1-versions.log`, `t4-ssh-git.log`, `t9-jupyter.log` (เปิด terminal จริงผ่าน API+websocket: `JT-yolo1=/usr/local/bin/yolo1` …) | PASS | ลิงก์ใน `/usr/local/bin` ไม่พึ่ง .bashrc |
| 5 | config root คนละโฟลเดอร์ (find) | `t2-t6.log`: 10 โฟลเดอร์ `.Claude/yolo1..5`, `.Codex/cyolo1..5`, `distinct roots: 10`; dry-run แสดง `CLAUDE_CONFIG_DIR`/`CODEX_HOME` ตรงบัญชี | PASS | |
| 6 | installer รอบ 2 ไม่ทำลายของเดิม | `t3-t7.log`: วาง credential/config ปลอม → รัน `ai-accounts-setup` → `created=0 kept=50`, `DIFF: identical (23 entries)` รวม checksum SKILL.md (รหัส shared-check) ทั้ง 2 CLI, `auth.json`/`.credentials.json` ปลอม และ config.toml ที่ถูกแก้ | PASS | ไฟล์ปลอมถูกลบคืนหลังทดสอบ |
| 7 | สร้าง container ใหม่ด้วย volume เดิม ไม่เสียของเดิม | `t10-recreate.log`: `up --force-recreate` → checksum SKILL.md + inode config.toml เท่าเดิม, marker file ยังอยู่, `created=0` | PASS | |
| 8 | volume ใหม่ได้รหัสสุ่มของตัวเอง | `t10-recreate.log` T11: checksum SKILL.md ต่างจาก volume ทดสอบ | PASS | |
| 9 | รหัสสุ่มมีเฉพาะใน SKILL.md | `t2-t6.log`: `grep -rlF <รหัส> /` (ยกเว้น proc/sys/dev) เจอไฟล์เดียวต่อ CLI คือ `shared/skills/shared-check/SKILL.md` | PASS | รายงาน/log ไม่พิมพ์รหัส (แสดงแค่ความยาว/checksum) |
| 10 | Git ปกติ | `t4-ssh-git.log`: git 2.55.0, init/commit/worktree ได้, ไม่มี `~/.gitconfig` ถูกสร้าง | PASS | |
| 11 | SSH ปกติ (key `Devtool_SSH/devtoolSSH`, BatchMode) | `t4-ssh-git.log`: `whoami=root host=multi-account-devtool`, `exit=0` | PASS | ผ่าน `host.docker.internal:2224` |
| 12 | SSH password `passwd` | `t4-ssh-git.log`: `password-login-ok` | PASS | |
| 13 | ไม่แก้ .bashrc/.profile/sshd config | `t4-ssh-git.log`: sha256 ตรงกับ image ต้นฉบับ, `grep -c ai-accounts` = 0 | PASS | |
| 14 | Docker-in-Docker | `t4-ssh-git.log`: `dockerd=29.8.1` | PASS | |
| 15 | `cyoloN mcp list` เห็น playwright ทั้ง 5 | `t2-t6.log`: cyolo1..5 → `playwright /usr/bin/playwright-mcp --browser chromium --headless --isolated --no-sandbox --output-dir /root/ai-accounts/playwright-output … enabled` | PASS | ไม่ต้องล็อกอิน |
| 16 | shared-check ทุกบัญชี `readlink -f` ไปไฟล์เดียวกันใน shared | `t2-t6.log`: yolo1..5 → `.Claude/shared/skills/shared-check/SKILL.md`, cyolo1..5 → `.Codex/shared/skills/shared-check/SKILL.md` | PASS | |
| 17 | Codex โหลด skill จาก shared จริง (มุมมองโมเดล) | `t7b-codex-prompt-input.log`: `cyolo1..5 debug prompt-input` มี `- shared-check: … (file: r0/shared-check/SKILL.md)`; Codex สร้าง `skills/.system` เอง | PASS | ไม่ต้องล็อกอิน |
| 18 | skill ใหม่ใน shared เห็นโดยไม่รัน installer ซ้ำ (แล้วลบออก) | `t3-t7.log`: yolo3 เห็น `dummy-new` ทันที (symlink), cyolo4 ได้ลิงก์หลังเปิด 1 ครั้ง; `t7b…log`: `cyolo2 debug prompt-input` เห็น `dummy-new`; ลบแล้วลิงก์ค้างถูกเก็บ (`after removal: 0`) | PASS | |
| 19 | wrapper แจ้งชัดเมื่อไม่มีโฟลเดอร์บัญชี | `t3-t7.log`: `cyolo5: ไม่พบโฟลเดอร์บัญชี …` + วิธีแก้, `exit=2` | PASS | |
| 20 | wrapper ส่ง `"$@"` ครบ | `t2-t6.log` dry-run: `--foo a\ b` ส่งต่อเป็น argument เดียว | PASS | |
| 21 | ไม่มี credential ใน shared | `t2-t6.log`: shared มีแค่ `mcp.json` + `SKILL.md`; ไม่มี auth.json/.credentials.json ในเครื่อง | PASS | |
| 22 | Codex credential แบบไฟล์ (key ถูกต้อง) | `t-verify-facts.log`: ค่าผิด → `expected one of file, keyring, auto, ephemeral in cli_auth_credentials_store`; config.toml ทุกบัญชีมี `"file"` | PASS | |
| 23 | ข้อเท็จจริง IS_SANDBOX / mkdir CODEX_HOME / `--mcp-config=` / `claude mcp list` | `t-claude-facts.log` (รายละเอียดใน setup-report ข้อ 5) | PASS | ตรงกับสเปกทุกข้อ |
| 24 | Playwright MCP ผ่าน stdio จริง (ไม่ล็อกอิน) | `t8-mcp-probe.log`, `mcp-probe-transcript.jsonl` (13 บรรทัด), `mcp-probe-example.png`: initialize → tools/list 25 → navigate `Page Title: Example Domain` → screenshot 21016 bytes | PASS | ใช้คำสั่งจาก shared mcp.json ตรงตัว |
| 25 | JupyterLab `/lab` = 200 | `t9-jupyter.log`: `host.docker.internal:8892/lab -> 200`, container IP `:8888/lab -> 200`, ภายใน 200 | PASS | |
| 26 | ไม่โหลด .env ส่วนตัวในการทดสอบ | `t9-jupyter.log`: จำนวน env ที่มี TOKEN/_KEY = 0 | PASS | |
| 27 | ล็อกอิน yolo1..yolo5 | — | SKIP | ต้องล็อกอิน (ผู้ใช้ทำเอง) |
| 28 | ล็อกอิน cyolo1..cyolo5 + ยืนยัน token ด้วย `codex exec` | — | SKIP | ต้องล็อกอิน |
| 29 | Claude เห็น skill shared-check (รหัสตรงไฟล์) / `/mcp` เห็น playwright | — | SKIP | ต้องล็อกอิน |
| 30 | เปิดหลายบัญชีพร้อมกันใช้งานจริง | config root แยกกัน (ข้อ 5) | SKIP | ต้องล็อกอิน |
| 31 | AI ใช้ Playwright MCP ผ่าน yoloN/cyoloN | MCP ใช้ได้ระดับ stdio (ข้อ 24) | SKIP | ต้องล็อกอิน |
