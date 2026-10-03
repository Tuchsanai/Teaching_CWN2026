# Deploy Clef-NVFP4 บน Vast.ai — คู่มือสร้างเครื่องใหม่

บันทึกจากการ deploy จริง 2026-10-02 · ใช้เวลาจริงตั้งแต่เช่าจนพร้อมใช้ **~12 นาที** ถ้าทำตามนี้ (รอบแรกเสียไป ~1.5 ชม. กับปัญหาด้านล่าง)

## TL;DR — คำสั่งเดียว

```bash
cd /root/workspace/CWN/Teaching/03_Jev_Application/clef
bash server/deploy_vast.sh              # เช่า → ส่งไฟล์ → start → รอจนพร้อม → พิมพ์ URL
# ปรับได้: MAX_DPH=0.8 MIN_INET=1000 LABEL=clef-5090-test bash server/deploy_vast.sh
```

เสร็จแล้วเปิด notebook ได้เลย — `clef_api_test.ipynb`, `clef_vision_benchmark.ipynb`, `jev_robotics_rl.ipynb` (A8)
หา direct URL เองจาก Vast API ด้วย label ที่ขึ้นต้น `clef-5090` (หรือตั้ง `CLEF_BASE_URL` ใน `clef/.env`)

**เลิกใช้ต้องลบเครื่องเสมอ** (stop ยังเสียค่า storage): `python /tmp/vast.py destroy --id <ID> --yes`

---

## 1. สิ่งที่ต้องมีฝั่งเครื่องเรา (local)

| ของ | ที่อยู่ / คำสั่ง |
|:--|:--|
| Vast API key + SSH key | `/root/workspace/DGX_2024/.env` → `VAST_API_KEY`, `VAST_SSH_KEY_FILE` (ผูก key กับบัญชีแล้ว) |
| Clef API key (Bearer ของ server เรา) | `clef/.env` → `CLEF_API_KEY` (สคริปต์สร้างให้ถ้ายังไม่มี) |
| TypeSafe key (Jev, ไม่เกี่ยวกับ Vast) | `/root/workspace/DGX_2024/.env` → `TYPESAFE_API_KEY` |
| toolkit `/tmp/vast.py` | สคริปต์ดึงจาก skill `vastai` ให้เอง (`/tmp` หายเมื่อ restart container) |

```bash
pip install 'vastai~=1.8'                       # SDK + CLI ของ Vast (ทดสอบ 1.8.2)
pip install typesafe-sdk                        # Jev — ใช้ใน jev_robotics_rl.ipynb (ทดสอบ 0.7.2)
pip install requests pillow pandas matplotlib numpy jupyter nbconvert nbformat   # สำหรับ notebook
```

## 2. สเปกเครื่องที่ใช้ได้ผล

| ค่า | ใช้ | เหตุผล |
|:--|:--|:--|
| GPU | **RTX 5090 (32 GB)** | NVFP4 ต้อง Blackwell; weight 20.2 GiB ใช้ VRAM รวม ~29 GiB |
| ราคา | ≤ $0.70/hr | นอกจีนที่เน็ต > 2000 Mbps ไม่มีต่ำกว่า $0.6 (ณ 2026-10-02 ได้ $0.63 ที่ Nevada US) |
| เน็ต | `--min-inet 2000` | image 11 GB + model 23 GB |
| ประเทศ | **ห้ามจีน** (skill ตัดให้แล้วด้วย `VAST_BLOCK_GEO=CN`) | huggingface.co ถูก block |
| CUDA driver | `--min-cuda 12.9` | image เป็น cu129 |
| disk | 80 GB | image ×2 + model + เผื่อ |
| port | `--env "-p 8000:8000"` | ได้ direct URL `http://<public_ip>:<HostPort>` |
| image | `vllm/vllm-openai:cu129-nightly-ac9126e58aa7bbab1856ba6593ba4d5003fea516` | vLLM 0.30.1rc1 — pin commit ไว้ (nightly เปลี่ยนทุกวัน) · ต้องมี `Qwen3_5ForConditionalGeneration` |

## 3. lib ที่ต้องลงบนเครื่อง Vast

image vLLM มี `vllm`, `torch`, `transformers`, `fastapi`, `uvicorn`, `safetensors`, `huggingface_hub` อยู่แล้ว
`start.sh` ทำเพิ่มแค่นี้ (ใช้ `python3` — image ไม่มีคำสั่ง `python`):

```bash
python3 -m pip uninstall -y torchcodec          # torchcodec ใน cu129-nightly build กับ CUDA 13 → import vllm พัง (OSError)
python3 -m pip install -q hf_transfer fastapi uvicorn pillow requests
export HF_HUB_ENABLE_HF_TRANSFER=1              # โหลด 23 GB เร็วขึ้นมาก (เจอจริง ~1 นาทีบนเครื่อง US)
```

ไฟล์ที่ต้องส่งขึ้นเครื่อง (`/workspace/`): `server.py`, `start.sh`, `server.env`
(`server.env` = `CLEF_API_KEY`, `CLEF_GPU_UTIL=0.88`, `CLEF_MAX_MODEL_LEN=16384`, `CLEF_MAX_NUM_SEQS=4` — สคริปต์สร้างให้แล้วลบทิ้งฝั่ง local)

## 4. ขั้นตอนแบบทำมือ (ถ้าไม่ใช้สคริปต์)

```bash
export VASTAI_ENV=/root/workspace/DGX_2024/.env VAST_LOADING_GRACE=1000
python /tmp/vast.py env && python /tmp/vast.py keys && python /tmp/vast.py sweep
python /tmp/vast.py rent --label clef-5090-x --gpu RTX_5090 --min-inet 2000 --max-dph 0.7 --min-cuda 12.9 \
    --disk 80 --image vllm/vllm-openai:cu129-nightly-ac9126e58aa7bbab1856ba6593ba4d5003fea516 --env "-p 8000:8000" --timeout 1500
ID=<instance_id จากผล rent>
python /tmp/vast.py run --id $ID --cmd 'curl -s -o /dev/null -w "%{http_code}\n" https://huggingface.co'   # ต้องได้ 200
for f in server/server.py server/start.sh server.env; do python /tmp/vast.py push --id $ID --src $f --dst /workspace/; done
python /tmp/vast.py run --id $ID --cmd '(setsid nohup bash /workspace/start.sh > /workspace/start.log 2>&1 < /dev/null &)'
python /tmp/vast.py watch --id $ID --file /workspace/server.log --ready "Application startup complete" --alive uvicorn --timeout 2400
curl http://<public_ip>:<HostPort ของ 8000/tcp>/health
```

## 5. เวลาที่ใช้จริง (เครื่อง US, 2026-10-02)

| ขั้น | เวลา |
|:--|--:|
| rent → running + SSH (pull image 11 GB) | ~4 นาที |
| โหลด model 23 GB (hf_transfer) | ~1 นาที |
| vLLM init + torch.compile + cudagraph | ~5 นาที |
| **รวม** | **~10–12 นาที** |

ค่าใช้จ่าย: GPU $0.60/hr + storage $0.03/hr **+ ค่า download ต่อ GB ของ host** (เครื่องนี้ $0.039/GB → โหลดครั้งแรก ~$0.97!)
→ ถ้าจะเช่าบ่อย ใส่ `--extra-query "inet_down_cost<0.01"` ใน `rent` (สคริปต์ยังไม่ได้ใส่ เพราะทำให้ offer น้อยลง)

## 6. ปัญหาที่เจอแล้ว — อาการ → วิธีแก้

| อาการ | สาเหตุ | แก้ (ทำในสคริปต์/ไฟล์แล้ว) |
|:--|:--|:--|
| `curl huggingface.co` ได้ `000` | เครื่องอยู่จีน, HF ถูก block | skill ตัดประเทศ `CN` อัตโนมัติ · ถ้าจำเป็น: `HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1` (ช้า ~17 MB/s) |
| mirror โหลดแล้ว `401 Unauthorized … cas-server.xethub.hf.co` | Xet storage ใช้กับ mirror ไม่ได้ | `HF_HUB_DISABLE_XET=1` |
| `rent` ลบเครื่องทิ้งตอนยัง `loading` | pull image 11 GB เกิน grace 420 s | `VAST_LOADING_GRACE=1000` |
| ค้าง `created`, `status_msg: Error response from daemon: failed to create task for container` | Docker ของ host เสีย | skill ตรวจ `status_msg` แล้วเปลี่ยนเครื่องให้ทันที |
| `torch.OutOfMemoryError … Tried to allocate 12.25 GiB` ตอน `profile_cudagraph_memory` | `max_num_seqs` default 256 × state ของ linear-attention | `max_num_seqs=4` ใน `server.py` (server ทำทีละ request อยู่แล้ว) |
| `OSError: Could not load this library: …libtorchcodec…` | torchcodec ใน image build กับ CUDA 13 | `pip uninstall -y torchcodec` ใน `start.sh` |
| `bash: python: command not found` | image มีแค่ `python3` | ใช้ `python3` ใน `start.sh` |
| `offer … หายไปแล้ว` | offer อายุสั้น | สคริปต์ลอง `rent` ซ้ำ 3 รอบ |
| ไม่มี offer ≤ $0.6 ที่เน็ต > 2000 นอกจีน | ตลาดตอนนั้น | `MAX_DPH=0.7` (default ของสคริปต์) หรือ `MIN_INET=1000` |

## 7. ทดสอบหลัง deploy

```bash
curl -s $URL/health                       # {"ok":true,"gpu":"NVIDIA GeForce RTX 5090","vram_used_gib":29.3,...}
```

แล้วรัน `clef_api_test.ipynb` ทั้งไฟล์ — ผลอ้างอิง: latency ฝั่ง server median ~125 ms (text) / ~200–300 ms (รูป), round-trip จากไทย ~0.7 s
