# LAB 004 · ข้อกำหนดการสร้างแบบละเอียด (สำหรับ AI อ้างอิง)

เอกสารนี้เก็บข้อกำหนดละเอียดที่เคยอยู่ใน README (พรอมต์ backend, HTML, deploy และขั้นตอน deploy ของผู้ประสานงานเดิม) ไว้ให้ AI ใช้อ้างอิงเมื่อสร้างหรือตรวจงาน ผู้เรียน **ไม่จำเป็นต้องอ่าน** ไฟล์นี้ พรอมต์สามข้อใน [README](../README.md) ใช้ได้โดยไม่ต้องอ่านไฟล์นี้

ข้อกำหนดด้านล่างตรงกับการ implement อ้างอิงที่อยู่ใน `api/`, `web/` และ `deploy/` ของโฟลเดอร์นี้ ถ้าสภาพแวดล้อมจริงต่างไป (เช่น flag ของ CLI เวอร์ชันใหม่) ให้ยึดผลจากการตรวจจริงและรายงานความต่าง ห้ามเดา

---

## A · สร้าง Backend

คัดลอกพรอมต์ด้านล่างไปวางใน `yolo3` ใน devtools

##### ข้อกำหนดเดิม 1 · Backend

```text
LAB 004 ขั้นที่ 1: สร้าง backend ใน /workspace/04_API_MultiAccount_Server/api
ถ้ายังไม่มี ให้สร้างโฟลเดอร์ /workspace/04_API_MultiAccount_Server/api และโฟลเดอร์ย่อยที่จำเป็น ทำงานเฉพาะภายใต้ /workspace/04_API_MultiAccount_Server เท่านั้น
ไฟล์ที่มีอยู่แล้วต้องเก็บไว้ และแก้เฉพาะส่วนที่จำเป็น
ถ้ามีไฟล์อยู่แล้ว ให้ตรวจเทียบกับข้อกำหนดนี้ แก้เฉพาะจุดที่ไม่ตรง แล้วรันเทสต์ ห้ามเขียนทับทั้งโฟลเดอร์
ห้ามล็อกอิน ห้ามเรียกโมเดลจริง ห้าม deploy ห้ามอ่านค่า credential

## Endpoint
- GET /health  ไม่ต้องใช้ token · บอกว่า CLI แต่ละตัวรันได้ (ผ่าน wrapper --version) · ห้ามบอกข้อมูลบัญชี
  ต้องเขียนชัดว่า health ไม่ได้พิสูจน์ว่าล็อกอินใช้ได้
- GET /v1/models  ต้องใช้ Bearer token · รายการโมเดล, effort ต่อโมเดล, บัญชีต่อ provider
  (credential_file_present = ดูแค่ว่ามีไฟล์ ห้ามเปิดไฟล์), limits, พารามิเตอร์ที่รองรับ
- POST /v1/chat/completions  ต้องใช้ Bearer token · รูปแบบคล้าย OpenAI
  ฟิลด์ที่รับ: model, messages, reasoning_effort, account, provider, stream(false เท่านั้น)
  ฟิลด์อื่นทั้งหมดตอบ 400 unsupported_parameter (เช่น max_completion_tokens, max_tokens, temperature, tools)
  ห้ามอ้างว่ารองรับ max_completion_tokens · usage เป็น null

## โมเดลและ effort (มาจากผลจริงของ LAB 003)
- fable, opus (claude): low medium high xhigh max
- gpt-6-astra (codex): low medium high xhigh max
- gpt-6-sol, gpt-6-luna (codex): none low medium high xhigh max
- minimal ห้ามมี · ค่าอื่นตอบ 400 unsupported_reasoning_effort · ค่าเริ่มต้น medium

## บัญชีและ wrapper
- บัญชีตั้งได้ด้วย CLAUDE_ACCOUNTS / CODEX_ACCOUNTS ค่าเริ่มต้น yolo1 / cyolo1 (1 บัญชีต่อ provider)
  ชื่อต้องเป็น yolo1..yolo5 / cyolo1..cyolo5 เท่านั้น บัญชีที่ไม่ได้เปิดตอบ 400 ไม่มีไฟล์ credential ตอบ 503
- API ต้องเรียกโมเดลผ่าน wrapper ชื่อ yoloN / cyoloN ที่อยู่ใน container ของ API เอง (api/wrappers/lab04-cli + symlink)
  ห้ามแก้หรือคัดลอก wrapper เดิมของ devtools · wrapper ใหม่ต้องแคบกว่า:
  - เลือก config dir ที่เป็นสำเนา: CLAUDE_CONFIG_DIR=/data/accounts/claude/yoloN, CODEX_HOME=/data/accounts/codex/cyoloN
  - รับแค่ --model --effort (Codex เพิ่ม --output-last-message ที่ต้องอยู่ใน $TMPDIR) หรือ --version อย่างอื่นปฏิเสธ
  - พรอมต์เข้าทาง stdin · ห้ามใช้ --dangerously-skip-permissions / --dangerously-bypass-approvals-and-sandbox
  - Claude: -p --output-format json --no-session-persistence --tools "" --strict-mcp-config
            --disable-slash-commands --setting-sources "" --permission-mode dontAsk
  - Codex: exec --skip-git-repo-check --ephemeral --ignore-user-config --ignore-rules --sandbox read-only
           --color never -C "$PWD" -c model_reasoning_effort=... -c approval_policy=never
           -c cli_auth_credentials_store=file -o <file> -
  - unset ตัวแปร auth ที่อาจทับบัญชี (ANTHROPIC_API_KEY, OPENAI_API_KEY ฯลฯ)
  ยืนยัน flag ทุกตัวกับ --help ของเวอร์ชันจริงก่อนใช้ ถ้าไม่มีจริงให้รายงาน ห้ามเดา

## การรัน subprocess
- asyncio.create_subprocess_exec แบบ argv list ห้ามใช้ shell · พรอมต์ส่งทาง stdin ไม่ใส่ใน argv
- HOME คงที่เป็น home ของผู้ใช้ app ใน container ห้ามเปลี่ยน HOME ต่อ request
- ต่อ request: cwd ว่างและ TMPDIR ของตัวเอง ลบทิ้งเมื่อจบ · env ขั้นต่ำ ไม่ส่ง env ของ server ต่อ
- timeout (ค่าเริ่ม 300 s) ฆ่าทั้ง process group · จำกัดขนาด stdout/stderr · ตัดคำตอบยาวเกิน 24,000 ตัวอักษร (finish_reason=length)
- จำกัด body 256 KiB ทั้งกรณีมี Content-Length และกรณี chunked ที่ไม่มี Content-Length (นับไบต์ระหว่างอ่าน)
- จำกัด 40 ข้อความ, 8,000 ตัวอักษรต่อข้อความ, 48,000 ตัวอักษรรวม, ข้อความสุดท้ายต้องเป็น user
- concurrency ต่อ (provider, account) ค่าเริ่ม 1 และรวมทั้ง server ค่าเริ่ม 4 · ไม่ว่างตอบ 429

## ความลับและ error
- token: server เก็บแค่ SHA-256 (API_TOKEN_SHA256) เทียบด้วย hmac.compare_digest ไม่มีค่านี้ต้องไม่ยอมเริ่ม
- CORS: origin ที่ระบุชัดเท่านั้น (http://127.0.0.1:8005, http://localhost:8005) ห้าม * และห้าม null · ไม่ใช้ cookie
- error ที่ส่งกลับเป็นข้อความคงที่ตามประเภท (upstream_auth_error, upstream_rate_limited, cli_timeout …) ห้ามส่ง stderr/stdout ดิบ
  Codex พิมพ์พรอมต์ซ้ำใน stderr ให้จัดประเภทจากบรรทัด ERROR เท่านั้น
- log ได้แค่ request id, provider, model, effort, account, จำนวนข้อความ, จำนวนตัวอักษร, สถานะ, เวลา
  ห้าม log เนื้อข้อความ คำตอบ token หรือ traceback · validation error ห้ามสะท้อนค่าที่ส่งมา

## ประวัติแชต
- รวม messages เป็นพรอมต์เดียว: คำอธิบายสั้น + CONVERSATION_JSON (json.dumps, ensure_ascii=False)

## ไฟล์และการทดสอบ
- api/app/{catalog,config,transcript,runner,main}.py, api/wrappers/lab04-cli
- api/requirements.txt pin ทุกแพ็กเกจรวม dependency ย่อย, requirements-dev.txt สำหรับเทสต์
- api/Dockerfile: base image pin tag+digest, ติดตั้ง Claude Code และ Codex เวอร์ชันเดียวกับ devtools,
  symlink yolo1..5 / cyolo1..5 ไปที่ wrapper, ผู้ใช้ไม่ใช่ root, ไม่มี credential ใน image
- .dockerignore กัน credential/secret/เทสต์ออกจาก image
- unittest ด้วย CLI ปลอม (tests/fakes) ครอบคลุม: argv/env/HOME/cwd, wrapper ปฏิเสธ flag อันตราย,
  effort ผิด, max_completion_tokens, บัญชีผิด/ไม่มีไฟล์, body เกินทั้งแบบมีและไม่มี Content-Length,
  timeout, error ไม่รั่ว, log ไม่มีเนื้อข้อความ, concurrency ต่อบัญชี, CORS

รันเทสต์ด้วย venv ชั่วคราวนอกโฟลเดอร์งาน รายงานผลจริง PASS/FAIL พร้อมจำนวนเทสต์
ทำเฉพาะขั้นนี้ แสดงตารางไฟล์ที่สร้าง/แก้และหน้าที่ของแต่ละไฟล์ แล้วหยุดรอ
```

**สิ่งที่ต้องตรวจหลัง `yolo3` ทำเสร็จ**

```bash
cd /workspace/04_API_MultiAccount_Server/api
python3 -m venv /tmp/lab04venv && /tmp/lab04venv/bin/pip install -q -r requirements-dev.txt
/tmp/lab04venv/bin/python -m unittest discover -s tests 2>&1 | tail -3
```

ผลจากโฟลเดอร์ต้นฉบับของแลปนี้ (CLI ปลอม ไม่ได้เรียกโมเดลจริง): `Ran 29 tests … OK`

> 🔍 **จุดที่ผู้เรียนต้องตรวจ:** เปิด `api/wrappers/lab04-cli` แล้วหาคำว่า `dangerously` ต้องเจอเฉพาะในคอมเมนต์ที่บอกว่า **ไม่ใช้** ถ้าไปอยู่ในบรรทัดคำสั่ง แปลว่า wrapper กว้างเกินไป

---

## B · สร้างหน้าแชต index.html

##### ข้อกำหนดเดิม 2 · HTML

```text
LAB 004 ขั้นที่ 2: สร้างหน้าแชตไฟล์เดียว /workspace/04_API_MultiAccount_Server/web/index.html
และ container เสิร์ฟไฟล์ static แยกจาก API ถ้ามีไฟล์แล้วให้ตรวจเทียบข้อกำหนดและแก้เฉพาะจุด ห้าม deploy

## หน้าเว็บ
- ไฟล์เดียว ไม่มี CDN หรือไฟล์ภายนอก มี <script> และ <style> อย่างละหนึ่งก้อน ไม่มี style= หรือ onclick= ใน HTML
- แถบซ้าย: API base URL (ค่าเริ่ม http://127.0.0.1:8004), ช่อง token แบบ password, ปุ่มเชื่อมต่อ
  token อยู่ในตัวแปร JavaScript เท่านั้น ห้าม localStorage/sessionStorage/cookie
- dropdown Provider → Model → Effort → Account เติมจาก /v1/models เท่านั้น
  effort เปลี่ยนตามโมเดล (Astra ไม่มี none, Sol/Luna มี none) account เปลี่ยนตาม provider
- ป้ายสถานะสามระดับ แยกให้ชัด: API ตอบ /health · Token ผ่าน /v1/models · บัญชีตอบจริงสำเร็จ (เฉพาะหลังได้คำตอบจริง)
- เชื่อมต่อใหม่: ล้าง catalog และสถานะเดิมก่อนเสมอ ถ้าเชื่อมต่อใหม่ไม่ผ่าน dropdown/ช่องพิมพ์ต้องปิด
  ห้ามเหลือตัวเลือกเก่าที่ส่งไป endpoint ที่เพิ่งล้มเหลวได้
  ระหว่างตรวจหรือระหว่างรอคำตอบ ให้ล็อกช่อง URL, token และปุ่มเชื่อมต่อ
- transcript แบบแชตทั่วไป: ข้อความผู้ใช้ชิดขวา ผู้ช่วยชิดซ้าย แต่ละคำตอบมีป้าย provider/model, effort, account, เวลา,
  จำนวนข้อความประวัติที่ส่ง · แสดงเนื้อหาด้วย textContent เท่านั้น (ไม่แปลง Markdown ไม่ใช้ innerHTML)
- ส่ง (ปุ่มหรือ Ctrl+Enter) ส่งประวัติทั้งหมดที่สำเร็จ + ข้อความใหม่ · ถ้าล้มเหลว ข้อความนั้นไม่ถูกนับในประวัติและคืนกลับช่องพิมพ์
- ล้างแชต, ดาวน์โหลด transcript เป็น JSON (ไม่มี token), ตัวนับจำนวนข้อความ/ตัวอักษรเทียบเพดาน
- เปลี่ยนโมเดลหรือบัญชีกลางบทสนทนา ให้แสดงข้อความแจ้งว่าประวัติจะถูกส่งเป็นข้อความให้ตัวใหม่ และบัญชีไม่แชร์ session
- error แสดงประเภท, HTTP status, request id และข้อความจาก API
- รองรับโหมดมืด และจอแคบ

## container ของหน้าเว็บ (web/)
- nginx แบบ unprivileged pin tag+digest เสิร์ฟ index.html อย่างเดียว ไม่ proxy ไป API
- build_csp.py คำนวณ sha256 ของ <script>/<style> ตอน build แล้วใส่ CSP:
  default-src 'none'; script-src/style-src ด้วย hash; img-src data:; connect-src เฉพาะ origin ของ API;
  base-uri 'none'; form-action 'none'; frame-ancestors 'none' พร้อม header nosniff, no-referrer, DENY frame
- .dockerignore ให้เข้า image เฉพาะไฟล์ที่ใช้

ตรวจ syntax ของ JavaScript และลอง build_csp.py ในเครื่อง ห้ามติดตั้งเบราว์เซอร์หรือเปิด server ทดสอบค้างไว้
ทำเฉพาะขั้นนี้ แล้วหยุดรอ
```

---

## C · เตรียม Deployment

##### ข้อกำหนดเดิม 3 · Deployment

```text
LAB 004 ขั้นที่ 3: เขียนสคริปต์ deploy ใน /workspace/04_API_MultiAccount_Server/deploy ห้ามรันจริงในขั้นนี้
ข้อเท็จจริง: docker ใน devtools คือ daemon ชั้นใน ใช้สร้าง sibling container ไม่ได้
daemon ชั้นนอกชื่อ docker-desktop เข้าได้ผ่าน control host ทาง SSH root@host.docker.internal พอร์ต 22022
control host เองเป็น container ดังนั้น localhost ของมันไม่ใช่พอร์ตที่ Docker Desktop publish

## deploy/lab04.sh (รันบน control host)
- ไม่ยอมทำงานถ้า docker info --format '{{.Name}}' ไม่ใช่ docker-desktop
- ตรวจ config ทุกค่าก่อนนำไปใส่คำสั่ง docker: ชื่อบัญชี yolo[1-5]/cyolo[1-5], ชื่อ container/volume/network,
  พอร์ต, path (ห้าม ..), PROBE_HOST · path ที่ต้อง mkdir ส่งเป็น argument ห้ามต่อเป็นสตริง shell
- แตะเฉพาะของที่มี label lab04=<หน้าที่> (api, web, loader, accounts, net) เจอชื่อซ้ำที่ไม่มี label ให้หยุด ห้ามลบ
- คำสั่งย่อย: check, build, token, creds, up, verify, smoke [--live], status, logs [N], down [--purge]
- token: สุ่ม 32 ไบต์ลง deploy/.secrets/api_token (chmod 600) ห้ามพิมพ์ค่า · container ได้แค่ SHA-256
- creds: สร้าง named volume, container loader ที่หยุดอยู่ (label lab04=loader),
  docker cp จาก devtools เป็น tar stream ส่งต่อเข้า loader ไม่ผ่านดิสก์ ไม่พิมพ์ค่า
  คัดลอกเฉพาะ yoloN/.credentials.json และ cyoloN/auth.json แล้ว chown ให้ uid 10001 · รายงานแค่ว่ามีไฟล์
- up: API และ web ผูก 127.0.0.1:8004 / 127.0.0.1:8005 · --read-only, --cap-drop ALL, no-new-privileges,
  จำกัด pids/memory · tmpfs ที่ /tmp และ /home/app (HOME ต้องเขียนได้) · รอ healthy แล้ว verify
- verify: เช็คสองทาง (ผ่าน network ของ container และผ่านพอร์ตที่ publish ด้วย PROBE_HOST=host.docker.internal)
  FAIL ต้องรายงานว่า FAIL ห้ามเหมาเป็น PASS
- smoke: health, 401 ไม่มี token, models, CORS ของหน้าเว็บ/origin แปลกปลอม, astra+none=400, fable+minimal=400,
  max_completion_tokens=400, บัญชีที่ไม่เปิด=400, CSP ของหน้าเว็บ · --live เท่านั้นที่เรียกโมเดลจริง
- deploy/lab04.env.example ไม่มีความลับ

## deploy/remote.sh (รันใน devtools)
- open: ssh -F /dev/null -o ControlMaster=yes -o ControlPath=<โฟลเดอร์ชั่วคราว 700>/ctl -o ControlPersist=2h -fN
  ผู้ใช้พิมพ์รหัสผ่านเอง · known_hosts อยู่ในโฟลเดอร์ชั่วคราว · ไม่ใช้คีย์ ไม่แก้ ~/.ssh
- ทุกคำสั่งหลังจากนั้นใช้ ssh -S <socket> -o BatchMode=yes
- daemon, sync (tar ไปที่ /root/workspace/CWN/Teaching/00_setup/04_API_MultiAccount_Server ยกเว้น deploy/.secrets),
  run <คำสั่งย่อยที่อนุญาต>, reveal-token (ผู้ใช้รันเองและต้องพิมพ์ yes), close

ตรวจ bash -n และทดสอบการปฏิเสธ config ผิดแบบ offline เท่านั้น ห้ามเปิด SSH ห้าม deploy
ทำเฉพาะขั้นนี้ แล้วหยุดรอ
```

---

## D · ขั้นตอน deploy แบบละเอียดเดิม (SSH ControlMaster)

### D.1 · ผู้เรียนเปิดการเชื่อมต่อ SSH เอง (ห้ามให้ AI พิมพ์รหัสผ่าน)

ใน 🖥️ Terminal **อีกแท็บ** (ไม่ใช่ในช่องสนทนาของ `yolo3`)

```bash
cd /workspace/04_API_MultiAccount_Server
bash deploy/remote.sh open      # ถามยืนยัน host key (พิมพ์ yes) แล้วถามรหัสผ่านหนึ่งครั้ง
bash deploy/remote.sh daemon    # ต้องเห็น devtools = daemon ชั้นใน และ control host = docker-desktop
```

socket อยู่ใน `/tmp/lab04-ssh-<uid>/` ใช้ได้เฉพาะผู้ใช้เดียวกันใน devtools `yolo3` จึงใช้การเชื่อมต่อนี้ต่อได้โดยไม่ต้องรู้รหัสผ่าน และปิดเองเมื่อว่าง 2 ชั่วโมง

### D.2 · ให้ `yolo3` สั่ง deploy ผ่าน socket นั้น

##### ข้อกำหนดเดิม 4 · สั่ง deploy

```text
LAB 004 ขั้นที่ 4: deploy ผ่าน deploy/remote.sh ที่ฉันเปิดการเชื่อมต่อ SSH ไว้แล้ว
ห้ามพิมพ์หรือเดารหัสผ่าน ห้ามรัน reveal-token ห้ามอ่านไฟล์ใน deploy/.secrets ห้ามเรียก smoke --live
ห้ามใช้ docker ของ devtools สร้าง container

รันตามลำดับ หยุดทันทีที่ขั้นใดล้มเหลว แล้วรายงานข้อความ error จริง:
1. bash deploy/remote.sh daemon
2. bash deploy/remote.sh sync
3. bash deploy/remote.sh run check
4. bash deploy/remote.sh run build
5. bash deploy/remote.sh run token
6. bash deploy/remote.sh run creds
7. bash deploy/remote.sh run up
8. bash deploy/remote.sh run smoke

รายงานเป็นตาราง ขั้น | ผลจริง | PASS/FAIL และระบุชัดว่า smoke เป็นแค่ readiness ยังไม่ใช่หลักฐานว่าบัญชีตอบได้จริง
แล้วหยุดรอ
```

ผลจริงของการ deploy อยู่ใน README หัวข้อ 5.1 (ไม่คัดลอกซ้ำที่นี่)

### D.3 · ผู้เรียนดู token และเปิดหน้าเว็บ

```bash
bash deploy/remote.sh reveal-token   # รันเองใน Terminal พิมพ์ yes · ห้ามวางค่าลงในแชตกับ AI หรือในภาพหน้าจอ
```

เปิดเบราว์เซอร์บน Windows ที่ **http://localhost:8005** (หรือ `http://127.0.0.1:8005`) วาง token แล้วกด **เชื่อมต่อ**

---

## E · ติดตั้ง OpenAI SDK แบบแยก venv (ไม่บังคับ)

```bash
python3 -m venv /tmp/lab04-sdk && /tmp/lab04-sdk/bin/pip install -q openai
/tmp/lab04-sdk/bin/python examples/openai_client.py                     # fable / low / บัญชีค่าเริ่มต้น
/tmp/lab04-sdk/bin/python examples/openai_client.py --model gpt-6-astra --effort low --account cyolo1
```
