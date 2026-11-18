---
name: gpu-api-capacity
description: วัดว่า API ตรวจภาพ (FastAPI + โมเดล YOLO ตรวจอุปกรณ์ความปลอดภัย best.pt จาก LAB 1 · POST /v1/detect พร้อม API key หลัง NGINX Load Balancer) บนเครื่อง GPU ที่เช่าจาก Vast.ai รองรับผู้ใช้พร้อมกันได้กี่คนภายใต้เกณฑ์ SLO (p95 ≤ 500 ms · error < 1%) ครบวงจรในคำสั่งเดียว — เช่าเครื่อง 2 GPU → ติดตั้ง + เปิด server → ทดสอบจากนอกเครื่อง → ยิงโหลดแบบไล่ระดับ N ของ GPU 1 ใบแบบทีละคำขอ / Micro-batching / Micro-batching + 4 process / 2 GPU หลัง Load Balancer → (เลือกได้) round-robin เทียบ least_conn เมื่อ replica เท่ากันและมีตัวช้า · replica ล่มกลางการยิงโหลด (NGINX ส่งซ้ำหรือไม่) → metrics.json และกราฟ → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล gpu-api-capacity", "วัดความจุ API ตรวจภาพ", "API บน GPU 1 ใบรับผู้ใช้พร้อมกันได้กี่คน", "Micro-batching ช่วยได้กี่เท่า", "เพิ่ม GPU หลัง Load Balancer แล้วรับได้กี่เท่า", "round-robin เทียบ least_conn", "replica ล่มแล้วผู้ใช้เจอ error ไหม", "ทำ LAB 6 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / จำนวน GPU / ราคา / ป้ายเครื่อง / เกณฑ์ SLO / ระดับ N / เวลาต่อระดับ / ชุดการวัด / โฟลเดอร์ผลที่ต่างไปจากเดิม
---

# gpu-api-capacity (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 6 ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูพอร์ตที่เปิด ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร และห้ามแก้ไฟล์ของสกิล vastai

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** โครงบนเครื่องเช่าต้องเป็นแบบนี้ (สคริปต์อ้างพาธนี้ตรง ๆ):

```
/workspace/lab6/
├── code/        ← scripts/* ทุกไฟล์ (แล้ว sed -i 's/\r$//' /workspace/lab6/code/*)
├── best.pt      ← model
├── samples/     ← samples/*.jpg
├── results/     ← ผลของ loadgen.py
├── run/         ← pid · log · cluster.conf (cluster.sh สร้างเอง)
└── .env         ← API_KEY (cluster.sh สุ่มครั้งแรก สิทธิ์ 600 · ห้ามพิมพ์ค่า)
```

| สคริปต์ | หน้าที่ |
|---|---|
| `install.sh` | `bash code/install.sh` ติดตั้ง NGINX + `ultralytics fastapi uvicorn python-multipart opencv-python-headless psutil nvidia-ml-py matplotlib` → `install_time.txt` จบด้วย `DONE` (ไฟล์เดียวที่ไม่ได้มาจากรอบจริงโดยตรง รวบรวมจาก import ของโค้ด) |
| `server.py` | FastAPI: `POST /v1/detect` (ช่อง `file` · Bearer key ผิด/ไม่มี = 401) · `GET /health` · ตอบวัตถุ (class, confidence, box) · ชื่อ replica · `timing_ms` (decode/queue/inference) · `batch_size` · ตั้งด้วย env `MODE single\|microbatch` `MAX_BATCH` `MAX_WAIT_MS` (5) `IMGSZ` (640) `CONF` (0.35) `SLOW_MS` · อุ่นโมเดลทุกขนาด batch 1..`MAX_BATCH` ก่อน `/health` ตอบพร้อม · เรียกโมเดลจาก thread เดียวเสมอ (cuDNN สร้างแผนแยกต่อ thread ครั้งละ ~2.6 วินาที) |
| `run_single.sh` | เปิด server 1 process บน GPU 0 พอร์ต 0.0.0.0:8080 โหมดทีละคำขอ (ใช้ทดสอบก่อนมี NGINX) |
| `cluster.sh` | `up <replica 1-2> <process ต่อ replica> <batch สูงสุด> [--lb round_robin\|least_conn] [--slow <replica>:<ms>] [--retry on\|off]` · `kill <replica>` (kill -9) · `start <replica> [--wait]` · `status` · `down` — replica r ใช้ GPU r · process ฟัง 127.0.0.1:(9000 + r×100 + p) · NGINX 0.0.0.0:8080 · `up` รอจนทุก process พร้อม (เพดาน 300 วินาที) |
| `test_api.py` | **รันบนเครื่องนี้** `python test_api.py http://<IP>:<พอร์ตภายนอกของ 8080> <ไฟล์ key> <โฟลเดอร์รูป> <out_dir>` → `/health` · ส่งรูปทุกรูปพร้อม key · ไม่มี key / key ผิด ต้องได้ 401 → `test_single.json` |
| `make_grid.py` | **รันบนเครื่องนี้** `python make_grid.py <out_dir> <โฟลเดอร์รูป>` → `dataset_samples.jpg` (กรอบ + คลาสจาก `test_single.json` · ขนาดไฟล์/ภาพ) |
| `loadgen.py` | ตัวยิงโหลด closed-loop (รันบนเครื่องเช่า ยิงเข้า NGINX :8080 · 8 process) `--name <ชุด>` → `results/<ชุด>.json` · ปรับ `--levels 1,4,16,...` `--level-s 20` `--warmup 5` `--timeout 10` `--slo-p95 500` `--slo-err 0.01` `--bisect 3` · หยุดเมื่อไม่ผ่าน 2 ระดับติดกันแล้วซอยครึ่ง · วัดซ้ำระดับเดียว `--recheck N --times 3` → `<ชุด>_recheck<N>.json` · ยิงระดับเดียวรายวินาที `--users N --duration 45 --at "15:<คำสั่ง>" --track gpu1` · จบด้วยบรรทัด `ความจุ:` และ `DONE` |
| `run_lb_compare.sh` | ชุด `lb`: `lc2` (least_conn) · `rr_slow` · `lc_slow` (replica 1 ช้าลงรูปละ 40 ms) ทั้งหมด 2×4 process batch 32 → จบด้วย `ALL DONE` |
| `run_failover.sh` | ชุด `failover`: `bash code/run_failover.sh <N>` ยิง 45 วินาที kill replica 1 ที่วินาที 15 · start คืนที่ 30 · รอบ `fo_noretry` (`--retry off`) และ `fo_retry` (`--retry on`) → `ALL DONE` |
| `summ_lb.py` | `python code/summ_lb.py <ชุด...>` พิมพ์ทุกระดับ + สัดส่วนคำขอต่อ replica (ใช้ตรวจเร็วบนเครื่องเช่า) |
| `report.py` | **รันบนเครื่องนี้** `python report.py <out_dir>` → `metrics.json` + กราฟ `latency_p95_vs_users` `throughput_vs_users` (ทุกครั้ง) · `scaling_vs_gpus` (ต้องมี `gpu1`+`gpu2` + ค่าประมาณ 3 ใบ) · `lb_rr_vs_least_conn` (ต้องมีชุด `lb` + `gpu2`) · `failover_timeline` (ต้องมีชุด `failover`) · วัดไม่ครบทุกชุดก็รันได้ · อ่าน SLO จากไฟล์ผล · ถ้ามี `<ชุด>_recheck<N>.json` จะเก็บทั้ง `capacity_users_strict` และ `capacity_users` |

นิยาม: **ผู้ใช้พร้อมกัน N** = ผู้ใช้จำลอง N คน ส่งรูป → ได้คำตอบ → ส่งรูปถัดไปทันที (ไม่มี think time · รอเกิน `timeout` = error) · **SLO** = p95 ≤ `slo_p95_ms` และ error < `slo_error` · **ความจุ** = N สูงสุดที่ผ่าน โดยทุกระดับที่ต่ำกว่าก็ผ่าน

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` / `num_gpus` | RTX 3090 / 2 | GPU ในเครื่องเดียว · `num_gpus` = 1 → ตัดชุด `gpu2` `lb` `failover` อัตโนมัติ (`cluster.sh` รับ replica ได้ 1–2 เท่านั้น) |
| `max_price` | $0.60/ชม. (2 ใบ) · $0.30/ชม. (1 ใบ) | ราคารวมทั้งเครื่อง (รวม disk) สูงสุด |
| `label` | `vapp-lab6` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | `verified=true rentable=true direct_port_count>=1 reliability>=0.95 inet_down>=500 cpu_cores_effective>=24 geolocation notin [CN]` เรียงตาม `dph_total` เอาถูกสุด | ใช้ **`cpu_cores_effective`** ไม่ใช่จำนวน core ที่เครื่องมี: รอบจริงเครื่องโชว์ 192 core แต่ container ได้จริง ~27 core และ 2 GPU × 4 process ใช้ CPU ของ server ~12.4 core ที่ความจุ |
| `image` / `disk_gb` / `ports` | image PyTorch 2.8 + CUDA 12.8 / 40 / เปิดพอร์ต 8080 | พอร์ต 8080 ให้ทดสอบ API จากนอกเครื่อง (Vast แมปเป็นพอร์ตภายนอกอื่น ดูด้วยสกิล vastai) |
| `ready_timeout` | 10 นาที | เกินแล้วยังไม่พร้อม / GPU ไม่ครบ → ลบแล้วเช่าเครื่องถัดไป |
| `model` / `samples` | `lab6_image_api/best.pt` / `lab6_image_api/samples/*.jpg` (6 รูป 640×640) | โมเดล YOLO และรูปที่ใช้ยิง · เปลี่ยนรูปได้ แต่ความจุจะเทียบกับรอบอ้างอิงไม่ได้ |
| `slo_p95_ms` / `slo_error` | 500 / 0.01 | เกณฑ์ SLO → `--slo-p95` `--slo-err` ทุกครั้งที่เรียก `loadgen.py` |
| `levels` | 1,4,16,32,64,128,256,512,1024 | ระดับ N (`--levels`) · ซอยครึ่ง `bisect` = 3 รอบ |
| `level_s` / `warmup` / `timeout` | 20 / 5 / 10 วินาที | เวลาต่อระดับ · ช่วงแรกที่ไม่นับ · รอเกินนี้ = error |
| `max_batch` / `procs` | 32 / 4 | ขนาด batch สูงสุดของ Micro-batching · process ต่อ GPU ของชุด `gpu1` `gpu2` `lb` `failover` |
| `runs` | `base1` `batch1` `gpu1` `gpu2` `lb` `failover` | ชุดที่จะวัด (ตารางถัดไป) · ผู้ใช้สั่ง "ไม่ต้องทำการทดลองเสริม" → ตัด `lb` `failover` |
| `fo_users` / `fo_duration` | 1/3 ของความจุ `gpu2` (รอบอ้างอิงใช้ 11 คน) / 45 วินาที | ชุด `failover` · replica ที่เปิดคืนใช้ ~92 วินาทีกว่าจะพร้อม ถ้าอยากเห็นตอนกลับมารับงานต้องยิงนานกว่า ~130 วินาที (สั่ง `loadgen.py --users` เองด้วย `--duration`) |
| `samples_grid` | ใช่ | ทำ `dataset_samples.jpg` |
| `out_dir` | `lab6_image_api/results` | โฟลเดอร์ผลบนเครื่องนี้ · มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ใหม่ เช่น `lab6_image_api/results_skill` |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` / `ssh_key` | `multi-account` · `/workspace/vastapp_lab` / `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | ที่ทำงานของสกิล vastai และกุญแจ SSH |

ชุดที่วัด (`runs`) ตามลำดับ — ทุกชุดใช้เครื่องเดียวกัน · `cluster.sh up` ปิดของเดิมให้เอง · ทุกคำสั่งที่นานรันแยกจาก SSH: `cd /workspace/lab6 && setsid nohup <คำสั่ง> > results/<ชุด>.log 2>&1 < /dev/null &` แล้วอ่าน log เป็นระยะจนเห็น `DONE` (หรือ `ALL DONE`) · `<L>` = `--levels <levels> --level-s <level_s> --warmup <warmup> --timeout <timeout> --slo-p95 <slo_p95_ms> --slo-err <slo_error>`

| ชุด | `cluster.sh up` | คำสั่งวัด | ไฟล์ผล | เวลาอ้างอิง |
|---|---|---|---|---|
| `base1` | `1 1 1` | `python code/loadgen.py --name base1 <L>` | `base1.json` | ~4 นาที |
| `batch1` | `1 1 <max_batch>` | `... --name batch1 <L>` | `batch1.json` | ~4 นาที |
| `gpu1` | `1 <procs> <max_batch>` | `... --name gpu1 <L>` | `gpu1.json` | ~4 นาที |
| `gpu2` | `2 <procs> <max_batch>` | `... --name gpu2 <L>` | `gpu2.json` | ~4 นาที |
| `lb` | (สคริปต์ up เอง) | `bash code/run_lb_compare.sh` (ใช้ค่า `levels`/SLO เริ่มต้น ถ้าเปลี่ยนให้สั่ง `up` + `loadgen.py` เองทีละชุดด้วยตัวเลือกเดียวกับในสคริปต์) | `lc2` `rr_slow` `lc_slow` `.json` | ~13 นาที |
| `failover` | (สคริปต์ up เอง) | `bash code/run_failover.sh <fo_users>` | `fo_noretry.json` `fo_retry.json` | ~6 นาที |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · **ห้ามแสดงค่า key ใด ๆ** (Vast · API key ของ server) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหา `gpu` × `num_gpus` ตาม `max_price` และ `offer_filter` เลือกถูกที่สุด เช่าด้วย `image` `disk_gb` เปิด `ports` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ · ดู CPU ที่ container ได้จริง (`cat /sys/fs/cgroup/cpu.max` หาร 100000) · จด GPU · ราคาจริงต่อชั่วโมง · ที่ตั้ง · CPU ที่ได้จริง · เวลาที่รอ
2. **ติดตั้ง + ทดสอบ**: สร้างโครง `/workspace/lab6/` ตามด้านบน คัดลอก `scripts/*` `model` `samples` ขึ้นเครื่อง ตัด `\r` · `setsid nohup bash code/install.sh` จนเห็น `DONE` · `bash code/cluster.sh up 1 1 1` (สร้าง key + เปิด NGINX) · ดึง key มาไว้ในไฟล์ชั่วคราว **นอก repo** (สิทธิ์ 600) แล้วรัน `test_api.py` กับ IP + พอร์ตภายนอกของ 8080 ต้องได้ 200 ทุกรูป และ 401 ทั้งไม่มี key / key ผิด · ถ้า `samples_grid` รัน `make_grid.py` · ลบไฟล์ key ชั่วคราวทันทีหลังทดสอบ
3. **ยิงโหลดทีละชุดตาม `runs`** ตามตารางด้านบน รายงานความคืบหน้าทุก 2–3 นาทีจาก log · ก่อนแต่ละชุดดู `cluster.sh status` ว่าตั้งค่าถูก
   - ระดับใดไม่ผ่านครั้งเดียวแต่ระดับที่สูงกว่าผ่าน (อาการชั่วคราว) → `python code/loadgen.py --name <ชุด> --recheck <N> --times 3 <L>` แล้วรายงานทั้งความจุแบบเข้ม (`capacity_users_strict`) และแบบนับรอบวัดซ้ำ (`capacity_users`) · รอบอ้างอิง `gpu2` ที่ N=64 p95 พุ่ง 1,752 ms ครั้งเดียว วัดซ้ำ 3 รอบผ่านหมด (~147 ms)
   - ผลแปลก เช่น error > 0 ในชุดปกติ · CPU ของตัวยิงโหลดเกิน ~1 core · GPU ใบหนึ่ง util 0 · 2 ใบได้ไม่ถึง 1.5 เท่าของ `gpu1` → ดู `run/server_*.log` และ `/var/log/nginx/error.log` ก่อนวัดซ้ำ · การวัดเพื่อวินิจฉัยใช้ชื่อ `diag_*` แล้วไม่ดึงกลับมาใน `out_dir`
4. **รวมผล**: ดึง `/workspace/lab6/results/*` (json · log) + `install_time.txt` + `run/cluster.conf` มาไว้ที่ `out_dir` (ไม่ดึง `.env`) แล้วรัน `python <โฟลเดอร์สกิล>/scripts/report.py <out_dir>` **บนเครื่องนี้** (ต้องมี matplotlib) · เปิดดูกราฟทุกรูปอย่างน้อย 1 ครั้ง · `grep` ค่า key ใน `out_dir` ต้องไม่พบ
5. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` ตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices): อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบ ราคารวม ≤ `max_price` และ CPU ที่ container ได้จริง ≥ 24 core
- [ ] `install_time.txt` จบด้วย `DONE` · `test_single.json`: `/health` 200 · ทุกรูป 200 พร้อมวัตถุที่ตรวจได้ · ไม่มี key และ key ผิด ได้ 401
- [ ] ทุกชุดที่วัดมี `<ชุด>.json` ที่มี `capacity_users` และ log จบด้วย `DONE` · error 0% ที่ระดับที่ผ่าน · CPU ของตัวยิงโหลดและ NGINX ต่ำกว่า 1 core (ไม่ใช่คอขวด) · ชุด 2 GPU คำขอกระจาย 2 replica ต่างกันไม่เกิน ~5% (round-robin)
  - อ้างอิง (2 × RTX 3090 · SLO p95 ≤ 500 ms): `base1` **22 คน** 63 req/s (GPU ~20% · คอขวดคือเรียกโมเดลทีละรูป) · `batch1` **52 คน** 157 req/s (2.4 เท่า) · `gpu1` **104 คน** 325 req/s (4.7 เท่า) · `gpu2` **176 คน** 651 req/s (1.69 เท่าของ `gpu1` · Efficiency 85% · Throughput 2.00 เท่า · ความจุแบบเข้ม 32 เพราะ spike ที่ N=64)
- [ ] `lb` (ถ้าวัด): replica เท่ากัน least_conn ≥ round-robin (อ้างอิง 256 vs 176) · replica ช้า 40 ms: least_conn > round-robin ชัดเจน (อ้างอิง 72 vs 32 · least_conn ย้ายงาน ~79% ไป GPU0)
- [ ] `failover` (ถ้าวัด): `fo_noretry` มี error (อ้างอิง 5,474 / 14,822 = 36.9% · 502/503) · `fo_retry` error 0 (อ้างอิง 0 / 9,601) · เปิด replica คืนใช้ ~92 วินาทีจนพร้อม
- [ ] `out_dir` มี `metrics.json` + กราฟตามชุดที่วัด และไม่มีค่า key ในไฟล์ใดเลย · ผลเดิมใน `lab6_image_api/results` ไม่ถูกเขียนทับ (ถ้าใช้ `out_dir` อื่น)
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · ทุกชุดใช้เครื่องเดียวกัน
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี (บัญชีอาจมีเครื่องของ LAB อื่นเปิดอยู่)
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. server NGINX และตัวยิงรันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องวัดซ้ำ ให้ต่อ SSH ใหม่แล้วอ่าน log ต่อ · ระหว่างรอไม่ต้องเปิดเครื่องทิ้งไว้เปล่า ๆ เมื่อวัดครบแล้วให้ไปขั้นรวมผลทันที
6. งบอ้างอิงรอบเต็ม (2 × RTX 3090 ทุกชุด ที่ California US): เครื่องเปิด 2 ชม. 40 นาที ที่ $0.395/ชม. (GPU $0.347 + disk $0.048) ยอดจริง **$1.011** (GPU $0.879 · disk $0.128 · ดาวน์โหลด $0.004) · รอบย่อ 2 ชุดน่าจะไม่เกิน ~45 นาที · ถ้าเครื่องเปิดเกิน 3 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU ที่ได้จริง) · เวลาติดตั้ง · ผลทดสอบ API (เวลาที่โมเดลใช้ต่อรูป · 401) · ทุกชุด ทุกระดับ N (Throughput · p50/p95/p99 · error · GPU util · CPU ของ server/NGINX/ตัวยิง · batch เฉลี่ย · ผ่าน SLO ไหม · ระดับที่วัดซ้ำ) · ตารางความจุ (จำนวน GPU · สถาปัตยกรรม · N · Throughput สูงสุด · p95 ที่ N นั้น · เท่าของ 1 ใบ · Efficiency) · `lb` และ `failover` (ถ้าวัด) · รายชื่อกราฟ · เวลาแต่ละขั้นและเวลารวม · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วเขียนประโยค "GPU 1 ใบ ทีละคำขอ N₀ คน · Micro-batching N₁ คน · + 4 process N₂ คน → 2 ใบ N₃ คน (x เท่า, efficiency y%)" ตามชุดที่วัด พร้อมคอขวดของแต่ละแบบจากตัวเลขที่วัดได้ · ถ้าวัดทั้ง `gpu1` และ `gpu2` ให้ประมาณ 3 ใบจาก `metrics.json` และบอกชัดว่าเป็นการคำนวณ ไม่ใช่ผลวัด · ถ้าไม่ได้วัด `gpu1` ให้เทียบ 2 ใบกับ `base1` และบอกว่าตัวเลขนี้รวมผลของสถาปัตยกรรมกับผลของ GPU ใบที่ 2 ไว้ด้วยกัน
