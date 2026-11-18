สร้างสกิล `llm-chat-capacity` เวอร์ชัน 0 และติดตั้งเป็นสกิลของโปรเจกต์ที่ `.claude/skills/llm-chat-capacity` แล้ว ยังไม่ได้รันสกิลจริงบน Vast.ai รอบนี้ไม่ได้เช่าเครื่องเลย ส่วนที่ลองรันแล้วคือ `report.py` ตัวที่คัดลอกมา ป้อนผลชุด 1 GPU เดิมเข้าไปอย่างเดียว ได้ `metrics.json` และกราฟ 4 รูป ความจุออกมาตรงกับของเดิม (ทีละคำถาม 2 คน · Continuous Batching 192 คน) แปลว่าขั้นที่ 9 ที่วัดแค่ 1 GPU ใช้ตัวสรุปผลนี้ได้

## สกิลทำอะไรได้
วัดว่าแชทบอท `shop-bot` (Qwen3-4B-Instruct-2507 เปิดด้วย vLLM หลัง NGINX ที่ต้องใช้ API key) รับผู้ใช้พร้อมกันได้กี่คน ตามเกณฑ์ SLO เดิม: TTFT p95 ≤ 2 วินาที · 95% ของคำถามได้ ≥ 15 token/วินาที · error < 1%

ทำครบในคำสั่งเดียว:
1. เช่าเครื่อง
2. ติดตั้ง vLLM และ NGINX แล้วโหลดโมเดล โดยส่ง HF_TOKEN ทาง stdin และตรวจว่าไม่เหลือ token บนเครื่อง
3. ทดสอบแชท และตรวจว่าเรียกแบบไม่มี key ได้ 401
4. ยิงโหลดทีละชุด: ทีละคำถาม → Continuous Batching 1 ใบ → 2 ใบหลัง least_conn → Round Robin เทียบ least_conn
5. สร้าง `metrics.json` และกราฟ
6. ลบเครื่องและสรุปค่าใช้จ่ายจากบิล

งานที่แตะ Vast.ai ทั้งหมดส่งต่อให้สกิล `vastai` ไม่ได้เขียนวิธีใช้ซ้ำ ในสกิลมีเกณฑ์ตรวจผ่านพร้อมตัวเลขอ้างอิงจาก LAB 6 (2 / 192 / 384 คน, efficiency 100%) และกติกาเรื่องเงิน: ลบเครื่องเสมอ เช่าครั้งละเครื่องเดียว แตะเฉพาะเครื่องป้ายที่กำหนด เตือนเรื่องค่าดาวน์โหลดที่แพงกว่าค่า GPU (งบอ้างอิง $0.597) ถ้าเครื่องเปิดเกิน 1.5 ชั่วโมงต้องรายงานก่อนทำต่อ

## ค่าที่ปรับได้ (ค่าเริ่มต้น)
| ค่า | ค่าเริ่มต้น |
|---|---|
| `gpu` / `num_gpus` | RTX 3090 / 2 (ถ้าใช้ 1 ใบ จะตัดชุด 2 GPU กับ lbmix ออกเอง) |
| `max_price` | $0.60/ชม. (2 ใบ) · $0.30/ชม. (1 ใบ) |
| `label` | `vapp-lab6` |
| `offer_filter` | verified · reliability ≥ 0.95 · เน็ต ≥ 500 Mbps · CPU ≥ 16 · CUDA ≥ 13 · ไม่เอาเครื่องในจีน |
| `image` / `disk_gb` | PyTorch 2.8 + CUDA 12.8 / 60 GB |
| `ready_timeout` / `max_idle_temp` | 10 นาที / 60°C |
| `model` | Qwen/Qwen3-4B-Instruct-2507 |
| `runs` | `single` `batch1` `batch2` `lbmix` |
| `levels_single` | 1,2,3,4,6,8 |
| `levels_batch1` | 1–256 ทีละ 32 |
| `levels_batch2` | 128–512 ทีละ 64 |
| `duration` / `warmup` / `max_tokens` | 30 วินาที / 5 วินาที / 150 |
| `lbmix_users` / `long_frac` / `long_max_tokens` | 448 / 0.2 / 600 |
| `samples` | ใช่ |
| `out_dir` | `lab6_llm_chat/results` (ถ้ามีผลเดิมอยู่จะใช้โฟลเดอร์ใหม่ ไม่เขียนทับ) |
| `keep_machine` | ไม่ |
| `container` / `ssh_key` | ค่าเดิมของ LAB |

## ไฟล์ที่สร้าง
- `lab6_llm_chat/skill_v0/SKILL.md`
- `lab6_llm_chat/skill_v0/scripts/` คัดลอกจาก `code/` ไม่ได้เขียนใหม่: `install.sh` · `cluster.sh` · `test_chat.py` · `precheck.py` · `precheck2.py` · `loadtest.py` · `run_lbmix.sh` · `report.py`
  - ไม่ได้คัดลอก `test_step2.json` เพราะเป็นไฟล์ผล ไม่ใช่โค้ด
- `.claude/skills/llm-chat-capacity/` เป็นสำเนาของ `skill_v0` ทั้งชุด เทียบแล้วตรงกันทุกไฟล์

ข้อสังเกต:
- **สคริปต์ดาวน์โหลดโมเดล:** LAB 6 ไม่มีไฟล์นี้ใน `code/` สกิลจึงบอกเป็นขั้นตอนให้ใช้คำสั่ง `hf download` และถ้าไม่มีคำสั่งนี้ให้ใช้ `huggingface-cli download` แทน
- **ภาพ `dataset_samples.png`:** ไม่มีโค้ดที่ใช้สร้างภาพนี้ สกิลจึงเก็บแค่ `dataset_samples.json`
