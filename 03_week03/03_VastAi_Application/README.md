# เช่า GPU บน Vast.ai มาเทรนโมเดล แล้วต่อเข้าเว็บแอป

![นักศึกษานั่งหน้าแล็ปท็อปที่เปิดเว็บตรวจความปลอดภัยหน้างาน ด้านหลังเป็นห้องเซิร์ฟเวอร์ GPU](image/cover.jpg)

บทนี้ต่อจาก [01_VastAi_Skill](../01_VastAi_Skill/readme.md) · บทก่อนเราเช่า GPU มา **รัน**โมเดลสำเร็จรูป บทนี้เราเช่า GPU มา **เทรน**โมเดลของเราเอง วัดผลว่าดีขึ้นจริงไหม แล้วต่อโมเดลเข้ากับเว็บแอป

ทุกขั้นเป็นพรอมต์ Copy & Paste ใน **Claude Code** ด้วยสกิล `vastai` · แต่ละ LAB อยู่ในโฟลเดอร์ของตัวเอง มี `README.md` ของตัวเอง (ทฤษฎี การทดลอง พรอมต์ทีละขั้น ผลจริง) · พรอมต์บอกเป้าหมายเป็นข้อ ๆ ส่วนคำสั่งจริง AI คิดเอง · ทุก LAB ปิดท้ายด้วยการเก็บงานเป็นสกิลเวอร์ชัน 0

![6 ขั้นของทุก LAB: Dataset, เช่า GPU บน Vast.ai, Training, Evaluation บน Test Set, AI server กับเว็บแอป, ลบเครื่อง](image/t0-pipeline.png)

| LAB | โฟลเดอร์ | ทำอะไร | คำถามของการทดลอง | ค่าเช่าจริง |
|---|---|---|---|---|
| [LAB 0](#lab-0--เตรียม-key-3-ตัว) | — | เตรียม key 3 ตัวในไฟล์ `.env` | — | ฟรี |
| [LAB 1](lab1_yolo/README.md) | [lab1_yolo](lab1_yolo/README.md) | เทรน YOLO ตรวจหมวกนิรภัย ด้วย Dataset จาก Roboflow → เว็บตรวจความปลอดภัยหน้างาน | เทรนต่อด้วยข้อมูลของเราแล้วดีขึ้นแค่ไหน | $0.38 |
| [LAB 2](lab2_multigpu/README.md) | [lab2_multigpu](lab2_multigpu/README.md) | เทรนงานเดิมบน 1 GPU เทียบ 2 GPU | เพิ่ม GPU แล้วเร็วขึ้นกี่เท่า คุ้มเงินไหม | $0.51 |
| [LAB 3](lab3_qlora/README.md) | [lab3_qlora](lab3_qlora/README.md) | QLoRA โมเดลเล็กให้แชทบอทร้านนวด (ข้อมูลฝึกจากโมเดลครู) | โมเดลเล็กที่เทรนเพิ่ม แทนโมเดลใหญ่ได้ไหม | $0.69 |
| [LAB 4](lab4_vlm/README.md) | [lab4_vlm](lab4_vlm/README.md) | Fine-tune VLM อ่านใบเสร็จ → เว็บสมุดรายจ่าย | เทรนด้วยใบเสร็จ 800 ใบ แล้วอ่านแม่นขึ้นเท่าไร | $0.58 |
| [LAB 5](lab5_image_api/README.md) | [lab5_image_api](lab5_image_api/README.md) | API ตรวจภาพ YOLO: Micro-batching + หลาย process + Load Balancer 1 → 2 ใบ | GPU 1 ใบรับผู้ใช้พร้อมกันได้กี่คน และคอขวดอยู่ที่ไหน | $1.02 |
| [LAB 6](lab6_llm_chat/README.md) | [lab6_llm_chat](lab6_llm_chat/README.md) | แชทบอท LLM: Continuous Batching + Load Balancer 1 → 2 ใบ | GPU 1 ใบคุยพร้อมกันได้กี่คน และเพิ่ม GPU แล้วรับได้เพิ่มเท่าไร | $0.60 |
| [LAB 7](lab7_job_queue/README.md) | [lab7_job_queue](lab7_job_queue/README.md) | อ่านใบเสร็จด้วย VLM เป็นงานคิว: RabbitMQ + GPU Worker 1 → 2 ใบ | งานหนักเข้าพร้อมกันเกินความจุ ระบบคิวช่วยอะไร และเพิ่ม Worker แล้วรับได้เพิ่มเท่าไร | $0.78 |
| [LAB 8](lab8_hybrid/README.md) | [lab8_hybrid](lab8_hybrid/README.md) | บริการสร้างภาพ: API gateway + RabbitMQ + GPU Worker 1 → 2 ใบ | GPU 1 ใบรับผู้ใช้พร้อมกันได้กี่คน และออกแบบระบบอย่างไรให้รับได้มากขึ้น | $0.57 |

**ต้องมีก่อน**
- ทำ [บท 01](../01_VastAi_Skill/readme.md) ถึง LAB 2 แล้ว: container `multi-account` รันอยู่ · มีสกิล `vastai` · ตั้ง API key และกุญแจ SSH ของ Vast.ai แล้ว
- Docker Desktop บนเครื่องนี้ (เว็บของทุก LAB รันด้วย `docker compose` บนเครื่องเรา)
- Claude Code เปิดที่โฟลเดอร์ของบทนี้ (`03_week03/03_VastAi_Application`) · "โฟลเดอร์ปัจจุบัน" ในทุกพรอมต์หมายถึงโฟลเดอร์นี้

> ⚠️ **เสียเงินจริง** — ทุก LAB จบด้วยพรอมต์ **ลบเครื่อง** ห้ามข้าม แล้วดูหน้า [Instances](https://cloud.vast.ai/instances/) ว่าว่าง

---

## LAB 0 · เตรียม key 3 ตัว

คัดลอกไฟล์ `.env_example` เป็น `.env` แล้วใส่ค่า 3 บรรทัด · ไฟล์ `.env` ไม่ถูกส่งขึ้น Git

| บรรทัดใน `.env` | ใช้ทำอะไร | เอามาจากไหน |
|---|---|---|
| `VAST_API_KEY` | เช่าเครื่อง | ตัวเดียวกับ [บท 01 LAB 0](../01_VastAi_Skill/readme.md#lab-0--เตรียมบัญชี-vastai-และกุญแจ-2-ดอก) |
| `ROBOFLOW_API_KEY` | ดาวน์โหลด Dataset ของ LAB 1–2 | 2 ขั้นข้างล่าง |
| `HF_TOKEN` | ดาวน์โหลดโมเดลและ Dataset ของ LAB 3–4 | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → Create new token → ชนิด Read |

### API key ของ Roboflow

**ขั้นที่ 1** · เปิด [app.roboflow.com](https://app.roboflow.com) แล้วล็อกอิน (สมัครฟรี)

![หน้า Sign In ของ Roboflow วงกลมหมายเลข 1 ที่ปุ่มล็อกอินด้วย Google GitHub หรืออีเมล](image/rf-01-signin.png)

**ขั้นที่ 2** · คลิกชื่อ workspace มุมซ้ายบน → **Settings** → **API Keys** → กดปุ่มคัดลอกของ **Private API Key** แล้ววางในไฟล์ `.env`

![หน้า API Keys ของ Roboflow วงกลมหมายเลข 1 ที่เมนู API Keys และหมายเลข 2 ที่ปุ่มคัดลอกของ Private API Key ค่า key ถูกเบลอ](image/rf-02-apikey.png)
*ค่า key และชื่อ workspace ในภาพถูกเบลอ*

- ใช้ **Private API Key** เท่านั้น · Publishable API Key ใช้ดาวน์โหลด Dataset ไม่ได้
- key เป็นความลับ ห้ามวางในแชท ในภาพหน้าจอ หรือในไฟล์อื่นนอกจาก `.env`

---

## ไฟล์ในโฟลเดอร์นี้

| ไฟล์ / โฟลเดอร์ | คืออะไร |
|---|---|
| `.env_example` | ตัวอย่างไฟล์ `.env` (key 3 ตัว) |
| `lab1_yolo/` | LAB 1 · เทรน YOLO ตรวจหมวกนิรภัย + เว็บตรวจความปลอดภัยหน้างาน |
| `lab2_multigpu/` | LAB 2 · เทรนงานเดิมบน 1 GPU เทียบ 2 GPU |
| `lab3_qlora/` | LAB 3 · QLoRA โมเดลเล็กให้แชทบอทร้านนวด |
| `lab4_vlm/` | LAB 4 · Fine-tune VLM อ่านใบเสร็จ + เว็บสมุดรายจ่าย |
| `lab5_image_api/` | LAB 5 · API ตรวจภาพ: วัดความจุ GPU 1 ใบ แล้วเพิ่มด้วย Micro-batching และ Load Balancer |
| `lab6_llm_chat/` | LAB 6 · แชทบอท LLM: Continuous Batching + Load Balancer |
| `lab7_job_queue/` | LAB 7 · งานคิวอ่านใบเสร็จด้วย RabbitMQ + GPU Worker |
| `lab8_hybrid/` | LAB 8 · ระบบผสมสำหรับบริการสร้างภาพ (RabbitMQ) + เว็บ PixelQueue |
| `image/` | ภาพประกอบของหน้ารวม |
