---
name: gpu-queue-capacity
description: วัดว่าบริการสร้างภาพจากข้อความ (Text-to-Image, โมเดล stabilityai/sdxl-turbo 512x512 แบบ 4 steps) บนเครื่อง GPU ที่เช่าจาก Vast.ai รองรับผู้ใช้พร้อมกันได้กี่คนภายใต้เกณฑ์ SLO ครบวงจรในคำสั่งเดียว เทียบ API แบบ Synchronous (ผู้ใช้ถือสายรอ) กับระบบผสม (gateway + คิว RabbitMQ + GPU Worker) — เช่าเครื่อง 2 GPU → ติดตั้ง diffusers + RabbitMQ → จับเวลาสร้างภาพ → ยิงโหลดแบบไล่ระดับ N ของ Baseline / ระบบผสม 1 Worker / 2 Worker → burst 200 งาน (Priority queue, Backpressure 429) → ฆ่า Worker กลางงานเพื่อพิสูจน์ว่างานไม่หาย → metrics.json และกราฟ 6 รูป → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล gpu-queue-capacity", "วัดความจุบริการสร้างภาพ", "ระบบคิวรับผู้ใช้ได้กี่คน", "Synchronous เทียบคิว", "เพิ่ม GPU Worker แล้วรับได้กี่เท่า", "ทำ LAB 8 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / ราคา / ระดับ N / เวลาต่อระดับ / ชุดการวัด / ป้ายเครื่องที่ต่างไปจากเดิม
---

# gpu-queue-capacity (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 8 ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** คัดลอกทั้งโฟลเดอร์ขึ้นไปที่ `/workspace/lab8/code/` ของเครื่องเช่า (ตัด `\r` ท้ายบรรทัดหลังคัดลอก) ทุกสคริปต์รันบนเครื่องเช่าด้วย `/venv/main/bin/python` ยกเว้นที่บอกไว้

| สคริปต์ | หน้าที่ |
|---|---|
| `stack.sh` | ตัวช่วยเปิด/ปิดระบบ: `setup` (pip ลง `/venv/main` + apt `rabbitmq-server` แล้วเปิด RabbitMQ) · `rabbit` · `sync [PORT]` (ค่าเริ่มต้น 8001 ภายใน) · `gateway` (พอร์ต 8000 ที่เปิดสู่ภายนอก) · `worker <GPU>` · `stop sync\|gateway\|worker <GPU>\|all` · `status` — ทุกตัวรันด้วย `setsid nohup` สุ่ม API key ครั้งเดียวเก็บที่ `/workspace/lab8/api_key.txt` (สิทธิ์ 600 ไม่พิมพ์ค่า) · log อยู่ที่ `/workspace/lab8/*.log` |
| `prompts.txt` | คำบรรยายภาพภาษาอังกฤษ 12 ข้อ ที่ตัวยิงโหลดวนใช้ทุกชุด |
| `bench_gen.py` | `python bench_gen.py prompts.txt` จับเวลาสร้างภาพบน GPU 0 เมื่อส่งครั้งละ 1/2/4/8 ภาพ → `bench_single_gpu.json` (โหลดโมเดลครั้งแรก = ดาวน์โหลดลง cache) |
| `make_samples.py` | (รันใน `code/`) สร้างภาพจาก 6 ข้อแรกเป็นตาราง → `dataset_samples.jpg` และงานตัวอย่าง 1 งาน → `example_job.json` `example_job.png` |
| `sync_server.py` | API แบบ Synchronous: `POST /generate` → JPEG · `GET /health` · `GET /stats` · ทีละ 1 ภาพบน GPU 0 (เปิดผ่าน `stack.sh sync`) |
| `gateway.py` | ด่านหน้าระบบผสม: `POST /jobs` (normal/express → 202 + เลขงาน, 429 + Retry-After เมื่องาน normal รอ ≥ 100 × Worker) · `GET /jobs/{id}?wait=10` · `GET /jobs/{id}/image` · `GET /stats` · คิว durable + Priority + Dead-letter (เปิดผ่าน `stack.sh gateway`) |
| `worker.py` | Worker 1 ตัวต่อ GPU 1 ใบ: prefetch 4 รวมทำเป็น batch · ack หลังเก็บภาพแล้ว · heartbeat ทุก 1 วินาที · ข้อความว่าง → Dead-letter (เปิดผ่าน `stack.sh worker <GPU>`) |
| `test_worker.py` | (รันนอกเครื่องเช่าได้) `python test_worker.py <BASE_URL> <key_file> <job_id ที่ค้าง> <out_dir>` ทดสอบงานค้าง 1 งาน + ส่ง 8 งานพร้อมกัน → `test_worker.json` |
| `loadtest.py` | ตัวยิงโหลด (รันบนเครื่องเช่าข้าง API): แบบไล่ระดับ `[--mode sync\|hybrid] --url ... --out ...` · ปรับ `--levels 16,32,64` `--level-sec` `--warmup-sec` `--refine` · แบบ burst `--burst [--mode hybrid]` `--burst-jobs` `--burst-sec` `--express-pct` · เก็บ ภาพ/วินาที p50/p95/p99 งานล้ม GPU util CPU ของตัวยิง ภาพต่อ batch · หยุดที่ระดับแรกที่ไม่ผ่าน SLO แล้วลองกึ่งกลาง |
| `killtest.py` | ขณะมี Worker 2 ตัว: ส่ง 90 งานใน 3 วินาที (มีงานเสีย 1 งาน) · SIGKILL Worker gpu1 ที่วินาทีที่ 4 · จดสถานะทุก 0.5 วินาที · เปิด Worker กลับ → `killtest.json` |
| `report.py` | `python report.py --results /workspace/lab8 --out /workspace/lab8/report` → `metrics.json` + กราฟ (ป้ายภาษาอังกฤษ) · ต้องมีแค่ `loadtest.json` ไฟล์อื่นไม่มีก็ข้ามพร้อมกราฟที่ต้องใช้ไฟล์นั้น (กราฟ 3 ต้องมีทั้งระบบผสม 1 และ 2 Worker) |

นิยาม: **ผู้ใช้พร้อมกัน N** = ผู้ใช้จำลอง N คน วน ส่งข้อความ → รอจนได้ภาพ (เกิน 30 วินาที = งานล้ม) → ดูภาพ 2.5–7.5 วินาที (เฉลี่ย 5) → ส่งใหม่ · ระบบผสม: ส่งงาน → รอจนเสร็จ → โหลดภาพ จึงนับว่าได้ภาพ · ถูกตอบ 429 = งานล้ม · **SLO** = เวลารอจนได้ภาพ p95 ≤ 10 วินาที และงานล้ม < 1% (ค่าคงที่บนสุดของ `loadtest.py`) · **ความจุ** = N มากที่สุดที่ผ่าน SLO

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` / `num_gpus` | RTX 3090 / 2 | GPU ในเครื่องเดียว (VRAM ≥ 24 GB ต่อใบ เพราะ sync_server กับ Worker gpu0 อยู่ใบเดียวกัน) · `num_gpus` = 1 → ข้ามชุด `hybrid2` และ `kill` |
| `max_price` | $0.60/ชม. | ราคารวมทั้งเครื่องสูงสุด · หาไม่ได้จริงใช้ `fallback` |
| `fallback` | RTX 4090 × 2 ไม่เกิน $1.00/ชม. | ใช้เมื่อไม่มีเครื่องตาม `gpu` + `max_price` และต้องบอกเหตุผลในสรุป |
| `label` | `vapp-lab8` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | `verified=true rentable=true direct_port_count>=2 reliability>=0.95 cpu_cores_effective>=12 inet_down>=300 disk_space>=50 geolocation notin [CN]` เรียงตาม `dph_total` | เกณฑ์เลือกเครื่อง (นอกจีนเพื่อโหลดจาก Hugging Face ได้) |
| `image` / `disk_gb` / `ports` | `vastai/pytorch:@vastai-automatic-tag` / 50 / `--env "-p 8000:8000"` | image ที่มี Python พร้อมใน `/venv/main` · เปิดพอร์ต 8000 ให้ gateway · เช่าด้วย `--ssh --direct` |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `model` / `size` / `steps` | `stabilityai/sdxl-turbo` / 512 / 4 | ค่าคงที่บนสุดของ `bench_gen.py` `sync_server.py` `worker.py` ต้องตรงกันทุกไฟล์ |
| `runs` | `bench` `sync` `hybrid1` `burst` `hybrid2` `kill` | ชุดที่จะวัด (ดูตารางถัดไป) · ผู้ใช้สั่ง "ไม่ต้องยิง burst" → ตัด `burst` ฯลฯ |
| `levels` | 1,8,16,24,32,48,64,96,128,160,192,256,320 | ระดับ N ของทุกชุดไล่ระดับ (`--levels`) |
| `level_sec` / `warmup_sec` / `refine` | 30 / 10 / 2 | เวลาต่อระดับ · ช่วงแรกที่ไม่นับ (ต้องน้อยกว่า `level_sec` · ถ้า `level_sec` = 20 ใช้ 5) · จำนวนครั้งที่ลองกึ่งกลางหลังระดับแรกที่ไม่ผ่าน |
| `burst_jobs` / `burst_sec` / `express_pct` | 200 / 10 / 10 | ชุด burst |
| `cap_per_worker` | 100 | เพดานงาน normal ที่รอต่อ Worker 1 ตัว (`PER_WORKER_CAP` ใน `gateway.py`) |
| `samples` | ใช่ | สร้าง `dataset_samples.jpg` และ `example_job.*` |
| `out_dir` | `lab8_hybrid/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ใหม่ เช่น `lab8_hybrid/results_skill_v0`) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

ชุดที่วัด (`runs`) ตามลำดับ — ทุกชุดใช้เครื่องเดียวกัน · ก่อนยิงโหลดทุกครั้งใส่ `ulimit -n 65536` · รันแบบ `cd /workspace/lab8/code && setsid nohup /venv/main/bin/python loadtest.py <ตัวเลือก> --out /workspace/lab8/<ไฟล์>.json > /workspace/lab8/<ไฟล์>.log 2>&1 < /dev/null &` แล้วอ่าน log เป็นระยะ จนมีบรรทัด `MAX USERS MEETING SLO` (ไล่ระดับ) หรือ `-> ...json` (burst)

| ชุด | ระบบที่ต้องเปิดอยู่ | ตัวเลือก `loadtest.py` / คำสั่ง | ไฟล์ผล | เวลาอ้างอิง |
|---|---|---|---|---|
| `bench` | — | `bench_gen.py prompts.txt` (+ `make_samples.py` ถ้า `samples`) | `bench_single_gpu.json` | ~3 นาที (รวมดาวน์โหลดโมเดล) |
| `sync` | `stack.sh sync` | `--url http://127.0.0.1:8001 --levels <levels> --level-sec .. --warmup-sec ..` | `loadtest.json` | ~6 นาที |
| `hybrid1` | `stack.sh gateway` + `stack.sh worker 0` | `--mode hybrid --levels ...` | `loadtest_hybrid.json` | ~7 นาที |
| `burst` | sync + gateway + worker 0 | `--burst --url http://127.0.0.1:8001` แล้ว `stack.sh stop sync` แล้ว `--burst --mode hybrid` | `burst_sync.json` `burst_hybrid.json` | ~5 นาที |
| `hybrid2` | + `stack.sh worker 1` | `--mode hybrid --levels ...` | `loadtest_hybrid_2gpu.json` | ~8 นาที |
| `kill` | gateway + worker 0 + worker 1 | `killtest.py --out /workspace/lab8/killtest.json` (เปิด Worker gpu1 กลับเอง) | `killtest.json` | ~1 นาที |

ถ้าไม่วัด `hybrid1` แต่วัด `hybrid2` ให้เปิด `worker 0` และ `worker 1` ก่อนยิงชุด `hybrid2` · ถ้าไม่วัด `burst` ให้ `stack.sh stop sync` หลังชุด `sync` เพื่อคืน VRAM ของ GPU 0

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `HF_TOKEN` · API key ของบริการ) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาเครื่องที่มี `gpu` × `num_gpus` ในเครื่องเดียวตาม `max_price` และ `offer_filter` เช่าด้วย `image` `disk_gb` `ports` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ
   - เกิน `ready_timeout` หรือ GPU ไม่ครบ → ลบทันทีแล้วเช่าเครื่องถัดไป · ไม่มีเครื่องตามเกณฑ์ → ใช้ `fallback` · จด GPU · ราคาจริงต่อชั่วโมง · ที่ตั้ง · CPU cores · IP และพอร์ตภายนอกที่จับคู่กับ 8000
2. **ติดตั้ง**: `mkdir -p /workspace/lab8/code` คัดลอก `scripts/*` ขึ้นไปที่ `/workspace/lab8/code/` แล้ว `sed -i 's/\r$//' /workspace/lab8/code/*` แล้ว `bash /workspace/lab8/code/stack.sh setup` (~3–5 นาที ต้องจบด้วย `pip-rc=0` `apt-rc=0` `rabbitmq up`)
3. **`bench`**: รัน `bench_gen.py prompts.txt` ใน `/workspace/lab8/code` โดยส่ง `HF_TOKEN` จาก `.env` ของโฟลเดอร์บทผ่าน stdin ของ SSH (`read -r T; HF_TOKEN=$T ...`) เข้าเป็นตัวแปรแวดล้อมของคำสั่งนั้นเท่านั้น ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ — โมเดลจะอยู่ใน cache แล้ว สคริปต์ถัดไปไม่ต้องใช้ token · เสร็จแล้วตรวจว่าไม่มี token ค้าง (`~/.cache/huggingface/token` · `grep -r` ใน `/workspace`) · ถ้า `samples` รัน `make_samples.py` ต่อ · เจอ error เรื่อง brotli → `/venv/main/bin/pip install -U brotli` แล้วรันใหม่
4. **ทดสอบระบบ**: `stack.sh sync` แล้วบนเครื่องเช่า `curl` `POST :8001/generate` พร้อม key ต้องได้ JPEG และไม่มี key ต้องได้ 401 · เมื่อเปิด gateway แล้ว ทดสอบจาก container (นอกเครื่องเช่า) ที่ `http://<IP>:<พอร์ตภายนอกของ 8000>`: `POST /jobs` พร้อม key ต้องได้ 202 + เลขงาน แล้ว `GET /jobs/{id}?wait=10` จนได้ `done` และโหลดภาพได้ · ไม่มี key ต้องได้ 401 (อ่าน key จากไฟล์บนเครื่องเช่าผ่าน SSH ใส่ตัวแปร ห้ามพิมพ์)
5. **ยิงโหลดทีละชุดตาม `runs`** ตามตารางด้านบน รายงานความคืบหน้าทุก 2–3 นาทีจากบรรทัด JSON ของแต่ละระดับ · ระหว่างชุดดู `stack.sh status`
   - ผลแปลก เช่น 2 Worker ได้ไม่เกิน 1 Worker หรือ GPU util ใบที่ 2 เป็น 0 → ดู `/stats` ของ gateway (`live_workers` ต้องเท่าจำนวน Worker) และ `worker_gpu*.log` ก่อนวัดซ้ำ · การวัดซ้ำเพื่อวินิจฉัยให้ใช้ชื่อไฟล์ `diag_*.json` เพื่อไม่ให้ `report.py` นับรวม
6. **รวมผล**: บนเครื่องเช่า `/venv/main/bin/python /workspace/lab8/code/report.py --results /workspace/lab8 --out /workspace/lab8/report` แล้วดึง `/workspace/lab8/*.json` `*.log` (ยกเว้น `jobs.db` และไฟล์ key) `report/*` `code/bench_single_gpu.json` `code/dataset_samples.jpg` `code/example_job.*` มาไว้ที่ `out_dir` · เปิดดูกราฟทุกรูปอย่างน้อย 1 ครั้ง และ `grep` ค่า key ใน `out_dir` ต้องไม่พบ
7. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices): อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล

สกิลนี้ไม่เปิดเว็บ ถ้าผู้ใช้ขอเว็บ (PixelQueue ของ LAB 8 ที่ `lab8_hybrid/code/web`) ให้ทำก่อนขั้นที่ 7 โดยเขียน `lab8_hybrid/code/web/.env` 2 บรรทัด `T2I_BASE_URL` `T2I_API_KEY` แล้วเปิดด้วย `docker compose -p vapp-lab8 up -d --build` (พอร์ต 3408) และปิดด้วย `docker compose -p vapp-lab8 down` ก่อนลบเครื่อง

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบในเครื่องเดียว ราคารวม ≤ `max_price` (หรือ `fallback` พร้อมเหตุผล) และพอร์ต 8000 เข้าจากภายนอกได้
- [ ] `bench`: ส่งครั้งละหลายภาพได้ภาพต่อวินาทีมากกว่าครั้งละ 1 ภาพ · อ้างอิง RTX 3090: 1 ภาพ 0.464 วิ (2.15 ภาพ/วิ) · 8 ภาพ 0.255 วิ/ภาพ (3.91 ภาพ/วิ) · VRAM สูงสุด 15.3 GB
- [ ] ทดสอบ key: มี key ได้ภาพ / 202 · ไม่มี key ได้ 401 ทั้ง sync และ gateway · ไม่มี `HF_TOKEN` ค้างบนเครื่องเช่า
- [ ] ทุกชุดไล่ระดับมีไฟล์ JSON ครบ มี `max_users_meeting_slo` และ CPU ของตัวยิงไม่เต็ม (ตัวยิงไม่ใช่คอขวด)
  - อ้างอิง (RTX 3090): Baseline **30 คน** (สูงสุด 2.15 ภาพ/วิ · GPU util ~60% เพราะทำทีละภาพ) · ระบบผสม 1 Worker **52 คน** (3.8 ภาพ/วิ · 1.73 เท่า เพราะรวมทำเป็น batch) · 2 Worker **104 คน** (7.4 ภาพ/วิ · Efficiency 100%) · ประมาณการ 3 ใบ 156 คน (คำนวณ ไม่ใช่ผลวัด)
- [ ] `hybrid1`/`hybrid2`: `avg_images_per_batch` > 1 ที่ระดับ N สูง · `hybrid2` GPU util ทั้ง 2 ใบไม่เป็น 0 และความจุมากกว่า `hybrid1` ชัดเจน
- [ ] `burst` (ถ้าวัด): ระบบผสมงานสำเร็จมากกว่าและภาพเสียเปล่าน้อยกว่า Synchronous · express รอน้อยกว่า normal ชัดเจน · มีการตอบ 429 · อ้างอิง: sync สำเร็จ 71/200 เสียเปล่า 129 ภาพ · ระบบผสม 200/200 เสียเปล่า 0 ตอบ 429 621 ครั้ง · express p95 2.1 วิ เทียบ normal 43.4 วิ
- [ ] `kill` (ถ้าวัด): `good_jobs_lost` = 0 · `bad_jobs_dead_lettered` = 1 · `redelivered_jobs` > 0 · `workers_alive_after` = 2 · อ้างอิง: 89/89 เสร็จ ส่งซ้ำ 4 งาน
- [ ] `out_dir` มี `metrics.json` + กราฟตามชุดที่วัด (ครบ 6 ชุด = 6 รูป · เฉพาะ `sync` + `hybrid2` = 2 รูป) และไม่มีค่า key ในไฟล์ใดเลย
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`) และไม่มี container เว็บ `vapp-lab8` ค้าง (ถ้าเปิดไว้)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` (หรือเพดานของ `fallback`) และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · ทุกชุดใช้เครื่องเดียวกัน ไม่เช่าเครื่อง 1 GPU แยก
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. server Worker และตัวยิงรันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องวัดซ้ำ ให้ต่อ SSH ใหม่แล้วอ่าน log ต่อ
6. งบอ้างอิงรอบเต็ม (2 × RTX 3090 ทุกชุด + เว็บ ที่เกาหลี): เครื่องเปิด 1 ชม. 37 นาที ที่ $0.345/ชม. ยอดจริง $0.572 (GPU $0.511 · disk $0.041 · รับส่งข้อมูล 7.4 GB $0.020) · ถ้าเครื่องเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU) · เวลาติดตั้ง · เวลาสร้างภาพเมื่อส่งครั้งละ 1/2/4/8 ภาพ (ถ้าวัด `bench`) · ทุกชุดไล่ระดับ ทุกระดับ N (ภาพต่อวินาที · p50 · p95 · งานล้ม · GPU util · ภาพต่อ batch · ผ่าน SLO ไหม) · ตารางความจุ (จำนวน GPU · สถาปัตยกรรม · ความจุ N · ภาพต่อวินาทีสูงสุด · p95 ที่ N นั้น · เท่าของ Baseline · Efficiency) · burst และ kill test (ถ้าวัด) · รายชื่อกราฟ · เวลาแต่ละขั้นและเวลารวม · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วเขียนประโยค "GPU 1 ใบ แบบ Synchronous รองรับ N คน · ระบบผสม 1 ใบ N₁ คน → 2 ใบ N₂ คน (x เท่าของ Baseline, Efficiency y%)" ตามชุดที่วัด พร้อมเหตุผลจากตัวเลขที่วัดได้
