---
name: cluster-vlm-train
description: เทรนโมเดล Vision-Language Qwen3-VL-8B-Instruct ด้วย LoRA ให้อ่านใบเสร็จ (Dataset CORD-v2) แล้วตอบเป็น JSON บนคลัสเตอร์หลายเครื่องที่เช่าจาก Vast.ai (เครื่องละ 2 GPU) ครบวงจรในคำสั่งเดียว — เช่า Node 1 → เตรียมโมเดลและ Dataset → (เลือกได้) หาขีดจำกัด VRAM → วัดความเร็ว 1 Node → เช่า Node 2… ต่อเข้าคลัสเตอร์ (โปรแกรมกลางเฉลี่ย Gradient แบบ Synchronous) → วัดความเร็วคลัสเตอร์ → เทรนจริงด้วยแนวทาง A (แบ่งโมเดล 1 ชุดลง GPU 2 ใบ) และ/หรือ B (GPU 1 ใบต่อโมเดล 1 ชุด) → Evaluation Base เทียบ Fine-tuned บน Test Set โดยแบ่งงานไปทุก GPU → ลบทุกเครื่องและสรุปค่าใช้จ่าย → ตาราง Speedup · Efficiency · เงินต่อ Epoch พร้อมกราฟ ใช้เมื่อผู้ใช้สั่ง "ใช้สกิล cluster-vlm-train", "เทรน VLM บนคลัสเตอร์หลายเครื่อง", "เทรนข้ามเครื่อง / multi-node", "VRAM ไม่พอจะเทรนอย่างไร", "เพิ่มเครื่องแล้วเร็วขึ้นกี่เท่า", "แนวทาง A เทียบ B", "ทำ LAB 5 ซ้ำ" หรือขอทำซ้ำด้วยรุ่น GPU / จำนวน Node / เพดานราคา / แนวทาง / Effective Batch / จำนวนใบที่เทรน / ป้ายเครื่อง / โฟลเดอร์ผลที่ต่างไปจากเดิม
---

# cluster-vlm-train (เวอร์ชัน 0)

ทำซ้ำงานของ LAB 5 ในคำสั่งเดียว ทุกงานที่แตะ Vast.ai (ค้นหาเครื่อง เช่า เปิดพอร์ต SSH คัดลอกไฟล์ ดูบิล ลบเครื่อง) **ให้ใช้สกิล `vastai`** ใน container `multi-account` (`/root/ai-accounts/.Claude/shared/skills/vastai/SKILL.md`) อ่านสกิลนั้นก่อนเริ่ม สกิลนี้ไม่อธิบายวิธีใช้ Vast.ai ซ้ำ บอกแค่ว่าต้องทำอะไร

โค้ดทั้งหมดใช้ชุดที่ผ่านการรันจริงแล้วในโฟลเดอร์ `scripts/` ข้างไฟล์นี้ **ห้ามเขียนใหม่** ถ้าต้องแก้จริง ๆ ให้แก้น้อยที่สุดและบอกในสรุป

| สคริปต์ | รันที่ | หน้าที่ |
|---|---|---|
| `receipt_data.py` | ทุก Node | `prepare` โหลด CORD-v2 (train 800 · val 100 · test 100) ย่อภาพด้านยาว ≤ 1280 px แปลงเฉลยเป็น JSON ลง `/workspace/lab5/data` · `samples` ทำภาพตัวอย่าง 6 ใบคู่เฉลย · เก็บ `PROMPT` ที่ใช้ทั้งเทรนและวัดผล |
| `setup_node2.sh` | ทุก Node | ติดตั้งแพ็กเกจรุ่นที่ใช้ได้แล้ว โหลดโมเดลลง `/workspace/models/Qwen3-VL-8B-Instruct` และเตรียม Dataset · อ่าน `HF_TOKEN` จาก stdin แล้วลบทิ้ง (ใช้ได้กับ Node 1 ด้วย ไม่จำกัดแค่ Node 2) |
| `vram_probe.py` | Node 1 | ลองเทรน 10 step ด้วยใบที่เฉลยยาวที่สุด วัด VRAM ต่อใบ / OOM · `--gpus 1|2 --batch --gc on|off --split --case` |
| `coordinator.py` | Node 1 (CPU) | โปรแกรมกลางพอร์ต 9000 รับเฉพาะ replica ที่มีรหัสลับ `/workspace/lab5/cluster_secret` · ทุกครั้งที่ปรับน้ำหนัก รับ Gradient LoRA (bf16) ของทุก replica → เฉลี่ย → ส่งกลับพร้อมกัน |
| `worker.py` | ทุก Node | replica 1 ตัว = โมเดล 1 ชุด · `--mode A --gpus 0,1` (แบ่ง 19/17 ชั้น ปิด GC) หรือ `--mode B --gpus 0|1` (เปิด GC) · ป้อนทีละใบ สะสม `--accum` ใบ · `--train-limit` · `--save-adapter` · บันทึกเวลา/VRAM/GPU util/checksum |
| `run_node1.sh` | Node 1 | วัดความเร็ว 1 Node · env `RUNS` (เช่น `"A_eb8 B_eb32"`) `STEPS` `WARMUP` `OUT` · replica: A = 1 · B = 2 |
| `net_probe.py` | Node 1 + Node อื่น | `server --port 9000` บน Node 1 · `client --host <ip ของ Node 1> --port <พอร์ตภายนอกของ 9000> --out net_probe.json` วัด TCP connect · RTT · ส่ง 7.6 MB ไป-กลับ |
| `run_2node.sh` | container | วัดความเร็วคลัสเตอร์ · env `NODES="ip:sshport ip:sshport …"` (ตัวแรก = Node 1) `COORD=<ip:พอร์ตภายนอกของ 9000>` `RUNS` `STEPS` `WARMUP` `SKIP` · replica: A = จำนวน Node · B = 2 × จำนวน Node |
| `run_train.sh` | container | เทรนจริงทีละแนวทาง · env `NODES` `COORD` `APPROACHES="A B"` `LIMIT` `EB` `EPOCHS` · จำนวนครั้งที่ปรับน้ำหนัก = `EPOCHS × LIMIT / EB` |
| `run_eval.sh` | container | วัดผล Test Set 100 ใบ แบ่ง 1 ส่วนต่อ GPU บนทุก Node แล้วให้คะแนนบน Node 1 · env `NODES` `MODELS=base,A,B` · ส่วนที่ตายจะถูกเปิดใหม่และทำต่อจากเดิม |
| `eval.py` | ทุก Node | `run --gpu --shard k/n --models` อ่านใบเสร็จแบบไม่สุ่ม · `report --models` ให้คะแนน JSON อ่านได้ · ยอดรวมตรง · Item F1 · วินาทีต่อใบ → `metrics.json` `predictions_*.jsonl` `images/accuracy_3models.png` `images/examples.jpg` |
| `compare_nodes.py` | เครื่องนี้ | `--raw <out_dir>/raw` ตาราง 1 Node เทียบคลัสเตอร์ → `raw/compare_nodes.json` |
| `summarize_train.py` | เครื่องนี้ | `<out_dir>` สรุปรอบเทรน → `raw/train_2node/summary.json` `losses.csv` |
| `report.py` | เครื่องนี้ | `--results <out_dir> --label-prefix <label> --train-set 800` → `metrics.json` และกราฟ 4 รูปใน `images/` (ส่วนที่ไม่มีผลดิบจะถูกข้าม · ต้องใช้ `matplotlib`) |

ที่เก็บไฟล์: บนทุก Node โค้ดอยู่ `/workspace/lab5/` (ใส่ `*.py` และ `setup_node2.sh` `run_node1.sh`) · ใน container สคริปต์ `run_2node.sh` `run_train.sh` `run_eval.sh` อยู่ `/workspace/vastapp_lab/lab5/` · ผลทั้งหมดเก็บบนเครื่องนี้ที่ `out_dir` ไม่ใช่ใน container

## ค่าที่ปรับได้ (ผู้ใช้ไม่บอก = ใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `gpu` | RTX 3090 | รุ่น GPU ทุก Node ใช้รุ่นเดียวกัน · **เครื่องละ 2 ใบเสมอ** (สคริปต์ใช้ GPU 0 กับ 1) · VRAM ต้อง ≥ 24 GB · ถ้า VRAM ไม่ใช่ 24 GB ให้ทำขั้น VRAM probe |
| `nodes` | 2 | จำนวน Node ในคลัสเตอร์ · 1 = วัดเส้นฐาน เทรน และวัดผลบนเครื่องเดียว ไม่มี Speedup · ผ่านการรันจริงแล้วที่ 1–2 Node (3 Node ขึ้นไปสคริปต์รองรับ แต่ยังไม่เคยรันจริง ต้องบอกผู้ใช้) |
| `max_price` | $0.60/ชม. **ต่อเครื่อง** | ราคารวมของแต่ละเครื่อง (GPU + disk) |
| `approach` | ทั้งคู่ (`A B`) | `A` = แบ่งโมเดล 1 ชุดลง GPU 2 ใบ ปิด Gradient Checkpointing (replica = จำนวน Node) · `B` = GPU 1 ใบต่อโมเดล 1 ชุด เปิด Gradient Checkpointing (replica = 2 × จำนวน Node) · ใช้ทั้งขั้นวัดความเร็ว เทรน และวัดผล |
| `speed_eb` | 8 และ 32 | Effective Batch ของขั้นวัดความเร็ว · ต้องหารด้วยจำนวน replica ลงตัว (ไม่ลงตัว สคริปต์จะข้ามรอบนั้น) · `ไม่วัด` = ข้ามขั้นวัดความเร็วทั้ง 1 Node และคลัสเตอร์ |
| `speed_updates` | EB ≤ 8: 20 ครั้ง ไม่นับ 3 ครั้งแรก · EB อื่น: 8 ครั้ง ไม่นับ 2 ครั้งแรก | จำนวนครั้งที่ปรับน้ำหนักต่อรอบวัด → `STEPS` / `WARMUP` (ผู้ใช้บอกจำนวนครั้งแต่ไม่บอกช่วงไม่นับ → ไม่นับ 2 ครั้งแรก) · ทุกรอบของ 1 Node และคลัสเตอร์ต้องใช้ค่าเดียวกัน |
| `train_eb` | 8 | Effective Batch ของการเทรนจริง → `EB` |
| `train_limit` | 400 ใบ | จำนวนใบเสร็จที่เทรน (ใบแรกของ Training Set หลังสุ่มด้วย seed 0 · สูงสุด 800 · ต้องหารด้วย `train_eb` ลงตัว) → `LIMIT` |
| `epochs` | 1 | จำนวน Epoch → `EPOCHS` |
| `evaluate` | ใช่ | วัดผล Test Set 100 ใบ Base เทียบ Fine-tuned ของทุกแนวทางที่เทรน (`MODELS=base,<approach>`) · `ไม่` = ข้าม |
| `vram_probe` | อัตโนมัติ | ทำเมื่อ `gpu` มี VRAM ไม่ใช่ 24 GB หรือผู้ใช้สั่ง · ไม่ทำ = ใช้ผลอ้างอิงของ RTX 3090 ด้านล่าง |
| `label` | `vapp-lab5-n` | ป้ายเครื่อง ต่อท้ายด้วยลำดับ Node → `vapp-lab5-n1` `vapp-lab5-n2` … (ผู้ใช้ให้ป้ายมาครบทุกเครื่อง เช่น `vapp-lab5-skill-n1` `-n2` → ใช้ตามนั้น และ prefix คือส่วนก่อนเลข) |
| `out_dir` | `lab5_cluster_vlm/results` | โฟลเดอร์ผลบนเครื่องนี้ · มีผลเดิมอยู่และผู้ใช้ไม่ได้สั่งให้ทับ → ใช้โฟลเดอร์ย่อยใหม่ เช่น `lab5_cluster_vlm/results/skill_v0_run` (ห้ามเขียนทับผลเดิม) |
| `keep_machine` | ไม่ | `ใช่` = ไม่ลบเครื่องตอนจบ (ต้องบอกผู้ใช้ชัดว่ายังคิดเงิน) |
| `offer_filter` | verified · ต่อ SSH ได้ตรง · เน็ต ≥ 500 Mbps ทั้งขาเข้าและขาออก · ค่ารับส่งข้อมูล ≤ $0.02/GB · CPU ≥ 12 cores · ไม่อยู่ในจีน | เกณฑ์เลือกเครื่อง |
| `image` / `disk_gb` / `port` | `pytorch/pytorch:2.8.0-cuda12.8-cudnn9-devel` / 80 / 9000 | เปิดพอร์ต 9000 ไว้ 1 พอร์ตบนทุกเครื่อง |
| `ready_timeout` | 8 นาที | รอเครื่องพร้อมเกินนี้ → ลบแล้วเช่าเครื่องอื่น |
| ค่าที่ตรึง | Qwen/Qwen3-VL-8B-Instruct bf16 · LoRA rank 8 alpha 16 เฉพาะ q_proj v_proj ส่วนภาษา · lr 0.0002 · seed 0 · ภาพด้านยาว 1280 px · loss เฉพาะคำตอบ JSON | เปลี่ยนไม่ได้ในเวอร์ชัน 0 |
| `container` / `ssh_key` | `multi-account` · `/workspace/vastapp_lab` / `/workspace/vastai_lab/Devtool_SSH/devtoolSSH` | ที่ทำงานของสกิล vastai และกุญแจ SSH |

## ขั้นตอน

จับเวลาทุกขั้นไว้ใช้ในสรุป · ห้ามแสดงค่า key ใด ๆ (Vast · `HF_TOKEN` · รหัสลับของคลัสเตอร์) ในคำตอบหรือไฟล์ผล · ห้ามใส่ IP และเลขเครื่องในไฟล์ผล

**ข้อควรรู้ที่เจอจริงใน LAB 5** (ทำทุกครั้ง)
- เครื่องที่ driver 535 + image CUDA 12.8 PyTorch มองไม่เห็น GPU (error 804) → ตั้ง `export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu` ก่อนรัน Python ทุกครั้ง (สคริปต์ `run_*.sh` ตั้งให้แล้ว)
- ทุกงานยาวรันแยกจาก SSH (`setsid nohup`) · SSH หลุดได้บ่อย ให้ต่อใหม่แล้วอ่าน log ต่อ อย่าเริ่มงานซ้ำ
- เครื่องที่อยู่หลัง public IP เดียวกันมักต่อหากันผ่าน IP นั้นไม่ได้ → ทุก Node ต้อง public IP คนละตัว
- คัดลอกไฟล์ใหญ่จาก Node 1 กลับมาแล้วหลุดซ้ำ ๆ → ส่งจาก Node 1 ไป Node อื่นแล้วดึงจาก Node นั้นแทน และเทียบ sha256 ทุกครั้ง
- เน็ตระหว่าง Node สะดุดได้ชั่วคราว (ส่ง Gradient 8–13 วินาที) → ถ้ารอบวัดความเร็วรอบไหนมีครั้งที่ช้าผิดปกติ วัดรอบนั้นใหม่ด้วยค่าเดิม (`SKIP` รอบที่ดีแล้ว) และเก็บผลรอบแรกไว้ในชื่อ `<run>_try1_network_stall`

1. **เช่า Node 1**: ใช้สกิล vastai ค้นหาเครื่อง `gpu` × 2 ใบในเครื่องเดียว ตาม `max_price` และ `offer_filter`
   - ถ้า `nodes` ≥ 2: เลือกจากประเทศหรือภูมิภาคที่ตอนนี้มีเครื่องผ่านเงื่อนไขอย่างน้อย `nodes` เครื่องที่ public IP คนละตัว แล้วเอาเครื่องที่ถูกที่สุดในกลุ่มนั้น
   - เช่าด้วย `image` `disk_gb` เปิด `port` ตั้งป้าย `<label>1` รอจน SSH เข้าได้และ `nvidia-smi` เห็นครบ 2 ใบ · เกิน `ready_timeout` → ลบแล้วเช่าเครื่องถัดไป
   - จด GPU · VRAM · ราคาต่อชั่วโมง · ที่ตั้ง · CPU · เน็ต · ค่ารับส่งข้อมูล · ที่อยู่ภายนอกของพอร์ต 9000 (= `COORD`)
2. **เตรียม Node 1**: คัดลอก `scripts/*.py` `setup_node2.sh` `run_node1.sh` ไปที่ `/workspace/lab5/` แล้ว `printf '%s\n' "$HF_TOKEN" | bash setup_node2.sh > setup.log 2>&1` (`HF_TOKEN` จาก `.env` ของโฟลเดอร์ปัจจุบัน ส่งผ่าน stdin เท่านั้น) รอจนมี `SETUP_DONE`
   - ตรวจ `data rc=0` และ `model rc=0` · ถ้าโหลดแล้ว error ตอนคลายข้อมูล ให้อัปเดต `brotli`
   - `python receipt_data.py samples --out /workspace/lab5/data --save /workspace/lab5/dataset_samples.jpg` แล้วดึงมาที่ `out_dir/dataset_samples.jpg` เปิดดู 1 ครั้ง
   - สร้างรหัสลับครั้งเดียว: `umask 077; python -c "import secrets;print(secrets.token_hex(32))" > /workspace/lab5/cluster_secret` (ห้ามแสดงค่า)
   - ตรวจว่าไม่มี token ค้าง (`~/.cache/huggingface/token` และ `grep -r` ใน `/workspace/lab5`)
3. **VRAM probe** (ทำตาม `vram_probe`): บน Node 1 รันทีละกรณี ทีละ process ผลลง `/workspace/lab5/vram_probe.json`
   `--gpus 1 --gc off --case A-1gpu` · `--gpus 2 --gc off --split 18 --case A-2gpu-split18` · `--gpus 2 --gc off --split 19 --case A-2gpu-split19` · `--gpus 1 --gc on --case B-b1` · `--gpus 1 --gc on --batch 2 --case B-b2` → ดึงมาที่ `out_dir/raw/vram_probe.json` (ทดสอบตามจริง ห้ามปรับค่าให้ผลออกตามที่คาด) · ถ้าผลต่างจากอ้างอิง (A ต้องใช้ 2 ใบ · B ได้ batch 1) ให้แจ้งผู้ใช้ก่อนเทรน
4. **วัดความเร็ว 1 Node** (ข้ามถ้า `speed_eb` = ไม่วัด): บน Node 1 `cd /workspace/lab5 && RUNS="<approach>_eb<speed_eb> …" [STEPS= WARMUP=] setsid nohup bash run_node1.sh > runs_node1.log 2>&1 &` รอจนมี `/workspace/lab5/runs_node1/ALL_DONE` (LAB 5 ทั้ง 4 รอบใช้ ~15 นาที) แล้วดึงทั้งโฟลเดอร์มาที่ `out_dir/raw/runs_node1/`
5. **เช่า Node 2…`nodes`** (ข้ามถ้า `nodes` = 1): เงื่อนไขและ image เดียวกับ Node 1 ป้าย `<label>2` … เลือกเครื่องที่ใกล้ Node 1 ที่สุด (ประเทศเดียวกันหรือติดกัน) public IP ต้องคนละตัวกับทุก Node
   - เตรียมด้วยไฟล์ชุดเดียวกันและ `setup_node2.sh` แบบเดียวกับขั้น 2 · คัดลอก `cluster_secret` จาก Node 1 ไปที่ `/workspace/lab5/cluster_secret` ผ่าน pipe ของ SSH (ห้ามแสดงค่า ห้ามพักไว้ในไฟล์ใน container)
   - ทดสอบการต่อ: Node 1 `python net_probe.py server --port 9000` · Node ใหม่ `python net_probe.py client --host <ip Node 1> --port <พอร์ตภายนอกของ 9000> --out /workspace/lab5/net_probe.json` → ดึงมาที่ `out_dir/raw/net_probe.json` (ลบ `target` ที่เป็น IP ออก) · ต่อไม่ได้ → ลบเครื่องนั้นแล้วเช่าเครื่องอื่น
6. **วัดความเร็วคลัสเตอร์** (ข้ามถ้า `nodes` = 1 หรือไม่วัด): ใน container `NODES="…" COORD=… RUNS="<ชุดเดียวกับขั้น 4>" [STEPS= WARMUP=] setsid nohup bash run_2node.sh > runs_2node.log 2>&1 &` รอจนพิมพ์ `ALL_DONE` · ตรวจว่า checksum ของทุก replica ตรงกัน · ดึง `/workspace/lab5/runs_2node/` จากทุก Node รวมไว้ที่ `out_dir/raw/runs_2node/<run>/` (ไฟล์ `worker_r*.json` ของแต่ละ Node อยู่บน Node ของตัวเอง ต้องดึงครบทุก Node)
   - ถ้าต้องแก้โค้ด ให้วัดรอบ 1 Node ของขั้น 4 ใหม่ด้วย เพื่อให้เทียบกันได้
7. **เทรนจริง**: ใน container `NODES="…" COORD=… APPROACHES="<approach>" LIMIT=<train_limit> EB=<train_eb> EPOCHS=<epochs> setsid nohup bash run_train.sh > run_train.log 2>&1 &` รายงานความคืบหน้าทุก 2–3 นาที (log พิมพ์ step ล่าสุดทุกนาที) รอจน `ALL_DONE`
   - แต่ละแนวทาง: ตรวจ checksum ตรงกันทุก replica · หาโฟลเดอร์ `adapter` ที่ replica rank 0 บันทึกไว้ (`/workspace/lab5/train_2node/<A|B>/adapter` อยู่บน Node ของ rank 0) → ดึงมาที่ `out_dir/adapter_<A|B>/` และกระจายไปที่ `/workspace/lab5/adapters/<A|B>` บน**ทุก** Node (เทียบ sha256)
   - ดึง `coordinator.json` `worker_r*.json` log และ `round_wall_s.txt` ของทุก Node มาที่ `out_dir/raw/train_2node/<A|B>/` แล้ว `python <skill>/scripts/summarize_train.py <out_dir>`
8. **Evaluation** (ข้ามถ้า `evaluate` = ไม่): ใน container `NODES="…" MODELS=base,<approach คั่นด้วย ,> setsid nohup bash run_eval.sh > run_eval.log 2>&1 &` รอจน `ALL_DONE` (LAB 5 สามโมเดลบน 4 GPU ~20 นาที) แล้วดึง `/workspace/lab5/eval/` ของ Node 1 มาที่ `out_dir/eval/` เปิดดู `images/accuracy_3models.png` และ `images/examples.jpg`
9. **ปิดทุกอย่าง (ห้ามข้าม เว้นแต่ `keep_machine`)**: ตรวจว่าผลใน `out_dir` ครบก่อน (`raw/runs_node1` `raw/runs_2node` `raw/train_2node` `adapter_*` `eval/`) ขาดให้ดึงก่อน
   - เขียน `out_dir/raw/nodes.json` ทีละ Node ด้วยคีย์ `<label>1` `<label>2` … (`gpu` `geolocation` `price_usd_per_hour` `cpu_cores` เน็ต `driver` `image` `disk_gb` `age_hours` `billed_usd` {gpu, disk, download, upload, total}) และ `lab_total_billed_usd` **ไม่ใส่ IP และเลขเครื่อง**
   - ใช้สกิล vastai ลบทุกเครื่องที่ป้ายขึ้นต้นด้วย `<label>` แล้วตรวจซ้ำว่าไม่เหลือในบัญชี · ดูบิลจริง (invoices) ราว 3 นาทีหลังลบ แล้วเติมยอดลง `nodes.json`
10. **สรุปผล (เครื่องนี้ ไม่ใช้เครื่องเช่า)**: `python <skill>/scripts/compare_nodes.py --raw <out_dir>/raw` (ถ้ามีคลัสเตอร์) แล้ว `python <skill>/scripts/report.py --results <out_dir> --label-prefix <label>` → `out_dir/metrics.json` และ `out_dir/images/speedup_vs_nodes.png time_per_update.png peak_vram.png cost_per_epoch.png` เปิดดูกราฟอย่างน้อย 2 รูป (บน Windows ตั้ง `PYTHONIOENCODING=utf-8`)
    - ค่าประมาณ 3 Node ใน `metrics.json` เป็นการคำนวณจากเวลาที่วัดได้ ไม่ใช่ผลวัด ต้องบอกแบบนี้ทุกครั้งที่อ้าง

## เกณฑ์ตรวจผ่าน

- [ ] ทุก Node มี `gpu` 2 ใบในเครื่องเดียว ราคาต่อเครื่อง ≤ `max_price` และ public IP คนละตัว · Node อื่นต่อเข้าพอร์ต 9000 ของ Node 1 ได้ (มี RTT ใน `net_probe.json`)
- [ ] Dataset ครบ: Training 800 · Validation 100 · Test 100 ใบ · มี `dataset_samples.jpg` · ไม่มี `HF_TOKEN` ค้างบนเครื่องเช่า
- [ ] (VRAM probe) A บน GPU 1 ใบ = Out of Memory · A บน 2 ใบเทรนได้ · B batch 1 เทรนได้ · B batch 2 = Out of Memory (อ้างอิง RTX 3090: น้ำหนัก 16.34 GiB · A 19/17 = 15.1 / 15.1 GiB · B batch 1 = 20.3 GiB)
- [ ] ทุกรอบวัดความเร็วและทุกรอบเทรน: checksum ของน้ำหนัก LoRA ทุก replica ตรงกัน · ขนาด Gradient 7.67 MB ต่อ replica ต่อครั้ง · VRAM สูงสุดต่อใบ < 24 GB
- [ ] Speedup ของคลัสเตอร์ 2 Node > 1 เท่า ทุกรอบ และ EB 32 ได้ Efficiency สูงกว่า EB 8
  - ค่าอ้างอิง LAB 5 (RTX 3090 × 2 ต่อเครื่อง · Quebec CA + Utah US · RTT 55.5 ms) วินาทีต่อการปรับน้ำหนัก 1 Node → 2 Node: A EB 8 9.19 → 7.29 (1.26×) · A EB 32 35.91 → 19.32 (1.86×) · B EB 8 5.29 → 4.65 (1.14×) · B EB 32 20.03 → 11.11 (1.80×)
- [ ] เทรนจริงจบครบทุกครั้งของการปรับน้ำหนัก loss ช่วงท้ายต่ำกว่าช่วงต้น · มี `adapter_<A|B>/adapter_model.safetensors` (~15.4 MB)
  - ค่าอ้างอิง (400 ใบ 1 Epoch EB 8 · 2 Node): A 334 วินาที · B 261 วินาที · loss เฉลี่ย 10 ครั้งแรก 0.073 → 10 ครั้งสุดท้าย 0.043
- [ ] (Evaluation) ครบ 100 ใบทุกโมเดล · Item F1 ของ Fine-tuned สูงกว่า Base
  - ค่าอ้างอิง: Base JSON 100% · ยอดรวมตรง 95.8% · Item F1 77.0% · Fine-tuned A 99.0 / 93.7 / 87.9% · B 99.0 / 93.7 / 87.2% · 2B (LAB 2) Base 88.4 / 69.9% · Fine-tuned 100 / 88.4%
- [ ] `out_dir` มี `raw/` ครบตามที่ทำ · `raw/nodes.json` · `metrics.json` · กราฟ 4 รูป · (ถ้าวัดผล) `eval/metrics.json` และภาพ 2 รูป
- [ ] ไม่มีเครื่องป้าย `<label>*` ค้างในบัญชี (ยกเว้น `keep_machine`)
- [ ] ไม่มีค่า key รหัสลับ IP หรือเลขเครื่องในคำตอบหรือไฟล์ผล

## กติกาเรื่องเงิน

1. **ลบทุกเครื่องเสมอ** เมื่อจบงาน และเมื่อขั้นใดล้มจนไปต่อไม่ได้ ก่อนหยุดให้ดึงผลที่มีกลับมา ลบ**ทุก** Node แล้วค่อยรายงานปัญหา · Node 1 คิดเงินตั้งแต่ขั้น 1 และ Node อื่นตั้งแต่ขั้น 5 จนถึงขั้น 9
2. ห้ามเช่าเครื่องที่ราคาเกิน `max_price` และห้ามมีเครื่องเปิดพร้อมกันเกิน `nodes` เครื่อง (เครื่องที่ไม่ผ่านต้องลบก่อนเช่าเครื่องใหม่) · เช่า Node 2 ขึ้นไปหลังขั้น 4 เสร็จเท่านั้น จะได้ไม่จ่ายเครื่องที่รออยู่เฉย ๆ
3. แตะเฉพาะเครื่องป้ายขึ้นต้นด้วย `<label>` ห้ามลบหรือแก้เครื่องป้ายอื่นในบัญชี
4. ข้ามการลบได้เฉพาะเมื่อ `keep_machine` = ใช่ และต้องบอกชัดในสรุปว่าเครื่องไหนยังเปิดและคิดเงินชั่วโมงละเท่าไร
5. งบอ้างอิง LAB 5 (2 Node ครบทุกขั้น รวมเวลาเขียนโค้ด): Node 1 เปิด 3.0 ชม. $1.23 · Node 2 เปิด 1.9 ชม. $1.20 · รวม **$2.44** · ใช้สกิลนี้ (ไม่ต้องเขียนโค้ด) ควรน้อยกว่านี้ · ถ้าเครื่องใดเปิดเกิน 3 ชั่วโมง หรือยอดรวมคาดว่าจะเกิน $3 ให้รายงานผู้ใช้ก่อนทำต่อ

## สรุปตอนจบ (ภาษาไทย)

ตาราง: เครื่องที่ได้แต่ละ Node (GPU · ราคา · ที่ตั้ง · CPU · เน็ต) และ RTT · (ถ้ามี) ขีดจำกัด VRAM · แนวทาง × จำนวน Node × Effective Batch (replica · วินาทีต่อการปรับน้ำหนัก แยกคำนวณ/สื่อสาร · ใบเสร็จต่อวินาที · Speedup · Efficiency · ราคาต่อชั่วโมง · เงินต่อ Epoch 800 ใบ) · การเทรน (เวลา · loss ต้น/ท้าย · VRAM · checksum · ขนาด adapter) · Evaluation (JSON อ่านได้ · ยอดรวมตรง · Item F1 · วินาทีต่อใบ ก่อน vs หลัง) · เวลาแต่ละขั้น · ค่าใช้จ่ายจริงแยกเครื่องและรวม · ผลเกณฑ์ตรวจผ่านทีละข้อ · สถานะเครื่อง (ลบแล้ว / ยังเปิด)
แล้วตอบโดยอ้างตัวเลขที่วัดได้: เพิ่ม Node แล้วเร็วขึ้นกี่เท่า · ทำไมไม่เร็วขึ้นตามจำนวน Node (เวลาสื่อสาร · รอ replica ที่ช้าที่สุด) · ทำไม Effective Batch ใหญ่ได้ Efficiency ดีกว่า · เมื่อไรควรใช้แนวทาง A เมื่อไรควรใช้แนวทาง B
