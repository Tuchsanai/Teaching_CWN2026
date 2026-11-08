# TEST-REPORT · สกิล `dag-planner`

- ทดสอบใน container `my-multi-account` (สเปกใช้ชื่อค่าเริ่มต้น `multi-account`) · เวลา host เริ่ม 09:52:43 → จบ 10:08:26 (≈ 16 นาที รวมการรันจริง 40.5 วินาที)
- ใช้บัญชีที่ `team.py check` บอกว่าพร้อม (ทุกข้อใช้แค่ 2 บัญชี Claude + 2 บัญชี Codex จึงไม่มี SKIP)
- ติดตั้งโดยคัดลอกโฟลเดอร์ไป `/root/ai-accounts/.Claude/shared/skills/dag-planner` และ `/root/ai-accounts/.Codex/shared/skills/dag-planner` · md5 ของทั้ง 7 ไฟล์ตรงกับต้นฉบับบน host ทั้งสองฝั่ง
- ใช้บัญชีอย่างประหยัด: รันจริงแค่ข้อ 7 (4 บล็อก difficulty 1) = 5 การเรียก · 525,591 tokens (in+out, ส่วนใหญ่เป็น cache) · ข้ออื่นไม่เรียกโมเดล ยกเว้น `team.py check` ที่มีแคช 10 นาที

## ผลทดสอบ

| ข้อ | ผล | หลักฐาน |
|---|---|---|
| 1 ทุกบัญชีที่พร้อมเห็น `SKILL.md` · `doctor` ผ่าน | **PASS** | `ls -L` เจอ `skills/dag-planner/SKILL.md` ใน yolo1, yolo2 (symlink `skills → ../shared/skills`) และ cyolo1, cyolo2 (wrapper สร้าง symlink `dag-planner → ../../shared/skills/dag-planner` ตอน `cyoloN login status`) · `doctor` ✅ ครบ (Python 3.12.3 · agent-team/yolo/cyolo · graph.md · `/workspace/plans` เขียนได้ · PNG ด้วย `/ms-playwright/chromium_headless_shell-1252/…` · บัญชีพร้อม 4) exit 0 |
| 2 `dag` จับข้อผิดพลาดครบ | **PASS** | ไฟล์เดียวที่มีครบ 4 แบบ → exit 1 ได้ `id ซ้ำ: B03` · `B05: depends_on อ้าง id ที่ไม่มีจริง 'B99'` · `B06: skill ไม่รู้จัก 'magic'` · `วงวน: B02 → B03 → B02` · ทดสอบแยกทีละแบบก็จับได้ทุกแบบ (+ size `XL` → "ใหญ่กว่า L ต้องแบ่ง") |
| 3 แผน 8 บล็อก ครบ 6 สกิล: ป้ายสกิลครบ · rank/สายวิกฤตถูก | **PASS** | `plans/cafe8/dag.png` มีป้ายสี+ไอคอน+รุ่น/effort ครบ yolo/cyolo/image/review/debate/best_of + legend · สคริปต์อิสระ (ไล่ทุกเส้นทาง ไม่ import โค้ดสกิล) ได้ rank B01 7.2 · B02 6.6 · B04 6 · B05 6 · B07 4.5 · B03 2.1 · B06 2.1 · B08 1.5 ตรงทุกตัว · สายวิกฤตยาวสุด B01→B02→B05→B07→B08 (7.2M) ตรงกัน → `RANK_OK True CRIT_OK True` |
| 4 `plan` จากโควตาจริง | **PASS** | โควตาจาก `team.py quota` (yolo1 78% · yolo2 98% · cyolo1/2 99%) · ตัวตรวจอิสระ: yolo→Claude, cyolo/image→Codex ถูกทุกบล็อก · review B05 = yolo2 ทำ + cyolo2 ตรวจ (คนละ CLI) · debate = Claude+Codex+ผู้ตัดสินอีกบัญชี · ทุกบล็อกบัญชีไม่ซ้ำ · dependency/exclusive ถูก · ไม่มีช่วงเวลาที่บัญชีใดเกิน slot (`PLAN_OK True`) · stress test ที่ slot เหลือ 1/2/1/3: ใช้ถึงเพดานพอดีแต่ไม่เกิน · `gantt-plan.png` มีแท่งของ B02/B05/B06 ในหลายแถว เชื่อมด้วยเส้นประ |
| 5 `plan --accounts` ให้บัญชีหนึ่งเหลือน้อย → ไม่ได้บล็อกใหญ่ | **PASS** | `--accounts yolo1,yolo2:8,cyolo1,cyolo2` → capacity ของ yolo2 = 1.69M (slot 1) ส่วนบัญชีอื่น 37–75M · yolo2 ไม่ได้บล็อกเลย · บล็อกใหญ่ B07 (L) / B04, B05 (M) ไปที่ yolo1 (แผนจริงก่อนหน้านี้ให้ yolo2) |
| 6 `export` ได้ `graph.json` ที่ agent-team ยอมรับ | **PASS** | `accepted 8` ด้วย `team.add_node()` ตัวจริง + ทุกฟิลด์อยู่ในตารางของ `agent-team/references/graph.md` · กรณีที่ต้องปฏิเสธก็ปฏิเสธจริง (ฟิลด์แปลก · image ฝั่ง yolo · ลำดับ node ผิด) · มี `cwd=/workspace/plans/<แผน>/app` |
| 7 รันจริงแผนเล็ก → `report` | **PASS** | แผน `mini` 4 บล็อก difficulty 1 (cyolo · image · review · yolo exclusive) · run `mini-20261108-100657` **4/4 done ใน 40.5 วินาที** · `gantt-actual.png` · `compare.png` · `REPORT.md` ถูกสร้าง · ตัวตรวจอิสระเทียบ ledger ทีละบล็อก: tokens / จำนวนครั้ง / บัญชี ตรงทุกบล็อก (รวม 525,591 = 525,591) → `REPORT_OK True` · `icon.png` เป็น PNG จริง · `calib.json` k = cyolo 0.0333 · image 0.0689 · review 0.0391 · yolo 0.03 · * 0.044 · `plan` ครั้งถัดไปเอา k มาใช้แล้ว (19.8 → 0.7 นาที) |
| 8 เรียกจาก host ผ่าน `docker exec` | **PASS** | ทุกข้อด้านบนรันจาก host ผ่าน `docker exec` (Git Bash) · ส่งไฟล์บล็อกด้วย `docker exec -i … dag cafe8 --blocks - < cafe8.json` และ `docker cp cafe8.json …:/workspace/plans/hostcp/blocks.json` แล้ว `dag hostcp` จากสำเนาฝั่ง `.Codex` · `docker exec … cat //root/…/SKILL.md` อ่านสกิลได้ |

ข้อสังเกตจากการรันจริง: แผนให้ B04 ไปที่ yolo2 แต่ agent-team ส่งไปที่ yolo1 จริง ซึ่งเป็นไปตามที่ออกแบบไว้ เพราะ export ส่งเป็นฝั่ง (`yolo`/`cyolo`) เพื่อให้ failover ยังทำงาน (agent-team ล้างค่า `planned` และ node ที่ผูกบัญชีจะไม่ย้ายบัญชีให้) · `REPORT.md` แสดงส่วนต่างนี้ และ `references/run.md` อธิบายเหตุผลไว้

## ไฟล์ที่สร้าง

| ไฟล์ | บรรทัด | หน้าที่ |
|---|---|---|
| `skills/dag-planner/SKILL.md` | 84 | ตาราง ต้องการ→คำสั่ง · กติกาแตกบล็อก · ตารางเลือกสกิล · ข้อห้าม · เรียกจาก host |
| `skills/dag-planner/scripts/dagplan.py` | 769 | คำสั่งหลัก doctor · dag · plan · export · run · report |
| `skills/dag-planner/scripts/kcquest.py` | 381 | KC-QUEST ที่ดึงจาก orch.py (rank · capacity · คะแนน U/F/R/V/L · MRV · จอง) + แตกบทบาทของบล็อกหลายบัญชี + จำลองเวลา |
| `skills/dag-planner/scripts/render.py` | 322 | วาด DAG · Gantt · compare เป็น SVG → PNG ด้วย headless Chromium |
| `skills/dag-planner/references/blocks.md` · `kcquest.md` · `run.md` | – | ฟิลด์ของบล็อก + ตัวอย่าง 8 บล็อก · สูตรย่อ · การรันจริงและรายงาน |
| `TEST-REPORT.md` | – | ไฟล์นี้ |

## ภาพตัวอย่าง (host: `./workspace/plans/` = `/workspace/plans/` ใน container)

- DAG 8 บล็อก 6 สกิล: `cafe8/dag.png` (แบบมีป้ายบัญชีหลัง plan)
- Gantt แผน: `cafe8/gantt-plan.png` · what-if: `cafe8-whatif/gantt-plan.png` · stress: `cafe8-stress/gantt-plan.png`
- รันจริง: `mini/gantt-actual.png` · `mini/compare.png` · `mini/REPORT.md` · ไฟล์ของทีม `mini/app/` (README.md · icon.png · hello.py · INDEX.md)
- ตัวปรับเวลา: `calib.json`

## หมายเหตุ

- ไม่ได้อ่านหรือแสดง credential หรืออีเมล · ไม่ได้ล็อกอินแทน · ไม่ได้ลบ/หยุด/สร้าง container หรือ volume · ไม่ได้แก้สกิลอื่นใน shared
- ใน container มีแผนทดสอบเหลืออยู่ใน `/workspace/plans/` (t2-bad · cafe8 · cafe8-whatif · cafe8-stress · hostcp · mini · mini-k) และ run ใน `/workspace/.agent-team/mini-20261108-100657/` ลบทิ้งได้ถ้าไม่ต้องการ
- `mini/app/__pycache__` มาจาก agent ที่รัน hello.py ตอนตรวจ ไม่ได้มาจากสกิล
