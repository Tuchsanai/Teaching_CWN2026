# เตรียม Input และรัน Loop

ทำงานจาก `AI_Workflow_Engineering_for_SA/002_LAB_Loop_FR_NFR/` ทุก path ในคำสั่งเริ่มจากโฟลเดอร์นี้ ต้องผ่าน LAB 001 ก่อนและมี Bash, Python 3, GNU date/timeout และ CLI ที่พร้อมใช้งาน

## นำ baseline มาใช้

เลือกไฟล์ผลของตนเอง `../001_LAB_Single_Prompt_Baseline/work/fr-nfr-v0.md` เป็นอันดับแรก ไม่แก้ไฟล์ต้นทาง หากไม่มีให้ใช้ไฟล์สำรอง `../001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md`
**ถ้าใช้ไฟล์สำรองต้องบันทึกว่าใช้ผลอ้างอิง** ทั้งใน `work/baseline-source.txt` และรายงานส่งงาน ถ้าสองไฟล์ยังไม่มี ให้กลับไปทำ LAB 001 หรือรอผลอ้างอิง ห้ามสร้าง baseline ปลอม

```bash
mkdir -p work
python3 - <<'PY'
from pathlib import Path
own = Path('../001_LAB_Single_Prompt_Baseline/work/fr-nfr-v0.md')
ref = Path('../001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md')
source = own if own.is_file() and own.stat().st_size else ref
if not source.is_file() or not source.stat().st_size:
    raise SystemExit('ไม่มี baseline: กลับไปทำ LAB 001 หรือรอไฟล์อ้างอิง')
for p in ['work/fr-nfr-v0.md', 'work/baseline-source.txt']:
    if Path(p).exists():
        raise SystemExit('มี Input เดิมแล้ว: ตรวจและใช้ต่อ หรือเก็บเป็นชุดใหม่ก่อน')
Path('work/fr-nfr-v0.md').write_bytes(source.read_bytes())
label = 'ผลนักศึกษา' if source == own else 'ใช้ผลอ้างอิง'
Path('work/baseline-source.txt').write_text(f'{label}\nต้นทาง: {source}\n', encoding='utf-8')
PY
```

[user-stories-lab002.md](user-stories-lab002.md) คัด 18 แถวจากต้นฉบับด้วย grep ไม่ตัดการอ้างข้าม US ภายในเซลล์ และไม่ถือว่ารหัสอ้างเป็นงานเพิ่ม ห้ามเดาเนื้อหาหมายเหตุ ก./ค./ช.

## สองวิธีฝึก

1. ขั้น 01–03 ใน README เป็นการทำด้วยตนเองหนึ่งรอบเพื่อเข้าใจการส่งไฟล์และ Feedback ทุกการเรียกเริ่ม session ใหม่ เก็บ prompt และ JSONL/stderr คู่กับผล อย่าใช้ resume/continue
2. ขั้น 04 ใช้ `bash input/run-loop.sh` เริ่มจาก v0 ทำ generator → checker → fixer → checker โดยอัตโนมัติ ไม่ต่อจากผล manual อย่างเงียบ ๆ หากทำ manual แล้ว ให้เก็บชุดเดิมตามคำสั่งด้านล่างก่อน

```bash
# เก็บสำเนาผลและหลักฐานทั้งหมดด้วยชื่อไม่ซ้ำ แล้วเริ่ม work ชุดใหม่จาก v0 เดิม
python3 - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import shutil
w = Path('work')
a = Path('work-archive') / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
a.parent.mkdir(exist_ok=True)
if not (w/'fr-nfr-v0.md').is_file() or not (w/'baseline-source.txt').is_file():
    raise SystemExit('ต้องมี baseline และที่มาก่อน archive')
w.rename(a)
w.mkdir()
for name in ['fr-nfr-v0.md', 'baseline-source.txt']:
    shutil.copy2(a/name, w/name)
print('เก็บผลเดิมที่', a)
PY
# ขีดจำกัดที่ตั้งสำหรับการฝึก ไม่ใช่สถิติผลรัน
MAX_ROUNDS=3 MAX_SECONDS=1800 MAX_TOKENS=0 bash input/run-loop.sh
# หรือเลือกอีกเครื่องมือในชุดทดลองใหม่
AI_CMD='claude -p' MAX_ROUNDS=3 bash input/run-loop.sh
```

`AI_CMD` ค่าเริ่มต้นคือ `codex exec` รองรับสองค่านี้ตรงตัวเพื่อไม่ใช้ eval ทุกครั้งเป็น process/session ใหม่ สคริปต์แนบเนื้อหา Input ลง prompt และส่งผ่าน stdin เพื่อรองรับเอกสารยาวโดยไม่ติดเพดานขนาด argument แล้วบันทึกคำตอบสุดท้ายด้วย `-o` สำหรับ Codex; ทางเลือก `claude -p` อ่านข้อความจาก result event ของ stream JSONL ผ่าน [loop-support.py](loop-support.py) ผู้เรียนเลือกเครื่องมือเดียวต่อชุด ไม่ได้เรียกทั้งสองพร้อมกัน

## เพดานและความหมายของ log

- `MAX_ROUNDS` รับ 1–3 ค่าเริ่มต้น 3 หนึ่งรอบคือ checker ตรวจร่างหนึ่งรุ่นเสร็จ ไม่ใช่หนึ่ง CLI call; generator ทำครั้งแรก และ fixer ทำเมื่อ FAIL และยังมีรอบเหลือเท่านั้น
- `MAX_SECONDS` ค่าเริ่มต้น 1800 วินาทีเป็นงบเวลาสำหรับ Loop ใช้ `date` วัดเวลาจริงและ `timeout` จำกัดแต่ละ call ตามเวลาที่เหลือ มีช่วง kill-after ไม่เกิน 5 วินาทีเมื่อ process ไม่ยอมจบ
- `MAX_TOKENS=0` หมายถึงไม่เปิดเพดานโทเคน หากกำหนดจำนวนเต็มบวก จะตรวจยอดหลัง call ก่อนเรียกครั้งถัดไป อาจเกินเพดานใน call สุดท้าย เพราะรู้ usage หลังจบเท่านั้น หากอ่านโทเคนไม่ได้และเปิดเพดานจะหยุด `token_usage_unknown` ไม่ถือว่าใช้ศูนย์
- งบเงินให้ผู้เรียนกำหนดก่อนเริ่มและบันทึกในรายงาน สคริปต์ไม่ได้ดึงราคา/ยอดเงินและไม่ได้บังคับเพดานเงินจริง ให้ใช้เพดานโทเคนและเวลาเป็นตัวควบคุมร่วมกับโควตาของเครื่องมือ ค่าใช้จ่ายที่ไม่มีหลักฐานเขียน “ไม่มีข้อมูล”
- หยุดเมื่อผ่านทุกข้อ, ครบเพดาน 3 รอบ, หรือคะแนนไม่เพิ่ม 2 รอบติด (รวมลดลงด้วย): เปรียบเทียบรอบสองกับรอบแรก แล้วรอบสามกับรอบสอง มีค่าเท่ากันถือว่าไม่เพิ่ม; ถ้าคะแนนเพิ่มให้เริ่มนับ streak ใหม่
- `work/loop-log.json` เป็นไปตาม [loop-log.schema.json](loop-log.schema.json): `calls` เก็บแต่ละการเรียกพร้อมเวลา/exit code/log/output/tokens, `rounds` เก็บผลที่ตรวจรูปแบบและคะแนนแล้ว, `stop_reason` เก็บเหตุหยุด, `total_tokens` เป็น null หากมี call ใดไม่ทราบ usage
- Codex อ่าน usage จาก event `turn.completed` รวม input_tokens + output_tokens ไม่บวก cached_input_tokens ซ้ำ และปฏิเสธผลที่พบ `turn.failed`; Claude อ่าน usage จาก result และรวม cache ที่แยกต่างหาก หากอ่าน JSONL/usage ไม่ได้ใส่ null ไฟล์ output ยังต้องมีและ exit code ต้องสำเร็จจึงตรวจต่อได้
- สคริปต์ตรวจตารางหลักและสองบรรทัดท้าย RESULT/SCORE แล้วใช้ grep อ่าน RESULT จากไฟล์ ตรวจผลทุกคู่ที่เคย PASS จากทุก round เพื่อหา regression ค่าใน log ไม่ได้พิสูจน์ความถูกต้องเชิงความหมายแทนมนุษย์

Exit code: 0 = PASS, 1 = ยัง FAIL และหยุดเพราะเพดานรอบ/ไม่คืบ, 2 = Input/CLI/รูปแบบรายงาน/งบมีปัญหาหรือถึงเพดานเวลา/โทเคน, 130 = ถูกขัดจังหวะ ตรวจ `stop_reason` และ JSONL/stderr ประกอบเสมอ ไม่ retry ทับหลักฐานเดิม

## ขอบเขตของตัวอย่าง

ตัวอย่างใน README ยังไม่มีผลรันจริงจากโมเดล ผู้จัดทำจะเติมผลรันจริงและหลักฐานภายหลัง เวลา/รอบ/โทเคน/ต้นทุน: ไม่มีข้อมูล การทดสอบสคริปต์ด้วยข้อมูลจำลองใช้ตรวจการควบคุม Loop เท่านั้น

## ตรวจสคริปต์โดยไม่เรียกโมเดล

รัน `python3 input/test-loop.py` จากโฟลเดอร์ LAB (ต้องมีแพ็กเกจ jsonschema สำหรับ test เท่านั้น; ตัว Loop ใช้ Python standard library) ชุดทดสอบสร้าง executable จำลองในโฟลเดอร์ชั่วคราวใต้ input/ ไม่เรียกบริการ AI จริง และตรวจ JSON ที่ได้กับ schema ทุกกรณี ผลเหล่านี้ใช้ยืนยันการควบคุม Loop ไม่ใช่ผลรันล่วงหน้าของบทเรียน ดูรายละเอียดใน [วิธีทดสอบสคริปต์โดยไม่เรียกโมเดล](verification.md)
