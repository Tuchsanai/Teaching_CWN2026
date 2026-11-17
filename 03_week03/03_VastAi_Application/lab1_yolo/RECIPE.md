# RECIPE — เทรน YOLO ตรวจอุปกรณ์ความปลอดภัย (PPE) บน RTX 4090 แล้วเปิด AI server

ไฟล์นี้เขียนให้ **AI อ่านแล้วทำตามเอง** ด้วยสกิล `vastai` · ผู้เรียนไม่ต้องรันคำสั่งใดเอง
สคริปต์ที่ใช้อยู่ในโฟลเดอร์ `lab1_yolo/` ข้างไฟล์นี้: `get_data.py` (ดาวน์โหลด dataset) · `train.py` (เทรน) · `eval.py` (วัดผลก่อน/หลัง) · `serve.py` (AI server) · ห้ามแก้สคริปต์เหล่านี้ระหว่างรัน ถ้าพังให้รายงานจุดที่พัง

คำถามของการทดลอง: โมเดลสำเร็จรูปที่เทรนบน COCO รู้จักแค่ "คน" ไม่รู้จักหมวกนิรภัยหรือเสื้อสะท้อนแสง — ถ้าเทรนต่อด้วยข้อมูลของเราราว 20 นาที จะดีขึ้นแค่ไหน

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `LABEL` | `vapp-v-lab1` | ชื่อเครื่องบน Vast.ai |
| `MAX_DPH` | `0.70` | เพดานราคารวม $/ชม. (GPU + disk) — **ห้ามขึ้นเกินนี้เอง** ถ้าไม่มีเครื่องให้หยุดแล้วถามผู้ใช้ |
| `EPOCHS` | `50` | จำนวน Epoch (ราว 7–8 นาทีบน RTX 4090) |
| `MAX_HOURS` | `3` | เครื่องเปิดได้นานสุด (ชั่วโมง) นับจากเช่า |

ค่าคงที่: dataset `roboflow-universe-projects/construction-site-safety` version `28` (Training 2605 · Validation 114 · Test 82 ภาพ, 10 คลาส, CC BY 4.0) · โมเดลตั้งต้น `yolo11s.pt` (เทรนบน COCO มาแล้ว) · `YOLO_MODEL=ppe-yolo11s`

## 1) เตรียมใน container `multi-account`

```bash
# คำสั่งอ้างอิง (รันบนเครื่องผู้ใช้ ในโฟลเดอร์ปัจจุบัน)
docker exec multi-account mkdir -p /workspace/vastapp_lab/lab1_yolo/src
for f in get_data.py train.py eval.py serve.py; do docker cp lab1_yolo/$f multi-account:/workspace/vastapp_lab/lab1_yolo/src/; done
docker cp .env multi-account:/workspace/vastapp_lab/.env                       # มี ROBOFLOW_API_KEY
```

- กุญแจ ssh: `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` (ลงทะเบียนกับบัญชีแล้ว)
- ส่ง `ROBOFLOW_API_KEY` ไปเครื่องที่เช่าผ่าน env ของคำสั่ง ssh เท่านั้น (`set -a; . /workspace/vastapp_lab/.env; set +a` แล้วใช้ `$ROBOFLOW_API_KEY`) — **ห้ามแสดงค่าบนจอ ห้ามเขียนลงไฟล์บนเครื่องที่เช่า**

## 2) ขั้นตอน

### 2.1 เช่าเครื่อง

- GPU `RTX_4090` 1 ใบ · verified · reliability > 0.98 · ssh แบบ direct · ไม่เอาเครื่องในจีน
- ราคารวม (GPU + disk 40 GB) ไม่เกิน `MAX_DPH` · เลือกเครื่องที่ถูกที่สุดที่ผ่านเงื่อนไข
- `cuda_max_good>=12.8` (image ใช้ CUDA 12.8) · `inet_down>=500` · `cpu_cores_effective>=12` (การเตรียมภาพตอนเทรนใช้ CPU)
- image `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime` · disk 40 GB · `--ssh --direct` · เปิดพอร์ต `--env '-p 8080:8080'` · ป้าย `LABEL`
- เครื่องค้าง `loading` เกิน 10 นาที หรือสถานะ `exited` `offline` `unknown` → ลบแล้วเช่าจาก host อื่น · มีได้ครั้งละ 1 เครื่อง

```bash
# คำสั่งอ้างอิง
vastai search offers 'gpu_name=RTX_4090 num_gpus=1 verified=true rentable=true direct_port_count>=2 reliability>0.98 inet_down>=500 cuda_max_good>=12.8 cpu_cores_effective>=12 geolocation notin [CN]' --storage 40 -o 'dph_total' --limit 10 --raw
vastai create instance <OFFER_ID> --image pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime --disk 40 --ssh --direct --env '-p 8080:8080' --label <LABEL>
```

### 2.2 ติดตั้งและดาวน์โหลด dataset (~3–5 นาที)

```bash
# คัดลอกสคริปต์ขึ้นเครื่อง (ssh/scp ใช้ -i /workspace/vastai_lab/Devtool_SSH/devtoolSSH -o StrictHostKeyChecking=no)
scp -P <SSH_PORT> src/get_data.py src/train.py src/eval.py src/serve.py root@<SSH_HOST>:/workspace/

# บนเครื่องที่เช่า
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq libgl1 libglib2.0-0 > /dev/null
pip install -q ultralytics roboflow fastapi uvicorn python-multipart
cd /workspace && ROBOFLOW_API_KEY=<จาก env> python get_data.py      # → /workspace/data/ppe/data.yaml
```

ตรวจผ่าน: `get_data.py` พิมพ์ `train: 2605 images` `valid: 114 images` `test: 82 images` และ `python -c "import torch;print(torch.cuda.is_available())"` ได้ `True`

### 2.3 เทรน (~7–8 นาที รวม export ONNX)

```bash
cd /workspace && setsid nohup python train.py --epochs <EPOCHS> > train.log 2>&1 < /dev/null &
```

- ดูความคืบหน้าทุก ~2 นาที จาก `/workspace/runs/ppe/results.csv` (1 แถวต่อ 1 Epoch) และ `tail -c 600 train.log` · รายงาน Epoch ปัจจุบันและ mAP50 ล่าสุด
- ตรวจผ่าน: มี `/workspace/runs/ppe/weights/best.pt` และ `/workspace/runs/ppe/train_info.json` (`best.onnx` ถ้า export ได้)

### 2.4 วัดผลบน Test Set (~1 นาที)

```bash
cd /workspace && python eval.py --out /workspace/results
```

`eval.py` วัด 2 โมเดลด้วยโค้ดเดียวกันบน Test Set 82 ภาพ (ไม่ได้ใช้เทรน):
- **ก่อนเทรน (Baseline)** = `yolo11s.pt` ของ COCO — จับคู่คลาส COCO `person→Person` และ `car/bus/truck→vehicle` ได้เท่านั้น คลาสอื่นได้ AP = 0
- **หลังเทรน** = `best.pt`

ผลลัพธ์ใน `/workspace/results/`: `metrics.json` · `images/before_after_1..5.jpg` · `images/curves.png` · `images/ap50_per_class.png`

### 2.5 เปิด AI server

- API key: สุ่ม 48 ตัวอักษร hex เก็บที่ `/workspace/yolo_api_key.txt` บนเครื่องที่เช่า — **ห้ามแสดงบนจอ**
- ใช้ `setsid nohup` ให้ server อยู่ต่อหลัง ssh หลุด แล้วรอจน `curl -sf localhost:8080/health` ผ่าน

```bash
cd /workspace && python -c "import secrets;print(secrets.token_hex(24))" > yolo_api_key.txt
YOLO_MODEL=ppe-yolo11s setsid nohup python serve.py > serve.log 2>&1 < /dev/null &
```

API: `GET /health` (ไม่ต้องใช้ key) · `POST /v1/detect?conf=0.35` (multipart `file`, header `Authorization: Bearer <key>`) → `{model, width, height, inference_ms, total_ms, detections:[{class, confidence, box:[x1,y1,x2,y2]}]}`

### 2.6 ทดสอบจากนอกเครื่อง

- หา public IP และพอร์ตภายนอกที่ map กับ `8080/tcp` → `URL=http://<ip>:<port>`
- ทดสอบจาก container `multi-account`: `GET $URL/health` · `POST $URL/v1/detect` ด้วยรูปจาก Test Set 1 รูป (ต้องได้กรอบกลับมา) · ส่งแบบไม่มี key ต้องได้ `401`

### 2.7 เขียนค่าเชื่อมต่อ

เขียนไฟล์ `/workspace/vastapp_lab/lab1_yolo/yolo.env` ใน container `multi-account` ให้มี 3 บรรทัด ไม่มีเครื่องหมายคำพูด ไม่มี comment และไม่แสดงค่า key บนจอ

```text
YOLO_BASE_URL=http://<ip>:<port>
YOLO_API_KEY=<key>
YOLO_MODEL=ppe-yolo11s
```

### 2.8 เก็บผลกลับ

ไฟล์ weights รวม ~57 MB · บาง host ส่งไฟล์ออกช้า ให้ใช้ `scp -C` และตั้ง timeout ของคำสั่งให้นานพอ (ไม่ต้องรอซ้ำถ้าขนาดไฟล์ตรงกับต้นทางแล้ว)

คัดลอกจากเครื่องที่เช่า → container (`/workspace/vastapp_lab/lab1_yolo/results/`) → โฟลเดอร์ `lab1_yolo/results/` ของโฟลเดอร์ปัจจุบัน (`docker cp`)

| ไฟล์บนเครื่องที่เช่า | ปลายทางใน `lab1_yolo/results/` |
|---|---|
| `/workspace/results/metrics.json` | `metrics.json` |
| `/workspace/results/images/*` | `images/` |
| `/workspace/runs/ppe/results.csv` · `args.yaml` · `train_info.json` | `train/` |
| `/workspace/runs/ppe/confusion_matrix_normalized.png` | `images/` |
| `/workspace/runs/ppe/weights/best.pt` · `best.onnx` | `weights/` |
| `/workspace/train.log` (เฉพาะ 60 บรรทัดสุดท้าย) | `train/train_tail.log` |

แล้วเขียน `lab1_yolo/results/run_info.json`: GPU · ราคา $/ชม. · ที่ตั้ง · CPU cores · image · เวลาแต่ละขั้น (เช่า→running, ติดตั้ง+dataset, เทรน, วัดผล, เปิด server) — **ห้ามใส่ IP, เลข instance, อีเมล**

## 3) กติกา

- ห้ามแสดง API key ของ Vast.ai, Roboflow หรือของ server บนจอ
- ห้ามขึ้นราคาเกิน `MAX_DPH` · ห้ามลบเครื่องที่ใช้งานได้โดยไม่ได้รับคำสั่ง · ห้ามแตะเครื่องที่ป้ายไม่ใช่ `LABEL`
- **จบขั้นนี้แล้วเปิดเครื่องทิ้งไว้** (เว็บต้องใช้ AI server ต่อ) แต่ห้ามเกิน `MAX_HOURS`
- รายงานทุกเครื่องที่สร้างและลบ

## 4) สรุปตอนจบ (ภาษาไทย)

1. ตารางเครื่อง: GPU · $/ชม. · ที่ตั้ง · CPU cores · image
2. ตารางเวลา: เช่า→running · ติดตั้ง+dataset · เทรน (`EPOCHS` Epoch) · วัดผล · เปิด server
3. ตารางก่อน vs หลังบน Test Set: mAP50 · mAP50-95 · AP50 ของ `Hardhat` `NO-Hardhat` `Safety Vest` `NO-Safety Vest` `Person`
4. ผลทางการของ Ultralytics (`test_official_ultralytics` ใน metrics.json): mAP50 · mAP50-95 · Precision · Recall
5. เวลาที่โมเดลใช้ต่อรูป (ms) และผลทดสอบ AI server (health · detect · ไม่มี key ได้ 401)
6. ไฟล์ `yolo.env` เขียนแล้ว และไฟล์ที่เก็บกลับมาใน `lab1_yolo/results/`
