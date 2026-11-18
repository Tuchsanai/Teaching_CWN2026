---
name: vlm-queue-capacity
description: วัดว่าบริการอ่านใบเสร็จด้วย VLM (Qwen/Qwen3-VL-2B-Instruct อ่านใบเสร็จ 4 ใบต่องานออกมาเป็น JSON) บนเครื่อง GPU ที่เช่าจาก Vast.ai รองรับผู้ใช้พร้อมกันได้กี่คนภายใต้เกณฑ์ SLO ครบวงจรในคำสั่งเดียว เทียบ Baseline API แบบ synchronous บน GPU 1 ใบ (ผู้ใช้รอได้ 30 วินาที) กับระบบคิว (API gateway + RabbitMQ + GPU Worker 1 ตัวต่อ GPU) ที่มี Worker 1 และ 2 ตัว — เช่าเครื่อง 2 GPU → ติดตั้งโมเดล + RabbitMQ → ยิงโหลดแบบไล่ผู้ใช้ N ของแต่ละระบบ → งานถล่ม 60 งานใน 10 วินาที → (เลือกได้) ฆ่า Worker กลางงานเพื่อพิสูจน์ว่างานไม่หาย → metrics.json และกราฟ → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล vlm-queue-capacity", "วัดความจุระบบคิวอ่านใบเสร็จ", "ระบบคิวรับผู้ใช้พร้อมกันได้กี่คน", "API ตรงเทียบคิว RabbitMQ", "เพิ่ม Worker / GPU แล้วรับได้กี่เท่า", "ทำ LAB 7 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / ราคา / ระดับ N / เวลาต่อระดับ / ชุดการวัด / ป้ายเครื่อง / โฟลเดอร์ผลที่ต่างไปจากเดิม
---

# vlm-queue-capacity (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 7 (ขั้นที่ 1–5 และ 7) ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** บนเครื่องเช่าวางเป็น `/workspace/lab7/code/*.py` และใบเสร็จตัวอย่างที่ `/workspace/lab7/samples/*.jpg` (ตัวยิงโหลดหา `../samples` จากโฟลเดอร์ของตัวเอง) แล้ว `sed -i 's/\r$//' /workspace/lab7/code/*.py` · ทุกสคริปต์รันบนเครื่องเช่าด้วย `/venv/main/bin/python` ยกเว้น `report.py`

| สคริปต์ | หน้าที่ |
|---|---|
| `common.py` | ค่าคิวที่ gateway กับ Worker ใช้ร่วมกัน: `receipts.jobs` (durable · ยาวสุด `LAB7_MAX_QUEUE` = 1000 · เกินแล้ว broker ปฏิเสธ → gateway ตอบ 503) · dead-letter `receipts.jobs.dlq` · คิว event `receipts.events` · ต่อ RabbitMQ ที่ `LAB7_AMQP_URL` (ค่าเริ่มต้น guest@127.0.0.1:5672) |
| `sync_api.py` | Baseline: API แบบ synchronous บน GPU 0 ใบเดียว พอร์ต `LAB7_PORT` (8000) · `POST /v1/jobs` (header `X-API-Key`, multipart `files` 1–8 รูป) ตอบผลในการเชื่อมต่อเดิม · `GET /v1/stats` (งานเสร็จ · รอ · อ่านหลังผู้ใช้เลิกรอ) · `GET /health` · อ่านทีละงาน ทีละใบ แบบไม่สุ่ม ได้ `{items:[{name,qty,price}], subtotal, tax, total}` |
| `gateway.py` | API gateway พอร์ต 8000: `POST /jobs` → 202 + `job_id` ทันที · `GET /jobs/{id}` สถานะ queued/running/done/failed · Worker · เวลารอคิว · เวลารวม · ผลอ่าน · `GET /jobs` · `GET /stats` ความยาวคิว · Worker ที่ต่ออยู่ · งานแต่ละสถานะ · งานส่งซ้ำ · dead-letter · `GET /health` · เก็บทุกงานใน SQLite `LAB7_DB` (`/workspace/lab7/jobs.db`) |
| `worker.py` | Worker 1 ตัวต่อ GPU 1 ใบ (`LAB7_GPU=0` หรือ `1`) อ่านแบบเดียวกับ `sync_api.py` · prefetch 1 · ack หลังอ่านครบเท่านั้น · งานที่ทำให้โค้ดพัง → dead-letter · ส่ง started/done/failed/heartbeat ผ่านคิว event · ต่อ RabbitMQ ใหม่เองเมื่อหลุด |
| `loadtest_sync.py` | ตัวยิงโหลดของ Baseline (รันบนเครื่องเช่า): `level --users N` · `sweep` · `burst --jobs 60 --within 10` · `sweep --then-burst` · ผู้ใช้รอเกิน `--timeout` 30 วินาที = ล้ม |
| `loadtest.py` | ตัวยิงโหลดของระบบคิว: โหมดเดียวกัน + `--start-users` `--gpus 0,1` (วัด GPU util ทั้งสองใบ) + `killtest --kill-gpu 1 --kill-at 20` (SIGKILL Worker ที่เปิดด้วย `LAB7_GPU=1`) · ส่งงาน → ถาม `GET /jobs/{id}` ทุก 0.5 วินาทีจนเสร็จ (ไม่มีเพดานเวลา) · บันทึกความยาวคิวทุก 1 วินาที |
| `report.py` | `python report.py --results <out_dir>` อ่าน `baseline/` `queue_1worker/` `queue_2worker/` `worker_kill/` → `metrics.json` + `charts/*.png` (ป้ายภาษาอังกฤษ) · โฟลเดอร์ไหนไม่มีก็ข้ามพร้อมกราฟที่ต้องใช้ · ต้องมี matplotlib (บนเครื่องเช่าไม่มี จึงรันใน container หลังดึงผลกลับ) |

ตัวเลือกร่วมของตัวยิงทั้งสอง: `--url` (`http://127.0.0.1:8000`) · `--key-file` (`/workspace/lab7/.api_key`) · `--out <โฟลเดอร์>` · `--receipts 4` · `--duration 75` · `--warmup 15` · `--think 10` · `--slo-p95 20` · `--slo-fail-pct 1` · `--max-users 64` · `--jobs 60` · `--within 10` · ผลแต่ละระดับเป็น `level_NXX.json` · `sweep_summary.json` · `burst.json` (`killtest.json` สำหรับ kill test)

นิยาม: **ผู้ใช้พร้อมกัน N** = ผู้ใช้จำลอง N คน วน ส่งงาน (สุ่มใบเสร็จ 4 ใบ) → รอผล → คิด 10 วินาที → ส่งใหม่ · นับเฉพาะงานที่ส่งในช่วงวินาทีที่ 15–75 ของแต่ละระดับ · **SLO** = เวลารอผล p95 ≤ 20 วินาที และงานล้ม < 1% · **ความจุ** = N มากที่สุดที่ผ่าน SLO · `sweep` ไล่ N = 1, 2, 4, 6, 8, … (เพิ่มทีละ 2) หยุดเมื่อไม่ผ่าน 2 ระดับติดกัน · `report.py` ตัดสิน SLO ใหม่จากไฟล์ `level_N*.json` ทุกไฟล์ด้วยเกณฑ์เดียวกัน

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` / `num_gpus` | RTX 3090 / 2 | GPU ในเครื่องเดียว (VRAM ≥ 16 GB ต่อใบ) · `num_gpus` = 1 → ข้ามชุด `queue2` และ `kill` |
| `max_price` | $0.60/ชม. | ราคารวมทั้งเครื่องสูงสุด |
| `label` | `vapp-lab7` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | verified · SSH ตรงได้ (`direct_port_count>=1`) · `inet_down>=500` · `cpu_cores_effective>=12` · นอกจีน · เรียงตามราคา | เกณฑ์เลือกเครื่อง (เครื่องในจีนมักโหลดจาก Hugging Face ไม่ได้) |
| `image` / `disk_gb` / `ports` | `vastai/pytorch` / 40 / เปิดพอร์ต 8000 (`--env "-p 8000:8000"`) | image ที่มี Python พร้อมใน `/venv/main` · พอร์ต 8000 ให้ gateway เรียกจากภายนอกได้ |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `model` | `Qwen/Qwen3-VL-2B-Instruct` → `/workspace/models/Qwen3-VL-2B-Instruct` | เปลี่ยนโมเดลได้ด้วย `LAB7_MODEL` ตอนเปิด `sync_api.py` / `worker.py` |
| `samples_dir` | `lab7_job_queue/samples` (6 ใบจาก Test Set ของ CORD-v2) | ใบเสร็จที่ตัวยิงสุ่มใช้ |
| `runs` | `baseline` `queue1` `queue2` `kill` | ชุดที่จะวัด (ตารางถัดไป) · ผู้ใช้สั่ง "ไม่ต้องทดลองฆ่า Worker" → ตัด `kill` |
| `levels` | `auto` | `auto` = ใช้ `sweep` (1, 2, 4, 6, …; `queue2` เริ่มที่ `start_users_2w`) · ถ้าผู้ใช้ให้รายการ เช่น `2,4,6,8,12,16` → รัน `level --users N` ทีละ N ตามรายการ |
| `stop_after_misses` | 2 | ไม่ผ่าน SLO กี่ระดับติดกันแล้วหยุดชุดนั้น (ใช้กับ `levels` แบบรายการด้วย เพื่อไม่เสียเงินกับระดับที่รู้ผลแล้ว · ผู้ใช้สั่ง "วัดครบทุกระดับ" → ไม่หยุด) |
| `start_users_2w` | 4 | N แรกของชุด `queue2` เมื่อ `levels` = `auto` |
| `level_sec` / `warmup_sec` / `think_sec` | 75 / 15 / 10 | `--duration` `--warmup` `--think` |
| `slo_p95` / `slo_fail_pct` / `sync_timeout` | 20 วิ / 1% / 30 วิ | เกณฑ์ SLO และเวลาที่ผู้ใช้ Baseline รอได้ |
| `burst_jobs` / `burst_within` | 60 / 10 วิ | งานถล่ม (`--jobs` `--within`) · `0` = ไม่ยิงงานถล่ม |
| `kill_gpu` / `kill_at` | 1 / 20 วิ | Worker ที่ถูกฆ่าและวินาทีที่ฆ่าในชุด `kill` |
| `out_dir` | `lab7_job_queue/results` | โฟลเดอร์เก็บผลในโฟลเดอร์บท (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ใหม่ เช่น `lab7_job_queue/results/skill_v0_run` ห้ามเขียนทับไฟล์เดิม) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

ชุดที่วัด (`runs`) ตามลำดับ — ทุกชุดใช้เครื่องเดียวกัน · ตัวยิงรันบนเครื่องเช่าแบบ `cd /workspace/lab7/code && setsid nohup /venv/main/bin/python <ตัวยิง> ... --out /workspace/lab7/results/<โฟลเดอร์> > /workspace/lab7/results/<โฟลเดอร์>/loadtest.log 2>&1 < /dev/null &` แล้วอ่าน log เป็นระยะจนมีบรรทัด `"mode": "burst"` (หรือ `sweep` / `killtest` ถ้าไม่ยิงงานถล่ม)

| ชุด | ระบบที่ต้องเปิดอยู่ | คำสั่งตัวยิง (`levels` = `auto`) | โฟลเดอร์ผล | เวลาอ้างอิง (RTX 3090) |
|---|---|---|---|---|
| `baseline` | `sync_api.py` (GPU 0) | `loadtest_sync.py sweep --then-burst` | `baseline/` | ไล่ N ~7 นาที + งานถล่ม ~10.5 นาที (server อ่านงานที่ผู้ใช้เลิกรอจนครบ) |
| `queue1` | RabbitMQ + `gateway.py` + Worker GPU 0 | `loadtest.py sweep --then-burst` | `queue_1worker/` | ไล่ N ~7 นาที + งานถล่ม ~11 นาที |
| `queue2` | + Worker GPU 1 | `loadtest.py sweep --start-users <start_users_2w> --gpus 0,1 --then-burst` | `queue_2worker/` | ไล่ N ~5 นาที + งานถล่ม ~5.5 นาที |
| `kill` | gateway + Worker GPU 0 + GPU 1 | `loadtest.py killtest --jobs <burst_jobs> --within <burst_within> --kill-gpu <kill_gpu> --kill-at <kill_at> --gpus 0,1` | `worker_kill/` | ~11 นาที (เหลือ Worker ตัวเดียวทำต่อ) |

`levels` แบบรายการ: แทน `sweep` ด้วยคำสั่งเดียวที่วน `level --users N` ทีละ N ตามรายการ (ชุด `queue2` ใส่ `--gpus 0,1`) อ่าน `slo_pass` จากบรรทัด JSON ของแต่ละระดับแล้วหยุดตาม `stop_after_misses` · จากนั้นยิง `burst` แยกถ้า `burst_jobs` > 0 · ระดับที่ข้ามไปต้องบอกในสรุปว่า "ไม่ได้วัด เพราะไม่ผ่าน SLO ติดกันแล้ว"

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `HF_TOKEN` · API key ของบริการ) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาเครื่องที่มี `gpu` × `num_gpus` ในเครื่องเดียวตาม `max_price` และ `offer_filter` เช่าด้วย `image` `disk_gb` `ports` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ
   - เกิน `ready_timeout` หรือ GPU ไม่ครบ → ลบทันทีแล้วเช่าเครื่องถัดไป · จด GPU · ราคาจริงต่อชั่วโมง · ที่ตั้ง · CPU cores · IP และพอร์ตภายนอกที่จับคู่กับ 8000
2. **ติดตั้ง** (อ้างอิง ~5 นาที):
   - `mkdir -p /workspace/lab7/{code,samples} /workspace/lab7/results/{baseline,queue_1worker,queue_2worker,worker_kill} /workspace/models` (ตัวยิงเขียน log ลงโฟลเดอร์ผลเหล่านี้ · log ของ gateway / Worker / RabbitMQ อยู่ที่ `/workspace/lab7/*.log`) คัดลอก `scripts/*.py` ไป `code/` และใบเสร็จจาก `samples_dir` ไป `samples/` แล้วตัด `\r`
   - `/venv/main/bin/pip install -U transformers accelerate fastapi uvicorn python-multipart pika httpx psutil nvidia-ml-py huggingface_hub`
   - ดาวน์โหลด `model` ลง `/workspace/models/Qwen3-VL-2B-Instruct` (~4 GB · ~30 วินาที) ถ้าต้องใช้ `HF_TOKEN` ให้ส่งผ่าน stdin ของ SSH เข้าเป็นตัวแปรของคำสั่งนั้นเท่านั้น ห้ามเขียนลงไฟล์
   - สุ่ม API key ครั้งเดียวด้วย Python `secrets` เขียนลง `/workspace/lab7/.api_key` (สิทธิ์ 600 ไม่พิมพ์ค่า) · ทุกสคริปต์อ่าน key จากไฟล์นี้
   - `apt-get install -y rabbitmq-server` แล้ว `rabbitmq-plugins enable rabbitmq_management` (หน้า management พอร์ต 15672)
   - **กับดักที่เจอจริง**
     - **CUDA error 804** (torch เปิด GPU ไม่ได้): image โหลด libcuda ตัว compat ก่อน และ apt สร้าง cache ไลบรารีใหม่ทำให้เป็นซ้ำ → หลัง apt ทุกครั้ง ย้าย `/etc/ld.so.conf.d/00-compat-*.conf` ออกไปไว้ที่ `/root/ld.so.conf.d.disabled/` แล้ว `ldconfig` · และเปิดทุกโปรเซสที่ใช้ GPU ด้วย `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/nvidia/lib64` · ตรวจด้วย `python -c "import torch; print(torch.cuda.device_count())"` ต้องได้ `num_gpus`
     - **RabbitMQ เปิดไม่ขึ้น** เพราะอ่าน `/root/.erlang.cookie` ไม่ได้ → เปิด `rabbitmq-server` เป็นผู้ใช้ `rabbitmq` แบบ `setsid nohup` ด้วย `HOME=/var/lib/rabbitmq` และสั่ง `rabbitmqctl` แบบ `cd /var/lib/rabbitmq; HOME=/var/lib/rabbitmq rabbitmqctl ...` · ต้องเห็น `rabbitmqctl status` ผ่านก่อนเปิด gateway
3. **`baseline`**: เปิด `LAB7_KEY_FILE=/workspace/lab7/.api_key setsid nohup python sync_api.py > /workspace/lab7/results/baseline/server.log 2>&1 &` (พร้อม `LD_LIBRARY_PATH`) รอ `/health` ตอบ แล้วทดสอบ 1 งานพร้อม key ต้องได้ผลอ่าน และไม่มี key ต้องได้ 401 · ยิงโหลดตามตาราง · จบแล้ว**ปิด `sync_api.py`** เพื่อคืน GPU 0 และพอร์ต 8000
4. **`queue1`**: เปิด RabbitMQ (ถ้ายังไม่เปิด) · `gateway.py` (log `gateway.log`) · `LAB7_GPU=0 ... worker.py` (log `worker_gpu0.log`) ทุกตัวแบบ `setsid nohup` · ทดสอบจาก container (นอกเครื่องเช่า) ที่ `http://<IP>:<พอร์ตภายนอกของ 8000>`: `POST /jobs` พร้อม key ต้องได้ 202 + `job_id` และ `GET /jobs/{id}` จนได้ `done` · ไม่มี key ต้องได้ 401 (อ่าน key จากไฟล์บนเครื่องเช่าผ่าน SSH ใส่ตัวแปร ห้ามพิมพ์) · ยิงโหลดตามตาราง
5. **`queue2`**: เปิด `LAB7_GPU=1 ... worker.py` (log `worker_gpu1.log`) แล้วดู `GET /stats` ต้องมี Worker ต่ออยู่ 2 ตัว · ยิงโหลดตามตาราง · ถ้าไม่วัด `queue1` ให้เปิด RabbitMQ + gateway + Worker ทั้งสองตัวตรงนี้
6. **`kill`**: Worker 2 ตัวต้องเปิดอยู่ (เปิดด้วย `LAB7_GPU=<เลข>` เพราะตัวยิงหา PID จากตัวแปรนี้) · ยิงตามตาราง · จบแล้วเปิด Worker ของ `kill_gpu` กลับ (ถ้าผู้ใช้ขอเว็บต่อ)
   - ระหว่างทุกชุดรายงานความคืบหน้าทุก 2–3 นาทีจากบรรทัด JSON ของแต่ละระดับ · ผลแปลก (เช่น 2 Worker ได้ไม่เกิน 1 Worker) → ดู `/stats` (`workers_connected`) และ `worker_gpu*.log` ก่อนวัดซ้ำ · การวัดซ้ำเพื่อวินิจฉัยให้ `--out` ไปโฟลเดอร์ `diag_*` เพื่อไม่ให้ `report.py` นับรวม
   - SSH หลุดไม่ต้องวัดซ้ำ ทุกโปรเซสรันแยกจาก SSH ให้ต่อใหม่แล้วอ่าน log ต่อ
7. **รวมผล**: ดึง `/workspace/lab7/results/*` ทั้งโฟลเดอร์ (JSON ทุกการทดลอง `loadtest.log` `server.log` · ไม่เอา `jobs.db` และ `.api_key`) มาไว้ที่ `out_dir` แล้วรันใน container `python <โฟลเดอร์สกิล>/scripts/report.py --results <out_dir>` (ไม่มี matplotlib → `pip install matplotlib` ก่อน) · เปิดดูกราฟทุกรูปอย่างน้อย 1 ครั้ง และ `grep` ค่า key ใน `out_dir` ต้องไม่พบ
8. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices): อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล

สกิลนี้ไม่เปิดเว็บ ถ้าผู้ใช้ขอเว็บดูคิว (ของ LAB 7 ที่ `lab7_job_queue/code/web`) ให้ทำก่อนขั้นที่ 8 โดยให้ Worker ครบ 2 ตัว เขียน `lab7_job_queue/code/web/.env` ตาม `.env.example` (ที่อยู่ภายนอกของพอร์ต 8000 + API key) แล้วเปิดด้วย `docker compose -p vapp-lab7 up -d --build` บน Docker Desktop ของเครื่องหลัก (พอร์ต 3407 · docker ใน container `multi-account` แยกจาก Docker Desktop) และปิดด้วย `docker compose -p vapp-lab7 down` ก่อนลบเครื่อง

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบในเครื่องเดียว ราคารวม ≤ `max_price` พอร์ต 8000 เข้าจากภายนอกได้ และ torch เห็น GPU ครบ
- [ ] ทดสอบ key: มี key ได้ผลอ่าน / 202 · ไม่มี key ได้ 401 ทั้ง `sync_api.py` และ `gateway.py` · ผลอ่าน 1 งานได้ใบเสร็จครบ 4/4 ใบ
- [ ] ทุกชุดไล่ระดับมี `level_N*.json` ครบ และ CPU ของตัวยิงไม่เต็ม (อ้างอิง < 2%: ตัวยิงไม่ใช่คอขวด)
  - อ้างอิง (RTX 3090 · 1 งาน = 4 ใบ ≈ 10–12 วินาทีบน GPU · GPU util ~45% เพราะสร้างทีละ token): Baseline **2 คน** (6 งาน/นาที · N = 4 ล้ม 100%) · คิว 1 Worker **2 คน** (6 งาน/นาที · N = 4 ล้ม 0% แต่ p95 36.7 วิ) · คิว 2 Worker **4 คน** (11 งาน/นาที · p95 13.9 วิ · 2.0 เท่า Efficiency 100%) · ประมาณการ 3 ใบ ~6 คน (คำนวณ ไม่ใช่ผลวัด)
- [ ] ความจุของ `queue2` มากกว่า `queue1` ชัดเจน และ GPU util ของทั้งสองใบไม่เป็น 0
- [ ] งานถล่ม (ถ้าวัด): คิวสำเร็จครบทุกงาน Baseline สำเร็จน้อยและ server อ่านงานที่ผู้ใช้เลิกรอ · อ้างอิง: Baseline 2/60 (อ่านทิ้ง 58 งาน) · คิว 1 Worker 60/60 ระบายหมดใน 651 วิ · 2 Worker 60/60 ใน 319 วิ · คิวยาวสุด 58 · ส่งซ้ำ 0 · dead-letter 0
- [ ] `kill` (ถ้าวัด): `lost` = 0 · `succeeded` = `sent` · `redelivered_jobs` ≥ 1 (งานในมือ Worker ที่ถูกฆ่า) · `dead_letter_queue` = 0 · อ้างอิง: 60/60 ส่งซ้ำ 1 งาน GPU0 ทำ 58 GPU1 ทำ 2
- [ ] `out_dir` มี `metrics.json` + กราฟตามชุดที่วัด (ครบ 4 ชุด = 5 รูป: `latency_vs_users` `throughput_vs_users` `scaling_vs_gpus` `burst_queue_length` `worker_kill_cumulative`) ไม่มีค่า key ในไฟล์ใด และไม่ได้เขียนทับผลเดิมที่ผู้ใช้ไม่ได้สั่งให้ทับ
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`) และไม่มี container เว็บ `vapp-lab7` ค้าง (ถ้าเปิดไว้)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · ทุกชุดใช้เครื่องเดียวกัน ไม่เช่าเครื่อง 1 GPU แยก
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. server Worker RabbitMQ และตัวยิงรันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องวัดซ้ำ
6. งานถล่มบน 1 GPU กินเวลาราว 10 นาทีต่อครั้ง ถ้าผู้ใช้ต้องการประหยัดให้เสนอ `burst_jobs` น้อยลง (เช่น 30) แต่ห้ามลดเองโดยไม่บอก
7. งบอ้างอิงรอบเต็ม (2 × RTX 3090 ที่แคนาดา ทุกชุด + เว็บ): เครื่องเปิด 1 ชม. 59 นาที ที่ $0.394/ชม. ยอดจริง $0.781 (GPU $0.741 · disk $0.040 · รับส่งข้อมูล 4.4 GB $0.000) · ถ้าเครื่องเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU) · ทุกชุดไล่ระดับ ทุกระดับ N (งาน/นาที · p50 · p95 · % ล้ม · GPU util · CPU ตัวยิง · ผ่าน SLO ไหม) · ตารางความจุ (จำนวน GPU · สถาปัตยกรรม · ความจุ N · Throughput สูงสุด · p95 ที่ N นั้น · เท่าของ 1 ใบ · Efficiency) · งานถล่ม (สำเร็จ · p95 · คิวยาวสุด · ระบายหมดในกี่วินาที) และ kill test (ถ้าวัด) · รายชื่อกราฟ · เวลาแต่ละขั้นและเวลารวม · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วเขียนประโยค "GPU 1 ใบ แบบไม่มีคิว รองรับ N คน · คิว 1 ใบ N₁ คน → 2 ใบ N₂ คน (x เท่า, Efficiency y%)" ตามชุดที่วัด พร้อมค่าประมาณ 3 ใบ (บอกชัดว่าเป็นการคำนวณ) และเหตุผลจากตัวเลขที่วัดได้
