---
name: yolo-ppe-train
description: เทรนโมเดล YOLO ตรวจอุปกรณ์ความปลอดภัยหน้างานก่อสร้าง (หมวกนิรภัย เสื้อกั๊ก หน้ากาก) บนเครื่อง GPU ที่เช่าจาก Vast.ai ครบวงจรในคำสั่งเดียว — เช่าเครื่อง → เตรียม Dataset construction-site-safety จาก Roboflow → Training → Evaluation ก่อน vs หลังเทรนบน Test Set → (เลือกได้) เปิด AI server + เว็บ SiteSafe → ลบเครื่องและสรุปค่าใช้จ่าย ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล yolo-ppe-train", "เทรน YOLO ตรวจหมวกนิรภัย/PPE", "ทำ LAB 1 ซ้ำ", "fine-tune YOLO บน Vast.ai" หรือขอเทรนโมเดลตรวจ PPE ด้วยจำนวน Epoch/GPU/งบที่ต่างไปจากเดิม
---

# yolo-ppe-train (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 1 ทั้งหมดในคำสั่งเดียว ทุกคำสั่งที่แตะ Vast.ai (ค้นหา เช่า SSH ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) — อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่สอนวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `label` | `vapp-lab1` | ป้ายเครื่องบน Vast.ai (แตะเฉพาะเครื่องป้ายนี้) |
| `gpu` | RTX 4090 × 1 | รุ่นและจำนวน GPU |
| `max_price` | $0.70/ชม. | ราคารวมสูงสุด (GPU + disk) |
| `offer_filter` | verified · เน็ตขึ้น/ลง ≥ 500 Mbps · CPU ≥ 12 cores · เลือกถูกสุด | เกณฑ์เลือกเครื่อง |
| `image` | `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime` | image ของเครื่อง |
| `disk_gb` | 40 | ขนาด disk |
| `ready_timeout` | 10 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องถัดไป |
| `dataset` | `roboflow-universe-projects/construction-site-safety` รุ่น 28 (YOLO) | Dataset |
| `base_model` | `yolo11s.pt` (COCO) | โมเดลตั้งต้น |
| `epochs` | 50 | จำนวน Epoch |
| `batch` | 32 | batch size |
| `out_dir` | `lab1_yolo/results` | โฟลเดอร์เก็บผลบนเครื่องนี้ (ถ้ามีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่) |
| `serve` | เปิด | เปิด AI server พอร์ต 8080 (`port 8080` ต้องเปิดตอนเช่า) |
| `web` | เปิด | เปิดเว็บ SiteSafe ที่ http://localhost:3401 และทดสอบ sample-1, 2, 5 (`web` ต้องมี `serve`) |
| `model_name` | `ppe-yolo11s` | ชื่อโมเดลที่ server รายงาน |
| `container` | `multi-account` · `/workspace/vastapp_lab` | ที่ทำงานของสกิล vastai |
| `ssh_key` | `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | กุญแจ SSH ใน container |

สคริปต์ที่ใช้อยู่ในโฟลเดอร์ `lab1_yolo` ของบท: `train.py` · `eval.py` · `serve.py` · เว็บ `web/` (docker compose)

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป

1. **เช่าเครื่อง** — ด้วยสกิล vastai ค้นหาตาม `gpu` `max_price` `offer_filter` เช่าด้วย `image` `disk_gb` ตั้งป้าย `label` เปิดพอร์ต 8080 ถ้า `serve` เปิด รอจน SSH เข้าได้และ `nvidia-smi` เห็น GPU จริง
   - ขึ้น running แต่ SSH ไม่ติด / log ติดตั้ง openssh ไม่ได้ → ลบทันทีแล้วเช่าเครื่องถัดไป ไม่ต้องรอครบ `ready_timeout`
2. **เตรียม Dataset** — บนเครื่องเช่า `pip install ultralytics roboflow` แล้วเปลี่ยน `opencv-python` เป็น `opencv-python-headless` (เครื่องไม่มี `libxcb` ทำให้ `import cv2` ล้ม) ดาวน์โหลด `dataset` รูปแบบ YOLO ไว้ใต้ `/workspace`
   - `ROBOFLOW_API_KEY` อ่านจาก `.env` ของโฟลเดอร์บท ส่งผ่าน stdin ของ SSH เท่านั้น ห้ามใส่ในบรรทัดคำสั่ง ห้ามเขียนลงไฟล์บนเครื่องเช่า ห้ามแสดงค่า เสร็จแล้วค้นว่าไม่มีค่า key ค้างในเครื่อง
3. **Training** — คัดลอก `train.py` จากเครื่องนี้ขึ้นเครื่องเช่า (โฟลเดอร์ใน container อาจไม่มีสคริปต์ล่าสุด) รันใน tmux session `train` เขียน log ที่ `/workspace/train.log`
   `python train.py --epochs <epochs> --batch <batch> --model <base_model>` (สคริปต์หา Dataset เองและแก้ path ใน `data.yaml` ให้)
   รายงานทุก ~2 นาทีจากบรรทัด `PROGRESS` ใน log (Epoch และ Validation mAP50) จนเจอ `DONE`
4. **Evaluation** — คัดลอก `eval.py` ขึ้นไปแล้วรัน `python eval.py --base <base_model>` ผลอยู่ที่ `/workspace/results` แล้วดึงทั้งโฟลเดอร์กลับมาที่ `out_dir` (`metrics.json` · `images/` · `train/` · `weights/best.pt`) เปิดดูภาพ `before_after_1.jpg` อย่างน้อย 1 รูป
5. **AI server** (ถ้า `serve`) — `pip install fastapi uvicorn python-multipart` คัดลอก `serve.py` ขึ้นไป รันใน tmux session `serve` (สคริปต์สร้าง key ที่ `/workspace/yolo_api_key.txt`) หาพอร์ตภายนอกที่แมปกับ 8080 แล้วทดสอบจากนอกเครื่อง 3 ข้อ: `GET /health` ได้ 200 · `POST /v1/detect` พร้อม `Authorization: Bearer <key>` ได้กรอบกลับมา · ไม่มี key ได้ 401
   เขียน `lab1_yolo/web/.env`: `YOLO_BASE_URL=http://<ip>:<port>` `YOLO_API_KEY=<key>` `YOLO_MODEL=<model_name>`
6. **เว็บ** (ถ้า `web`) — `docker compose up -d --build` ในโฟลเดอร์ `lab1_yolo/web` รอ http://localhost:3401 ได้ 200 ส่ง `public/samples/sample-1.jpg`, `sample-2.jpg`, `sample-5.jpg` ไปที่ `/api/detect` ของเว็บทีละรูป จดผล ผ่าน/ไม่ผ่าน · คนไม่สวมหมวก · เวลาโมเดล · เวลาไป-กลับ
7. **ปิดทุกอย่าง (ห้ามข้าม)** — ด้วยสกิล vastai ลบเครื่องป้าย `label` แล้วตรวจซ้ำว่าไม่เหลือในบัญชี · ถ้าเปิดเว็บ `docker compose down` **ไม่ใส่ `-v`** (เก็บประวัติใน volume `vapp-lab1_pgdata`) · ดูบิลจริง: อายุเครื่อง ราคาต่อชั่วโมง ยอด GPU · disk · รับส่งข้อมูล

## เกณฑ์ตรวจผ่าน

- [ ] เครื่องเห็น GPU ตาม `gpu` และราคารวม ≤ `max_price`
- [ ] Dataset ครบ 3 ชุด (รุ่น 28: Training 2,605 · Validation 114 · Test 82 ภาพ · 10 คลาส) และไม่มีค่า Roboflow key บนเครื่องเช่า
- [ ] `train.log` มี `DONE` และ Epoch ครบตาม `epochs`
- [ ] `out_dir/metrics.json` มี `before` และ `after` · `after.mAP50` > `before.mAP50`
  - ค่าอ้างอิง (50 Epoch, RTX 4090): ก่อน 0.090 → หลัง 0.782 บน Test Set · เทรน ~7 นาที
  - `epochs` ≥ 50 ต้องได้ `after.mAP50` ≥ 0.70 · น้อยกว่านั้นต้อง ≥ 0.50
- [ ] (ถ้า `serve`) ทดสอบ server ผ่านครบ 3 ข้อ
- [ ] (ถ้า `web`) เว็บตอบ 200 และตรวจรูปตัวอย่างได้ครบ 3 รูป
- [ ] ไม่มีเครื่องป้าย `label` ค้างในบัญชี
- [ ] ไม่มีค่า key ใด ๆ (Vast · Roboflow · YOLO API) ปรากฏในคำตอบหรือไฟล์ผลลัพธ์

## กติกาเรื่องเงิน

1. **ลบเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ลบเครื่องก่อนแล้วค่อยรายงานปัญหา
2. ห้ามเช่าเครื่องที่ราคารวมเกิน `max_price` ห้ามเช่าพร้อมกันเกิน 1 เครื่อง (เครื่องเสียต้องลบก่อนเช่าใหม่)
3. แตะเฉพาะเครื่องป้าย `label` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ผู้ใช้สั่งให้เปิดค้างไว้ (เช่น จะใช้เว็บต่อ) จึงข้ามการลบได้ — ต้องบอกชัดในสรุปว่าเครื่องยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. งานบนเครื่องเช่าที่นานรันใน tmux เสมอ การเชื่อมต่อหลุดต้องไม่ทำให้เสียเวลาเทรนซ้ำ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้ (GPU · ราคา · ที่ตั้ง) · เวลาแต่ละขั้น · mAP50 / mAP50-95 ก่อน vs หลังบน Test Set และ AP50 ของ Hardhat, NO-Hardhat, Safety Vest, NO-Safety Vest, Person · ผลทดสอบ server/เว็บ (ถ้าเปิด) · ค่าใช้จ่ายจริง · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
