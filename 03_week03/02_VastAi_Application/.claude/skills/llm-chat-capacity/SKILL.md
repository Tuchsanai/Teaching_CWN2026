---
name: llm-chat-capacity
description: วัดว่าแชทบอท LLM แบบ streaming (โมเดล Qwen/Qwen3-4B-Instruct-2507 เปิดด้วย vLLM ชื่อ shop-bot หลัง NGINX พร้อม API key) บนเครื่อง GPU ที่เช่าจาก Vast.ai รองรับผู้ใช้พร้อมกันได้กี่คนภายใต้เกณฑ์ SLO (TTFT p95 ≤ 2 วินาที · 95% ของคำถามได้ ≥ 15 token/วินาที · error < 1%) ครบวงจรในคำสั่งเดียว — เช่าเครื่อง → ติดตั้ง vLLM + NGINX + โหลดโมเดล → ทดสอบแชท → ยิงโหลดแบบไล่ระดับ N ของ GPU 1 ใบแบบตอบทีละคำถาม / Continuous Batching / 2 GPU หลัง Load Balancer least_conn → (เลือกได้) เทียบ Round Robin กับ least_conn เมื่อคำตอบยาวไม่เท่ากัน → metrics.json และกราฟ → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล llm-chat-capacity", "วัดความจุแชทบอท", "แชทบอทรับผู้ใช้พร้อมกันได้กี่คน", "Continuous Batching ช่วยได้กี่เท่า", "เพิ่ม GPU หลัง Load Balancer แล้วรับได้กี่เท่า", "Round Robin เทียบ least_conn", "ทำ LAB 7 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / จำนวน GPU / ราคา / ระดับ N / เวลาต่อระดับ / ชุดการวัด / ป้ายเครื่อง / โฟลเดอร์ผลที่ต่างไปจากเดิม
---

# llm-chat-capacity (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 7 ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** คัดลอกทุกไฟล์ขึ้นไปไว้ **ระดับเดียวกัน** ที่ `/workspace/lab7/` ของเครื่องเช่า (สคริปต์อ้างพาธนี้ตรง ๆ · `precheck2.py` import `loadtest.py` จากโฟลเดอร์นี้) แล้ว `sed -i 's/\r$//' /workspace/lab7/*.sh /workspace/lab7/*.py` · สคริปต์ Python บนเครื่องเช่ารันด้วย `/opt/vllm-env/bin/python` ยกเว้นที่บอกไว้

| สคริปต์ | หน้าที่ |
|---|---|
| `install.sh` | `bash install.sh` ติดตั้ง apt `nginx build-essential python3-dev` (ปิด NGINX ของระบบ) + `uv venv /opt/vllm-env` Python 3.12 + `vllm` → `/workspace/lab7/install_time.txt` (จบด้วย `DONE` · ~4–5 นาที) |
| `cluster.sh` | `start [--gpus 1\|2] [--mode batch\|single] [--lb least_conn\|round_robin]` · `lb least_conn\|round_robin` (reload NGINX อย่างเดียว) · `status` · `stop` — vLLM ตัวละ 1 GPU พอร์ต 8001/8002 ชื่อโมเดล `shop-bot` บริบท 4096 · `batch` = Continuous Batching (`max-num-seqs` 256) · `single` = ทีละ 1 คำถาม · NGINX พอร์ต 8000 streaming + header `X-Served-By` · สุ่ม key ครั้งเดียวที่ `/workspace/lab7/secrets/api_key` (600 ไม่พิมพ์ค่า) · ทุกตัวรันด้วย `setsid nohup` · log ที่ `/workspace/lab7/logs/` · ปรับผ่านตัวแปรแวดล้อม `MODEL_PATH` `SERVED_NAME` `MAX_LEN` `GPU_MEM` |
| `test_chat.py` | ถาม 2 ข้อผ่าน NGINX พร้อม key (≤ 150 token) + เรียกแบบไม่มี key ต้องได้ 401 → พิมพ์ JSON (คำตอบ · vLLM ที่ตอบ · TTFT · token · token/วินาที) |
| `precheck.py` | ตรวจ GPU 0 ก่อนวัด: อุณหภูมิ/clock ตอนว่างและตอนตอบผู้ใช้ 1 คน 3 ข้อ (ผ่าน NGINX) → พิมพ์ข้อความ เก็บเป็น `precheck_<label>.txt` |
| `precheck2.py` | `precheck2.py <out.json>` ตรวจ GPU 2 ใบ ยิงตรงเข้า vLLM แต่ละพอร์ต: อุณหภูมิ · clock · ความเร็วผู้ใช้ 1 คน · `speed_diff_over_10pct` (ต้องเปิด `--gpus 2` อยู่) |
| `loadtest.py` | ตัวยิงโหลด (รันบนเครื่องเช่าข้าง NGINX): `--levels 1,2,3 --label <ชุด> --out results` · ปรับ `--duration` `--warmup` `--max-tokens` `--procs` `--vllm-ports 8001,8002` `--no-repeat` · คำถามยาวปน `--long-frac 0.2 --long-max-tokens 600` · ชุดคำขอตัวอย่าง `--samples 8` → `dataset_samples.json` · คำถามลูกค้าร้านขายของใช้ในบ้าน 40 ข้อ closed-loop ไม่มี think time · หยุดเองเมื่อไม่ผ่าน 2 ระดับติดกัน · ระดับก้ำกึ่ง (ห่างเส้น ≤ 5%) วัดซ้ำ 2 ครั้งใช้ค่ากลาง · ค่า SLO เป็นค่าคงที่บนสุดของไฟล์ → `loadtest_<label>.json` |
| `run_lbmix.sh` | ชุด `lbmix`: ยิง 448 คน 120 วินาที (warm-up 30) คำถามยาว 20% ครั้งแรก round robin แล้ว least_conn → `results/loadtest_mix_*.json` แล้วตั้งกลับเป็น least_conn · จบด้วยไฟล์ `results/lbmix_done.txt` |
| `report.py` | **รันบนเครื่องนี้นอก container** `python report.py --results <out_dir>` → `metrics.json` + กราฟ 4 รูป (`ttft_p95_vs_n` `speed_p5_vs_n` `throughput_vs_n` `capacity_vs_gpus`) และถ้ามี `loadtest_mix_*` เพิ่ม `lb_ttft_p95` `lb_running_per_gpu` · ใช้ได้แม้มีแค่ชุด 1 GPU (ไม่มีค่าประมาณ 3 ใบ) |

นิยาม: **ผู้ใช้พร้อมกัน N** = ผู้ใช้จำลอง N คน ถาม → รอคำตอบ streaming จนจบ → ถามข้อใหม่ทันที · **SLO** = TTFT p95 ≤ 2 วินาที · ความเร็วต่อผู้ใช้ p5 ≥ 15 token/วินาที · error < 1% · **ความจุ** = ระดับ N สูงสุดที่ผ่าน และทุกระดับที่ต่ำกว่าก็ผ่าน

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` / `num_gpus` | RTX 3090 / 2 | GPU ในเครื่องเดียว (VRAM ≥ 24 GB) · `num_gpus` = 1 → ตัดชุด `batch2` และ `lbmix` อัตโนมัติ |
| `max_price` | $0.60/ชม. (2 ใบ) · $0.30/ชม. (1 ใบ) | ราคารวมทั้งเครื่อง (รวม disk) สูงสุด |
| `label` | `vapp-lab7` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | `verified=true rentable=true direct_port_count>=1 reliability>=0.95 inet_down>=500 cpu_cores_effective>=16 cuda_max_good>=13.0 geolocation notin [CN]` ค้นพร้อม disk `disk_gb` เรียงตาม `dph_total` | ไดรเวอร์ต้องรองรับ CUDA 13 (vLLM รุ่นล่าสุด) · นอกจีนเพื่อโหลดจาก Hugging Face เร็ว · ถ้าเครื่อง 1 ใบหา CPU 16 cores ไม่ได้ ลดเหลือ 8 ได้ |
| `image` / `disk_gb` / `ports` | image PyTorch 2.8 + CUDA 12.8 / 60 / ไม่เปิดพอร์ตเพิ่ม | ตัวยิงรันบนเครื่องเดียวกับแชทบอท จึงไม่ต้องเปิดพอร์ต |
| `ready_timeout` / `max_idle_temp` | 10 นาที / 60°C | เกินเวลา หรือ GPU ใบใดร้อนเกินนี้ตอนว่าง → ลบแล้วเช่าเครื่องอื่น |
| `model` | `Qwen/Qwen3-4B-Instruct-2507` ลงที่ `/workspace/models/Qwen3-4B-Instruct-2507` | เปลี่ยนโมเดลต้องส่ง `MODEL_PATH` ให้ `cluster.sh` |
| `runs` | `single` `batch1` `batch2` `lbmix` | ชุดที่จะวัด (ดูตารางถัดไป) · ผู้ใช้สั่ง "ไม่ต้องวัด 2 GPU" → ตัด `batch2` `lbmix` |
| `levels_single` / `levels_batch1` / `levels_batch2` | 1,2,3,4,6,8 / 1,32,64,96,128,160,192,224,256 / 128,192,256,320,384,448,512 | ระดับ N ของแต่ละชุด |
| `duration` / `warmup` | 30 / 5 วินาที | เวลาต่อระดับ · ช่วงแรกที่ไม่นับ |
| `max_tokens` | 150 | เพดานความยาวคำตอบ |
| `lbmix_users` / `long_frac` / `long_max_tokens` | 448 / 0.2 / 600 | ชุด `lbmix` (ค่าเขียนไว้ใน `run_lbmix.sh` ถ้าเปลี่ยนให้สั่ง `loadtest.py` เองด้วยตัวเลือกเดียวกัน) |
| `samples` | ใช่ | เก็บชุดคำขอตัวอย่าง 8 ข้อ → `dataset_samples.json` |
| `out_dir` | `lab7_llm_chat/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ใหม่ เช่น `lab7_llm_chat/results/skill_v0_run`) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` / `ssh_key` | `multi-account` · `/workspace/vastapp_lab` / `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | ที่ทำงานของสกิล vastai และกุญแจ SSH |

ชุดที่วัด (`runs`) ตามลำดับ — ทุกชุดใช้เครื่องเดียวกัน · เปลี่ยนชุดด้วย `bash cluster.sh stop` แล้ว `start` ใหม่ · ก่อนยิงใส่ `ulimit -n 65536` · รันแบบ `cd /workspace/lab7 && setsid nohup /opt/vllm-env/bin/python loadtest.py <ตัวเลือก> --out results > results/loadtest_<label>.log 2>&1 < /dev/null &` แล้วอ่าน log เป็นระยะจนมีบรรทัด `รองรับผู้ใช้พร้อมกันได้`

| ชุด | `cluster.sh start` | ก่อนวัด | ตัวเลือก `loadtest.py` | ไฟล์ผล | เวลาอ้างอิง |
|---|---|---|---|---|---|
| `single` | `--gpus 1 --mode single` | — | `--levels <levels_single> --label single_1gpu` | `loadtest_single_1gpu.json` | ~3 นาที |
| `batch1` | `--gpus 1 --mode batch` | `precheck.py > results/precheck_batch_1gpu.txt` | `--levels <levels_batch1> --label batch_1gpu` | `loadtest_batch_1gpu.json` | ~6 นาที |
| `batch2` | `--gpus 2 --mode batch --lb least_conn` | `precheck2.py results/precheck_batch_2gpu.json` | `--levels <levels_batch2> --vllm-ports 8001,8002 --label batch_2gpu` | `loadtest_batch_2gpu.json` | ~5 นาที |
| `lbmix` | ใช้ระบบของ `batch2` ต่อ | — | `setsid nohup bash run_lbmix.sh &` | `loadtest_mix_round_robin.json` `loadtest_mix_least_conn.json` | ~5 นาที |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `HF_TOKEN` · API key ของแชทบอท) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาเครื่องที่มี `gpu` × `num_gpus` ตาม `max_price` และ `offer_filter` เลือกถูกที่สุด เช่าด้วย `image` `disk_gb` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ แล้วดูอุณหภูมิแต่ละใบ
   - เกิน `ready_timeout` · GPU ไม่ครบ · ใบใดร้อนเกิน `max_idle_temp` → ลบทันทีแล้วเช่าเครื่องถัดไป · จด GPU · ราคาจริงต่อชั่วโมง · ที่ตั้ง · CPU cores · RAM · ราคาดาวน์โหลดต่อ GB · เวลาที่รอ
2. **ติดตั้ง**: `mkdir -p /workspace/lab7/results /workspace/models` คัดลอก `scripts/*` ขึ้นไปที่ `/workspace/lab7/` ตัด `\r` แล้วรัน `bash install.sh` แบบ `setsid nohup` (ต้องจบด้วย `DONE` ใน `install_time.txt` · จดเวอร์ชัน vLLM)
3. **โหลดโมเดล**: ส่ง `HF_TOKEN` จาก `.env` ของโฟลเดอร์บทผ่าน stdin ของ SSH (`read -r T; HF_TOKEN=$T /opt/vllm-env/bin/hf download <model> --local-dir /workspace/models/<ชื่อ>` · ไม่มีคำสั่ง `hf` ใช้ `huggingface-cli download` แทน) เข้าเป็นตัวแปรแวดล้อมของคำสั่งนั้นเท่านั้น ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ · จดเวลาดาวน์โหลด · เสร็จแล้วตรวจว่าไม่มี token ค้าง (`~/.cache/huggingface/token` · `grep -r` ค่า token ใน `/workspace` และ `/root`)
4. **ทดสอบแชท**: `bash cluster.sh start --gpus 1 --mode batch` (~2–3 นาที) → `test_chat.py` ต้องได้คำตอบ 2 ข้อและไม่มี key ได้ 401 · ถ้า `samples` รัน `loadtest.py --samples 8 --out results` · ปิดการเชื่อมต่อ SSH แล้วต่อใหม่ `cluster.sh status` ต้องยังพร้อม
5. **ยิงโหลดทีละชุดตาม `runs`** ตามตารางด้านบน รายงานความคืบหน้าทุก 2–3 นาทีจาก log · ระหว่างชุดดู `cluster.sh status`
   - ผลแปลก เช่น CPU ของตัวยิงเต็ม · error > 0 · 2 GPU ได้ไม่ถึง 1.5 เท่าของ 1 GPU · GPU ใบหนึ่ง util 0 → ดู `logs/vllm-*.log` `logs/nginx_error.log` ก่อนวัดซ้ำ · การวัดซ้ำเพื่อวินิจฉัยใช้ label `diag_*` แล้วย้ายออกจาก `results/` ก่อนรวมผล เพื่อไม่ให้ `report.py` นับรวม
6. **รวมผล**: ดึง `/workspace/lab7/results/*` (json · log · txt) + `install_time.txt` มาไว้ที่ `out_dir` (ไม่ดึง `secrets/` `run/`) แล้วรัน `python lab7_llm_chat/skill_v0/scripts/report.py --results <out_dir>` **บนเครื่องนี้** (ต้องมี matplotlib) · เปิดดูกราฟทุกรูปอย่างน้อย 1 ครั้ง · `grep` ค่า key ใน `out_dir` ต้องไม่พบ
7. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices): อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบ ราคารวม ≤ `max_price` ไดรเวอร์รองรับ CUDA ≥ 13 และ GPU ทุกใบตอนว่าง ≤ `max_idle_temp`
- [ ] `install_time.txt` จบด้วย `DONE` · `test_chat.py` ได้คำตอบ 2 ข้อ และไม่มี key ได้ HTTP 401 · ไม่มี `HF_TOKEN` ค้างบนเครื่องเช่า
- [ ] ทุกชุดที่วัดมี `loadtest_<label>.json` ที่มี `supported_users` · error 0% · CPU ของตัวยิงไม่เต็ม (ตัวยิงไม่ใช่คอขวด) · GPU ไม่ลด clock เพราะร้อน
  - อ้างอิง (RTX 3090 · vLLM 0.34.0): ทีละคำถาม **2 คน** (ไม่ผ่านที่ TTFT เพราะคิวรอ · ~82 token/วินาทีรวม) · Continuous Batching 1 ใบ **192 คน** (96 เท่า · ~3,100 token/วินาที · ไม่ผ่านที่ความเร็ว p5 ที่ 224) · 2 ใบ least_conn **384 คน** (2.00 เท่า · Efficiency 100% · ~6,160 token/วินาที) · ความเร็วผู้ใช้ 1 คน ~84 token/วินาที
- [ ] `batch2`: `precheck2` 2 ใบเร็วต่างกันไม่เกิน 10% (ถ้าเกินให้บอกในสรุป) · least_conn แบ่งคำถามให้ 2 vLLM ต่างกันไม่เกิน ~5%
- [ ] `lbmix` (ถ้าวัด): least_conn TTFT p95 ต่ำกว่า Round Robin · อ้างอิง: Round Robin 1.55 วินาที (GPU 1 ชนเพดาน 256) เทียบ least_conn 0.36 วินาที (ทั้ง 2 ใบ ~220) · ทั้ง 2 วิธีไม่ผ่าน SLO ความเร็วที่ 448 คนเมื่อมีคำตอบยาว
- [ ] `out_dir` มี `metrics.json` + กราฟ 4 รูป (+ 2 รูปถ้ามี `lbmix`) และไม่มีค่า key ในไฟล์ใดเลย · ผลเดิมใน `lab7_llm_chat/results` ไม่ถูกเขียนทับ (ถ้าใช้ `out_dir` อื่น)
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · ทุกชุดใช้เครื่องเดียวกัน
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. vLLM NGINX และตัวยิงรันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องวัดซ้ำ ให้ต่อ SSH ใหม่แล้วอ่าน log ต่อ
6. ค่ารับส่งข้อมูลอาจแพงกว่าค่า GPU (ติดตั้ง vLLM + โมเดล ~11.5 GB) ตอนเลือกเครื่องให้ดูราคาดาวน์โหลดต่อ GB ด้วย ถ้าเกิน $0.02/GB ให้บอกในสรุป
7. งบอ้างอิงรอบเต็ม (2 × RTX 3090 ทุกชุด ที่ Missouri US): เครื่องเปิด 48 นาที ที่ $0.369/ชม. ยอดจริง $0.597 (GPU $0.277 · disk $0.018 · ดาวน์โหลด 11.5 GB $0.299 · อัปโหลด $0.003) · ถ้าเครื่องเปิดเกิน 1.5 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU · อุณหภูมิ) · เวอร์ชัน vLLM · เวลาติดตั้ง / ดาวน์โหลดโมเดล / เปิด server · ผลทดสอบแชท · ทุกชุด ทุกระดับ N (TTFT p50/p95 · token/วินาทีต่อผู้ใช้ p50/p5 · token/วินาทีรวม · คำถามที่รอคิว · error · ผ่าน SLO ไหม · ระดับที่วัดซ้ำ) · ตารางความจุ (จำนวน GPU · สถาปัตยกรรม · N · token/วินาทีรวม · TTFT p95 ที่ N นั้น · เท่าของ 1 ใบ · Efficiency) · `lbmix` (ถ้าวัด) · รายชื่อกราฟ · เวลาแต่ละขั้นและเวลารวม · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วเขียนประโยค "GPU 1 ใบ ทีละคำถาม N₀ คน · Continuous Batching N₁ คน (x เท่า) → 2 ใบ N₂ คน (y เท่า, Efficiency z%)" ตามชุดที่วัด พร้อมเหตุผลจากตัวเลขที่วัดได้ (เกณฑ์ไหนทำให้ไม่ผ่าน)
