---
name: multigpu-speedup
description: ทดสอบว่าเพิ่ม GPU จาก 1 เป็น 2 ใบในเครื่องเดียวแล้วเทรนเร็วขึ้นกี่เท่าและคุ้มเงินไหม บนเครื่องที่เช่าจาก Vast.ai ครบวงจรในคำสั่งเดียว — เช่าเครื่อง 2 GPU → เตรียม Dataset hard-hat-workers → เทรน YOLO11m ด้วย 1 GPU แล้ว 2 GPU (ค่าเดิมทุกอย่าง) → วัดวินาทีต่อ Epoch / step · GPU util · CPU ที่ใช้ · เวลา all-reduce → ค้นราคาตลาด คิด speedup · efficiency · เงินต่อ Epoch พร้อมกราฟ 4 รูป → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล multigpu-speedup", "เทียบความเร็ว 1 กับ 2 GPU", "ทดสอบความเร็วหลาย GPU", "ทำ LAB 2 ซ้ำ", "multi-GPU / DDP คุ้มไหม" หรือขอทำซ้ำด้วยรุ่น GPU / ราคา / จำนวน Epoch / ป้ายเครื่องที่ต่างไปจากเดิม
---

# multigpu-speedup (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 2 ทั้งหมดในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง ค้นราคา เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** สคริปต์ที่รันบนเครื่องเช่าให้คัดลอกขึ้นไปที่ `/workspace/lab2/code/` ส่วน `report.py` ให้รันบนเครื่องนี้

| สคริปต์ | รันที่ | หน้าที่ |
|---|---|---|
| `download_dataset.py` | เครื่องเช่า | โหลด hard-hat-workers รุ่น 13 (joseph-nelson, รูปแบบ YOLO) ลง `/workspace/hardhat` · อ่าน `ROBOFLOW_API_KEY` จาก stdin ไม่เขียนลงดิสก์ |
| `dataset_stats.py` | เครื่องเช่า | นับภาพ / label / กรอบของแต่ละคลาสใน train · valid · test และขนาด Dataset (พิมพ์ JSON) |
| `show_samples.py` | เครื่องเช่า | ภาพตัวอย่าง 8 รูปจาก Training Set เรียง 4×2 วาดกรอบและชื่อคลาสจาก label จริง |
| `bench.py` | เครื่องเช่า | `--gpus 1|2` เทรน yolo11m ค่าเดิมทุกรอบ (ภาพ 640 · batch 32 ต่อ GPU · seed 0 · ไม่ validate ระหว่างเทรน) ตรวจว่า GPU ว่างก่อนเริ่ม · 2 GPU วัด all-reduce 80 MB เพิ่ม · เขียน `bench_<N>gpu[_tag].json` และข้อมูลดิบ (`results.csv` `gpu_util.csv` `cpu.csv` `data.yaml`) |
| `report.py` | เครื่องนี้ | `--results <out_dir>` อ่าน `raw/bench/bench_1gpu.json` `bench_2gpu.json` และ `raw/prices.json` คำนวณ ideal · speedup · efficiency · เงินต่อ Epoch → `metrics.json` และกราฟ 4 รูปใน `images/` (ต้องใช้ `matplotlib`) |

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` | RTX 3090 | รุ่น GPU (ทุกใบในเครื่องเป็นรุ่นเดียวกัน · VRAM ≥ 24 GB ถ้าใช้ batch 32) |
| `num_gpus` | 2 | จำนวน GPU ในเครื่อง **ไม่เกิน 2 ใบ** · 2 = เทรน 1 GPU แล้ว 2 GPU บนเครื่องเดียวกันแล้วเทียบ · 1 = วัดเส้นฐาน 1 GPU อย่างเดียว ไม่มี speedup และข้าม `report.py` |
| `max_price` | $0.60/ชม. | ราคารวมของทั้งเครื่องสูงสุด (GPU + disk) |
| `epochs` | 5 | Epoch ต่อรอบ → `bench.py --epochs` **ต้อง ≥ 3** (ค่าเฉลี่ยไม่นับ Epoch แรกกับ Epoch สุดท้าย) |
| `label` | `vapp-lab2` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `offer_filter` | verified · ต่อ SSH ได้ตรง (direct port) · เน็ตเร็ว · CPU ≥ 16 cores · ไม่อยู่ในจีน · เลือกถูกสุด | เกณฑ์เลือกเครื่อง |
| `image` | PyTorch 2.8 + CUDA 12.8 (เช่น `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel`) | image ของเครื่อง |
| `disk_gb` | 60 | ขนาด disk |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `model` / `imgsz` / `batch_per_gpu` / `seed` | `yolo11m.pt` / 640 / 32 / 0 | ค่าการเทรน → `--model` `--imgsz` `--batch-per-gpu` `--seed` (ต้องเท่ากันทั้ง 2 รอบ) |
| `out_dir` | `lab2_multigpu/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `lab2_multigpu/results/skill_v0_run`) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `ROBOFLOW_API_KEY`) ในคำตอบหรือไฟล์ผล

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาเครื่องที่มี `gpu` × `num_gpus` **ในเครื่องเดียว** ตาม `max_price` และ `offer_filter` แล้วเช่าด้วย `image` และ `disk_gb` ตั้งป้าย `label` รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU ครบ
   - เกิน `ready_timeout` หรือเห็น GPU ไม่ครบ → ลบทันทีแล้วเช่าเครื่องถัดไป · เครื่องที่ถูกที่สุดอาจถูกคนอื่นเช่าไปแล้ว → ข้ามไปเครื่องถัดไป
   - จด `nvidia-smi topo -m` (GPU ต่อกันแบบ NVLink หรือ PCIe: PIX/PXB/PHB/NODE/SYS · ข้าม CPU socket ไหม) ราคาจริงต่อชั่วโมง ที่ตั้ง จำนวน CPU
2. **เตรียมเครื่องและ Dataset**: `pip install ultralytics roboflow` (ใช้ Python ของ image) คัดลอก `scripts/*.py` ขึ้นไปที่ `/workspace/lab2/code/`
   - `ROBOFLOW_API_KEY` อ่านจาก `.env` ของโฟลเดอร์บท ส่งผ่าน stdin ของ SSH ไปที่ `python download_dataset.py` ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ เสร็จแล้วตรวจว่าไม่มี key ค้างบนเครื่อง (`grep -r` ใน `/workspace` และ `~/.config/roboflow`)
   - `python dataset_stats.py /workspace/hardhat` · `python show_samples.py /workspace/hardhat /workspace/dataset_samples.jpg` แล้วดึงภาพกลับมาที่ `out_dir/dataset_samples.jpg` เปิดดู 1 ครั้ง
3. **ทดสอบสั้น**: `python bench.py --gpus 1 --fraction 0.05 --epochs 2 --tag smoke` และ (ถ้า `num_gpus` = 2) `--gpus 2` ค่าเดียวกัน ต้องจบได้และมีไฟล์ JSON (รอบสั้น mAP50 = 0 ถือว่าปกติ) รวม ~3 นาที
4. **รอบจริง 1 GPU**: `cd /workspace/lab2/code && setsid nohup python bench.py --gpus 1 --epochs <epochs> [ค่าการเทรนอื่น] > /workspace/bench_1gpu.log 2>&1 &` (แยกจาก SSH) รายงานทุก 2–3 นาทีว่าถึง Epoch ไหน (นับแถวใน `/workspace/bench/bench_1gpu/train/results.csv`) รอจนมีบรรทัด `saved /workspace/bench/bench_1gpu.json`
   - อ้างอิง RTX 3090: ~128 วินาทีต่อ Epoch · 5 Epoch ใช้ ~12 นาที
5. **รอบจริง 2 GPU** (ข้ามถ้า `num_gpus` = 1): เหมือนขั้น 4 แต่ `--gpus 2` ค่าอื่นเท่าเดิม log ที่ `/workspace/bench_2gpu.log` รอบนี้ต้องเริ่มหลังรอบ 1 GPU จบแล้วเท่านั้น (สคริปต์จะหยุดเองถ้า GPU ไม่ว่าง) · ถ้าต้องแก้สคริปต์ ให้รันรอบ 1 GPU ใหม่ด้วยเพื่อให้เทียบกันได้
   - อ้างอิง: ~74 วินาทีต่อ Epoch · 5 Epoch ใช้ ~8 นาที
6. **ดึงผลและราคา**: ดึง `/workspace/bench/` ทั้งโฟลเดอร์ (JSON ทุกรอบ + ข้อมูลดิบ) มาไว้ที่ `out_dir/raw/bench/` และ log ทั้งหมดมาไว้ที่ `out_dir/raw/`
   - ใช้สกิล vastai ค้นราคาตลาด **ตอนนี้** ของเครื่อง `gpu` แบบ 1 ใบ และ 2 ใบที่ถูกที่สุด (verified · ต่อ SSH ได้ตรง · ไม่อยู่ในจีน · disk `disk_gb`) เขียน `out_dir/raw/prices.json` รูปแบบนี้ (`report.py` อ่านตามนี้):
     ```json
     {"searched_at_utc": "...", "search_filter": "...",
      "market": {"1gpu": {"offer_id": 0, "num_gpus": 1, "gpu_name": "...", "usd_per_hour": 0.0, "geolocation": "..."},
                 "2gpu": {"offer_id": 0, "num_gpus": 2, "gpu_name": "...", "usd_per_hour": 0.0, "geolocation": "..."}},
      "rented": {"label": "<label>", "instance_id": 0, "num_gpus": 2, "gpu_name": "...", "usd_per_hour": 0.0, "geolocation": "..."}}
     ```
   - บนเครื่องนี้: `python <skill>/scripts/report.py --results <out_dir>` → `out_dir/metrics.json` และ `out_dir/images/1_epoch_time.png 2_speedup.png 3_cost_per_epoch.png 4_bottleneck.png` เปิดดูกราฟอย่างน้อย 2 รูป
7. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices) ได้แก่ อายุเครื่อง ราคาต่อชั่วโมง ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องมี `gpu` ครบ `num_gpus` ใบในเครื่องเดียว และราคารวม ≤ `max_price`
- [ ] Dataset ครบ: Training 14,748 ภาพ (ตัวเลขอ้างอิงของรุ่น 13) มี 2 คลาส `head` `helmet` · มี `dataset_samples.jpg` · ไม่มี `ROBOFLOW_API_KEY` ค้างบนเครื่องเช่า
- [ ] ทั้งสองรอบใช้ค่าเดียวกัน (`model` `epochs` `imgsz` `batch_per_gpu` `seed` `fraction` = 1.0) และ `steps_per_epoch` ของ 2 GPU ≈ ครึ่งหนึ่งของ 1 GPU
- [ ] รอบ 2 GPU มี `allreduce_80mb.median_ms` และ GPU util ของทั้ง 2 ใบ
- [ ] speedup ของ 2 GPU > 1.3 เท่า และ ≤ 2 เท่า · mAP50 ของสองรอบต่างกันไม่เกิน 0.02 · (5 Epoch) mAP50 ≥ 0.90
  - ค่าอ้างอิง (RTX 3090 × 2 ต่อแบบ PHB, 5 Epoch): 128.3 → 73.9 วินาทีต่อ Epoch · speedup 1.74 เท่า · efficiency 86.9% · step 278 → 320 ms · all-reduce 80 MB 21.4 ms · GPU util 85.5% → 81% · CPU 2.8 → 5.3 cores · mAP50 0.962 / 0.963
- [ ] `out_dir` มี `raw/bench/bench_1gpu.json` `bench_2gpu.json` · `raw/prices.json` · `metrics.json` · กราฟ 4 รูป
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)
- [ ] ไม่มีค่า key ใด ๆ ปรากฏในคำตอบหรือไฟล์ผลลัพธ์

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าเครื่องใหม่) · ทั้ง 2 รอบใช้เครื่องเดียวกัน ไม่เช่าเครื่อง 1 GPU แยก (ราคาตลาด 1 GPU ใช้แค่คิดเงินต่อ Epoch)
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. งานเทรนรันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องเทรนซ้ำ ให้ต่อ SSH ใหม่แล้วอ่าน log ต่อ
6. งบอ้างอิงรอบเต็ม (5 Epoch × 2 รอบ): เครื่องเปิดราว 50–60 นาทีที่ ~$0.41/ชม. หรือราว $0.40 ถ้าเครื่องเปิดเกิน 2 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง · CPU · GPU ต่อกันแบบไหน) · Dataset (ภาพ/กรอบต่อชุด) · 1 กับ 2 GPU (วินาทีต่อ Epoch · ideal · speedup · efficiency · วินาทีต่อ step · GPU util · CPU ที่ใช้ · all-reduce · mAP50 · ราคาต่อชั่วโมง · เงินต่อ Epoch ทั้งราคาตลาดและเครื่องที่เช่าจริง) · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วตอบ 3 ข้อ: เร็วขึ้นกี่เท่า · แบบไหนคุ้มเงินที่สุดต่อ 1 Epoch · ทำไมไม่เร็วขึ้นตามจำนวน GPU (อ้างตัวเลขที่วัดได้ เช่น เวลา step ที่เพิ่ม · all-reduce · GPU util)
