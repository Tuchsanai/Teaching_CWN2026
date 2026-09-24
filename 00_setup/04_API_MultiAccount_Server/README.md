# API หลายบัญชี: FastAPI + หน้าแชต index.html ที่เรียก Claude Code และ Codex CLI

## 1 · ภาพรวมสถาปัตยกรรม

![ภาพแนวคิดฉบับร่าง: devtools เป็นศูนย์ควบคุม สร้าง index.html และสั่ง build พร้อมคัดลอก config บัญชีไปยัง API container ใหม่ที่มี FastAPI, yoloN/cyoloN และโมเดล Fable/Opus กับ Astra/Sol/Luna ส่วนเบราว์เซอร์ส่งคำถามและรับคำตอบกับ API container โดยตรง](assets/architecture.png)

*ภาพแนวคิด **ฉบับร่าง** ไม่ใช่ภาพหน้าจอจริง และยังไม่ใช่ฉบับสุดท้าย (ฉบับสุดท้ายจะสร้างแยกภายหลัง) ภาพนี้ยังไม่ได้แสดง container ของหน้าเว็บ (`lab04-web`) และเส้นทาง SSH ไปยัง control host ให้ยึดผังข้อความด้านล่างเป็นหลัก*

```text
 เบราว์เซอร์บน Windows host
   │ ① เปิดหน้าเว็บ  http://localhost:8005 ─────────▶ lab04-web  (nginx เสิร์ฟ index.html อย่างเดียว)
   │ ② fetch + Bearer token  http://127.0.0.1:8004 ─▶ lab04-api  (FastAPI)
   │                                                     └─ yolo1 / cyolo1  (wrapper ใน container นี้)
   │                                                          └─ claude -p / codex exec
   │                                                               └─ volume lab04-accounts (สำเนา credential)
 devtools (JupyterLab + yolo3) ── ssh -S <socket> ──▶ control host :22022 ── docker ──▶ daemon "docker-desktop"
   └─ docker ในตัวเอง = daemon ชั้นใน (ไม่ใช้)            (lab04-api, lab04-web, devtools เป็นพี่น้องกัน)
```

ทำไมหน้าเว็บต้องมี container ของตัวเอง: ถ้าเปิด `index.html` แบบ `file://` เบราว์เซอร์จะส่ง origin เป็น `null` ซึ่ง API ไม่อนุญาต (การอนุญาต `null` เปิดทางให้หน้าเว็บอื่นใช้ได้ด้วย) จึงเลือกทางที่เล็กที่สุดคือ nginx ที่เสิร์ฟไฟล์เดียวบนพอร์ต `8005`

![ภาพแนวคิดฉบับร่างของหน้าแชต: แถบเลือก Provider, Model, Effort, Account ด้านบน กล่องสถานะ FastAPI connected และตัวอย่างข้อความสนทนา](assets/chat-ui-concept.png)

*ภาพแนวคิด **ฉบับร่าง** ไม่ใช่ภาพหน้าจอจริง หน้าเว็บที่สร้างจริงจัดวางต่างจากภาพนี้ (ตั้งค่าอยู่แถบซ้าย สถานะเป็นสามป้ายด้านบน) ข้อความในภาพเป็นตัวอย่างสมมติ ไม่ใช่คำตอบจากโมเดล*

---

## 2 · สร้าง Backend

พรอมต์ทั้งสามชุดด้านล่างสมมติว่ายังไม่มีโค้ดใดเลย ให้คัดลอกไปวางตามลำดับในบทสนทนาเดียวกับ AI (`yolo3`) ที่เปิดผ่าน JupyterLab ใน devtools ซึ่งบัญชี yolo/cyolo ล็อกอินไว้พร้อมแล้ว

##### 📋 พรอมต์ 1 · สร้าง Backend

```text
ช่วยสร้าง backend ใหม่ด้วย FastAPI ตั้งแต่ศูนย์ในตำแหน่งที่ทำงานอยู่ตอนนี้ โดยเลือกชื่อไฟล์และสร้างโครงสร้างที่จำเป็นเองได้เลย
1. API ต้องรันใน container ของตัวเองแยกจาก devtools ส่วน devtools ใช้เป็นแค่ศูนย์สั่งงานเท่านั้น
2. มี endpoint POST /v1/chat/completions แบบเดียวกับ OpenAI รับ messages, model, reasoning_effort และ account โดยมี provider เป็นตัวเลือกเสริม
3. มี endpoint ตรวจสุขภาพ และ endpoint บอกรายการโมเดล ระดับ effort และบัญชีที่ใช้ได้ เพื่อให้หน้าเว็บนำไปสร้างตัวเลือก
4. โมเดลที่ต้องรองรับ: Claude รุ่น fable และ opus ใช้ effort ได้ low, medium, high, xhigh, max ผ่านตัวเรียกของบัญชี yolo ส่วน Codex รุ่น gpt-6-astra ใช้ effort ชุดเดียวกัน และ gpt-6-sol กับ gpt-6-luna ใช้ได้เพิ่มอีกระดับคือ none ผ่านตัวเรียกของบัญชี cyolo
5. อย่างน้อยต้องใช้ account1 ที่มีอยู่แล้วได้ และรองรับบัญชีอื่นที่ตรวจพบว่าตั้งค่าไว้จริง
6. ติดตั้ง CLI ไว้ใน container ของ API เอง และคัดลอกสำเนา credential ที่ล็อกอินไว้แล้วไปเก็บในที่เก็บส่วนตัวอย่างปลอดภัย ห้ามเขียนทับต้นฉบับ ห้ามแสดงค่าความลับ และห้ามใส่ไว้ใน image
7. ส่งประวัติแชตที่มากับแต่ละคำขอให้โมเดลเห็นทั้งหมด ตอบเฉพาะคำตอบจริงจากโมเดล และปฏิเสธพารามิเตอร์ที่ทำไม่ได้พร้อมบอกเหตุผล
8. ป้องกัน API ด้วย token ตั้งเพดานขนาดคำขอและเวลาให้เหมาะสม และข้อความ error ต้องอ่านเข้าใจได้โดยไม่เผยความลับ
9. เก็บค่าตั้งค่าไว้ในไฟล์ .env ไม่ผูกกับตำแหน่งโฟลเดอร์ใดโฟลเดอร์หนึ่ง
10. เลือกวิธีเขียนเอง ตรวจ help ของ CLI ที่ติดตั้งอยู่จริง และทดสอบโดยไม่เรียกโมเดลจริงที่เสียเงิน เสร็จแล้วสรุปสิ่งที่สร้างและผลทดสอบ แล้วรอพรอมต์ถัดไป
```

---

## 3 · สร้างหน้าแชต

##### 📋 พรอมต์ 2 · สร้างหน้าแชต

```text
ต่อไปช่วยสร้างหน้าแชตเป็นไฟล์ index.html ใหม่ตั้งแต่ศูนย์ ที่ใช้งานกับ backend ที่เพิ่งสร้างในขั้นก่อน
1. เสิร์ฟหน้าเว็บจาก container แยกของตัวเอง และให้เบราว์เซอร์เรียก container ของ API โดยตรง
2. มี dropdown เลือก provider, model, effort และ account ที่ดึงจากรายการของ API และปรับตัวเลือกให้ตรงกับที่เลือกอยู่
3. ให้ผู้ใช้กรอกที่อยู่ API และ token ในช่องแบบรหัสผ่านเอง ห้ามฝังความลับไว้ในไฟล์ และไม่จำ token ไว้ถาวร
4. หน้าแชตอ่านง่าย ใช้ได้ทั้งจอกว้างและจอแคบ ส่งประวัติทั้งหมดไปกับทุกคำถาม และแสดงสถานะกำลังทำงานกับ error ให้ชัด
5. มีปุ่มเริ่มแชตใหม่ และปุ่มดาวน์โหลดบทสนทนา
6. แสดงสถานะตามจริงว่าเชื่อมต่อ API ได้หรือยัง token ผ่านหรือยัง และได้คำตอบจริงหรือยัง
7. เลือกหน้าตาและไฟล์ที่จำเป็นเอง เสร็จแล้วสรุปสิ่งที่ทำ แล้วรอพรอมต์ถัดไป
```

---

## 4 · เปิดใช้งานและทดลอง

##### 📋 พรอมต์ 3 · เปิดใช้งานและทดลอง

```text
ต่อไปช่วย build และ deploy API กับหน้าแชตที่เพิ่งสร้างทั้งสองตัวให้ใช้งานได้จริง
1. ให้ทั้งสอง service รันเป็น container ระดับเดียวกับ devtools บน Docker host ที่ตั้งใจใช้ ห้าม deploy ลงใน Docker ชั้นในของ devtools
2. ตรวจหาช่องทางเข้าถึง Docker ที่ใช้ได้จริงเอง ห้ามเดา host, พอร์ต หรือ path ขึ้นมาเอง ถ้าไม่พบข้อมูลที่จำเป็น ให้ถามฉันเฉพาะส่วนที่ขาด
3. อ่านค่าตั้งค่าจากไฟล์ .env และถ้ายังไม่มี .env.example ให้สร้างพร้อมค่าตัวอย่างที่ไม่ใช่ความลับ ห้ามแต่งค่าความลับขึ้นเอง
4. ใช้พอร์ต 8004 สำหรับ API และ 8005 สำหรับหน้าเว็บเป็นค่าเริ่มต้นที่เปลี่ยนได้ใน .env ตรวจก่อนว่าชนกับอะไรไหม และห้ามหยุดหรือแก้ service อื่นที่ไม่เกี่ยวข้อง
5. คัดลอก credential ที่ล็อกอินไว้แล้วอย่างปลอดภัยตามที่ขอไว้ก่อนหน้า แล้วตรวจ health และรายการโมเดลให้ผ่าน
6. ทดลองแชตจริงบนหน้าเว็บ 10 รอบในบทสนทนาเดียว ใช้ Fable 5 รอบแล้วเปลี่ยนเป็น Astra อีก 5 รอบ โดยถามให้เห็นว่ายังจำเรื่องก่อนหน้าได้ เก็บภาพหน้าจอจริงที่อ่านออกและบทสนทนาไว้
7. ถ้ามี computer use ให้ใช้ ถ้าควบคุมเบราว์เซอร์ไม่ได้ให้บอกตรง ๆ พร้อมวิธีตรวจเองแบบง่ายที่สุด ห้ามแต่งผลหรือคำตอบขึ้นเอง
8. สุดท้ายให้ URL ที่ใช้ได้จริง บอกวิธีใส่ token อย่างปลอดภัยโดยไม่พิมพ์ค่าความลับออกมา และสรุปผลที่เกิดขึ้นจริง
```

---

## 5 · ผลจริงจากการ deploy และทดสอบ

### 5.1 · ผลการ deploy ของผู้ประสานงาน (24 ก.ย. 2026)

ผู้ประสานงานสั่งผ่าน 🖥️ Terminal ใน JupyterLab ด้วย SSH socket ของตัวเอง (`/tmp/lab04-coordinator.sock`) ซึ่งเทียบเท่ากับ `remote.sh run …` และบน control host โหลดค่าจาก `/root/workspace/DGX_2024/.env` ก่อนรัน `deploy/lab04.sh` (ไฟล์นี้เป็นของสภาพแวดล้อมผู้ประสานงาน ไม่ใช่ส่วนของแลป และไม่ได้เปิดเผยค่าในเอกสารนี้)

| ขั้น | ผลจริง | หลักฐานดิบ |
|---|---|---|
| daemon | control host ใช้ `docker-desktop` · devtools คือ `567edcb8c206` (ชั้นใน) | ภาพ [`02-jupyter-outer-docker.png`](assets/02-jupyter-outer-docker.png), [`03-deploy-preflight.png`](assets/03-deploy-preflight.png) |
| build | สร้าง `lab04-api:0.4.0` และ `lab04-web:0.4.0` สำเร็จ · wrapper ใน image รายงาน `2.1.281 (Claude Code)` และ `codex-cli 0.156.1` | [`build.log`](assets/build.log), ภาพ [`04-build-success.png`](assets/04-build-success.png) |
| token | สร้างไฟล์ token บน control host โดยไม่แสดงค่า | [`deploy.log`](assets/deploy.log) |
| creds | คัดลอก `claude/yolo1` และ `codex/cyolo1` · ใน volume มีแค่ `.credentials.json` และ `auth.json` (present) | [`deploy.log`](assets/deploy.log) |
| up + verify | healthy · พอร์ต `127.0.0.1:8004` / `127.0.0.1:8005` · PASS ทั้ง container network และพอร์ตที่ publish ผ่าน `host.docker.internal` | [`deploy.log`](assets/deploy.log) |
| smoke (readiness) รอบแรก | 11 PASS, 0 FAIL · ไม่มีการเรียกโมเดล | [`smoke.log`](assets/smoke.log) |
| smoke รอบล่าสุด (เพิ่มตรวจบัญชี N4) | **13 PASS, 0 FAIL** · ไม่มีการเรียกโมเดล | [`smoke-with-account-checks.log`](assets/smoke-with-account-checks.log), ภาพ [`12-account-checks.png`](assets/12-account-checks.png) |

![ภาพหน้าจอจริง: Terminal ใน JupyterLab รันคำสั่ง ssh -S /tmp/lab04-coordinator.sock ไปยัง control host พอร์ต 22022 แล้วรัน lab04.sh token, creds, up ผลแสดง copied claude/yolo1 และ codex/cyolo1, ไฟล์ credential present ทั้งสองไฟล์, published ports 127.0.0.1:8004 และ 127.0.0.1:8005 และ PASS สามรายการของ verify](assets/05-containers-running.png)

*ภาพหน้าจอจริงจาก 🖥️ Terminal ของ JupyterLab บน devtools: ขั้น token · creds · up · verify*

![ภาพหน้าจอจริง: Terminal ใน JupyterLab รัน lab04.sh smoke ผ่าน ssh -S ผลแสดง PASS 11 รายการ ได้แก่ health, 401 เมื่อไม่มี token, models, credential file, CORS ทั้งสองแบบ, astra+none 400, fable+minimal 400, max_completion_tokens 400, หน้าเว็บ 200 และ CSP ปิดท้ายด้วย smoke: 11 PASS, 0 FAIL](assets/08-api-smoke.png)

*ภาพหน้าจอจริงของ `smoke` รอบแรก (11 รายการ) · รอบล่าสุด 13 รายการที่รวม N4 อยู่ในหัวข้อ 5.4*

ข้อสังเกตจากการ deploy จริง: Claude Code ใน container **ใช้งานได้โดยคัดลอกแค่ `.credentials.json`** (ไม่ต้องใช้ `.claude.json`) และ Codex ตอบได้จริงด้วย `auth.json` อย่างเดียว

### 5.2 · พร้อม ≠ ใช้ได้จริง

| ระดับ | ดูจากไหน | พิสูจน์อะไร | ไม่ได้พิสูจน์อะไร |
|---|---|---|---|
| L0 | ป้าย **API: ตอบ /health** | container รันอยู่ และ wrapper `--version` รันได้ | บัญชีล็อกอินได้ |
| L1 | ป้าย **Token: ผ่าน /v1/models** | token ถูก และ CORS ผ่าน | บัญชีล็อกอินได้ |
| L2 | dropdown บัญชีขึ้น "มีไฟล์ credential" | มีไฟล์สำเนาใน volume | ไฟล์นั้นยังใช้ได้ |
| L3 | ป้าย **ตอบจริงสำเร็จ: claude/yolo1** | บัญชีนั้นตอบโมเดลจริงได้ในรอบนี้ | บัญชีอื่น หรือโมเดล/effort อื่น |

ป้าย L3 ขึ้นเฉพาะหลังได้คำตอบจริงเท่านั้น และแยกต่อ provider/account

### 5.3 · แชตจริง 10 รอบ ในบทสนทนาเดียว

ผู้ประสานงานพิมพ์ในหน้าเว็บจริงที่ `http://localhost:8005/` ผ่าน computer use ไม่มีการจำลองคำตอบ รอบ 1–5 ใช้ **claude / fable / low / yolo1** แล้วเปลี่ยนเป็น **codex / gpt-6-astra / low / cyolo1** ในรอบ 6–10 โดย **ไม่ล้างแชต** ตารางด้านล่างคัดลอกจาก [`assets/ten-exchanges.json`](assets/ten-exchanges.json) ตรงตามที่บันทึก (ข้อความเดียวกันอยู่ใน [`ten-exchanges.txt`](assets/ten-exchanges.txt) และ 5 รอบแรกใน [`fable-five-exchanges.txt`](assets/fable-five-exchanges.txt)) เครื่องหมาย `**` ในคำตอบเป็นข้อความดิบที่โมเดลส่งมา หน้าเว็บไม่ render Markdown

| # | provider / model / effort / account | ข้อความผู้ใช้ | คำตอบจริง | ส่งประวัติ (ข้อความ) | เวลา |
|---|---|---|---|---|---|
| 1 | claude / fable / low / yolo1 | ฉันชื่อเมย์ กำลังเปิดร้านกาแฟชื่อ Cloud Cup มีลาเต้ราคา 80 บาท ช่วยทักทายและจำข้อมูลนี้สำหรับบทสนทนานี้ ตอบสั้น ๆ ไม่เกินสองประโยค | สวัสดีค่ะคุณเมย์ ยินดีที่ได้รู้จักและขอให้ร้าน Cloud Cup ไปได้สวยนะคะ ฉันจำไว้แล้วว่าร้านของคุณมีลาเต้ราคา 80 บาทค่ะ | 1 | 6.1 s |
| 2 | claude / fable / low / yolo1 | ถ้าซื้อลาเต้สองแก้วแล้วลด 10% ต้องจ่ายเท่าไร? แสดงวิธีคิดสั้น ๆ | ลาเต้ 2 แก้ว = 80 × 2 = 160 บาท<br>ลด 10% = 160 × 0.10 = 16 บาท<br>ต้องจ่าย = 160 − 16 = \*\*144 บาท\*\* ค่ะ | 3 | 4.1 s |
| 3 | claude / fable / low / yolo1 | เพิ่มอเมริกาโนราคา 60 บาทในเมนู ช่วยสรุปเมนูของร้านตอนนี้เป็นสองบรรทัด | เมนูร้าน Cloud Cup ตอนนี้ค่ะ<br>- ลาเต้ 80 บาท<br>- อเมริกาโน 60 บาท | 5 | 5.4 s |
| 4 | claude / fable / low / yolo1 | ร้านชื่ออะไร เจ้าของชื่ออะไร และเครื่องดื่มสองอย่างราคาต่างกันกี่บาท? | ร้านชื่อ Cloud Cup เจ้าของชื่อคุณเมย์ค่ะ ลาเต้ 80 บาทกับอเมริกาโน 60 บาท ราคาต่างกัน 20 บาทค่ะ | 7 | 4.7 s |
| 5 | claude / fable / low / yolo1 | ช่วยคิดสโลแกนภาษาไทยหนึ่งประโยคสำหรับร้านนี้ โดยใส่ชื่อร้านด้วย | "Cloud Cup — เติมความสุขให้ทุกวันของคุณ ด้วยกาแฟที่นุ่มดุจก้อนเมฆ" ค่ะ | 9 | 5.1 s |
| 6 | codex / gpt-6-astra / low / cyolo1 | จากประวัติที่ได้รับ ช่วยบอกชื่อเจ้าของ ชื่อร้าน และราคาเครื่องดื่มทั้งสองอย่างอย่างสั้น ๆ | เจ้าของชื่อคุณเมย์ ร้าน Cloud Cup มีลาเต้ราคา 80 บาท และอเมริกาโนราคา 60 บาทค่ะ | 11 | 10.9 s |
| 7 | codex / gpt-6-astra / low / cyolo1 | ลูกค้าซื้อลาเต้หนึ่งแก้วและอเมริกาโนสองแก้ว จ่ายเงิน 500 บาท จะได้เงินทอนเท่าไร? | รวมราคา 80 + (60 × 2) = 200 บาท<br>จ่าย 500 บาท ได้เงินทอน 500 − 200 = \*\*300 บาท\*\* ค่ะ | 13 | 8.6 s |
| 8 | codex / gpt-6-astra / low / cyolo1 | เปลี่ยนราคาลาเต้เป็น 85 บาท ตั้งแต่ตอนนี้ ส่วนอเมริกาโนราคาเดิม สรุปเมนูใหม่สั้น ๆ | ลาเต้ 85 บาท<br>อเมริกาโน 60 บาท | 15 | 5.9 s |
| 9 | codex / gpt-6-astra / low / cyolo1 | ใช้ราคาใหม่ ลาเต้สองแก้วกับอเมริกาโนหนึ่งแก้วรวมเท่าไร และต่างจากราคาเดิมเท่าไร? | ราคาใหม่: (85 × 2) + 60 = \*\*230 บาท\*\*<br>ราคาเดิม: (80 × 2) + 60 = 220 บาท จึงแพงขึ้น \*\*10 บาท\*\* ค่ะ | 17 | 7.0 s |
| 10 | codex / gpt-6-astra / low / cyolo1 | สรุปส่งท้ายไม่เกินสามบรรทัด: เจ้าของและชื่อร้าน ราคาเมนูปัจจุบัน และยอดรวมออร์เดอร์ล่าสุด | เจ้าของชื่อคุณเมย์ ร้าน Cloud Cup<br>เมนูปัจจุบัน: ลาเต้ 85 บาท และอเมริกาโน 60 บาท<br>ออร์เดอร์ล่าสุด: ลาเต้ 2 แก้วกับอเมริกาโน 1 แก้ว รวม 230 บาท | 19 | 8.5 s |

สิ่งที่หลักฐานนี้ยืนยัน

- **บันทึกข้อความจริง 20 ข้อความ** (ผู้ใช้ 10 · ผู้ช่วย 10) และแถบแจ้งเปลี่ยนเป้าหมาย 1 รายการก่อนรอบ 6 ซึ่งไม่นับในประวัติ
- จำนวนประวัติที่ส่งเพิ่มเป็น 1, 3, 5, … 19 ทุกรอบ แปลว่าหน้าเว็บส่ง **ประวัติทั้งหมด** ไปทุกครั้ง
- หลังเปลี่ยนทั้ง provider และบัญชีในรอบ 6 Astra ตอบชื่อเจ้าของ ชื่อร้าน และราคาจากรอบของ Fable ได้ เพราะได้รับประวัติเป็นข้อความ ไม่ใช่เพราะ session ร่วมกัน
- รอบ 8–10 ใช้ราคาใหม่ (ลาเต้ 85 บาท) ที่เพิ่งกำหนดในบทสนทนา
- ป้ายสถานะมุมขวาบนขึ้น **ตอบจริงสำเร็จ: claude/yolo1, codex/cyolo1** (L3) แยกตามบัญชี

![ภาพหน้าจอจริง: หน้าแชต LAB 004 ในเบราว์เซอร์ เลือก claude / fable / low / yolo1 แสดงคำตอบของ Fable รอบ 2–5 พร้อมป้าย effort low, account yolo1, เวลา และส่งประวัติ 3, 5, 7, 9 ข้อความ ป้ายด้านบนเป็นสีเขียวทั้งสาม: API ตอบ /health, Token ผ่าน /v1/models, ตอบจริงสำเร็จ claude/yolo1](assets/06-fable-five-exchanges.png)

*ภาพหน้าจอจริง: Fable 5 รอบแรก (บัญชี yolo1)*

![ภาพหน้าจอจริง: หน้าแชตเดียวกันหลังเปลี่ยนเป็น codex / gpt-6-astra / low / cyolo1 แสดงคำตอบของ Astra รอบ 7–10 พร้อมส่งประวัติ 13, 15, 17, 19 ข้อความ คำตอบสุดท้ายสรุปเจ้าของคุณเมย์ ร้าน Cloud Cup ลาเต้ 85 บาท อเมริกาโน 60 บาท ออร์เดอร์ล่าสุด 230 บาท ป้ายด้านบนขึ้นตอบจริงสำเร็จ claude/yolo1, codex/cyolo1 และตัวนับด้านล่างแสดง 20 ข้อความ](assets/07-astra-ten-exchanges.png)

*ภาพหน้าจอจริง: Astra 5 รอบหลัง (บัญชี cyolo1) ในบทสนทนาเดียวกัน*

**ขอบเขตของหลักฐาน:** เรียกจริงแค่ 2 ชุด คือ `fable/low/yolo1` และ `gpt-6-astra/low/cyolo1` · Opus, Sol, Luna และ effort อื่นยังไม่ได้เรียกผ่าน API ของแลปนี้ (ตารางการรองรับมาจากการรันจริงใน LAB 003) · การที่ Codex ตอบได้ **ไม่ใช่** การทดสอบว่า sandbox ห้ามคำสั่ง shell ได้จริง

### 5.4 · ทดสอบการปฏิเสธและขอบเขตบัญชี

| # | ทดสอบ | วิธี | ผลจริง | หลักฐาน |
|---|---|---|---|---|
| N1 | effort ใน dropdown | เลือกแต่ละโมเดลของ Codex แล้วอ่านตัวเลือก | ✅ Sol และ Luna มี `none low medium high xhigh max` · Astra มี `low medium high xhigh max` (ไม่มี `none`) | [`dropdown-checks.json`](assets/dropdown-checks.json) · แถบแจ้งเปลี่ยนเป้าหมายไป sol/luna/astra เห็นในภาพ 09–10 |
| N2 | effort ผิดที่ส่งตรงเข้า API | `smoke` | ✅ `gpt-6-astra + effort none` และ `fable + effort minimal` ได้ HTTP 400 | [`smoke.log`](assets/smoke.log) |
| N3 | `max_completion_tokens` | `smoke` | ✅ HTTP 400 | [`smoke.log`](assets/smoke.log) |
| N4 | บัญชีที่ไม่ได้เปิด / ชื่อบัญชี Claude บนโมเดล Codex | `smoke` รุ่นปัจจุบัน | ✅ `account yolo2 (not enabled for this API) rejected (HTTP 400)` และ `Claude account name on a Codex model rejected (HTTP 400)` · smoke รวม 13 PASS, 0 FAIL · ไม่เรียกโมเดล | [`smoke-with-account-checks.log`](assets/smoke-with-account-checks.log), ภาพ [`12-account-checks.png`](assets/12-account-checks.png) |
| N5 | token ผิด | ใส่ token ผิดแล้วกดเชื่อมต่อ | ✅ ป้าย **Token: ถูกปฏิเสธ (401)** · dropdown ทั้งสี่ว่างและปิด · ช่องพิมพ์และปุ่มส่งปิด · ป้ายบัญชีกลับเป็น "ยังไม่มีคำตอบจริง" | ภาพ [`09-invalid-token.png`](assets/09-invalid-token.png) |
| N6 | เชื่อมต่อใหม่ไป endpoint ผิด | เปลี่ยน URL เป็น `http://127.0.0.1:8009` แล้วกดเชื่อมต่อ | ✅ ป้าย **API: ติดต่อไม่ได้ (network/CORS)** · dropdown ว่างและปิด ส่งต่อไม่ได้ · จากนั้นเชื่อมต่อกลับไป `:8004` ได้ตามปกติ · หมายเหตุ: CSP ของหน้าเว็บ (`connect-src` เฉพาะพอร์ต 8004) ก็บล็อกพอร์ตนี้อยู่แล้ว ข้อความ network/CORS จึงรวมทั้งสองสาเหตุ | ภาพ [`10-invalid-endpoint.png`](assets/10-invalid-endpoint.png) |
| N7 | origin แปลกปลอม | `smoke` | ✅ CORS rejects a foreign origin | [`smoke.log`](assets/smoke.log) |

![ภาพหน้าจอจริง: หลังใส่ token ผิด ป้าย Token เป็นสีแดง ถูกปฏิเสธ (401) dropdown Provider, Model, Reasoning effort, Account ว่างทั้งหมด ช่องความสามารถของ API ขึ้นยังไม่ได้เชื่อมต่อ และปุ่มส่งเป็นสีจาง](assets/09-invalid-token.png)

*ภาพหน้าจอจริง N5: token ผิด*

![ภาพหน้าจอจริง: API base URL เป็น http://127.0.0.1:8009 ป้าย API เป็นสีแดง ติดต่อไม่ได้ (network/CORS) ป้าย Token ยังไม่ตรวจ dropdown ว่างทั้งหมด และปุ่มส่งเป็นสีจาง](assets/10-invalid-endpoint.png)

*ภาพหน้าจอจริง N6: endpoint ผิด*

![ภาพหน้าจอจริง: Terminal รัน lab04.sh smoke รอบล่าสุด แสดง PASS 13 รายการ รวม account yolo2 (not enabled for this API) rejected และ Claude account name on a Codex model rejected ปิดท้ายด้วย smoke: 13 PASS, 0 FAIL](assets/12-account-checks.png)

*ภาพหน้าจอจริง N4: ตรวจขอบเขตบัญชีใน smoke รอบล่าสุด*

### 5.5 · ขอบเขตเมื่อสลับบัญชี

- บัญชีคนละบัญชี = config dir คนละโฟลเดอร์ใน volume โควตาและ subscription แยกกัน ไม่มี session ร่วม
- สิ่งเดียวที่ข้ามไปถึงบัญชีใหม่คือ **ข้อความในประวัติ** ที่หน้าเว็บส่งไป
- การเพิ่มบัญชี (เช่น `yolo2`) ต้องทำครบสามอย่าง: ใส่ใน `CLAUDE_ACCOUNTS` ของ `deploy/lab04.env`, `run creds`, `run up` ถ้าใส่ชื่อแต่ยังไม่ได้คัดลอก API ตอบ 503 `account_not_provisioned`
- ค่าเริ่มต้นของแลปนี้เปิดแค่ 1 บัญชีต่อ provider

### 5.6 · เรียก API จาก Python ด้วย OpenAI SDK (ไม่บังคับ)

API นี้รับรูปแบบคำขอแบบเดียวกับ Chat Completions จึงใช้ไลบรารี `openai` ได้ โดยมีเงื่อนไข

- key ที่ใส่คือ **token ของ API แลปนี้** (ไฟล์ `deploy/.secrets/api_token` บน control host) **ไม่ใช่** credential ของ OpenAI หรือ Anthropic
- `account` ไม่ใช่ฟิลด์ของ OpenAI จึงส่งผ่าน `extra_body`
- ห้ามส่ง `max_completion_tokens`, `max_tokens`, `temperature`, `tools`, `stream=True` เพราะ API ตอบ 400
- `base_url` ค่าเริ่มต้นสำหรับรัน **ใน devtools** คือ `http://host.docker.internal:8004/v1` ถ้ารันจาก Terminal บน Windows ให้ใช้ `http://localhost:8004/v1`

แกนของโค้ด ([`examples/openai_client.py`](examples/openai_client.py)) ที่คัดลอกไปใช้ได้

```python
import getpass
from openai import OpenAI

client = OpenAI(base_url="http://host.docker.internal:8004/v1",
                api_key=getpass.getpass("LAB 004 API token: "),   # token ของแลป ไม่ใช่ key ของ provider
                max_retries=0, timeout=330)

resp = client.chat.completions.create(
    model="fable",                       # fable | opus | gpt-6-astra | gpt-6-sol | gpt-6-luna
    reasoning_effort="low",              # low medium high xhigh max (sol/luna มี none เพิ่ม)
    messages=[
        {"role": "system", "content": "ตอบเป็นภาษาไทย สั้น ๆ ไม่เกินสองประโยค"},
        {"role": "user", "content": "ฉันชื่อเมย์ เปิดร้านกาแฟชื่อ Cloud Cup ลาเต้ราคา 80 บาท"},
        {"role": "assistant", "content": "รับทราบค่ะคุณเมย์ ร้าน Cloud Cup ลาเต้ 80 บาท"},
        {"role": "user", "content": "ลาเต้สามแก้วราคาเท่าไร และร้านชื่ออะไร"},
    ],
    extra_body={"account": "yolo1"},     # ฟิลด์เฉพาะของแลปนี้
)
print("model:", resp.model)
print("reply:", resp.choices[0].message.content)
```

ข้อความ `system` ในที่นี้ยังเป็นแค่ข้อความในประวัติตามหัวข้อ 6 ไม่ใช่ system prompt จริงของ CLI

**ผลจริง (ผู้ประสานงานรันผ่าน Jupyter ด้วย computer use · `openai` 3.19.2):**

```bash
python examples/openai_client.py --model gpt-6-astra --effort low --account cyolo1
```

```text
model: gpt-6-astra
reply: ลาเต้สามแก้วราคา 240 บาทค่ะ ร้านชื่อ Cloud Cup
```

![ภาพหน้าจอจริง: Terminal ใน JupyterLab รัน examples/openai_client.py --model gpt-6-astra --effort low --account cyolo1 ใส่ token แบบซ่อน แล้วแสดง model: gpt-6-astra และ reply: ลาเต้สามแก้วราคา 240 บาทค่ะ ร้านชื่อ Cloud Cup](assets/11-openai-sdk.png)

*ภาพหน้าจอจริง: OpenAI Python SDK เรียก API ของแลปนี้ · คำตอบใช้ประวัติที่ส่งไปในโค้ด (ร้าน Cloud Cup, ลาเต้ 80 บาท) · เป็นการเรียกจริง 1 ครั้งด้วย Astra/low/cyolo1 เท่านั้น*

---

## 6 · ประวัติแชตถูกส่งให้ CLI อย่างไร (อ่านเพิ่มเติม)

<details>
<summary>เปิดอ่าน: ทำไมหน้าเว็บต้องส่งประวัติทั้งหมดทุกรอบ และต่างจาก Chat API จริงอย่างไร</summary>

`claude -p` และ `codex exec` ตอบคำถาม **ครั้งเดียวแล้วจบ** API นี้ยังสั่งไม่ให้เก็บ session (`--no-session-persistence`, `--ephemeral`) ดังนั้น **CLI จำอะไรข้ามรอบไม่ได้เลย** สิ่งที่ทำให้ถามต่อได้คือ **หน้าเว็บส่งประวัติข้อความทั้งหมดไปทุกครั้ง** แล้ว API แปลงเป็นพรอมต์ก้อนเดียว

```text
You are the assistant in a simple web chat application.
The conversation so far is given below as a JSON array of {"role", "content"} objects, oldest first.
...
CONVERSATION_JSON:
[
 {"role": "user", "content": "สวัสดี ฉันชื่อมะลิ"},
 {"role": "assistant", "content": "สวัสดีค่ะคุณมะลิ"},
 {"role": "user", "content": "ฉันชื่ออะไร"}
]
```

| เรื่อง | Chat API จริง (native) | API ของแลปนี้ (transcript → CLI) |
|---|---|---|
| ความจำระหว่างรอบ | ฝั่ง client ส่ง `messages` เหมือนกัน | เหมือนกัน แต่ถูก **รวมเป็นข้อความเดียว** ส่งทาง stdin |
| ขอบเขตของ role | แยกโดยโครงสร้างของ API | ใส่ role ไว้ใน JSON ทำให้ข้อความที่ผู้ใช้พิมพ์ถูก escape อยู่ใน `content` เสมอ แต่ทั้งก้อนยังเป็น **ข้อความธรรมดา** ที่โมเดลอ่าน **ไม่ได้รับประกันว่ากัน prompt injection ได้** ข้อความในประวัติยังชักนำโมเดลได้เหมือนข้อความทั่วไป |
| `system` | system prompt จริง | เป็นแค่ข้อความที่ขอให้โมเดลเคารพ ไม่มีสิทธิ์พิเศษ |
| เปลี่ยนโมเดล/บัญชีกลางบทสนทนา | ส่ง messages เดิมให้โมเดลใหม่ | เหมือนกัน · ตัวใหม่เห็นแค่ **ข้อความ** ไม่รู้ว่ารอบก่อนใครตอบ และบัญชีคนละบัญชีไม่แชร์ session |
| `max_completion_tokens`, `temperature`, `tools`, `stream` | รองรับ | **ปฏิเสธด้วย HTTP 400** เพราะ CLI ไม่ได้รับค่าเหล่านี้ ไม่ทำเป็นว่ารองรับ |
| token usage | มีตัวเลขจริง | `"usage": null` ไม่เดาตัวเลข |
| ต้นทุนต่อรอบ | คิดตาม token | ทุกรอบเริ่ม CLI ใหม่และส่งประวัติทั้งหมด ยิ่งคุยยาวยิ่งช้าและกินโควตา มีเพดาน 40 ข้อความ / 48,000 ตัวอักษร |

</details>

---

## 7 · ข้อจำกัดด้านความปลอดภัยที่ต้องรู้ (อ่านเพิ่มเติม)

<details>
<summary>เปิดอ่าน: สิ่งที่ป้องกันไว้ และข้อจำกัดที่ยังมีอยู่</summary>

| เรื่อง | สิ่งที่ทำ | ข้อจำกัดที่ยังมีอยู่ |
|---|---|---|
| wrapper ใน API | `yoloN`/`cyoloN` ของ container เอง รับแค่ `--model/--effort` ไม่ใช้ flag ข้ามการขออนุญาต | wrapper เดิมใน devtools ยังข้ามการขออนุญาตตามเดิม (ไม่ได้แก้) |
| เครื่องมือของ Claude | `--tools ""` เอา built-in tool ออกทั้งหมด + `--permission-mode dontAsk` | ยืนยันแล้วว่าตอบแชตได้ด้วย flag ชุดนี้ · **ยังไม่ได้ทดสอบเฉพาะ** ว่าโมเดลถูกห้ามใช้เครื่องมือเมื่อพยายามใช้ |
| เครื่องมือของ Codex | `--sandbox read-only`, `approval_policy=never`, cwd ว่าง, ไม่โหลด config/rules ของผู้ใช้ | **ไม่มี flag ที่ตรวจแล้วว่าปิด shell tool ได้** Codex ยังพยายามรันคำสั่งได้ภายใต้ sandbox · sandbox ใช้ bubblewrap ซึ่งอาจรันไม่ได้ภายใต้ seccomp ของ Docker · ยืนยันแล้วว่า Codex **ตอบแชตได้** ใน container แต่ **ยังไม่ได้ทดสอบเฉพาะ** ว่า sandbox บังคับห้ามคำสั่ง shell ได้จริง |
| HOME | คงที่ที่ `/home/app` (tmpfs) · cwd และ TMPDIR แยกต่อ request | ทุกบัญชีใช้ HOME เดียวกัน การแยกบัญชีอาศัย `CLAUDE_CONFIG_DIR` / `CODEX_HOME` ไม่ใช่การแยกระดับ OS |
| credential | สำเนาเฉพาะ `.credentials.json` / `auth.json` ใน named volume ไม่อยู่ใน image (deploy จริงยืนยันว่าพอสำหรับทั้งสอง CLI) | สำเนาสองชุดใช้ refresh token เดียวกัน ถ้าฝั่งหนึ่ง refresh ก่อน อีกฝั่งอาจหลุด ต้องล็อกอินใหม่ใน devtools แล้ว `run creds` ซ้ำ |
| token ของ API | container เห็นแค่ SHA-256 · หน้าเว็บเก็บในหน่วยความจำ | ค่า hash เห็นได้จาก `docker inspect` · ใครมี token ก็ใช้โควตาบัญชีได้ |
| พอร์ต | ผูก `127.0.0.1` ของ Docker Desktop host เท่านั้น | ทุกโปรแกรมบนเครื่อง Windows เครื่องนั้นเรียกได้ถ้ามี token |
| log | เก็บแค่ metadata (โมเดล บัญชี จำนวนตัวอักษร เวลา สถานะ) | CLI เองอาจเขียนข้อมูลลงใน config dir ของบัญชี (เช่น log ของ Codex ใน `CODEX_HOME`) |
| ลบทิ้ง | `run down --purge` ลบ container, volume สำเนา credential และ network ที่มี label `lab04` | ไม่ลบ image และไม่แตะของที่ไม่มี label |

</details>

---

## 8 · แก้ปัญหาที่พบบ่อย (อ่านเพิ่มเติม)

<details>
<summary>เปิดอ่าน: อาการ สาเหตุ และสิ่งที่ขอให้ AI ทำ</summary>

| อาการ | สาเหตุที่เป็นไปได้ | ทางแก้ |
|---|---|---|
| `lab04.sh` บอกว่า daemon ไม่ใช่ `docker-desktop` | สั่งงานกับ Docker ของ devtools ซึ่งเป็น daemon ชั้นใน | บอก AI ให้ deploy ผ่าน control host ไปยัง Docker Desktop ชั้นนอก |
| `remote.sh` บอก `no open connection` | การเชื่อมต่อไป control host หมดอายุหรือถูกปิด | บอก AI ให้เปิดการเชื่อมต่อไป control host ใหม่ |
| `verify` FAIL เฉพาะ published port | `PROBE_HOST` ไม่ตรงกับตำแหน่งของ control host | control host เป็น container ใช้ `host.docker.internal` · รันบน host เองใช้ `127.0.0.1` แล้วยืนยันในเบราว์เซอร์ |
| ป้าย API แดง `network/CORS` | API ไม่รัน หรือเปิดหน้าเว็บจาก origin อื่น (`file://`) | เปิดผ่าน `http://localhost:8005` เท่านั้น |
| `upstream_auth_error` | สำเนา credential หมดอายุหรือถูก refresh ทับ | ล็อกอินใหม่ใน devtools แล้วบอก AI ให้คัดลอก credential ใหม่ (`run creds`) โดยไม่ต้องเปิด container ใหม่ |
| `upstream_rate_limited` | บัญชีชนเพดานการใช้ | รอ หรือเปลี่ยนบัญชี |
| `busy` (429) | บัญชีนั้นกำลังตอบอีกคำขอ (1 คำขอต่อบัญชี) | รอให้คำตอบก่อนหน้าจบ |
| `transcript_too_long` | ประวัติเกิน 48,000 ตัวอักษร | กดล้างแชต |
| `cli_timeout` | effort สูงกับโจทย์ยาวเกิน 300 s | ลด effort หรือให้ AI ปรับ `CLI_TIMEOUT_S` |

</details>

---

## 9 · ไฟล์ในโฟลเดอร์นี้

<details>
<summary>เปิดอ่าน: หน้าที่ของแต่ละไฟล์</summary>

| ไฟล์ | หน้าที่ |
|---|---|
| `api/app/main.py` | FastAPI: endpoint, token, CORS, จำกัด body, ตรวจคำขอ, concurrency, log แบบไม่มีเนื้อหา |
| `api/app/catalog.py` | โมเดล effort และพารามิเตอร์ที่รับ/ปฏิเสธ |
| `api/app/config.py` | ค่าตั้งจาก env และการตรวจแบบ fail closed |
| `api/app/transcript.py` | แปลง messages เป็นพรอมต์ CONVERSATION_JSON |
| `api/app/runner.py` | เรียก wrapper แบบ argv + stdin, timeout, จำกัด output, จัดประเภท error |
| `api/wrappers/lab04-cli` | wrapper แบบแคบ ติดตั้งเป็น `yolo1..5` / `cyolo1..5` ใน image |
| `api/Dockerfile`, `api/requirements*.txt`, `api/.dockerignore` | image ของ API (ไม่มี credential) และ dependency ที่ pin |
| `api/tests/` | unittest 29 เทสต์ พร้อม CLI ปลอม |
| `web/index.html` | หน้าแชตไฟล์เดียว |
| `web/Dockerfile`, `web/build_csp.py`, `web/nginx.conf.in` | container เสิร์ฟหน้าเว็บ พร้อม CSP แบบ hash |
| `deploy/lab04.sh`, `deploy/lab04.env.example` | deploy บน control host (daemon ชั้นนอก) |
| `deploy/remote.sh` | สั่งงานจาก devtools ผ่าน SSH ControlMaster ชั่วคราว |
| `examples/openai_client.py` | ตัวอย่างเรียก API ด้วย OpenAI Python SDK (token ผ่าน getpass) |
| `assets/architecture.png`, `assets/chat-ui-concept.png` | ภาพแนวคิด **ฉบับร่าง** (ไม่ใช่ภาพหน้าจอ) |
| `assets/01-…png` – `assets/12-…png` | ภาพหน้าจอจริงจากการ deploy และทดสอบของผู้ประสานงาน |
| `assets/build.log`, `deploy.log`, `smoke.log`, `smoke-with-account-checks.log` | log จริงของ build · token/creds/up/verify · smoke รอบแรก (11) และรอบล่าสุด (13) |
| `assets/ten-exchanges.json`, `.txt`, `fable-five-exchanges.txt`, `dropdown-checks.json` | transcript จริง 10 รอบ และผลตรวจ dropdown |
| `assets/authoring-environment-note.md` | บันทึกแพ็กเกจ apt ที่ติดตั้งใน devtools ระหว่างเขียนแลป |
| `docs/implementation-reference.md` | ข้อกำหนดการสร้างแบบละเอียดสำหรับ AI อ้างอิง (ผู้เรียนไม่ต้องอ่าน) |

</details>

## 10 · สถานะและสิ่งที่ยังค้างอยู่

เสร็จและมีหลักฐานแล้ว

- [x] deploy บน `docker-desktop`: build · creds · up · verify ([`build.log`](assets/build.log), [`deploy.log`](assets/deploy.log))
- [x] `smoke` readiness 13 PASS / 0 FAIL รวมตรวจบัญชี N4 ([`smoke-with-account-checks.log`](assets/smoke-with-account-checks.log)) · รอบแรก 11 PASS ([`smoke.log`](assets/smoke.log))
- [x] Claude Code ใช้ได้ด้วย `.credentials.json` อย่างเดียว · Codex ตอบได้ด้วย `auth.json`
- [x] แชตจริง 10 รอบ (Fable/low/yolo1 × 5 แล้ว Astra/low/cyolo1 × 5) ประวัติครบ 20 ข้อความ
- [x] N1–N7 ครบ
- [x] OpenAI Python SDK (`openai` 3.19.2) เรียก API ได้จริง ([`11-openai-sdk.png`](assets/11-openai-sdk.png))

ยังค้าง (งานที่ขอไว้)

- [ ] ภาพแนวคิดฉบับสุดท้ายแทนฉบับร่างใน `assets/` · **ยังไม่ได้ทำ** รอความชัดเจนเรื่องเครื่องมือสร้างภาพ

ข้อจำกัดที่รู้อยู่ (ทำเพิ่มได้ ไม่ใช่เงื่อนไขของแลปแชตนี้)

- การบังคับห้ามคำสั่ง/เครื่องมือของ sandbox Codex และ `--tools ""` ของ Claude **ยังไม่ได้ทดสอบเฉพาะ** (หัวข้อ 7)
- โมเดลและ effort อื่นนอกจาก Fable/low และ Astra/low ยังไม่ได้เรียกผ่าน API นี้ (อ้างอิง LAB 003)
- แพ็กเกจ apt ใน devtools คงไว้ตามที่บันทึกใน [`authoring-environment-note.md`](assets/authoring-environment-note.md) ไม่มีการลบ
