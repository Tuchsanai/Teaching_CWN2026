---
name: llm-chat-capacity
description: วัดว่าแชทบอท LLM แบบ streaming (vLLM + NGINX, โมเดล Qwen3-4B-Instruct-2507 ชื่อ shop-bot) บนเครื่อง GPU ที่เช่าจาก Vast.ai รองรับผู้ใช้พร้อมกันได้กี่คนภายใต้เกณฑ์ SLO ครบวงจรในคำสั่งเดียว — เช่าเครื่อง → ติดตั้ง vLLM + NGINX + โหลดโมเดล → เปิดแชทบอทและทดสอบ key → ยิงโหลดแบบ closed-loop ไล่จำนวนผู้ใช้ N เทียบ ตอบทีละคำถาม / Continuous Batching 1 GPU / 2 GPU หลัง Load Balancer / Round Robin กับ least_conn เมื่อคำตอบยาวไม่เท่ากัน → metrics.json และกราฟ → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล llm-chat-capacity", "วัดความจุแชทบอท", "แชทบอทรับผู้ใช้พร้อมกันได้กี่คน", "load test vLLM", "Continuous Batching ช่วยได้กี่เท่า", "ทำ LAB 6 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / จำนวน GPU / ราคา / ระดับ N / ป้ายเครื่องที่ต่างไปจากเดิม
---

# llm-chat-capacity (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 6 ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** สคริปต์ที่รันบนเครื่องเช่าให้คัดลอกขึ้นไปที่ `/workspace/lab6/` ส่วน `report.py` ให้รันบนเครื่องนี้

| สคริปต์ | รันที่ | หน้าที่ |
|---|---|---|
| `install.sh` | เครื่องเช่า | ติดตั้ง NGINX + C compiler (apt) และ vLLM ใน venv `/opt/vllm-env` (Python 3.11 ผ่าน uv) จับเวลาไว้ที่ `/workspace/lab6/logs/install_time.txt` (ต้อง `mkdir -p /workspace/lab6/logs` ก่อน) |
| `cluster.sh` | เครื่องเช่า | `start --gpus 1\|2 --mode batch\|single --lb least_conn\|round_robin` · `lb <วิธี>` (สลับโดยไม่เปิด vLLM ใหม่) · `status` · `stop` — vLLM ตัวละ 1 GPU ที่พอร์ต 8001/8002 (`setsid nohup` ทำงานต่อแม้ SSH หลุด) · NGINX พอร์ต 8000 แบบ streaming ใส่ header `X-vLLM-Backend` · สุ่ม API key เองเก็บที่ `/workspace/lab6/secrets/api_key` (ไม่พิมพ์ค่า) · `single` = `--max-num-seqs 1` · `batch` = 256 · ค่าอื่นแก้ผ่านตัวแปรแวดล้อม (`MODEL_PATH` `SERVED_NAME` `MAX_LEN` `GPU_UTIL`) |
| `test_chat.py` | เครื่องเช่า | ถาม 2 ข้อพร้อมกันแบบ streaming (150 token) + เรียกแบบไม่มี key / key ผิดต้องได้ 401 → `/workspace/lab6/logs/test_result.json` |
| `loadtest.py` | เครื่องเช่า | ตัวยิงโหลด closed-loop: `--label <ชื่อ> --levels 1,2,...` `--duration` `--warmup` `--max-tokens` `--long-frac` `--long-max-tokens` · คำถามร้านของใช้ในบ้าน 40 ข้อ · แบ่งผู้ใช้หลาย process · เก็บ TTFT p50/p95/p99 · ความเร็วต่อผู้ใช้ p50/p5 · token/วินาทีรวม · error · GPU util/clock/อุณหภูมิ · running/waiting ของ vLLM แต่ละตัว · CPU% ตัวยิง · หยุดเองเมื่อไม่ผ่าน SLO 2 ระดับติดกัน → `/workspace/lab6/results/loadtest_<label>.json` (เขียนทับทุกระดับ เผื่อหลุดกลางทาง) และพิมพ์ตารางตอนจบ |
| `report.py` | เครื่องนี้ | `python report.py <out_dir>` อ่าน `loadtest_*.json` ทุกไฟล์ใน `out_dir` → `metrics.json` (ความจุทุกชุด + ตารางตามจำนวน GPU) · `ttft_p95_vs_n.png` `throughput_vs_n.png` `capacity_vs_gpus.png` · ถ้ามี `loadtest_lb_*.json` เพิ่ม `lb_compare` และ `lb_compare.png` (ต้องใช้ `matplotlib`) |

นิยาม: **ผู้ใช้พร้อมกัน N** = ผู้ใช้จำลอง N คน ถาม → รอ stream จนจบ → ถามใหม่ทันที (ไม่มี think time) · **SLO** = TTFT p95 ≤ 2 วินาที · ความเร็วต่อผู้ใช้ p5 ≥ 15 token/วินาที · error < 1% (ค่าคงที่ `SLO` บนสุดของ `loadtest.py`) · **ความจุ** = N มากที่สุดที่ผ่าน SLO

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` | RTX 3090 | รุ่น GPU (VRAM ≥ 16 GB ต่อใบ สำหรับโมเดล 4B + KV cache) |
| `num_gpus` | 2 | GPU ในเครื่อง **1 หรือ 2** · 1 = วัดแค่ `single_1gpu` กับ `batch_1gpu` (ข้ามชุด 2 GPU และ LB) |
| `max_price` | $0.60/ชม. (2 ใบ) · $0.30/ชม. (1 ใบ) | ราคารวมทั้งเครื่องสูงสุด (GPU + disk) |
| `label` | `vapp-lab6` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | verified · ต่อ SSH ได้ตรง · เน็ตขาเข้า ≥ 500 Mbps · CPU ≥ 16 cores · ไดรเวอร์รองรับ CUDA ≥ 13 (vLLM รุ่นล่าสุดต้องใช้) · ไม่อยู่ในจีน · เลือกถูกสุด | เกณฑ์เลือกเครื่อง · ดูค่ารับส่งข้อมูลต่อ GB ด้วย (ต้องดาวน์โหลด ~11 GB) |
| `image` / `disk_gb` | `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel` / 60 | image และ disk · ไม่ต้องเปิดพอร์ตเพิ่ม (ตัวยิงรันบนเครื่องเดียวกับแชทบอท) |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `model` | `Qwen/Qwen3-4B-Instruct-2507` → `/workspace/models/Qwen3-4B-Instruct-2507` | โมเดล (ชื่อที่ผู้ใช้เรียก `shop-bot` · บริบท 4096) · เปลี่ยนโมเดล = ตั้ง `MODEL_PATH` ตอนเรียก `cluster.sh` |
| `runs` | ทั้ง 4 ชุดด้านล่าง (`num_gpus` = 1 → 2 ชุดแรก) | ชุดที่จะวัด |
| `levels_single` | 1,2,3,4,6,8 | ระดับ N ของ `single_1gpu` |
| `levels_batch_1gpu` | 1,32,64,128,192,256,384,512 | ระดับ N ของ `batch_1gpu` |
| `levels_batch_2gpu` | 128,256,384,512,640,768 | ระดับ N ของ `batch_2gpu` |
| `duration` / `warmup` | 30 / 5 วินาที | เวลาต่อระดับ / ช่วงแรกที่ไม่นับ |
| `max_tokens` | 150 | เพดานคำตอบ |
| `lb_users` / `lb_duration` / `lb_warmup` | 448 / 90 / 30 | ชุด LB: ผู้ใช้ระดับเดียว (~90% ของ 2×256) · วัด 90 วินาที ไม่นับ 30 วินาทีแรก (`--duration` = 120 คือรวม warm-up) |
| `long_frac` / `long_max_tokens` | 0.2 / 600 | ชุด LB: สัดส่วนคำถามที่ขอคำตอบยาว และเพดาน token ของคำถามกลุ่มนั้น |
| `out_dir` | `lab6_llm_chat/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `lab6_llm_chat/results/skill_v0_run`) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

ชุดที่วัด (`runs`) และคำสั่ง `loadtest.py` ของแต่ละชุด:

| label | เปิดแชทบอทด้วย | ยิงโหลด |
|---|---|---|
| `single_1gpu` | `cluster.sh start --gpus 1 --mode single` | `--label single_1gpu --levels <levels_single>` |
| `batch_1gpu` | `cluster.sh start --gpus 1 --mode batch` | `--label batch_1gpu --levels <levels_batch_1gpu> --procs 16` |
| `batch_2gpu` | `cluster.sh start --gpus 2 --mode batch --lb least_conn` | `--label batch_2gpu --levels <levels_batch_2gpu> --procs 16` |
| `lb_round_robin` · `lb_least_conn` | (vLLM 2 ตัวเดิม) `cluster.sh lb round_robin` แล้ว `cluster.sh lb least_conn` | `--label lb_<วิธี> --levels <lb_users> --duration 120 --warmup 30 --long-frac 0.2 --long-max-tokens 600` |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `HF_TOKEN` · API key ของแชทบอท) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาเครื่องที่มี `gpu` × `num_gpus` ในเครื่องเดียวตาม `max_price` และ `offer_filter` เช่าด้วย `image` `disk_gb` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ
   - เกิน `ready_timeout` หรือ GPU ไม่ครบ → ลบทันทีแล้วเช่าเครื่องถัดไป · จด GPU · ราคาจริงต่อชั่วโมง · ที่ตั้ง · CPU cores · RAM · CUDA สูงสุดของไดรเวอร์
2. **ติดตั้งและโหลดโมเดล**: `mkdir -p /workspace/lab6/logs` คัดลอก `scripts/{install.sh,cluster.sh,test_chat.py,loadtest.py}` ขึ้นไปที่ `/workspace/lab6/` (`chmod +x *.sh`) แล้ว `bash /workspace/lab6/install.sh` (~3 นาที)
   - ดาวน์โหลดโมเดลด้วย `/opt/vllm-env/bin/hf download <model> --local-dir /workspace/models/Qwen3-4B-Instruct-2507` (~1 นาที, 7.6 GB) โดยส่ง `HF_TOKEN` จาก `.env` ของโฟลเดอร์บทผ่าน stdin ของ SSH เข้าเป็นตัวแปรแวดล้อมของคำสั่งนั้นเท่านั้น ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ เสร็จแล้วตรวจว่าไม่มี token ค้าง (`~/.cache/huggingface/token` · `grep -r` ใน `/workspace` · env)
3. **เปิดและทดสอบ**: `cd /workspace/lab6 && ./cluster.sh start --gpus 1 --mode batch` (ครั้งแรก ~3 นาทีเพราะ compile · ครั้งถัดไป ~40 วินาที) แล้ว `/opt/vllm-env/bin/python test_chat.py` ต้องได้คำตอบ 2 ข้อ และ `no_key` / `wrong_key` ได้ 401 ทั้งคู่ → ดึง `test_result.json` มาไว้ที่ `out_dir`
4. **ยิงโหลดทีละชุดตาม `runs`**: ทุกชุดใช้เครื่องเดียวกัน ก่อนเปลี่ยนโหมดหรือจำนวน GPU ให้ `./cluster.sh stop` ก่อน `start` ใหม่ (สลับวิธี LB ใช้ `./cluster.sh lb` ไม่ต้อง stop)
   - รันตัวยิงแยกจาก SSH เสมอ: `cd /workspace/lab6 && setsid nohup /opt/vllm-env/bin/python loadtest.py <ตัวเลือกของชุด> > /workspace/lab6/results/loadtest_<label>.log 2>&1 &` รายงานความคืบหน้าทุก 2–3 นาทีจากบรรทัด `[loadtest] N=...` รอจนมีบรรทัด `สถานะ:`
   - เวลาอ้างอิง: `single_1gpu` ~2 นาที (หยุดที่ N=3) · `batch_1gpu` ~4 นาที · `batch_2gpu` ~3 นาที · LB ชุดละ ~5–7 นาที (รวมรอคำถามที่ค้างให้จบ)
   - ผลก้ำกึ่งเส้น SLO (ต่างไม่ถึง ~0.1) หรือผลแปลก เช่น 2 GPU ได้ไม่เกิน 1 GPU → ยิงซ้ำระดับนั้นพร้อมดู `nvidia-smi` (clock · อุณหภูมิ · throttle) เก็บไว้ในโฟลเดอร์ย่อย `out_dir/diag_<ชื่อ>/` (ตั้ง `--out-dir` แยก) เพื่อไม่ให้ `report.py` นับรวม
5. **ดึงผลและสรุป**: ดึง `/workspace/lab6/results/loadtest_*.json` และ `.log` มาไว้ที่ `out_dir` แล้วบนเครื่องนี้ `python <skill>/scripts/report.py <out_dir>` (ไม่มี matplotlib → สร้าง venv แยกแล้วติดตั้ง) เปิดดูกราฟทุกรูปอย่างน้อย 1 ครั้ง และ `grep` ว่าไม่มีค่า key ในไฟล์ผล
6. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices): อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบในเครื่องเดียว ราคารวม ≤ `max_price` และไดรเวอร์รองรับ CUDA ≥ 13
- [ ] `test_result.json`: ได้คำตอบ 2 ข้อ (TTFT < 1 วินาที) · ไม่มี key และ key ผิดได้ 401 · ไม่มี `HF_TOKEN` ค้างบนเครื่องเช่า
- [ ] ทุกชุดใน `runs` มี `loadtest_<label>.json` ทุกระดับ error = 0% และ CPU% ของตัวยิงไม่เต็ม (ตัวยิงไม่ใช่คอขวด)
- [ ] `single_1gpu`: มีคำถามกำลังทำทีละ 1 ข้อ ความจุเล็กมาก · `batch_1gpu`: ความจุมากกว่า `single_1gpu` หลายสิบเท่า และ waiting = 0 ที่ระดับที่ผ่าน
  - ค่าอ้างอิง (RTX 3090, Qwen3-4B, 150 token): ทีละคำถาม 1 คน (~76 token/วิ) · Continuous Batching 128 คน (2,984 token/วิ, TTFT p95 0.31 วิ, p5 21.5 token/วิ) · ตัวที่ทำให้ตกคือความเร็ว p5 ต่อผู้ใช้ ไม่ใช่ TTFT · สูงสุด ~3,240 token/วิ
- [ ] `batch_2gpu` (ถ้าวัด): `requests_per_backend` มีทั้ง vllm-1 และ vllm-2 · GPU ทั้ง 2 ใบ util ~100% · ถ้าความจุ < 2 เท่าของ 1 ใบ ต้องอธิบายด้วยตัวเลข (เช่น clock / อุณหภูมิ ใบหนึ่งต่ำกว่า)
  - ค่าอ้างอิง: 128 คน (5,519 token/วิ) แต่ N=256 ตกเพียง 0.04 token/วิ เพราะ GPU ใบที่ 2 ร้อนจน clock ต่ำกว่า · รอบวินิจฉัยผ่านที่ 256 (p5 17.0)
- [ ] ชุด LB (ถ้าวัด): least_conn TTFT p95 ต่ำกว่า Round Robin ชัดเจน และงานค้างสองใบใกล้กัน · อ้างอิง: RR 74.5 วิ (งาน 52/255 มีคิว ~138) · least_conn 0.60 วิ (222/222 ไม่มีคิว)
- [ ] `out_dir` มี `metrics.json` + กราฟ 3 รูป (+ `lb_compare.png` ถ้าวัดชุด LB) และไม่มีค่า key ในไฟล์ใดเลย
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · ทุกชุดใช้เครื่องเดียวกัน ไม่เช่าเครื่อง 1 GPU แยก
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. vLLM NGINX และตัวยิงรันแยกจาก SSH เสมอ การเชื่อมต่อหลุดต้องไม่ทำให้ต้องวัดซ้ำ ให้ต่อ SSH ใหม่แล้วอ่าน log ต่อ
6. งบอ้างอิงรอบเต็ม (2 × RTX 3090 ทั้ง 4 ชุด): เครื่องเปิดราว 1.5 ชม. ที่ ~$0.36/ชม. ยอดจริง $0.84 (GPU $0.48 · disk $0.06 · รับส่งข้อมูล 11.5 GB $0.30) · ถ้าเครื่องเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU · CUDA) · เวอร์ชัน vLLM และเวลาติดตั้ง / ดาวน์โหลดโมเดล / เปิด server · ทุกชุด ทุกระดับ N (TTFT p50/p95 · ความเร็วต่อผู้ใช้ p50/p5 · token/วินาทีรวม · กำลังทำ/รอคิว · GPU util · ผ่าน SLO ไหม) · ตารางตามจำนวน GPU (สถาปัตยกรรม · ความจุ N · token/วินาทีรวม · TTFT p95 ที่ N นั้น · เท่าของ 1 ใบ · Efficiency) · ชุด LB (ถ้ามี) · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วเขียนประโยค "GPU 1 ใบ แบบทีละคำถาม รองรับ N คน · ด้วย Continuous Batching รองรับ N คน (x เท่า)" และ (ถ้าวัด 2 GPU) "1 ใบ N₁ คน → 2 ใบ N₂ คน (x เท่า, efficiency y%)" พร้อมเหตุผลจากตัวเลขที่วัดได้
