# NINFER_RECIPE — เปิด AI server (NInfer + Qwen) บน RTX 5090 ของ Vast.ai

ไฟล์นี้เขียนให้ **AI อ่านแล้วทำตามเอง** ด้วยสกิล `vastai` · ผู้เรียนไม่ต้องรันคำสั่งใดเอง
AI สร้างคำสั่งจาก "คำสั่งอ้างอิง" แล้วส่งไปรันบนเครื่องที่เช่าผ่าน ssh · ห้ามสร้างไฟล์สคริปต์ทิ้งไว้ใน repo

แหล่งอ้างอิง: [github.com/Neroued/ninfer](https://github.com/Neroued/ninfer) (ตัวรันโมเดล) · [huggingface.co/neroued](https://huggingface.co/neroued) (ไฟล์โมเดล) · ตรวจกับต้นทาง 18 พ.ย. 2026

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `MODEL` | `qwen3.8-27b-nvfp4` | รหัสโมเดลจากตารางข้อ 1 |
| `LABEL` | `lab-5090` | ชื่อเครื่องบน Vast.ai |
| `MAX_DPH` | `1.20` | เพดานราคารวม $/ชม. — **ห้ามขึ้นเกินนี้เอง** ถ้าไม่มีเครื่องให้หยุดแล้วถามผู้ใช้ |

## 1) โมเดลที่เลือกได้ (ไฟล์เดียว ใช้ RTX 5090 ใบเดียว)

| `MODEL` | HF repo | ไฟล์ | `LLM_MODEL` (ชื่อใน API) | ขนาดไฟล์ |
|---|---|---|---|---|
| `qwen3.8-27b-nvfp4` ⭐ | `neroued/Qwen3.8-27B-nvfp4-NInfer` | `qwen3_8_27b_nvfp4.ninfer` | `qwen3.8-27b` | 22.1 GiB |
| `qwen3.8-27b` | `neroued/Qwen3.8-27B-NInfer` | `qwen3_8_27b.ninfer` | `qwen3.8-27b` | 19.0 GiB |
| `qwen3.6-27b` | `neroued/Qwen3.6-27B-NInfer` | `qwen3_6_27b.ninfer` | `qwen3.6-27b` | 16.3 GiB |
| `qwen3.6-27b-nvfp4` | `neroued/Qwen3.6-27B-nvfp4-NInfer` | `qwen3_6_27b_nvfp4.ninfer` | `qwen3.6-27b` | 17.1 GiB |
| `qwen3.6-35b-a3b` | `neroued/Qwen3.6-35B-A3B-NInfer` | `qwen3_6_35b_a3b.ninfer` | `qwen3.6-35b-a3b` | 21.2 GiB |

## 2) ขั้นตอน

### 2.1 เช่าเครื่อง

- GPU `RTX_5090` 1 ใบ · verified · ราคารวม (GPU + disk 90 GB) ไม่เกิน `MAX_DPH` · ป้าย `LABEL`
- driver ของเครื่องต้องรองรับ CUDA 13.1 ขึ้นไป (`cuda_max_good>=13.1`) เพราะ image ใช้ CUDA 13.1
- ความเร็วดาวน์โหลดของเครื่องมากกว่า 2500 Mbps (ไฟล์โมเดล ~20 GiB) · เลือกเครื่องที่ค่าดาวน์โหลดต่อ GB ต่ำ
- image `nvidia/cuda:13.1.2-devel-ubuntu24.04` (image เดียวกับ Dockerfile ของ NInfer) · disk 90 GB · ssh แบบ direct · เปิดพอร์ต `-p 8080:8080`
- เครื่องค้าง `loading` เกิน 10 นาที หรือสถานะเป็น `exited` `offline` `unknown` → ลบแล้วเช่าเครื่องจาก host อื่น
- มีได้ครั้งละ 1 เครื่อง · ทำงานให้จบในรอบเดียว (รอด้วย `sleep` แล้วตรวจสถานะเป็นช่วง)

### 2.2 ติดตั้ง NInfer และโหลดโมเดล (~8–10 นาที)

รันบนเครื่องที่เช่าแบบเบื้องหลัง (`nohup … &`) แล้วดู log ทุก ~60 วินาที · **โหลดโมเดลพร้อมกับ build**

```bash
# คำสั่งอ้างอิง — แทน <REPO> <FILE> ด้วยค่าจากตารางข้อ 1
export DEBIAN_FRONTEND=noninteractive
mkdir -p /workspace/ninfer/models && cd /workspace
apt-get update -qq && apt-get install -y -qq git cmake ninja-build pkg-config build-essential python3-pip \
  libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libcurl4-openssl-dev \
  libjpeg-dev libhwloc-dev liburing-dev
pip install -q --break-system-packages -U "huggingface_hub[hf_xet]"

HF_XET_HIGH_PERFORMANCE=1 hf download <REPO> <FILE> --local-dir /workspace/ninfer/models > /workspace/download.log 2>&1 &

git clone -q https://github.com/Neroued/ninfer.git /tmp/n && cp -a /tmp/n/. /workspace/ninfer/
cd /workspace/ninfer && cmake --preset rtx5090-release > /workspace/build.log 2>&1 \
  && cmake --build build/rtx5090-release -j"$(nproc)" >> /workspace/build.log 2>&1
wait
```

ตรวจผ่าน: มี `/workspace/ninfer/build/rtx5090-release/apps/ninfer-serve` และ `/workspace/ninfer/models/<FILE>` ขนาดตรงตาราง

ก่อน build ให้อ่าน `README.md` และ `docs/serving.md` ของ repo ที่ clone มา · ถ้าคำสั่งในไฟล์นี้ไม่ตรงกับต้นทาง **ให้ยึดต้นทาง** แล้วรายงานจุดที่ต่าง

### 2.3 เปิด server

- API key ของ server: สุ่ม 48 ตัวอักษร hex เก็บที่ `/workspace/ninfer_api_key.txt` บนเครื่องที่เช่า — **ห้ามแสดงบนจอ**
- ใช้ `setsid nohup` ให้ server อยู่ต่อหลัง ssh หลุด แล้วรอจน `curl -sf localhost:8080/health` ผ่าน

```bash
# คำสั่งอ้างอิง
cd /workspace/ninfer
setsid nohup ./build/rtx5090-release/apps/ninfer-serve models/<FILE> \
  --host 0.0.0.0 --port 8080 \
  --max-context 16384 --max-concurrency 4 --kv-dtype fp8 \
  --spec mtp --draft-tokens 3 --proposal-head optimized \
  --no-thinking --cors --api-key "$(cat /workspace/ninfer_api_key.txt)" \
  > /workspace/ninfer.log 2>&1 < /dev/null &
```

### 2.4 ทดสอบจากนอกเครื่อง

- หา public IP และพอร์ตภายนอกที่ map กับ `8080/tcp` → `URL=http://<ip>:<port>`
- ทดสอบจาก container `multi-account`: `GET $URL/health` และถามภาษาไทย 1 ข้อผ่าน `POST $URL/v1/chat/completions` (header `Authorization: Bearer <key>` · `model` = `LLM_MODEL`)
- วัด: เวลาตอบ · token ต่อวินาที · VRAM จาก `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`

### 2.5 เขียนค่าเชื่อมต่อ

เขียนไฟล์ `/workspace/vastai_lab/chatbot.env` ใน container `multi-account` ให้มี 3 บรรทัด ไม่มีเครื่องหมายคำพูด ไม่มี comment และไม่แสดงค่า key บนจอ

```text
LLM_BASE_URL=http://<ip>:<port>
LLM_MODEL=<LLM_MODEL จากตาราง>
LLM_API_KEY=<key>
```

## 3) กติกา

- ห้ามแสดง API key ของ Vast.ai หรือของ server บนจอ
- ห้ามขึ้นราคาเกิน `MAX_DPH` และห้ามลบเครื่องที่ใช้งานได้โดยไม่ได้รับคำสั่ง
- รายงานทุกเครื่องที่สร้างและลบ
- จบงานสรุปเป็นตารางภาษาไทย: เครื่อง (GPU · $/ชม. · ที่ตั้ง) · โมเดล · เวลา build / โหลด / เปิด server · ผลทดสอบ · VRAM · ไฟล์ `chatbot.env` เขียนแล้ว
