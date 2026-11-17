# RECIPE — LAB 4 · Fine-tune VLM อ่านใบเสร็จด้วย LoRA แล้วเปิด AI server บน Vast.ai

ไฟล์นี้เขียนให้ **AI อ่านแล้วทำตามเอง** ด้วยสกิล `vastai` · ผู้เรียนไม่ต้องรันคำสั่งใดเอง
AI สั่งงานผ่าน `docker exec multi-account …` และ ssh ไปยังเครื่องที่เช่า · สคริปต์ทั้งหมดอยู่ใน `lab4_vlm/scripts/` แล้ว **ไม่ต้องเขียนสคริปต์ใหม่**

คำถามของการทดลอง: VLM รุ่นเล็ก (`Qwen/Qwen3-VL-2B-Instruct`) อ่านใบเสร็จแล้วตอบเป็น JSON ได้แม่นแค่ไหน และ Fine-tune ด้วย LoRA บนใบเสร็จ 800 ใบช่วยเพิ่มความแม่นเท่าไร

แหล่งอ้างอิง: dataset [naver-clova-ix/cord-v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2) (CC BY 4.0 · Training 800 / Validation 100 / Test 100) · โมเดล [Qwen/Qwen3-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) (Apache-2.0) · ตรวจกับต้นทาง 18 พ.ย. 2026

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `LABEL` | `lab4-vlm` | ป้ายของเครื่องบน Vast.ai — **ทำงานกับเครื่องที่ป้ายตรงนี้เท่านั้น ห้ามแตะเครื่องอื่นในบัญชี** |
| `MAX_DPH` | `1.00` | เพดานราคารวม $/ชม. — **ห้ามขึ้นเกินนี้เอง** ถ้าไม่มีเครื่องให้หยุดแล้วรายงาน |
| `MAX_HOURS` | `3` | เครื่องเปิดได้นานสุดกี่ชั่วโมง ถ้าเกินให้เก็บผลเท่าที่มีแล้วรายงาน |

## 1) ไฟล์ที่ใช้

| ไฟล์ใน `lab4_vlm/scripts/` | หน้าที่ |
|---|---|
| `receipt_common.py` | พรอมต์ · schema เป้าหมาย · การให้คะแนน (ใช้ร่วมกันทุกสคริปต์) |
| `setup.sh` | ติดตั้ง library · โหลดโมเดล · เรียก `prepare_data.py` |
| `prepare_data.py` | โหลด CORD-v2 → ย่อภาพด้านยาวไม่เกิน 1280 px → `data/{train,validation,test}.jsonl` |
| `train.py` | เทรน LoRA (rank 8, 2 Epoch) → `out/adapter/` + `out/train_log.json` |
| `serve.sh` | เปิด vLLM เสิร์ฟ 2 ชื่อโมเดล: `receipt-base` (โมเดลเดิม) และ `receipt-ft` (โมเดลเดิม + LoRA) |
| `eval.py` | วัดผลบน Test Set 100 ใบผ่าน AI server ทีละใบ → `out/pred_<tag>.jsonl` + `out/metrics_<tag>.json` |
| `report.py` | รวมเป็น `out/metrics.json` และวาด `compare.png` `loss.png` `example_1..4.png` |

schema ที่ให้โมเดลตอบ (ใบเสร็จ 1 ใบ = JSON 1 ก้อน):

```json
{"items":[{"name":"...","qty":1,"price":25000}],"subtotal":25000,"tax":null,"total":25000}
```

## 2) ขั้นตอน

ทำให้จบในรอบเดียว · งานที่นานให้รันแบบเบื้องหลังบนเครื่องที่เช่า (`setsid nohup … > log 2>&1 < /dev/null &`) แล้วรอด้วยลูปตรวจ log เช่น `until grep -q SETUP_DONE setup.log; do sleep 15; done` (ตั้ง timeout ของคำสั่งให้พอ และดู log ถ้านานผิดปกติ)

### 2.1 เช่าเครื่อง

- GPU `RTX_4090` หรือ `RTX_5090` 1 ใบ (VRAM ≥ 24 GB) · verified · ssh แบบ direct · `inet_down>=1000` · `reliability>0.99` · ราคารวมกับ disk 60 GB ไม่เกิน `MAX_DPH` · เลือกเครื่องที่ถูกที่สุดที่ผ่านเงื่อนไข โดยดูค่าดาวน์โหลดต่อ GB (`inet_down_cost`) ด้วย เพราะงานนี้ดาวน์โหลดราว 11 GB
- image `vastai/base-image:@vastai-automatic-tag` · disk 60 GB · เปิดพอร์ต `--env '-p 8000:8000'` · `--label LABEL`
- กุญแจ ssh: `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` (ใน container `multi-account`)
- เครื่องค้าง `loading` เกิน 10 นาที หรือสถานะ `exited` `offline` `unknown` → ลบแล้วเช่าจาก host อื่น
- **ทดสอบความเร็วโหลดทันทีที่ ssh เข้าได้** (ค่า `inet_down` ที่โฆษณาไม่รับประกันความเร็วไปยัง Hugging Face):

```bash
# คำสั่งอ้างอิง — ต้องได้มากกว่า 20 MB/s (20000000 B/s) ถ้าช้ากว่านี้ให้ลบเครื่องแล้วเช่าจาก host อื่น
curl -sL -o /dev/null -w '%{speed_download} B/s\n' --max-time 8 \
  https://huggingface.co/datasets/naver-clova-ix/cord-v2/resolve/main/data/test-00000-of-00001-9c204eb3f4e11791.parquet
```

- มีได้ครั้งละ 1 เครื่อง
- คำสั่ง `vastai create instance … --raw` พิมพ์ `instance_api_key` ออกมาด้วย ให้กรองบรรทัดนั้นทิ้ง (เช่น ต่อท้ายด้วย `| grep -v api_key`)

### 2.2 ส่งสคริปต์และเตรียมเครื่อง (~2–5 นาที)

- คัดลอก `lab4_vlm/scripts/` ของโฟลเดอร์ปัจจุบันเข้า container (`docker cp` → `/workspace/vastapp_lab/lab4_vlm/scripts/`) แล้ว `scp` ไฟล์ทั้งหมดไปที่ `/workspace/lab4/` บนเครื่องที่เช่า
- `HF_TOKEN` อ่านจากไฟล์ `.env` ของโฟลเดอร์ปัจจุบัน ส่งเป็น environment ของคำสั่ง ssh เท่านั้น — **ห้ามแสดงค่าบนจอและห้ามเขียนลงไฟล์**

```bash
# คำสั่งอ้างอิง (บนเครื่องที่เช่า)
cd /workspace/lab4 && HF_TOKEN=<token> setsid nohup bash setup.sh > setup.log 2>&1 < /dev/null &
```

ตรวจผ่าน: `setup.log` ลงท้ายด้วย `SETUP_DONE` · `data/images/` มี 1000 ไฟล์ · log แจ้ง `train: 800 ใบ` `validation: 100 ใบ` `test: 100 ใบ`

### 2.3 เทรน LoRA (~7 นาทีบน RTX 4090 · ใช้ VRAM ราว 11 GB)

```bash
# คำสั่งอ้างอิง
cd /workspace/lab4 && . /workspace/venv/bin/activate && mkdir -p out
setsid nohup python train.py --data data --out out > train.log 2>&1 < /dev/null &
```

ตรวจผ่าน: `train.log` มีบรรทัด `เสร็จ:` · มี `out/adapter/adapter_model.safetensors` · validation loss หลัง Epoch สุดท้ายต่ำกว่าก่อนเทรน

### 2.4 เปิด AI server

- API key ของ server: สุ่ม 48 ตัวอักษร hex เก็บที่ `/workspace/receipt_api_key.txt` บนเครื่องที่เช่า (`openssl rand -hex 24`) — **ห้ามแสดงบนจอ**

```bash
# คำสั่งอ้างอิง
cd /workspace/lab4 && . /workspace/venv/bin/activate && bash serve.sh /workspace/lab4/out/adapter
# รอจนพร้อม (ราว 3 นาที: โหลดโมเดล + เตรียม engine)
curl -sf localhost:8000/health && curl -s localhost:8000/v1/models -H "Authorization: Bearer $(cat /workspace/receipt_api_key.txt)"
```

ตรวจผ่าน: `/v1/models` มีทั้ง `receipt-base` และ `receipt-ft`

### 2.5 วัดผล Base และ Fine-tuned บน Test Set (~1–2 นาทีต่อโมเดล)

พรอมต์เดียวกัน ภาพเดียวกัน server เดียวกัน ต่างกันแค่ชื่อโมเดล

```bash
# คำสั่งอ้างอิง
cd /workspace/lab4 && . /workspace/venv/bin/activate && export RECEIPT_API_KEY="$(cat /workspace/receipt_api_key.txt)"
python eval.py --model receipt-base --tag base --data data --out out
python eval.py --model receipt-ft   --tag ft   --data data --out out
python report.py --data data --out out
```

ตัวชี้วัด (ทั้งหมดวัดบน Test Set 100 ใบ ซึ่งไม่ได้ใช้เทรน):

| ตัวชี้วัด | ความหมาย |
|---|---|
| `json_ok_pct` | ร้อยละของคำตอบที่ parse เป็น JSON ตาม schema ได้ (ตัดเครื่องหมาย ```` ```json ```` ที่ครอบคำตอบออกก่อน) |
| `total_exact_pct` | ร้อยละของใบที่ยอดรวม (total) ตรงเฉลยทุกหลัก — คิดจากใบที่เฉลยมียอดรวม (95 จาก 100 ใบ) |
| `item_f1_pct` | F1 ของรายการสินค้า — รายการถูกเมื่อ **ชื่อและราคา** ตรงเฉลยทั้งคู่ (micro F1 รวมทุกใบ) |
| `sec_per_receipt` | เวลาเฉลี่ยต่อใบ (วินาที) |

### 2.6 ทดสอบจากนอกเครื่อง แล้วเขียนค่าเชื่อมต่อ

- หา public IP และพอร์ตภายนอกที่ map กับ `8000/tcp` → `URL=http://<ip>:<port>`
- ทดสอบจาก container `multi-account`: `GET $URL/v1/models` พร้อม header `Authorization: Bearer <key>` ต้องเห็นทั้งสองโมเดล
- เขียนไฟล์ `/workspace/vastapp_lab/lab4_vlm/receipt.env` ใน container แล้วคัดลอกมาไว้ที่ `lab4_vlm/web/receipt.env` ของโฟลเดอร์ปัจจุบัน (`docker cp`) · 4 บรรทัด ไม่มีเครื่องหมายคำพูด ไม่มี comment และไม่แสดงค่า key บนจอ

```text
RECEIPT_BASE_URL=http://<ip>:<port>
RECEIPT_API_KEY=<key>
RECEIPT_MODEL_BASE=receipt-base
RECEIPT_MODEL_FT=receipt-ft
```

### 2.7 เก็บผลกลับ (ก่อนลบเครื่องเสมอ)

`scp` จากเครื่องที่เช่า → container → `docker cp` มาที่โฟลเดอร์ปัจจุบัน

| จากเครื่องที่เช่า (`/workspace/lab4/`) | ปลายทางในโฟลเดอร์ปัจจุบัน |
|---|---|
| `out/metrics.json` `out/metrics_base.json` `out/metrics_ft.json` `out/train_log.json` | `lab4_vlm/results/` |
| `out/pred_base.jsonl` `out/pred_ft.jsonl` `out/example_ids.json` | `lab4_vlm/results/` |
| `out/compare.png` `out/loss.png` `out/example_*.png` | `lab4_vlm/results/` |
| `train.log` `setup.log` | `lab4_vlm/results/logs/` |
| `out/adapter/` (LoRA adapter ราว 35 MB) | `lab4_vlm/adapter/` |

**ไม่ลบเครื่องในขั้นนี้** — AI server ต้องเปิดอยู่ให้เว็บใช้ต่อ

## 3) เปิดเว็บ (พรอมต์ที่ 2)

- เว็บรันบน Docker ของเครื่องผู้ใช้ (ไม่ใช่ใน container `multi-account`): ในโฟลเดอร์ `lab4_vlm/web/` สั่ง `docker compose up -d --build` แล้วเปิด `http://localhost:3404`
- ต้องมี `lab4_vlm/web/receipt.env` จากข้อ 2.6 ก่อน · ตรวจ `GET http://localhost:3404/api/status` ต้องได้ `{"ok":true,"base":true,"ft":true}`
- ทดสอบอ่านใบเสร็จตัวอย่างผ่าน API ของเว็บ (`POST /api/read` ด้วยภาพจาก `lab4_vlm/web/public/samples/` ทั้งโมเดล `base` และ `ft`) แล้วรายงานผลเทียบเฉลยใน `samples.json`

## 4) ลบเครื่อง (พรอมต์ที่ 3)

- ก่อนลบ: ตรวจว่าไฟล์ในข้อ 2.7 อยู่ครบในโฟลเดอร์ปัจจุบัน · จดเวลาที่เครื่องเปิด (`duration` หรือ `start_date`) และ `dph_total` ของเครื่อง
- ลบเฉพาะเครื่องที่ป้ายตรง `LABEL` (`vastai destroy instance <id> -y`) แล้วตรวจ `vastai show instances` ว่าไม่มีป้ายนี้เหลือ
- ค่าใช้จ่าย: ดูจาก `vastai show invoices-v1 --charges` ของเครื่องนั้น ถ้ารายการยังไม่ขึ้นให้ประมาณจาก ชั่วโมงที่เปิด × `dph_total` และบอกว่าเป็นค่าประมาณ
- ปิดเว็บ: ในโฟลเดอร์ `lab4_vlm/web/` สั่ง `docker compose down -v`

## 5) กติกา

- ห้ามแสดง API key ของ Vast.ai, `HF_TOKEN` หรือ key ของ AI server บนจอ
- ห้ามขึ้นราคาเกิน `MAX_DPH` · ห้ามแตะเครื่องที่ป้ายไม่ตรง `LABEL` · ห้ามลบเครื่องที่ใช้งานได้โดยไม่ได้รับคำสั่ง (ยกเว้น host ที่โหลดช้าในข้อ 2.1)
- ห้ามแต่งตัวเลข — รายงานตาม `metrics.json` เท่านั้น
- รายงานทุกเครื่องที่สร้างและลบ
- จบพรอมต์ที่ 1 สรุปเป็นตารางภาษาไทย:

| หัวข้อ | สิ่งที่รายงาน |
|---|---|
| เครื่อง | GPU · $/ชม. · ที่ตั้ง |
| เวลา | เตรียมเครื่อง / เทรน / วัดผล Base / วัดผล Fine-tuned (นาที) |
| การเทรน | จำนวนพารามิเตอร์ที่เทรน · validation loss ก่อน → หลัง · VRAM สูงสุด |
| ผล Base vs Fine-tuned | `json_ok_pct` · `total_exact_pct` · `item_f1_pct` · `sec_per_receipt` ของทั้งสองโมเดล |
| AI server | โมเดลที่เปิด · ทดสอบจากนอกเครื่องผ่านหรือไม่ · `receipt.env` เขียนแล้ว |
| ไฟล์ที่เก็บกลับ | รายการไฟล์ใน `lab4_vlm/results/` และ `lab4_vlm/adapter/` |
