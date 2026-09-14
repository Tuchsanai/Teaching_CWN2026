# ชุด QA สไลด์และ UI

รันจากโฟลเดอร์บทเรียนด้วย Python ที่มี Playwright และ Chromium:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install playwright==1.62.0
.venv/bin/python -m playwright install chromium
PYTHON="$PWD/.venv/bin/python" bash tests/run_all.sh
```

ชุดนี้รันจริงด้วย Playwright 1.62.0 / Chromium; รุ่นเป้าหมาย 1.63 ไม่อยู่ใน package index ของเครื่องที่ตรวจ จึงไม่อ้างว่าใช้รุ่นนั้นแล้ว หากมี runtime ที่เตรียมไว้ ใช้ `bash tests/run_all.sh` ได้โดยตรง; ค่าเริ่มต้นคือ Python ของสภาพแวดล้อมทดสอบที่เตรียมไว้ และ fallback เป็น `python3`

สคริปต์เรียก `launch()` ก่อน หากเปิด browser ไม่ได้จึงลอง `connect_over_cdp('http://127.0.0.1:9222')` โดยสร้าง context ของตนเองและไม่ปิด browser ที่ใช้ร่วมกัน

## แยกรัน

```bash
python3 -B tests/test_slides.py --html AI_Workflow_Engineering_SA.html --out-dir tests
python3 -B tests/test_ui.py --out-dir tests
python3 -B tests/check_links.py
```

`test_slides.py` เปิด `file://` รอจำนวนหน้า กด ArrowRight จนครบ ถ่ายภาพทุกหน้า แล้วทดสอบ overview และบทบาทลูกค้า/ครัว/หน้าร้าน/ผู้จัดการใน iframe ทั้งสองรุ่น ตรวจ `scrollHeight` ของ `.slot.active .slide` ไม่เกิน 730 ที่ viewport 1600×900 และเก็บ console error/pageerror

`test_ui.py` เรียก [runner ของ LAB 006](../006_LAB_Test_Scenarios_Traceability/tests/run-scenarios.py) ผ่าน subprocess พร้อม `--allow-fail` ใช้ [scenario ต้นฉบับ](../006_LAB_Test_Scenarios_Traceability/input/ui-scenarios.json) ครบทุกเคสทั้ง v1/v2 แต่ละเคสใช้ context ใหม่ ปิด network และถ่ายภาพเต็มหน้า viewport 1280×900

เคสที่ตกบน v1 เพราะฟีเจอร์ v2 และเคส fixture mismatch คงสถานะ fail พร้อมเหตุผล ไม่มีการตัดออกหรือแก้ scenario/HTML เพื่อให้ผ่าน

`check_links.py` เดินทุก `.md`/`.html` ไม่ตาม directory symlink ตรวจ Markdown destinations และ HTML href/src รวม markup สไลด์ใน text/plain script; ไม่อ่าน srcdoc เป็นลิงก์ภายนอก ไม่ตีความ JavaScript template เป็น path ไฟล์ ข้าม URL ที่มี scheme, protocol-relative URL และ anchor ภายใน ตัด anchor/query และถอด URL encoding ก่อนตรวจไฟล์ ไม่ตรวจว่า anchor ID หรือเว็บไซต์ภายนอกมีจริง

## ผลและ exit code

- [results.json](results.json): ส่วน slides และ ui แยกรุ่น พร้อมสาเหตุและ path ภาพ
- [link-report.json](link-report.json): `checked`/`broken` คือขอบเขตนักศึกษา; `evidence.files` คือจำนวน Markdown/HTML ที่ตรวจในหลักฐาน, `evidence.checked`/`evidence.broken` คือจำนวนลิงก์และรายการเสียในหลักฐาน นับแต่ละ occurrence
- [screenshots/slides/](screenshots/slides/): slide-NNN.png ครบทุกหน้า และ overview.png
- [screenshots/ui-v1/](screenshots/ui-v1/) / [screenshots/ui-v2/](screenshots/ui-v2/): ภาพทั้งเคสผ่านและตก
- [runs/](runs/): ผล runner แยกเวลา; การรันซ้ำย้ายภาพ UI รอบก่อนมาเก็บที่นี่
- [link-fixes.json](link-fixes.json): รายการแก้ path และจำนวนครั้งที่แทน
- [รายงานสำหรับอ่าน](../docs/test-report.md): ตารางผล ข้อจำกัด และสิ่งที่ยังไม่ทดสอบ

Slides คืน exit 1 เมื่อ browser/setup หรือข้อยืนยันไม่ผ่าน; UI คืน exit 1 เมื่อ runner/หลักฐานทำงานไม่ครบ ส่วน fail ของ scenario คงอยู่ใน JSON ตามความหมาย `--allow-fail` จึงต้องอ่าน failed ควบคู่กับ exit code

Link checker แยกสองขอบเขตด้วย keys ของ [protected-evidence.json](protected-evidence.json) เท่านั้น: ไฟล์ที่ระบุเป็นหลักฐานดิบผูก SHA-256 และไฟล์อื่นทั้งหมดเป็นขอบเขตนักศึกษา ไม่ใช้ pattern ชื่อ README/summary คัดไฟล์ออก ค่าเริ่มต้นคืน exit 0 เมื่อ `broken` ของขอบเขตนักศึกษาว่าง และ exit 1 เมื่อขอบเขตนี้มีลิงก์เสีย รายการลิงก์เสียในหลักฐานยังอยู่ครบใน `link-report.json` ส่วน `evidence.broken` เป็น known issue โดยไม่แก้ต้นฉบับ

ใช้ `python3 -B tests/check_links.py --all --out tests/link-report-all.json` เพื่อตรวจรวมหลักฐานดิบเข้า `checked`/`broken` ด้วย โหมดนี้คืน exit 1 เมื่อมีลิงก์เสียใด ๆ และยังคงส่วน `evidence` ไว้ การแยกไฟล์ผลด้วย `--out` ช่วยรักษาผลขอบเขตนักศึกษาล่าสุด

`run_all.sh` รันทั้งสามชุดตามลำดับแม้ชุดก่อนหน้าไม่ผ่าน แล้วคืนสถานะรวมตามขอบเขตเริ่มต้น

การรันซ้ำปรับผลล่าสุดของชุดนั้นใน results.json ให้ตรงภาพล่าสุด ภาพสไลด์และผลเดิมย้ายเข้า runs/ ก่อนรันใหม่ รายงาน Markdown เป็น snapshot ของรอบที่ระบุวันที่ ปรับตาม JSON หลังรันใหม่ด้วย `python3 -B tests/write_report.py` แล้วรัน link checker ซ้ำ เพราะรายงานอาจเพิ่มลิงก์

ใช้ `-B`/`PYTHONDONTWRITEBYTECODE=1` เพื่อลดไฟล์ cache ถ้ารัน `py_compile` ให้ลบ `__pycache__/` หลังตรวจ อย่าแนบ `.ipynb_checkpoints/` เป็นชิ้นงาน

ภาพทุกหน้าเป็นหลักฐานเปิดและเดินหน้าได้ ไม่ใช่การตรวจภาพด้วยสายตาทุก pixel; การจำลองบทบาทในหน้าเดียวไม่ทดแทนการตรวจสิทธิ์บนระบบจริง
