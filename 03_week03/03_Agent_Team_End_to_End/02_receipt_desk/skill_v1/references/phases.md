# คำสั่งจริงของแต่ละขั้น (เรียกจาก host · Git Bash)

ตั้งตัวแปรก่อน (Git Bash แปลง `/root/...` → ใช้ `MSYS_NO_PATHCONV=1`)

```bash
export MSYS_NO_PATHCONV=1
S=/root/ai-accounts/.Claude/shared/skills
D="docker exec multi-account python3 $S/dag-planner/scripts/dagplan.py"
T="docker exec multi-account python3 $S/agent-team/scripts/team.py"
ACC=yolo1,yolo2,yolo3,cyolo1          # = accounts
```

## B · Planning + What-if

```bash
docker exec -i multi-account python3 $S/dag-planner/scripts/dagplan.py dag <plan> --blocks - < plan/blocks.json
$D plan <plan> --max-agents 4 --accounts $ACC          # ชื่อบัญชีอย่างเดียว = โควตาจริง · ใช้ calib.json อัตโนมัติ
docker cp multi-account:/workspace/plans/<plan>/. ./plan/   # เก็บ blocks/dag/gantt-plan/PLAN/plan/dag

# What-if: blocks เดิม (md5sum ก่อน/หลังต้องตรง)
docker exec multi-account md5sum /workspace/plans/<plan>/blocks.json
docker exec multi-account bash -c "cat /workspace/plans/<plan>/blocks.json" > /tmp/b.json
docker exec -i multi-account python3 $S/dag-planner/scripts/dagplan.py dag <plan>-2 --blocks - < /tmp/b.json
$D plan <plan>-2 --max-agents 2 --accounts $ACC
docker exec -i multi-account python3 $S/dag-planner/scripts/dagplan.py dag <plan>-nocodex --blocks - < /tmp/b.json
$D plan <plan>-nocodex --max-agents 4 --accounts yolo1,yolo2,yolo3
# คัดลอก gantt-plan.png → ./plan/whatif/gantt-<plan>-2.png, gantt-<plan>-nocodex.png (+ PLAN.md)
```

ฟิลด์บล็อก: `id title size depends_on skill difficulty timeout output done` (+ `max_rounds` สำหรับ review · `n` สำหรับ best_of) · ตัวอย่างครบที่ `dag-planner/references/blocks.md`

## C · Build + รันต่อ + เปลี่ยนขอบเขตตรวจ

```bash
docker exec multi-account mkdir -p /workspace/e2e_lab/<plan> /workspace/plans/<plan>/app
docker cp ./docs multi-account:/workspace/plans/<plan>/app/docs      # ไม่รวม BUGS-SECRET ถ้าไม่มีบล็อก BUG_MODE
$D export <plan>
$D run <plan> --detach            # แล้ว $T status --run <run_id> ทุก ~2 นาที
$D report <plan>                  # REPORT.md · gantt-actual · compare · calib.json
$T stats --run <run_id>           # โทเคนต่อบัญชี ต้องตรงกับ REPORT

# รันต่อ (G1b): เฉพาะบล็อกที่ไม่เสร็จ · run เดิม · บัญชีเดิม
$T run --resume <run_id> --set B03.prompt="<prompt เดิม> + แก้เฉพาะข้อที่ผู้ตรวจขอรอบล่าสุด: <ยกข้อความตรงตัว> ห้ามเขียนใหม่ทั้งไฟล์"
# เปลี่ยนขอบเขตตรวจ (G1c · คนตัดสินแล้ว)
$T run --resume <run_id> --set B03.criteria="ผ่านเมื่อกรณีทดสอบ BR ทุกข้อใน docs/TEST-DATA.md ผ่านครบ และไม่ขัดกับ Requirement ข้อใด · ข้อนอกขอบเขตจดใต้หัวข้อ FOLLOW-UPS พร้อมระดับ" --set B03.prompt="..."
$D report <plan>
```

คำสั่งยาวกว่าไม่กี่นาที: รันแบบ detach/เบื้องหลังแล้ว poll

## C · Rent · Train · Deploy · Capacity (หลัง G2) — ใน container ที่ `/workspace/vastapp_lab/<label>/`

```bash
./vast.sh show instances --raw
./vast.sh search offers 'gpu_name=RTX_3090 num_gpus=2 verified=true rentable=true direct_port_count>=3 dph_total<=0.60 disk_space>=80' -o 'dph_total' --raw
LABEL=<label> ./rent.sh <offer> 1          # 80 GB · ports 22/8000/8080 · ผล create ลงไฟล์ (ไม่แสดง)
./poll_instance.sh <id> 300                # ไม่ running/SSH ไม่เข้าใน 5 นาที → destroy แล้วลอง offer ถัดไป (≤ 3)
```

- Dataset/โมเดล: ดาวน์โหลดจาก Hugging Face (`huggingface_hub.snapshot_download`) ลง `/workspace/<label>/{models,data}` ใน tmux · นับจาก parquet จริง
- เทรน: ส่ง `app/ai/train` + `scripts/train/*` ขึ้นเครื่อง → `tmux new -d -s p 'bash pipeline.sh'` · 1 GPU `python train_lora.py` · N GPU `torchrun --standalone --nproc_per_node N` (global batch เท่ากัน)
- วัดผล: `run_eval.sh <gpu> <ft|base> <adapter|none> <val|test>` · val ก่อน (ตรึง threshold) · ก่อน/หลังเทรนรันคนละ GPU พร้อมกัน
- Deploy: `merge_lora.py <base> <lora> <out>` → `gpu.sh push` → `gpu.sh start all` → `gpu.sh status all` · เว็บ `GW_URL=http://<ip>:<port8000> bash web.sh env && bash web.sh up`
- Capacity: `lt.sh push` → `lt.sh run prep` → `lt.sh run capacity --workers 1` (`gpu.sh stop worker1` ก่อน) → `--workers 2` → `urgent` → `queuefull` → `crash` → `dlq` → `state` → `lt.sh pull` → `python plot.py`
- ปิดงาน: `vastai copy <id>:/workspace/<label>/.../runs/best/ local:./results/model/lora/` → sha256 เทียบ → `./vast.sh destroy instance <id> -y` → `show instances --raw` (ป้ายนี้ 0) → `./vast.sh show invoices-v1 --charges`

## D · Verification

- playwright-cli: 1 session ต่อ subagent (`-s c1` … `-s c6`) · สคริปต์ที่ไม่ใช่เบราว์เซอร์เรียก `http://127.0.0.1:<port>`
- ผู้ตรวจไขว้ Test Plan: วางแผน + docs (ไม่มี BUGS-SECRET) ไว้ที่ `/workspace/e2e_lab/<plan>_testplan` → กราฟ 1 node `{"id":"plan_review","account":"cyolo1","prompt":"ตรวจ TEST-PLAN.md: ตรวจได้จริงไหม ตัวเลขถูกไหม กำกวมไหม ซ้ำไหม จัดระดับ สูง/กลาง/ต่ำ"}` → `cat g.json | docker exec -i multi-account python3 $S/agent-team/scripts/team.py run - --workers cyolo1`
- เว็บชุดที่สอง: `bash mock.sh env && bash mock.sh up` · พักการอ่าน `mock.sh stop-reader` / `start-reader`
- Playwright: `npx playwright test --project=chromium --shard=i/4 --reporter=json` · trace + screenshot เฉพาะข้อที่ล้ม · `python make_index.py round1 round2`
- BUG_MODE: ตั้ง `BUG_MODE=1` ใน env ของทั้ง 2 ชุด → `up -d` → ตรวจค่าใน container (แสดงแค่ว่าเป็น 1) → รันชุดเดิมด้วย `RUN=bug-hunt` → กลับเป็น 0 แล้วตรวจซ้ำ

## ตัวเลขอ้างอิงจากรอบต้นแบบ ReceiptDesk (ใช้ประมาณการ ไม่ใช่เกณฑ์)

| เรื่อง | ค่า |
|---|---|
| Requirement | US 24 (Must 16) · FR 31 · BR 14 · NFR 10 · ข้อสมมติ 16 · ข้อมูลทดสอบ 96 แถว (กรณีขอบ BR 62) |
| แผน | 14 บล็อก · Critical Path B01→B02→B04→B11→B14 · แผน 63.5 นาที |
| What-if | max-agents 2: วางได้ 8/14 (debate/best_of ใช้ 3 agent) · ไม่มี Codex: วางได้ 0/14 |
| ทีม | รอบแรก 9/14 (review ไม่ APPROVED ใน 3 รอบ ทำให้ 4 บล็อก blocked) · รันต่อ 1: ยัง 9/14 · เปลี่ยนขอบเขตตรวจ: 14/14 · จริง 92 นาที · โทเคน 3.27 ล้าน (ไม่รวม cache read) |
| k จากของจริง | cyolo 0.27 · yolo 0.66 · debate 1.27 · image 0.07 |
| GPU | 2× RTX 3090 $0.414/ชม. · เช่าสำเร็จครั้งที่ 3 · 1 Epoch 400 ใบ: 205.9 s (1 GPU) vs 108.8 s (2 GPU) = Speedup 1.89 · Efficiency 94.6% |
| Gate | M1 46%→94.7% (เกณฑ์ 95%) · ผ่าน 2/6 → ไม่ผ่าน |
| Deploy | อ่าน 0.88 s/ใบ · E2E 5/5 ตรง DB |
| Capacity | 100 ใบ: 1 Worker 99–134 s · 2 Worker 49–63 s · Speedup 2.08 · ด่วน 10 ใบ 5.7 s · คิวเต็ม 429 · crash หาย 0 · DLQ 2/2 |
| ทดสอบ | 59 TC (M 21 · A 32 · R 6) · ผ่าน 46 ล้ม 11 บล็อก 2 · P1 87.5% · BUG_MODE จับได้ 3/3 |
| เงิน | เปิดเครื่อง 4 ชม. 48 นาที · ค่าเช่ารวม ≈ $2.06 |
