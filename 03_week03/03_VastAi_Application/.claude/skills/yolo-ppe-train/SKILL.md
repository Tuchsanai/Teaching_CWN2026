---
name: yolo-ppe-train
description: เทรนโมเดล YOLO11s ตรวจอุปกรณ์ความปลอดภัยหน้างานก่อสร้าง (หมวกนิรภัย เสื้อสะท้อนแสง หน้ากาก) บนเครื่อง GPU ที่เช่าจาก Vast.ai ครบวงจรในคำสั่งเดียว — เช่าเครื่อง → เตรียม Dataset construction-site-safety รุ่น 28 จาก Roboflow พร้อมภาพตัวอย่าง → Training → Evaluation ก่อน (COCO) vs หลังเทรนบน Test Set พร้อมกราฟและภาพเทียบ → (เลือกได้) เปิด AI server /v1/detect และเว็บ SiteSafe → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล yolo-ppe-train", "เทรน YOLO ตรวจหมวกนิรภัย / PPE", "ทำ LAB 1 ซ้ำ", "fine-tune YOLO บน Vast.ai" หรือขอทำซ้ำด้วยจำนวน Epoch / GPU / เพดานราคา / ป้ายเครื่อง / เปิด server หรือเว็บ ที่ต่างไปจากเดิม
---

# yolo-ppe-train (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 1 ทั้งหมดในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร
- คำสั่ง `vastai` ใน container ใช้ได้ใน login shell: `docker exec multi-account bash -lc 'vastai ...'` (`sh -c` เฉย ๆ หาไม่เจอ)
- ราคาในสกิลนี้เขียนเป็น "USD" เสมอ (ห้ามเขียนเครื่องหมายดอลลาร์ตามด้วยตัวเลข เพราะตอนโหลดสกิลจะถูกแทนค่าเป็นอย่างอื่น)

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** ให้คัดลอกขึ้นไปที่ `/workspace/code/` บนเครื่องเช่า และรันจาก `/workspace` (`cd /workspace && python code/<ไฟล์>`)

| สคริปต์ | หน้าที่ |
|---|---|
| `download_dataset.py` | โหลด construction-site-safety รุ่น 28 (roboflow-universe-projects, รูปแบบ YOLO) ลง `/workspace/datasets/construction-site-safety-28` · อ่าน `ROBOFLOW_API_KEY` จาก stdin ไม่เขียนลงดิสก์ |
| `dataset_samples.py` | `python code/dataset_samples.py <dataset_dir> <out.jpg>` นับภาพ/กรอบต่อคลาสของ train · valid · test (พิมพ์ JSON) และทำภาพตาราง 8 รูป (4×2) จาก Training Set ที่วาดกรอบเฉลย เลือกรูปให้ครอบคลุมคลาสมากที่สุด |
| `train.py` | fine-tune จาก `yolo11s.pt` (COCO) · ค่าจาก env `EPOCHS` `IMGSZ` `BATCH` `SEED` `BASE_MODEL` · พิมพ์ `[progress] epoch N/E ... val_mAP50=...` ทุก Epoch · รันซ้ำคำสั่งเดิมแล้ว resume จาก `last.pt` · จบด้วย `[done]` และ `runs/ppe_yolo11s/train_info.json` (เวลาเทรน) |
| `eval.py` | วัดโมเดลก่อน (COCO: person→Person, car/bus/truck→vehicle คลาสอื่นได้ 0) กับหลังเทรน ด้วยวิธีเดียวกันบน Test Set → `/workspace/eval_out/metrics.json` · `images/before_after_1..5.jpg` · `images/ap50_per_class.png` · `images/curves.png` · `samples/` (3 รูปพบ NO-Hardhat + 3 รูปสวมหมวกครบ + `samples.json`) |
| `serve.py` | AI server FastAPI พอร์ต 8080 โหลด `best.pt` ค้างบน GPU · `GET /health` (ไม่ใช้ key) · `POST /v1/detect` ช่อง `file` + `Authorization: Bearer <key>` (ไม่มี/ผิด = 401) · กรอบ confidence ≥ 0.35 · สุ่ม key ครั้งแรกเก็บที่ `/workspace/serve_api_key.txt` ไม่พิมพ์ค่า |

เว็บ SiteSafe (Next.js + PostgreSQL, docker compose project `vapp-lab1`, พอร์ต 3401) อยู่ที่ `lab1_yolo/code/web` ของโฟลเดอร์บท ใช้เมื่อ `web` = ใช่ เท่านั้น ไม่ต้องสร้างใหม่

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `label` | `vapp-lab1` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `gpu` | RTX 4090 × 1 | รุ่นและจำนวน GPU (VRAM ≥ 16 GB ถ้าใช้ batch 32) |
| `max_price` | 0.70 USD/ชม. | ราคารวมของทั้งเครื่องสูงสุด (GPU + disk) |
| `offer_filter` | verified · เน็ตขาเข้าและขาออก ≥ 500 Mbps · CPU ≥ 12 cores · เลือกถูกสุด | เกณฑ์เลือกเครื่อง |
| `image` | `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime` | image ของเครื่อง (runtime ขนาดเล็ก ดึงเร็ว) |
| `disk_gb` | 40 | ขนาด disk |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| `epochs` | 50 | จำนวน Epoch → env `EPOCHS` |
| `imgsz` / `batch` / `seed` | 640 / 32 / 0 | ค่าการเทรน → env `IMGSZ` `BATCH` `SEED` |
| `base_model` | `yolo11s.pt` (COCO) | โมเดลตั้งต้น → env `BASE_MODEL` (เปลี่ยนแล้วต้องตั้ง `BEFORE_W=/workspace/<ไฟล์>` ตอนรัน `eval.py` ด้วย) |
| `serve` | ใช่ | เปิด AI server (ต้องเปิดพอร์ต 8080 ตอนเช่า) |
| `web` | ใช่ | เปิดเว็บ SiteSafe ที่ http://localhost:3401 และทดสอบรูปตัวอย่าง 6 รูป (`web` ต้องมี `serve`) |
| `model_name` | `ppe-yolo11s` | ชื่อโมเดลที่ server รายงาน → env `MODEL_NAME` |
| `out_dir` | `lab1_yolo/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `lab1_yolo/results/skill_v0_run`) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ไฟล์ผลทั้งหมดเขียนบนเครื่องนี้ (โฟลเดอร์ที่เปิด Claude Code) ไม่ใช่ใน container · ห้ามแสดงค่า key ใด ๆ (Vast · `ROBOFLOW_API_KEY` · key ของ AI server)

1. **เช่าเครื่อง**: ใช้สกิล vastai ค้นหาตาม `gpu` `max_price` `offer_filter` เช่าด้วย `image` `disk_gb` ตั้งป้าย `label` เปิดพอร์ต 8080 (ถ้า `serve`) รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU จริง
   - ขึ้น running แต่ SSH ไม่ติด หรือเกิน `ready_timeout` → ลบทันทีแล้วเช่าเครื่องถัดไป · เครื่องที่ถูกที่สุดอาจถูกคนอื่นเช่าไปแล้ว → ข้ามไปเครื่องถัดไป
   - จดราคาจริงต่อชั่วโมง ที่ตั้ง CPU cores เวลาที่รอจนพร้อม
2. **เตรียม Dataset**: `pip install ultralytics roboflow` (ใช้ Python ของ image) ถ้า `import cv2` ล้มเพราะไม่มี `libxcb`/`libGL` ให้เปลี่ยนเป็น `opencv-python-headless` · คัดลอก `scripts/*.py` ขึ้นไปที่ `/workspace/code/`
   - `ROBOFLOW_API_KEY` อ่านจาก `.env` ของโฟลเดอร์บท ส่งผ่าน stdin ของ SSH ไปที่ `cd /workspace && python code/download_dataset.py` ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์ เสร็จแล้วตรวจว่าไม่มี key ค้าง (`grep -r` ใน `/workspace` และ `~/.config/roboflow`)
   - `python code/dataset_samples.py /workspace/datasets/construction-site-safety-28 /workspace/dataset_samples.jpg > /workspace/dataset_stats.json` แล้วดึงภาพกลับมาที่ `out_dir/dataset_samples.jpg` เปิดดู 1 ครั้ง
3. **Training**: `cd /workspace && EPOCHS=<epochs> [IMGSZ= BATCH= SEED= BASE_MODEL=] setsid nohup python code/train.py > /workspace/train.log 2>&1 &` (แยกจาก SSH)
   - รายงานทุก ~2 นาทีจากบรรทัด `[progress]` ล่าสุดใน log (Epoch และ val mAP50) จนเจอ `[done]` · บรรทัดสุดท้าย `epoch E+1/E` คือการ validate ด้วย `best.pt` ไม่ใช่ Epoch เกิน
   - การเชื่อมต่อหลุด: ต่อ SSH ใหม่แล้วอ่าน log ต่อ · ถ้า process ตายกลางทาง สั่งคำสั่งเดิมซ้ำ สคริปต์ resume เอง
   - อ้างอิง RTX 4090: Epoch แรก ~50 วินาที (รวมโหลด) จากนั้น ~9 วินาทีต่อ Epoch · 50 Epoch ~8.5 นาที
4. **Evaluation**: `cd /workspace && python code/eval.py > /workspace/eval.log 2>&1` (~10 วินาที) แล้วดึงกลับมาไว้ใน `out_dir`:
   - `/workspace/eval_out/` ทั้งหมด → `out_dir/` (`metrics.json` · `images/` · `samples/`)
   - `/workspace/runs/ppe_yolo11s/{args.yaml,results.csv,train_info.json}` → `out_dir/train/` · `/workspace/train.log` → `out_dir/train/train_progress.log` · `/workspace/eval.log` → `out_dir/eval.log`
   - `/workspace/runs/ppe_yolo11s/weights/best.pt` → `out_dir/weights/best.pt`
   - เปิดดู `images/before_after_1.jpg` และ `images/ap50_per_class.png` อย่างน้อยอย่างละ 1 ครั้ง
5. **AI server** (ถ้า `serve`): `pip install fastapi uvicorn python-multipart` แล้ว `cd /workspace && MODEL_NAME=<model_name> setsid nohup python code/serve.py > /workspace/serve.log 2>&1 &` รอบรรทัด `loaded on 0`
   - หาพอร์ตภายนอกที่แมปกับ 8080 ด้วยสกิล vastai แล้วทดสอบจากนอกเครื่อง 3 ข้อ: `GET /health` ได้ 200 และ `ready: true` · `POST /v1/detect` รูปจาก `out_dir/samples` พร้อม key ได้กรอบกลับมา · ไม่มี key ได้ 401
   - อ่าน key จาก `/workspace/serve_api_key.txt` ผ่าน SSH ลงไฟล์ `lab1_yolo/code/web/.env` โดยตรง (ไม่พิมพ์ค่า): `YOLO_BASE_URL=http://<ip>:<port>` `YOLO_API_KEY=<key>` `YOLO_MODEL=<model_name>`
6. **เว็บ** (ถ้า `web`): ใน `lab1_yolo/code/web` สั่ง `docker compose up -d --build` (ห้ามลบ `.env`) รอ http://localhost:3401 ได้ 200 และมุมบนบอกว่า AI server พร้อม
   - ส่งรูป `out_dir/samples/*.jpg` ครบ 6 รูปผ่าน `POST /api/detect` ของเว็บ (หรือกดในเบราว์เซอร์) จดผล ผ่าน/ไม่ผ่าน · คนไม่สวมหมวก · เวลาโมเดล · เวลาไป-กลับ แล้วตรวจว่าขึ้นในหน้า `/history` ครบ
7. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน แล้วใช้สกิล vastai ลบเครื่องป้าย `label` และตรวจซ้ำว่าไม่เหลือในบัญชี · ถ้าเปิดเว็บ `docker compose down` **ไม่ใส่ `-v`** (เก็บประวัติใน volume `vapp-lab1_pgdata`) · ดูบิลจริง (invoices): อายุเครื่อง ราคาต่อชั่วโมง ยอด GPU · disk · รับส่งข้อมูล รวมเครื่องที่เปิดไม่ขึ้นด้วย

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องเห็น GPU ตาม `gpu` และราคารวม ≤ `max_price`
- [ ] Dataset ครบ 3 ชุด (ค่าอ้างอิงรุ่น 28: Training 2,605 · Validation 114 · Test 82 ภาพ · 10 คลาส) · มี `dataset_samples.jpg` · ไม่มี `ROBOFLOW_API_KEY` ค้างบนเครื่องเช่า
- [ ] `train.log` มี `[done]` และ `results.csv` มีครบ `epochs` แถว
- [ ] `out_dir/metrics.json` มี `before` และ `after` · `test_images` = 82 · `after.mAP50` > `before.mAP50`
  - `epochs` ≥ 50 → `after.mAP50` ≥ 0.70 · 10–49 Epoch → ≥ 0.50
  - ค่าอ้างอิง (RTX 4090, 50 Epoch): mAP50 0.090 → 0.782 · mAP50-95 0.066 → 0.504 · AP50 Hardhat 0 → 0.94 · NO-Hardhat 0 → 0.58 · Person 0.75 → 0.88 · ~8.5 ms ต่อรูป · val mAP50 ที่ Epoch 10/25/50 = 0.66/0.77/0.82
- [ ] `out_dir` มี `images/before_after_1..5.jpg` · `ap50_per_class.png` · `curves.png` · `samples/` 6 รูป + `samples.json` · `train/` · `weights/best.pt`
- [ ] (ถ้า `serve`) ทดสอบ server ผ่านครบ 3 ข้อ และ `lab1_yolo/code/web/.env` มีครบ 3 ค่า
- [ ] (ถ้า `web`) เว็บตอบ 200 ตรวจรูปตัวอย่างครบ 6 รูป และขึ้นในหน้าประวัติครบ
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี (ยกเว้น `keep_machine`)
- [ ] ไม่มีค่า key ใด ๆ ปรากฏในคำตอบหรือไฟล์ผลลัพธ์ (`.env` ของเว็บเป็นที่เดียวที่เก็บ key ได้ และห้าม commit)

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบเครื่อง แล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` และห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าใหม่) · เครื่องที่เปิดไม่ขึ้นก็ถูกคิดเงินตามเวลาที่เปิด จึงต้องลบทันที
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. งานเทรนและ server รันแยกจาก SSH เสมอ (`setsid nohup`) การเชื่อมต่อหลุดต้องไม่ทำให้ต้องเทรนซ้ำ
6. เงินเดินตลอดเวลาที่เครื่องเปิด ไม่ใช่เฉพาะตอนเทรน ทำทุกขั้นต่อเนื่อง ไม่ปล่อยเครื่องว่าง · งบอ้างอิงรอบเต็ม (50 Epoch + server + เว็บ): เครื่องเปิด ~21 นาทีที่ ~0.41 USD/ชม. รวม ~0.21 USD (นับเครื่องที่เปิดไม่ขึ้นด้วย) ถ้าเครื่องเปิดเกิน 1 ชั่วโมงให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคาต่อชั่วโมง · ที่ตั้ง · CPU · เวลารอจนพร้อม) · Dataset (ภาพต่อชุด · กรอบต่อคลาสใน Training Set) · เวลาเทรนและ val mAP50 ที่ Epoch 10/25/สุดท้าย · ก่อน vs หลังบน Test Set (mAP50 · mAP50-95 · AP50 ของ Hardhat, NO-Hardhat, Safety Vest, NO-Safety Vest, Person · เวลาต่อรูป) · ผลทดสอบ server/เว็บ (ถ้าเปิด) · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง (GPU · disk · รับส่งข้อมูล) · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
