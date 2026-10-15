# checklist — ผลทดสอบจริง (2026-10-15, เวลาไทย)

container ทดสอบ: `mad-test` (compose project `mad-test`) · SSH `2233` · JupyterLab `8896`
image `tuchsanai/multi-account-devtool:2569_1` = `sha256:b423af3b443f…` (tag `:latest` ID เดียวกัน) · volume `mad-test_ai-accounts`, `mad-test_multi-account-dind` (แยกจาก volume `ai-accounts` ที่ใช้งานจริง)
env_file ชี้ไฟล์ที่ไม่มี (`DEVTOOLS_ENV_FILE=/nonexistent/.env`) — ไม่ได้โหลด .env ส่วนตัว
รอบนี้เปลี่ยนจากรอบก่อน: เพิ่ม `requirements.txt` (`vastai~=1.8`) + ขั้น `pip install -r` ใน Dockerfile; Claude/Codex อัปเดตตาม `latest` ตอน build

| # | รายการ | หลักฐาน | ผล | เหตุผล |
|---|---|---|---|---|
| 1 | build image | `docker build` exit 0, 22 ขั้น (build ใหม่ทั้งหมด ไม่มี cache) | PASS | |
| 2 | push `2569_1` | `2569_1: digest: sha256:9638853cece0…` exit 0 | PASS | ล็อกอิน Docker Hub ไว้แล้วบน host |
| 3 | `vastai~=1.8` จาก requirements.txt | `pip show vastai` → `1.8.3`, `vastai --help` เรียกได้ | PASS | |
| 4 | `claude`/`codex` ติดตั้งตามวิธีในสเปก | `2.1.300 (Claude Code)`, `codex-cli 0.162.1` | PASS | |
| 5 | 10 คำสั่ง `--version` (yolo1..5, cyolo1..5) | 10/10 | PASS | |
| 6 | docker exec: claude/codex/yolo1/cyolo1 | 4/4 | PASS | |
| 7 | SSH key `Devtool_SSH/devtoolSSH`: claude/codex/yolo1/cyolo1 | `ssh -i … -p 2233 root@localhost` BatchMode, 4/4 | PASS | |
| 8 | JupyterLab Terminal: claude/codex/yolo1/cyolo1 | เปิด terminal ผ่าน REST + websocket (มี XSRF) 4/4 | PASS | |
| 9 | SSH password login | `PasswordAuthentication yes` ใน `sshd_config.d` (root/passwd) | PASS | |
| 10 | config root คนละโฟลเดอร์ (find) | dry-run ได้ `CLAUDE_CONFIG_DIR`/`CODEX_HOME` ไม่ซ้ำ 10 ค่า, find เจอ 10 โฟลเดอร์ | PASS | |
| 11 | installer รอบ 2 ไม่ทำลายของเดิม | checksum ทุกไฟล์ + เป้า symlink (รวม SKILL.md ที่มีรหัส shared-check) ก่อน = หลัง; `created=0 kept=50 warnings=0` | PASS | ตัด `CODEX_HOME/tmp/` และ `playwright-output/` ออก (ไฟล์ runtime ที่ Codex/MCP เขียนเอง) |
| 12 | ไม่แก้ .bashrc / Git / SSH | sha256 ของ `.bashrc`, `git config --global`, authorized_keys + sshd_config.d ก่อน = หลัง; git 2.55.0 | PASS | |
| 13 | `cyoloN mcp list` เห็น playwright | 5/5 | PASS | ไม่ต้องล็อกอิน |
| 14 | shared-check ทุกบัญชี `readlink -f` ไปไฟล์เดียวกัน | yolo1..5 → `.Claude/shared/skills/shared-check/SKILL.md`; cyolo1..5 → `.Codex/shared/skills/shared-check/SKILL.md` | PASS | |
| 15 | ไม่มี credential ใน shared | find `.credentials.json`/`auth.json`/`.claude.json` ใน shared = 0 | PASS | |
| 16 | skill ใหม่ใน shared เห็นทุกบัญชีโดยไม่รัน installer ซ้ำ | `zz-new-test` เห็น 10/10 (Codex หลังเปิด wrapper 1 ครั้ง); ลบแล้วเหลือ 0 และ checksum กลับเท่าเดิม | PASS | |
| 17 | `docker compose up --force-recreate` ของใน volume ยังอยู่ | diff รายการ checksum 19 รายการ ก่อน/หลัง recreate = เหมือนกัน | PASS | รอบแรกได้ FAIL เพราะ quoting ใน script ทดสอบผิด แก้แล้วทดสอบซ้ำ |
| 18 | Playwright MCP ตาม shared mcp.json ผ่าน stdio | `mcp_stdio_probe.py`: initialize → tools/list 25 → navigate `Page Title: Example Domain` → screenshot PNG 1280×720 83320 bytes | PASS | ต้องบันทึกไฟล์ใน `--output-dir` หรือ `/workspace` (ดู setup-report ข้อ 5) |
| 19 | Docker-in-Docker | `docker version` ใน container → server 29.9.1 | PASS | |
| 20 | JupyterLab `/lab` = 200 | `http://localhost:8896/lab` → 200 | PASS | |
| 21 | ไม่โหลด .env ส่วนตัวเข้า container ทดสอบ | env ที่ชื่อ `GITHUB_TOKEN`/`HF_TOKEN`/`VAST_API_KEY`/`DOCKER_TOKEN` = 0 | PASS | |
| 22 | ล็อกอิน yolo1..yolo5 + เรียก skill shared-check | — | SKIP | ต้องล็อกอิน (ผู้ใช้ทำเอง) |
| 23 | yoloN `/mcp` เห็น playwright | — | SKIP | ต้องล็อกอิน |
| 24 | cyoloN `codex login --device-auth` + ยืนยันด้วย `codex exec` | — | SKIP | ต้องล็อกอิน |
