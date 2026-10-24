# เฉลย · เปิด ai-box (หู + ปาก + จัดอันดับ) บน Vast.ai RTX 4090 × 2

> ใช้เมื่อพรอมต์เปิด GPU-2/GPU-3 ไม่สำเร็จ — ส่งไฟล์นี้ให้ `yolo1` อ่านพร้อม skill `vastai` ได้เลย: `ใช้ skill vastai ทำตาม 00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra/_solution/vast_aibox/README.md`
> โค้ด: `server.py` (FastAPI ตัวเดียว) · `Dockerfile` · `requirements.txt` · `voices/nongchang.wav` + `.txt` (เสียงมาสคอต) · `bench.py` (วัดผล) · `make_voice_fixtures.py` (เสียงลูกค้าสำหรับ e2e)
> **ตัวเลขทั้งหมดในไฟล์นี้วัดบน RTX 5090 ในเครื่อง** (Windows + Docker Desktop/WSL2, 23 ต.ค. 2026) ด้วยอิมเมจเดียวกัน — ยังไม่ได้วัดบน 4090 จริง (ดูข้อ 6)

## 0) แบ่งงานยังไง

| เครื่อง | ป้าย | `MODELS` | โหลดอะไร | VRAM ที่ใช้ (วัด) |
|---|---|---|---|---|
| 👂 GPU-2 | `bm-stt-4090` | `stt` | faster-whisper `large-v3` float16 | ~4.8 GB |
| 🗣️ GPU-3 | `bm-voice-4090` | `tts,rerank` | VoxCPM2 (เสียง "น้องช่าง") + `BAAI/bge-reranker-v2-m3` | ~8.3 GB (peak ~8.8 GB) |
| (เครื่องเรา) | – | `all` | ทั้ง 3 ตัวในใบเดียว | ~13.1 GB |

ทั้ง 2 เครื่องใช้ **โค้ดชุดเดียว พอร์ตเดียว (8090) key เดียวกัน** ต่างกันแค่ `MODELS`

API (ทุกตัวยกเว้น `/health` ต้องมี `Authorization: Bearer <key>`):
`GET /health` · `POST /v1/audio/transcriptions` (multipart `file`, `language`) · `POST /v1/audio/speech` (`{input, voice:"nongchang"}` → wav 16-bit 48 kHz) · `POST /v1/rerank` (`{query, documents, top_n}`)

## 1) เช่าเครื่อง (skill `vastai`) — ทำ 2 เครื่อง

| เงื่อนไข | ค่า |
|---|---|
| GPU | `RTX_4090` × 1 · ป้าย `bm-stt-4090` และ `bm-voice-4090` · เพดาน **$0.50/ชม.** ต่อเครื่อง |
| driver | `cuda_max_good >= 12.8` (driver ≥ 570 · อิมเมจใช้ CUDA 12.8) |
| เน็ต | ดาวน์โหลด ≥ 500 Mbps (โมเดลรวม ~3 GB / ~7 GB) · `reliability > 0.98` |
| image · disk | `pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime` · **50 GB** |
| พอร์ต | Docker options `-p 8090:8090` |

เครื่องค้าง `loading` เกิน ~10 นาที → ลบแล้วเช่าใหม่จาก host อื่น

## 2) ติดตั้ง (ทำเหมือนกันทั้ง 2 เครื่อง)

คัดลอกโฟลเดอร์ `_solution/vast_aibox/` ไปที่ `/workspace/aibox` (เช่น `scp -P <ssh_port> -r vast_aibox root@<ssh_host>:/workspace/aibox` หรือ `vastai copy`) แล้ว:

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq ffmpeg curl gcc libc6-dev     # gcc: torch.compile ของ VoxCPM2 ต้องใช้
cd /workspace/aibox
# ล็อก torch/torchaudio ตามอิมเมจ (กัน pip ลง torch ตัวอื่นทับ)
python -c "import torch,torchaudio,torchvision;v=lambda m:m.__version__.split('+')[0];print(f'torch=={v(torch)}\ntorchaudio=={v(torchaudio)}\ntorchvision=={v(torchvision)}')" > /tmp/c.txt
pip install -q -r requirements.txt -c /tmp/c.txt
SP=$(python -c "import site;print(site.getsitepackages()[0])")
echo "export LD_LIBRARY_PATH=$SP/nvidia/cublas/lib:$SP/nvidia/cudnn/lib:\$LD_LIBRARY_PATH" >> ~/.bashrc   # CTranslate2 หา cuBLAS/cuDNN
```

> ขั้นตอนนี้ตรงกับ `Dockerfile` ที่ build และรันจริงในเครื่อง (pip ~3 นาที) · ถ้าเครื่องมี Docker ใช้ `docker build -t aibox . && docker run --gpus all -p 8090:8090 -v aibox-hf:/hf -e MODELS=... -e AIBOX_API_KEY=... aibox` แทนได้

## 3) เปิด server

สร้าง key **ครั้งเดียวบนเครื่องแรก** แล้วใช้ key เดียวกันกับอีกเครื่อง (ห้ามพิมพ์ key บนจอ):

```bash
head -c 24 /dev/urandom | xxd -p > /workspace/.aibox_key && chmod 600 /workspace/.aibox_key
source ~/.bashrc && cd /workspace/aibox
# GPU-2 (bm-stt-4090):   MODELS=stt
# GPU-3 (bm-voice-4090): MODELS=tts,rerank
MODELS=stt AIBOX_API_KEY="$(cat /workspace/.aibox_key)" HF_HOME=/workspace/hf \
  setsid nohup uvicorn server:app --host 0.0.0.0 --port 8090 > /workspace/aibox.log 2>&1 < /dev/null &
until curl -sf localhost:8090/health; do sleep 5; done; echo
```

| สิ่งที่ควรเห็น | เวลาโหลด (วัด) |
|---|---|
| `{"status":"ok","models":{"stt":"ok","tts":"disabled","rerank":"disabled"},...}` | stt ~10 วิ (+ดาวน์โหลด 3 GB ครั้งแรก) |
| `{"status":"ok","models":{"stt":"disabled","tts":"ok","rerank":"ok"},"voices":["nongchang"]}` | rerank ~5 วิ · tts **75–95 วิ** (torch.compile) |

ระหว่างโหลด `/health` ตอบ 503 `status:"loading"` — รอได้ ไม่ใช่ error

env ที่ปรับได้: `WHISPER_MODEL` (`large-v3`/`large-v3-turbo`) · `WHISPER_COMPUTE` (`float16`/`int8_float16`) · `STT_MAX_BATCH` (8) · `STT_BEAM` (5) · `TTS_TIMESTEPS` (10) · `TTS_COMPILE` (1)

## 4) ทดสอบจากนอกเครื่อง + เขียน `.env.aibox`

หา public IP และพอร์ตภายนอกที่ map กับ `8090/tcp` ของแต่ละเครื่อง แล้วทดสอบจากเครื่องเรา:

```bash
K=$(cat key-file)    # อย่า echo
curl -s http://<ip_stt>:<port_stt>/health
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://<ip_stt>:<port_stt>/v1/rerank      # ไม่มี key → 401
curl -s -H "Authorization: Bearer $K" -F file=@V01.wav -F language=th http://<ip_stt>:<port_stt>/v1/audio/transcriptions
printf '{"input":"สวัสดีครับ ผมน้องช่าง","voice":"nongchang"}' > /tmp/t.json
curl -s -H "Authorization: Bearer $K" -H 'content-type: application/json' --data-binary @/tmp/t.json \
  http://<ip_voice>:<port_voice>/v1/audio/speech -o hello.wav      # ภาษาไทยใน JSON ส่งผ่านไฟล์ (Git Bash บน Windows ส่ง -d ไทยเพี้ยน)
printf '{"query":"สีทาภายนอกรับประกันกี่ปี","documents":["เหล็ก DB12","สีภายนอกรับประกัน 5 ปี"],"top_n":1}' > /tmp/r.json
curl -s -H "Authorization: Bearer $K" -H 'content-type: application/json' --data-binary @/tmp/r.json http://<ip_voice>:<port_voice>/v1/rerank
```

เขียน **4 บรรทัด** (ไม่มี quote ไม่มี comment) ลง `04_Multi_Agent_Orchestra/.env.aibox`:

```text
STT_URL=http://<ip_stt>:<port_stt>
TTS_URL=http://<ip_voice>:<port_voice>
RERANK_URL=http://<ip_voice>:<port_voice>
AIBOX_API_KEY=<key>
```

## 5) ผลวัด (RTX 5090 ในเครื่อง · รายละเอียดทั้งหมดใน `bench.json`)

### Whisper: large-v3 vs large-v3-turbo (FLEURS th_th test 25 คลิป = 300 วิ · en_us 5 คลิป · beam 5)

| โมเดล | compute | CER ไทย | วิ/คลิป ไทย (คลิปเฉลี่ย 12 วิ) | WER อังกฤษ |
|---|---|---|---|---|
| **large-v3** ✅ | **float16** | **7.6%** | 1.78 | 10.9% |
| large-v3 | int8_float16 | 8.1% | 2.31 | 9.9% |
| large-v3-turbo | float16 | 13.1% | 0.61 | 10.9% |
| large-v3-turbo | int8_float16 | 13.7% | 0.69 | 10.9% |

เลือก **large-v3 float16**: turbo เร็วกว่า ~2.9 เท่า แต่ CER ไทยแย่กว่า 5.5 จุด (สัมพัทธ์ +72%) — ไม่ใช่ช่องว่างเล็ก · float16 ทั้งเร็วกว่าและแม่นกว่า int8 บนการ์ดนี้
(CER: NFKC, ตัดช่องว่าง/วรรคตอน, สะกดตัวเลขเป็นคำทั้งสองฝั่ง · ผ่าน API จริง: CER 8.4% ทั้งแบบทีละคลิปและยิงพร้อมกัน 8)

> บทเรียน: ค่า `compression_ratio_threshold=2.4` ของ Whisper ตั้งไว้สำหรับภาษาละติน — ข้อความไทย (UTF-8 3 ไบต์/ตัว) มีค่า 1.4–2.7 ตามธรรมชาติ ทำให้ถูกมองว่า "วนซ้ำ" แล้วถอดใหม่ด้วย temperature → ช้า 2 เท่าและสุ่ม · server ใช้ 3.3 สำหรับไทย

### ความจุพร้อมกัน (closed-loop · latency = ส่ง → ได้ผลครบ)

| งาน | 1 | 2 | 4 | 6 | 8 | 12 | 16 | เป้า | รับได้ |
|---|---|---|---|---|---|---|---|---|---|
| STT คลิปไทย 5 วิ (p95, วิ) | 1.10 | 1.06 | 1.31 | 2.10 | 2.02 | 2.29 | 3.73 | ≤ 2 | **4** (8 = เส้นขอบ) · ~5.7 คลิป/วิ |
| TTS ไทย 1–2 ประโยค (p95 time-to-audio, วิ) | 1.51 | 2.55 | 4.78 | 35.4* | – | – | – | ≤ 4 | **2** (3 = 3.3–4.1 วิ) |
| rerank query + 20 passages (p95, วิ) | 0.055 | – | 0.108 | – | 0.167 | – | 0.42 | – | ~53 req/s |

STT ใช้ **micro-batch** (คำขอที่มาภายใน 25 ms รวมเป็น batch ≤ 8 → `encode`+`generate` ครั้งเดียว) — ก่อนทำ batch, ยิงพร้อมกัน 2 คลิป p95 = 7.6 วิ · VoxCPM2 ทำทีละงาน (CUDA graphs ของ torch.compile) งานที่เกินรอคิว → ตั้ง `prefetch` ของ stt-worker = 4, tts-worker = 2
\* ที่ 6 งานมีคำขอหนึ่งช้า 35 วิ (VoxCPM2 `retry_badcase` สร้างใหม่) — หางยาวแบบนี้เป็นเหตุผลให้คุมคิวด้วย prefetch

### VoxCPM2 (เสียง nongchang · bf16 · 10 steps · 48 kHz)

| | RTF | time-to-audio เฉลี่ย | ความยาวเสียงเฉลี่ย | ไป-กลับด้วย Whisper |
|---|---|---|---|---|
| ไทย 5 ประโยค | 0.23 | 1.18 วิ | 5.2 วิ | CER 2.5% |
| อังกฤษ 5 ประโยค | 0.21 | 1.01 วิ | 4.7 วิ | WER 6.3% |

ไม่ใช้ torch.compile: RTF ~1.0 (ช้ากว่า 5 เท่า) · ตัวเลขในประโยคไทย ("185 บาท", "DB12") อ่านถูก · ข้อผิดที่เหลือ: "ปอร์ตแลนด์→ปอดแลนด์", "notched→notch"

### rerank & VRAM

- rerank: p50 21 ms / p95 44 ms ต่อคำขอ (20 passages) · top-1 ถูก 5/5 คำถามทดสอบ
- VRAM (nvidia-smi − ค่าเดิมของเครื่อง ~2.4 GB): Whisper large-v3 fp16 ~4.8 GB · reranker ~1.2 GB · VoxCPM2 ~7.1 GB · รวม ~13.1 GB · peak ตอนโหลดผสม (2 STT + 2 TTS + 2 rerank) +0.5 GB

**สรุป 4090 24 GB:** รวมใบเดียวได้ (เหลือ ~10 GB) · แยก 2 ใบตามแบบ v3 เหลือเยอะ (stt ~19 GB, tts+rerank ~15 GB) — แยกเพราะ **compute** ไม่ใช่ VRAM: STT batch กับ TTS แย่ง GPU กันทำให้ทั้งคู่ช้า
VoxCPM2 ไม่หนักเกิน: 7 GB, เร็วกว่าเวลาจริง ~4.5 เท่า · ถ้า 4090 ช้ากว่าเป้า ลด `TTS_TIMESTEPS=6` หรือใช้ Nano-vLLM ของ VoxCPM (README ระบุ RTF ~0.13 บน 4090)

## 6) ข้อควรรู้

- วัดบน WSL2 ซึ่ง launch CUDA kernel ช้ากว่า Linux (~17 µs/GEMM เล็ก) — Whisper (CTranslate2) ไวต่อเรื่องนี้ บน Vast (Linux) ควรเร็วกว่าตาราง แต่ 4090 มี compute น้อยกว่า 5090 → **ให้รัน `bench.py --stage stt_server,conc` บนเครื่องจริงแล้วปรับ prefetch**
- เสียง `nongchang` = voice design ของ VoxCPM2 ("cheerful, friendly young Thai man ... hardware-store assistant", seed 13 · F0 กลาง ~174 Hz) แล้วใช้เป็นไฟล์อ้างอิงโคลน (reference + continuation) ทุกคำขอ → เสียงเดิมทุกครั้ง
- `voice` อื่นที่ไม่มีไฟล์ใน `voices/` + `instructions` = voice design (ใช้ทำเสียงลูกค้าใน `make_voice_fixtures.py`)

## 7) เสร็จแล้วลบเครื่องเสมอ

`ใช้ skill vastai ลบเครื่อง bm-stt-4090 และ bm-voice-4090 แล้วยืนยันว่าไม่มีเครื่องเหลือ พร้อมสรุปค่าใช้จ่าย` — **stop ยังเสียค่า disk** ต้อง destroy
