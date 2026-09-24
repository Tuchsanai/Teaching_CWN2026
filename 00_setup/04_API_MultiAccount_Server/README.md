# API หลายบัญชี: FastAPI + หน้าแชต index.html ที่เรียก Claude Code และ Codex CLI

## 1 · ภาพรวมสถาปัตยกรรม

*แผนภาพฉบับใหม่ยังไม่ได้ทำ สรุปสั้น ๆ คือ พรอมต์ 1 สร้าง backend พรอมต์ 2 สร้างไฟล์ `index.html` ส่วนพรอมต์ 3 deploy container แอปตัวเดียวที่เสิร์ฟหน้าเว็บที่ `GET /` และให้บริการ API บนพอร์ตเดียวกันด้วย origin เดียวกัน พอร์ต 8004 ในแผนภาพเป็นแค่ตัวอย่างค่าเริ่มต้นที่เปลี่ยนได้ ไม่รับประกันว่าจะได้พอร์ตนี้ ถ้าพอร์ตไม่ว่าง AI จะเลือกพอร์ตว่างแทนแล้วรายงานพอร์ตที่ใช้จริง*

```text
 เบราว์เซอร์บน Windows host
   │ เปิด http://localhost:8004/ (ตัวอย่าง) ▶ app container (FastAPI + yolo/cyolo ของตัวเอง)
   │   ├─ GET /  → ส่ง index.html (ไฟล์ที่สร้างไว้นอก container และ mount แบบอ่านอย่างเดียว)
   │   └─ POST /v1/chat/completions + Bearer token (origin เดียวกัน)
   │                   └─ yolo1 / cyolo1 → Claude Code CLI / Codex CLI
   │                        └─ volume ส่วนตัว: สำเนาข้อมูลล็อกอินที่คัดลอกมาจาก devtools
 devtools (JupyterLab + yolo3) = ศูนย์สั่งงาน: สร้างโค้ด backend และ index.html แล้วสั่ง deploy
   └─ app container รันบน Docker host ชั้นนอก เป็นพี่น้องกับ devtools (ไม่ใช่ Docker ชั้นในของ devtools)
```

ในแบบใหม่ไม่มี container หน้าเว็บแยกและไม่ใช้พอร์ต 8005 เบราว์เซอร์โหลด HTML จาก container แอปแล้วส่งคำขอกลับไปที่ container เดียวกัน

![ภาพหน้าจอจริงจากเวอร์ชันก่อนหน้าแบบสอง container: หน้าแชตที่เปิดจากพอร์ต 8005 แสดงคำตอบจริงจาก Fable](assets/13-current-chat-real.png)

*ภาพหน้าจอจริงจาก **เวอร์ชันก่อนหน้าแบบสอง container** (หน้าเว็บ 8005 + API 8004) ไม่ใช่หลักฐานว่าพรอมต์ชุดใหม่ด้านล่างใช้ได้*

---

## 2 · สร้าง Backend

พรอมต์ทั้งสามชุดเป็น **ข้อความภาษาธรรมชาติ** ไม่ใช่โค้ด Python ให้คัดลอกข้อความในกรอบไปวางในบทสนทนากับ `yolo3` ที่เปิดอยู่ใน **Terminal ของ JupyterLab** บน devtools (ไม่ใช่วางลง cell ของ notebook เพื่อรัน) วางตามลำดับ 1 → 2 → 3 ในบทสนทนาเดียวกัน พรอมต์สมมติว่ายังไม่มีโค้ด ไฟล์ หรือแลปก่อนหน้าใดเลย และบัญชี yolo/cyolo ใน devtools ล็อกอินไว้แล้ว

##### 📋 พรอมต์ 1 · สร้าง Backend

```text
ช่วยสร้าง backend ใหม่ตั้งแต่ศูนย์ด้วย FastAPI ในโฟลเดอร์ที่ทำงานอยู่ตอนนี้ โดยตั้งชื่อไฟล์และโครงสร้างเองได้
1. devtools นี้เป็นแค่ศูนย์สั่งงาน ตัวแอปจะรันใน container ใหม่ตัวเดียวที่แยกจาก devtools ภายในมี FastAPI และตัวเรียก yolo/cyolo ของตัวเอง
2. container แอปต้องเสิร์ฟไฟล์ index.html ที่ GET / ด้วย ไฟล์นี้จะสร้างในขั้นถัดไปไว้นอก image แล้ว mount เข้ามาแบบอ่านอย่างเดียว จึงไม่ต้องมี web server หรือ container หน้าเว็บแยก ถ้ายังไม่มีไฟล์ให้ตอบ error ที่อ่านเข้าใจได้
3. endpoint ที่ต้องมี: GET /health สำหรับตรวจสุขภาพโดยไม่ต้องใช้ token, GET /v1/models บอกโมเดล effort และบัญชีที่ใช้ได้เพื่อให้หน้าเว็บสร้างตัวเลือก และ POST /v1/chat/completions
4. POST /v1/chat/completions รับ messages, model, reasoning_effort, account และ provider แบบไม่บังคับ ตอบแบบไม่ stream ในรูปแบบเดียวกับ OpenAI โดยคำตอบอยู่ที่ choices[0].message.content
5. โมเดลและ effort ที่ต้องรองรับ: provider claude รุ่น fable และ opus ใช้ low, medium, high, xhigh, max ผ่านบัญชี yolo · provider codex รุ่น gpt-6-astra ใช้ low, medium, high, xhigh, max ส่วน gpt-6-sol และ gpt-6-luna ใช้ none, low, medium, high, xhigh, max ผ่านบัญชี cyolo · คู่อื่นให้ปฏิเสธพร้อมบอกเหตุผล
6. บัญชีหลักคือ yolo1 สำหรับ Claude และ cyolo1 สำหรับ Codex ให้ตรวจหาบัญชีอื่นที่ตั้งค่าไว้จริงใน devtools เพื่อเปิดใช้เพิ่มได้ และห้ามใช้ชื่อบัญชีข้าม provider
7. ตรวจคำสั่ง yolo1 และ cyolo1 ที่ใช้งานได้อยู่แล้วใน devtools ว่าเรียก CLI ตัวใด รุ่นใด และชี้ config ไปที่ใด โดยดูได้แค่เนื้อ wrapper ชื่อไฟล์ และรุ่นของ CLI ห้ามเปิดหรือพิมพ์เนื้อไฟล์ความลับ แล้วติดตั้ง Claude Code CLI และ Codex CLI รุ่นที่เข้ากันได้กับที่ใช้อยู่ใน devtools ไว้ใน container แอปเอง
8. สร้างคำสั่ง yolo1 และ cyolo1 ใน container แอปให้ทำงานได้ด้วยตัวเอง โดยปรับ path ของ wrapper และ config ให้ชี้ไปที่ volume ส่วนตัวของ container ห้ามเรียกโมเดลด้วยการ docker exec เข้า devtools หรือ SSH กลับไป ต้องยังเลือก model และ effort ได้ และแต่ละบัญชีใช้โฟลเดอร์ config ของตัวเองแยกกัน
9. ตอน deploy ให้คัดลอกจากบัญชีต้นฉบับใน devtools เฉพาะไฟล์ล็อกอินและ config ที่จำเป็นไปไว้ใน volume ส่วนตัวนี้ ห้ามแก้หรือเขียนทับต้นฉบับ และห้ามให้ข้อมูลล็อกอินไปอยู่ใน image, log หรือ HTML
10. ใช้เป็นแชตข้อความอย่างเดียว ปิดเครื่องมือของ CLI ที่รันคำสั่งหรือแก้ไฟล์ได้เท่าที่ CLI ที่ติดตั้งจริงรองรับ ห้ามใช้โหมดข้ามการขออนุญาต จำกัดเวลาและทรัพยากรของการเรียก CLI แต่ละครั้งให้เหมาะสม และถ้าปิดไม่ได้ทั้งหมดให้บอกตรง ๆ
11. ส่งประวัติทั้งหมดใน messages ของแต่ละคำขอให้โมเดลเห็น เพราะ CLI ไม่จำข้ามรอบ และตอบเฉพาะคำตอบจริงจากโมเดลเท่านั้น
12. ป้องกัน /v1/models และ /v1/chat/completions ด้วย Bearer token ตั้ง timeout ให้เหมาะสม จำกัดขนาดคำขอและจำนวนข้อความ และส่ง error ที่อ่านเข้าใจได้โดยไม่เผยรายละเอียดภายใน
13. เก็บค่าตั้งค่าไว้ใน .env และทำ .env.example ที่ไม่มีค่าความลับ ห้ามให้ token หรือข้อมูลล็อกอินไปอยู่ใน image, log หรือผลลัพธ์ที่แสดงออกมา
14. ก่อน bind หรือ publish พอร์ตของ container แอปใหม่ ให้ตรวจบน Docker host ที่จะใช้จริงก่อนว่ามีพอร์ตใดถูกใช้หรือถูก publish อยู่แล้วบ้าง ใช้ 8004 เป็นค่าเริ่มต้น ถ้าไม่ว่างให้เลือกพอร์ตว่างอื่นแทน บันทึกพอร์ตที่ใช้จริงไว้ใน .env และให้หน้าเว็บ API และ URL ที่ใช้เปิดหน้าเว็บอ้างค่าเดียวกันนี้ทั้งหมด ห้ามหยุดหรือแก้ container หรือ service อื่นเพื่อแย่งพอร์ตคืน ตอน deploy ให้ตรวจซ้ำอีกครั้งเผื่อพอร์ตถูกใช้ไประหว่างนั้น และรายงานพอร์ตที่เลือกใช้จริง
15. ตรวจ help ของ CLI ที่ติดตั้งอยู่จริงก่อนเลือกวิธีเรียก เขียนเทสต์ที่จำลอง CLI โดยไม่เรียกโมเดลจริงในขั้นนี้ แล้วสรุปสิ่งที่สร้างและผลเทสต์ตามจริง จากนั้นรอพรอมต์ถัดไป
```

---

## 3 · สร้างหน้าแชต

##### 📋 พรอมต์ 2 · สร้างหน้าแชต

```text
ต่อไปช่วยสร้างหน้าแชตเป็นไฟล์ index.html ไฟล์เดียวตั้งแต่ศูนย์ สำหรับ backend ที่เพิ่งสร้าง
1. เก็บ index.html ไว้นอก image ในโฟลเดอร์ของงานนี้ เพื่อให้ container แอปเดิม mount แบบอ่านอย่างเดียวแล้วแสดงที่ GET / โดยไม่ต้องมี web server อื่น
2. เรียก API ด้วย origin เดียวกับหน้าเว็บ โดยไม่ฝังชื่อ host หรือพอร์ตไว้ในไฟล์
3. ให้ผู้ใช้กรอก token ในช่องแบบรหัสผ่าน เก็บไว้ในหน่วยความจำของหน้าเท่านั้น ห้ามฝังความลับในไฟล์ และห้ามบันทึกลงที่เก็บของเบราว์เซอร์หรือ URL
4. ดึงรายการจาก GET /v1/models มาสร้าง dropdown ของ provider, model, effort และ account โดยให้ effort และ account เปลี่ยนตามโมเดลที่เลือก
5. ส่งประวัติข้อความทั้งหมดไปกับทุกคำถาม และแสดงข้อความจากโมเดลเป็นข้อความธรรมดาที่ไม่ถูกแปลงเป็น HTML
6. ปิดการส่งระหว่างรอคำตอบ แสดงสถานะกำลังทำงาน ถ้าเกิด error ให้แสดงชัด ๆ และกดลองใหม่ได้โดยไม่เพิ่มคำถามซ้ำในประวัติ
7. ใต้คำตอบแต่ละข้อ แสดง model, account และ effort ที่ใช้ตอบจริง
8. มีปุ่มเริ่มแชตใหม่ และปุ่มดาวน์โหลดบทสนทนา
9. อ่านง่ายทั้งจอกว้างและจอแคบ ใช้ฟอนต์ภาษาไทยที่ชัด ขนาดตัวอักษรประมาณ 18px และวางบทสนทนาไว้กึ่งกลางในความกว้างที่อ่านสบาย
10. เสร็จแล้วสรุปสิ่งที่ทำตามจริง แล้วรอพรอมต์ถัดไป
```

---

## 4 · เปิดใช้งานและทดลอง

##### 📋 พรอมต์ 3 · เปิดใช้งานและทดลอง

```text
ต่อไปช่วย deploy แอปที่สร้างไว้ให้ใช้งานได้จริง แล้วทดสอบ
1. build และรัน container แอปตัวเดียวที่มีทั้ง FastAPI และ yolo/cyolo บน Docker host ชั้นนอกที่ devtools รันอยู่ ให้เป็นพี่น้องกับ devtools ห้าม deploy ลง Docker ชั้นในของ devtools และไม่ต้องมี container หน้าเว็บแยก
2. ตรวจหาช่องทางเข้าถึง Docker host ที่ถูกต้องเอง อ่านค่าจาก .env ที่ไม่ใส่ path แบบเต็มหรือชื่อ host ตายตัว และถามฉันเฉพาะข้อมูลการเชื่อมต่อที่หาไม่พบจริง ๆ
3. ก่อน bind หรือ publish พอร์ตของ container แอป ให้ตรวจบน Docker host ที่จะใช้จริงว่ามีพอร์ตใดถูกใช้หรือถูก publish อยู่แล้วบ้าง ใช้ 8004 เป็นค่าเริ่มต้น ถ้าไม่ว่างให้เลือกพอร์ตว่างอื่น บันทึกพอร์ตที่ใช้จริงไว้ใน .env และให้หน้าเว็บ API และ URL ที่ใช้เปิดหน้าเว็บใช้ค่าเดียวกัน ห้ามหยุดหรือแก้ container หรือ service อื่นเพื่อแย่งพอร์ตคืน ตรวจซ้ำอีกครั้งตอนรัน container เผื่อพอร์ตถูกใช้ไประหว่างนั้น และรายงานพอร์ตที่เลือกใช้จริง
4. สร้าง token ของ API โดยไม่แสดงค่าออกมา และบอกวิธีที่ฉันจะอ่านค่าเองได้อย่างปลอดภัย
5. คัดลอกข้อมูลล็อกอินของ yolo1 และ cyolo1 (และบัญชีอื่นที่เปิดใช้) จาก devtools ไปไว้ใน volume ส่วนตัวของ container แอปอย่างปลอดภัย โดยไม่เขียนทับต้นฉบับและไม่พิมพ์ค่าความลับ แล้วรัน yolo1 --version และ cyolo1 --version ภายใน container แอป และให้แต่ละบัญชีตอบคำถามสั้น ๆ จริงหนึ่งครั้งจากใน container เพื่อยืนยันว่าทำงานได้โดยไม่พึ่ง devtools
6. mount index.html เข้า container แบบอ่านอย่างเดียว
7. ตรวจว่า /health ตอบได้ /v1/models ตอบรายการเมื่อมี token และคำขอที่ไม่มี token หรือ token ผิดถูกปฏิเสธ
8. ใช้ computer use เปิดหน้าเว็บจริง แล้วคุยในบทสนทนาเดียว 10 รอบ: Fable 5 รอบ แล้วเปลี่ยนเป็น gpt-6-astra อีก 5 รอบ โดยถามให้เห็นว่ายังจำเรื่องก่อนหน้าได้ เก็บภาพหน้าจอจริงที่อ่านออกและบทสนทนาไว้
9. ถ้าควบคุมเบราว์เซอร์ไม่ได้ ให้บอกตรง ๆ พร้อมวิธีตรวจเองที่ง่ายที่สุด ห้ามแต่งผล คำตอบ หรือภาพหน้าจอขึ้นเอง
10. สรุป URL ที่ใช้ได้จริง ผลที่ผ่านและไม่ผ่านตามจริง และสิ่งที่ยังไม่ได้ทดสอบ
```

> **สถานะ:** พรอมต์สามชุดด้านบนเป็นฉบับแก้ไขแบบ container เดียว **ยังรอการทดลองรันจากศูนย์** ผลจริงทั้งหมดในหัวข้อ 5 ด้านล่างเป็นของ **เวอร์ชันก่อนหน้าแบบสอง container** (หน้าเว็บ 8005 + API 8004) ไม่ใช่หลักฐานว่าพรอมต์ชุดใหม่ใช้ได้

---

## 5 · ผลจริงจากเวอร์ชันก่อนหน้า (สอง container: หน้าเว็บ 8005 + API 8004)

> ผลจริง ภาพหน้าจอ และ log ทั้งหมดในหัวข้อ 5 มาจากเวอร์ชันก่อนหน้าที่แยก `lab04-web` (nginx, พอร์ต 8005) ออกจาก `lab04-api` (พอร์ต 8004) เก็บไว้เป็นหลักฐานของเวอร์ชันนั้นเท่านั้น ยังไม่ได้ทดสอบกับแบบ container เดียวในหัวข้อ 1–4
>
> **อัปเดต:** ผู้ประสานงานได้ลบโค้ดเวอร์ชันก่อนหน้า (`api/`, `web/`, `deploy/`, `examples/`, `prompt-trial-01`) และลบ container `lab04-api` / `lab04-web`, image ของทั้งสอง, volume สำเนา credential `lab04-accounts` และ network `lab04-net` ออกจากทั้งโฟลเดอร์ staging และโฟลเดอร์หลักแล้ว devtools และบัญชีต้นฉบับที่ล็อกอินไว้ยังอยู่ครบ ชื่อไฟล์ คำสั่ง และ path ที่อ้างถึงในหัวข้อ 5–8 จึงเป็นบันทึกย้อนหลังเท่านั้น ไม่มีอยู่ในโฟลเดอร์นี้แล้ว

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

แกนของโค้ด (เดิมอยู่ที่ `examples/openai_client.py` ซึ่งถูกลบแล้ว) ที่คัดลอกไปใช้ได้

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

## 6 · ประวัติแชตถูกส่งให้ CLI อย่างไร (อ่านเพิ่มเติม · อ้างอิงเวอร์ชันก่อนหน้า)

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

## 7 · ข้อจำกัดด้านความปลอดภัยที่ต้องรู้ (อ่านเพิ่มเติม · อ้างอิงเวอร์ชันก่อนหน้า)

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

## 8 · แก้ปัญหาที่พบบ่อย (อ่านเพิ่มเติม · อ้างอิงเวอร์ชันก่อนหน้า)

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

โค้ดของเวอร์ชันก่อนหน้าแบบสอง container (`api/`, `web/`, `deploy/`, `examples/`) และ `prompt-trial-01` **ถูกผู้ประสานงานลบแล้ว** ตอนนี้ยังไม่มีโค้ดของพรอมต์ชุดใหม่ในโฟลเดอร์นี้ เหลือเพียงหลักฐานย้อนหลังและเอกสารด้านล่าง

<details>
<summary>เปิดอ่าน: หน้าที่ของแต่ละไฟล์</summary>

| ไฟล์ | หน้าที่ |
|---|---|
| `assets/architecture.png`, `assets/chat-ui-concept.png` | ภาพแนวคิด **ฉบับร่าง** (ไม่ใช่ภาพหน้าจอ) |
| `assets/01-…png` – `assets/12-…png` | ภาพหน้าจอจริงจากการ deploy และทดสอบของผู้ประสานงาน |
| `assets/build.log`, `deploy.log`, `smoke.log`, `smoke-with-account-checks.log` | log จริงของ build · token/creds/up/verify · smoke รอบแรก (11) และรอบล่าสุด (13) |
| `assets/ten-exchanges.json`, `.txt`, `fable-five-exchanges.txt`, `dropdown-checks.json` | transcript จริง 10 รอบ และผลตรวจ dropdown |
| `assets/authoring-environment-note.md` | บันทึกแพ็กเกจ apt ที่ติดตั้งใน devtools ระหว่างเขียนแลป |
| `docs/implementation-reference.md` | ข้อกำหนดการสร้างแบบละเอียดสำหรับ AI อ้างอิง (ผู้เรียนไม่ต้องอ่าน) |

</details>

## 10 · สถานะและสิ่งที่ยังค้างอยู่

แบบ container เดียว (พรอมต์ชุดใหม่ในหัวข้อ 2–4)

- [ ] ทดลองรันพรอมต์ 1–3 จากศูนย์ · **ยังไม่ได้ทำ**
- [ ] แผนภาพสถาปัตยกรรมฉบับใหม่ · **ยังไม่ได้ทำ** (หัวข้อ 1 ใช้ข้อความสรุปแทนไปก่อน)

เวอร์ชันก่อนหน้าแบบสอง container: เสร็จและมีหลักฐานแล้ว

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
