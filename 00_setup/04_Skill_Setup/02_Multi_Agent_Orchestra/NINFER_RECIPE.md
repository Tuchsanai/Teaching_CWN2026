# NINFER_RECIPE — เปิด AI server (NInfer + Qwen) บน Vast.ai RTX 5090 (ฉบับ LAB 04.2)

> ไฟล์นี้เขียนให้ **AI (`yolo1` + skill `vastai`) อ่านแล้วทำตามเอง** — นักศึกษาไม่ต้องรันสคริปต์ใด ๆ
> AI ต้องสร้างคำสั่ง/สคริปต์เองจาก "คำสั่งอ้างอิง" ด้านล่าง แล้วส่งไปรันบนเครื่องที่เช่าผ่าน skill `vastai` (`push` / `run`)
> ห้ามสร้างไฟล์ `.sh` ทิ้งไว้ใน repo · ไฟล์ชั่วคราวให้อยู่ใน `/tmp` ของ container หรือ `/workspace` ของเครื่องที่เช่า

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์ (ไม่ระบุ = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `MODEL` | `qwen3.8-27b-nvfp4` | รหัสโมเดลจากตารางข้อ 1 |
| `LABEL` | `bm-ninfer-5090` | ชื่อเครื่องบน Vast.ai |
| `OUT_ENV` | `<RUN>/.env.vast` (นอก git ทุก worktree อ่านได้) | ไฟล์ที่เขียนค่าเชื่อมต่อ (ข้อ 2.5) |
| `MAX_DPH` | `1.20` | เพดานราคา $/ชม. — **ห้ามขึ้นเกินนี้เอง** ถ้าไม่มี offer ให้ถามผู้ใช้ |

## 1) โมเดลที่เลือกได้ (ทั้งหมดใน Hugging Face ของ `neroued` ที่เป็น Qwen สำหรับ NInfer)

ทุกตัว: ต้องใช้ **RTX 5090 (32 GB, sm_120a) + CUDA 13.1 ขึ้นไป** · คำสั่ง `ninfer-serve` เหมือนกันหมด ต่างกันแค่ 3 ค่า (repo · ไฟล์ · ชื่อโมเดล)

| `MODEL` | HF repo | ไฟล์ `.ninfer` | `LLM_MODEL` (ชื่อใน API) | ขนาดไฟล์ | VRAM ที่ใช้ (ประมาณ) | จุดเด่น |
|---|---|---|---|---|---|---|
| `qwen3.8-27b-nvfp4` ⭐ | `neroued/Qwen3.8-27B-nvfp4-NInfer` | `qwen3_8_27b_nvfp4.ninfer` | `qwen3.8-27b` | 22.1 GiB | **20.7–24.4 GB (วัดจริง 2 ครั้ง)** | รุ่นใหม่สุด แม่นสุด (GPQA 90.4) · ค่าที่ทดสอบใน LAB |
| `qwen3.8-27b` | `neroued/Qwen3.8-27B-NInfer` | `qwen3_8_27b.ninfer` | `qwen3.8-27b` | 19.0 GiB | ~18 GB | รุ่นใหม่ ไฟล์เล็กกว่า (Q4/Q5) |
| `qwen3.6-27b` | `neroued/Qwen3.6-27B-NInfer` | `qwen3_6_27b.ninfer` | `qwen3.6-27b` | 16.3 GiB | ~15 GB | เล็กสุด โหลดเร็วสุด |
| `qwen3.6-27b-nvfp4` | `neroued/Qwen3.6-27B-nvfp4-NInfer` | `qwen3_6_27b_nvfp4.ninfer` | `qwen3.6-27b` | 17.1 GiB | ~16 GB | prefill เร็ว (NVFP4 บน Blackwell) |
| `qwen3.6-35b-a3b` | `neroued/Qwen3.6-35B-A3B-NInfer` | `qwen3_6_35b_a3b.ninfer` | `qwen3.6-35b-a3b` | 21.2 GiB | ~20 GB | MoE (ใช้งานจริงทีละ 3B) **ตอบเร็วสุด** |

- VRAM ≈ น้ำหนักโมเดล (ไม่รวมส่วน Vision ที่ไม่ได้โหลด) + KV cache ของ `--max-context 16384` · ตัวเลข "ประมาณ" คำนวณจากค่าจริงของ qwen3.8-27b-nvfp4 (ไฟล์ 22.1 GiB → ใช้จริง 20.7–24.4 GB) ยังไม่ได้วัดตัวอื่น ให้ AI รายงานค่าจริงจาก `nvidia-smi` หลัง server พร้อม
- ข้อมูลจาก model card บน Hugging Face (ตรวจ 15 ต.ค. 2026) — ถ้า repo เปลี่ยน ให้ AI เช็ค `https://huggingface.co/api/models?author=neroued` ก่อน

## 2) ขั้นตอน (AI ทำเองทั้งหมด)

### 2.1 เช่าเครื่อง
skill `vastai` เช่า 1 เครื่อง ตามเงื่อนไข:
- GPU `RTX_5090` · เพดาน `MAX_DPH` · ป้าย `LABEL`
- เน็ตดาวน์โหลด **≥ 2000 Mbps** (โมเดล ~20 GiB)
- image `nvidia/cuda:13.1.2-devel-ubuntu24.04` · disk **90 GB** · Docker options `-p 8080:8080`
- **ก่อนเช่า** ดู `vastai show instances` ถ้ามีเครื่องป้าย `LABEL` อยู่แล้วและ running → ใช้เครื่องเดิม ไม่เช่าซ้ำ (งานนี้อาจถูกเรียกซ้ำโดย orchestrator)
- ถ้าเครื่องค้าง `loading` เกิน ~10 นาที หรือ status ขึ้น `Failed to connect to cloud.vast.ai` (host เน็ตมีปัญหา) → **ลบเครื่องนั้นแล้วเช่าเครื่องใหม่จาก host อื่น** (เจอจริง 15 ต.ค. 2026)
- **ทำงานให้จบในรอบเดียว**: รอด้วย `sleep` + เช็คสถานะเป็นช่วง ๆ ห้ามจบงานไปก่อนแล้ว "ตั้งเวลากลับมาดู" (โหมด `-p` จะปิดตัวและงานเบื้องหลังหยุดตาม)

### 2.2 ติดตั้ง NInfer + โหลดโมเดล (บนเครื่องที่เช่า · ~8–10 นาที)
สร้างสคริปต์เองจากคำสั่งอ้างอิง แล้วรันแบบเบื้องหลัง (`nohup … &`) และคอยดู log ทุก ~60 วินาที เพราะนานเกิน timeout ของ ssh ครั้งเดียว
**ให้โหลดโมเดลพร้อมกับ build** (ทดสอบจริง: build 448 วิ · โหลด 128 วิ · รวม ~8 นาที)

```bash
# คำสั่งอ้างอิง — แทน <REPO> <FILE> ด้วยค่าจากตารางข้อ 1
export DEBIAN_FRONTEND=noninteractive
mkdir -p /workspace/ninfer/models && cd /workspace
apt-get update -qq && apt-get install -y -qq git cmake ninja-build pkg-config build-essential python3-pip \
  libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libcurl4-openssl-dev
pip install -q --break-system-packages -U "huggingface_hub[hf_xet]"

# โหลดโมเดล (เบื้องหลัง) — ข้ามถ้ามีไฟล์แล้ว
HF_XET_HIGH_PERFORMANCE=1 hf download <REPO> <FILE> --local-dir /workspace/ninfer/models > /workspace/download.log 2>&1 &

# clone + build (ข้ามถ้ามี build/apps/ninfer-serve แล้ว)
git clone -q https://github.com/Neroued/ninfer.git /tmp/n && cp -a /tmp/n/. /workspace/ninfer/
cd /workspace/ninfer && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release > /workspace/build.log 2>&1 \
  && cmake --build build -j"$(nproc)" >> /workspace/build.log 2>&1
wait   # รอโหลดโมเดลเสร็จ
```

ตรวจผ่าน: มีไฟล์ `/workspace/ninfer/build/apps/ninfer-serve` และ `/workspace/ninfer/models/<FILE>` ขนาดตรงตาราง

### 2.3 เปิด server (~15 วินาที)
- API key: สุ่มเอง 48 ตัวอักษร hex เก็บไว้ที่ `/workspace/ninfer_api_key.txt` บนเครื่องที่เช่า (มีแล้วใช้ของเดิม) — **ห้ามพิมพ์ key บนจอ**
- ใช้ `setsid nohup` ให้ server อยู่ต่อหลัง ssh หลุด แล้วรอจน `curl -sf localhost:8080/health` ผ่าน (สูงสุด 10 นาที ถ้า process ตายให้ดู `tail -30 /workspace/ninfer.log`)

```bash
# คำสั่งอ้างอิง
cd /workspace/ninfer
pkill -f ninfer-serve; sleep 3
setsid nohup ./build/apps/ninfer-serve models/<FILE> \
  --host 0.0.0.0 --port 8080 \
  --max-context 16384 --kv-capacity auto --max-concurrency 4 --kv-dtype fp8 \
  --spec mtp --draft-tokens 3 --lm-head-draft \
  --no-thinking --cors --api-key "$(cat /workspace/ninfer_api_key.txt)" \
  > /workspace/ninfer.log 2>&1 < /dev/null &
```

| flag | ทำไม |
|---|---|
| `--max-context 16384` | แชทบอทร้านวัสดุใส่รายการสินค้าใน prompt ได้พอ แต่ไม่ต้องยาวมาก → ประหยัด VRAM |
| `--max-concurrency 4` | รับลูกค้าพร้อมกันได้ 4 คน |
| `--spec mtp --draft-tokens 3 --lm-head-draft` | เดาคำล่วงหน้า → ตอบเร็วขึ้น ~2–3 เท่า |
| `--no-thinking` | ไม่ต้องให้โมเดล "คิดยาว" ก่อนตอบ → ตอบไวเหมาะกับแชท |
| `--cors --api-key` | ให้เว็บเรียกได้ แต่ต้องมี key |

### 2.4 ทดสอบจากนอกเครื่อง
- หา public IP และ HostPort ที่ map กับ `8080/tcp` → `URL=http://<ip>:<port>`
- ทดสอบ `GET $URL/health` และถามภาษาไทย 1 ข้อผ่าน `POST $URL/v1/chat/completions` (header `Authorization: Bearer <key>`, `model` = `LLM_MODEL` จากตาราง) เช่น "สวัสดีครับ ปูนซีเมนต์ถุงละเท่าไร"
- รายงาน: เวลาตอบ, token/วินาที, VRAM จริงจาก `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`

### 2.5 เขียนค่าเชื่อมต่อ
เขียนทับไฟล์ `OUT_ENV` ให้มี **3 บรรทัด ไม่มีเครื่องหมายคำพูด ไม่มี comment**:

```text
LLM_BASE_URL=http://<ip>:<port>
LLM_MODEL=<LLM_MODEL จากตาราง>
LLM_API_KEY=<key>
```

ห้ามแสดง key บนจอ (ใช้ `scp`/`cat` ลงไฟล์โดยตรง) · ไฟล์นี้ถูก ignore ไม่ถูก commit

## 3) กติกา

- ห้ามพิมพ์ `VAST_API_KEY` หรือ API key ของ server บนจอ
- ห้ามขึ้นเพดานราคาเกิน `MAX_DPH` และห้ามลบเครื่องเองโดยไม่ได้รับคำสั่ง
- ถ้า offer หาย / เครื่องไม่พร้อม ให้ skill ลองตัวใหม่ได้ (ปกติ) แต่รายงานทุกเครื่องที่สร้างและลบ
- จบงานสรุปเป็นตารางภาษาไทย: เครื่อง (GPU, $/ชม., เน็ต) · โมเดล · เวลา build/โหลด/start · ผลทดสอบ · VRAM จริง · ไฟล์ `.env.vast` เขียนแล้ว (ไม่แสดง key)
