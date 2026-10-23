# เฉลย · เปิด Qwen บน Vast.ai RTX 5090 ด้วย NInfer (สิ่งที่ AI ทำจริงในพรอมต์ ④)

> ใช้เมื่อพรอมต์ ④ ไม่สำเร็จ — ส่งไฟล์นี้ให้ `yolo1` อ่านพร้อม skill `vastai` ได้เลย: `ใช้ skill vastai ทำตาม 00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra/_solution/vast_qwen/README.md`
> ทดสอบจริง 23 ต.ค. 2026 · NInfer commit `64d10fbf` (branch `master`) · ตั้งแต่เช่าจนใช้ได้ ~8 นาที

## 1) เช่าเครื่อง (skill `vastai`)

| เงื่อนไข | ค่า |
|---|---|
| GPU | `RTX_5090` × 1 · ป้าย `bm-qwen-5090` · เพดาน **$1.20/ชม.** |
| driver | รองรับ CUDA ≥ 13.4 (README ของ NInfer รับรอง 13.4) |
| เน็ต | ดาวน์โหลด ≥ 2000 Mbps (โมเดล 23.7 GB) |
| image · disk | `nvidia/cuda:13.4.1-devel-ubuntu24.04` · 90 GB |
| พอร์ต | Docker options `-p 8080:8080` |

เครื่องค้าง `loading` เกิน ~10 นาที หรือขึ้น `Failed to connect to cloud.vast.ai` → ลบแล้วเช่าเครื่องใหม่จาก host อื่น

## 2) build NInfer + โหลดโมเดลพร้อมกัน (บนเครื่องที่เช่า)

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq git cmake ninja-build pkg-config build-essential python3-pip \
  libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libcurl4-openssl-dev libhwloc-dev liburing-dev
pip install -q --break-system-packages -U "huggingface_hub[hf_xet]"
mkdir -p /workspace/models
HF_XET_HIGH_PERFORMANCE=1 hf download neroued/Qwen3.8-27B-nvfp4-NInfer qwen3_8_27b_nvfp4.ninfer \
  --local-dir /workspace/models > /workspace/download.log 2>&1 &
git clone -q https://github.com/Neroued/ninfer.git /workspace/ninfer && cd /workspace/ninfer
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build -j"$(nproc)"
wait
```

ใช้เวลาจริง: build 154 วิ · โหลดโมเดล 91 วิ (ขนานกัน)

## 3) เปิด server

```bash
head -c 24 /dev/urandom | xxd -p > /workspace/.api_key && chmod 600 /workspace/.api_key   # ห้ามพิมพ์ key บนจอ
cd /workspace/ninfer
setsid nohup ./build/apps/ninfer-serve /workspace/models/qwen3_8_27b_nvfp4.ninfer \
  --host 0.0.0.0 --port 8080 --api-key "$(cat /workspace/.api_key)" --model-id qwen3.8-27b \
  --max-context 16384 --kv-capacity 65536 --max-concurrency 4 --kv-dtype fp8 \
  --spec mtp --draft-tokens 3 --no-thinking \
  > /workspace/ninfer.log 2>&1 < /dev/null &
until curl -sf localhost:8080/health; do sleep 3; done
```

| flag | ทำไม |
|---|---|
| `--max-concurrency 4` + `--kv-capacity 65536` | รับพร้อมกัน 4 คน คนละ 16k token (ค่าเริ่มต้นของ kv-capacity = max-context ซึ่งต้องแบ่งกันทั้ง 4 คน) · ตรงกับ `prefetch=4` ของ chat-worker |
| `--spec mtp --draft-tokens 3` | เดาคำล่วงหน้า → เร็วขึ้น |
| **ไม่ใส่** `--lm-head-draft` | กับภาษาไทย draft ถูกรับแค่ 6–9% (~80 tok/s) · ถอดออกได้ 28–37% (~123 tok/s) |
| `--no-thinking` | ตอบไว ไม่คิดยาว (เช็คได้จาก `reasoning_tokens=0`) |

## 4) ทดสอบ + เขียน `.env.vast`

หา public IP และพอร์ตภายนอกที่ map กับ `8080/tcp` แล้วถามภาษาไทยผ่าน `POST /v1/chat/completions` (header `Authorization: Bearer <key>` · `model: qwen3.8-27b`) จากนอกเครื่อง · เขียน 3 บรรทัด (ไม่มี quote ไม่มี comment) ลง `04_Multi_Agent_Orchestra/.env.vast`:

```text
LLM_BASE_URL=http://<ip>:<port>/v1
LLM_MODEL=qwen3.8-27b
LLM_API_KEY=<key>
```

ผลที่ได้: VRAM 24.1/32.6 GB · ~123 token/วินาที ต่อคน · เริ่มตอบ ~0.65 วิ · ยิงพร้อมกัน 4 รวม ~258 token/วินาที

## 5) เสร็จแล้วลบเครื่องเสมอ

`ใช้ skill vastai ลบเครื่อง bm-qwen-5090 แล้วยืนยันว่าไม่มีเครื่องเหลือ พร้อมสรุปค่าใช้จ่าย` — **stop ยังเสียค่า disk** ต้อง destroy
