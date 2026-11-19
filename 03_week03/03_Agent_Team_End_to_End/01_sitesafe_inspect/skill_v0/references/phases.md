# คำสั่งจริงของแต่ละขั้น (เรียกจาก host · Git Bash)

ตั้งตัวแปรก่อน (Git Bash แปลง `/root/...` → ใช้ `MSYS_NO_PATHCONV=1` หรือ `//root/...`)

```bash
export MSYS_NO_PATHCONV=1
S=/root/ai-accounts/.Claude/shared/skills
D="docker exec multi-account python3 $S/dag-planner/scripts/dagplan.py"
T="docker exec multi-account python3 $S/agent-team/scripts/team.py"
```

## B · Planning

```bash
docker exec -i multi-account python3 $S/dag-planner/scripts/dagplan.py dag <plan> --blocks - < plan/blocks.json
$D plan <plan> --max-agents 3 --accounts yolo2,yolo3,cyolo1      # ชื่อบัญชีอย่างเดียว = ใช้โควตาจริง
docker cp multi-account:/workspace/plans/<plan>/. ./plan/           # แล้วลบไฟล์ที่ไม่ใช่ blocks/dag/gantt/PLAN/plan
```

ฟิลด์บล็อกที่ใช้จริง: `id title size depends_on skill difficulty timeout output done` (+ `worker` `max_rounds` สำหรับ review) · ดูตัวอย่างครบที่ `dag-planner/references/blocks.md`

## C · Build (หลัง G1)

```bash
docker cp ./docs multi-account:/workspace/plans/<plan>/app/docs    # ทีมต้องเห็นเอกสาร
$D export <plan>
$D run <plan> --detach          # แล้วดูด้วย $T status --run <run_id>
$D report <plan>                # REPORT.md · gantt-actual.png · compare.png · calib.json
$T stats --run <run_id>         # โทเคนต่อบัญชี (ตรวจให้ตรงกับ REPORT)
```

รันต่อ (G1b): แก้ `graph.json` เฉพาะ node ที่ล้ม (ต่อท้าย prompt ด้วยข้อที่ผู้ตรวจขอ · `max_rounds: 3`) แล้ว
`cat fixed.json | docker exec -i multi-account python3 $S/agent-team/scripts/team.py run - --resume <run_id>` → `$D report <plan>`

## C · Rent · Train · Deploy (หลัง G2) — ทำใน `/workspace/vastapp_lab/<label>/` ของ container

```bash
./vast.sh show instances --raw                                   # ก่อนเช่า: มีเครื่องอะไรอยู่
./vast.sh search offers 'gpu_name=RTX_3090 num_gpus=1 verified=true rentable=true direct_port_count>=1 dph_total<=0.30' -o 'dph_total' --raw
./vast.sh create instance <offer> --image vastai/pytorch --disk 40 --ssh --direct --label <label>
./poll_instance.sh <id> 300                                      # เกิน 5 นาทียังไม่ running → destroy แล้วเลือกใหม่
./vast.sh ssh-url <id>
```

- เทรน: ส่ง `scripts/` + โค้ดทีม (`app/ai/train`) ขึ้นเครื่อง แล้ว `tmux new -d -s train 'bash run_pipeline.sh > pipeline.log 2>&1'`
- Deploy: RabbitMQ จาก apt (ฟัง 127.0.0.1 · ลบผู้ใช้ guest) · gateway uvicorn `--ssl-keyfile/--ssl-certfile` ใบรับรองสร้างเอง SAN = IP เครื่อง · Worker ใน tmux · เว็บ `docker compose -p <plan>-e2e --env-file ../.env --env-file .env up -d --build`
- ปิดงาน: `vastai copy <id>:/workspace/.../model/ local:./results/model/` → sha256 เทียบ → `./vast.sh destroy instance <id> -y` → `show instances --raw` (ป้ายนี้ 0) → `./vast.sh show invoices-v1 --charges`

## D · Verification

- playwright-cli: 1 session ต่อ subagent (`-s c1` … `-s c4`) · สคริปต์ที่ไม่ใช่เบราว์เซอร์เรียก `http://127.0.0.1:<port>`
- ผู้ตรวจไขว้ Test Plan: กราฟ 1 node `{"id":"plan_review","account":"cyolo1","difficulty":3,"prompt":"ตรวจ ... TEST-PLAN.md ... ตรวจได้จริงไหม ตัวเลขถูกไหม กำกวมไหม ซ้ำไหม จัดระดับ สูง/กลาง/ต่ำ"}` → `team.py run - --workers cyolo1`
- Playwright: `npx playwright test --project=chromium` · trace + screenshot เฉพาะข้อที่ล้ม

## ตัวเลขอ้างอิงจากรอบต้นแบบ (ใช้ประมาณการ ไม่ใช่เกณฑ์)

| เรื่อง | ค่า |
|---|---|
| Requirement | US 20 (Must 16) · FR 22 · BR 7 · NFR 8 · ข้อสมมติ 14 |
| แผน | 10 บล็อก · Critical Path 5 บล็อก · แผน 112.5 นาที |
| ทีม | รอบแรก 39 นาที 6/10 เสร็จ (review ไม่ผ่านใน 2 รอบ) · รันต่อ 10/10 · โทเคนรวม 2.5 ล้าน (ไม่รวม cache read) |
| k จากของจริง | cyolo 0.24 · yolo 0.78 · image 0.07 |
| GPU | RTX 3090 $0.2215/ชม. · เทรน 30 Epoch 9 นาที · inference ~20 ms/รูป · เปิดเครื่องรวม 3.4 ชม. = $0.76 |
| ทดสอบ | 39 TC · ผ่าน 27 ล้ม 2 บล็อก 10 · BUG_MODE จับได้ 2/3 |
