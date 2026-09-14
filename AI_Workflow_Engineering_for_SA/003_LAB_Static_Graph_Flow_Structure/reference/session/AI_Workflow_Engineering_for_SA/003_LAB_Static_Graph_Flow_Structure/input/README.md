# Input ของ LAB 003

working directory ของคำสั่งทั้งหมดคือ `AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/`
เริ่มจาก working directory นี้และใช้ session ใหม่ต่อ node ไม่ใช้ resume/continue

## ไฟล์ตั้งต้น

- `input/fr-nfr-input.md` คือเอกสาร FR/NFR จริงที่ส่งต่อจาก LAB 002
- `input/us-by-role.md` คือ 18 แถวจาก appendix ตรงตัว ใช้ตรวจ FR/US ไม่ใช้แต่ง FR ใหม่
- `input/graph.json` ระบุ dependency ที่ตายตัว; `input/node-output.schema.json` คือสัญญารูปแบบข้อมูล
- `../docs/case-study-source.md` และ `../docs/data-issues.md` เป็นบริบทกับทะเบียนสมมติฐาน

## เลือกผลจาก LAB 002

เลือก `../002_LAB_Loop_FR_NFR/work/fr-nfr-vN.md` โดยแทน N ด้วยรุ่นที่ตรวจจริง อ่าน `work/check-round-N.md` และ `work/loop-log.json` ของ LAB 002 ประกอบ ห้ามเดาว่ารุ่นเลขสูงสุดผ่านแล้ว
หากไม่มีผลงานตนเอง ให้เลือกไฟล์ FR/NFR ใน `../002_LAB_Loop_FR_NFR/reference/` เมื่อมีจริง แล้วบันทึก **ใช้ผลอ้างอิง** พร้อม path และสถานะผลตรวจที่ทราบ
ขณะเตรียมคู่มือมีเพียงไฟล์กันโฟลเดอร์ว่างใน reference จึงให้ fr-nfr-input.md เป็นไฟล์ชี้ทาง ห้ามนำ README หรือ log มาแทนเอกสาร FR/NFR
ถ้ายังไม่มีทั้งสองแหล่ง หยุดที่เตรียม Input และรายงาน “ไม่มีข้อมูล”; ห้ามเรียก node เพื่อให้แต่งข้อกำหนดแทน
หากเอกสารมีข้อ FAIL ให้บันทึกข้อค้างไว้และแก้ที่ LAB 002 ก่อนเริ่ม node ที่พึ่งกฎนั้น

## วิธีคัดลอกสำหรับนักศึกษา

คำสั่งนี้เป็นแบบฟอร์ม ผู้เรียนต้องแทน `<FR_NFR_FILE>` ด้วย path ที่เลือกก่อนรัน ไม่ต้องระบุชื่อบัญชีจริง

```bash
mkdir -p work/logs
SOURCE_FR='<FR_NFR_FILE>'
test -s "$SOURCE_FR" || exit 1
if [ -f work/input-source.md ]; then
  echo 'มีชุดงานเดิม: เก็บทั้งชุดเป็นรุ่นใหม่ก่อน' >&2
  exit 1
fi
cp "$SOURCE_FR" input/fr-nfr-input.md
python3 - "$SOURCE_FR" <<'CHECK'
import hashlib,sys
from pathlib import Path
p=Path('input/fr-nfr-input.md')
origin=sys.argv[1]
kind='ใช้ผลอ้างอิง' if '/reference/' in origin else 'ใช้ผลนักศึกษา'
Path('work/input-source.md').write_text(
    '# ที่มา Input\n\n'+kind+'\nต้นทาง: '+origin+'\nSHA-256: '+
    hashlib.sha256(p.read_bytes()).hexdigest()+
    '\nรุ่น/ผลตรวจ LAB 002: รอนักศึกษาระบุจากหลักฐาน\nข้อค้าง: รอนักศึกษาระบุ\n',encoding='utf-8')
CHECK
```

เปิด `work/input-source.md` เติมรุ่น ผลตรวจ path หลักฐานและข้อค้างตามจริงก่อนขั้น 3.0
การคัดลอกไม่ใช่การตรวจผ่าน ถ้าต้นทางไม่มีผลตรวจให้ระบุว่าไม่มีข้อมูล ห้ามเขียน PASS แทน
เก็บ input snapshot และ SHA-256 เดิมไว้ทุกชุด เพื่อให้รู้ว่าแต่ละ node ใช้ FR รุ่นเดียวกัน
เมื่อเริ่มชุดใหม่ ให้เก็บ work เดิมและ input/fr-nfr-input.md เดิมไว้ด้วย ห้ามทับหลักฐานเก่า

## กติกาแหล่งข้อมูล

หมายเหตุ ก./ค./ช. **ไม่พบนิยามในต้นฉบับ** ใช้เฉพาะข้อความในตารางตาม A-02 และคงสถานะยังไม่ยืนยัน
DI-04/A-03: คงรหัสอ้างใน US-20 ตามต้นฉบับ เสนอการเชื่อมกฎปิด/เปิดกับ US-12/US-13 โดยไม่แก้เงียบ ๆ
DI-07/A-05: แยกสถานะออเดอร์ รายการ ชำระเงิน และโต๊ะ การแมปชื่อสถานะยังไม่ยืนยัน
A-01: การออกแบบเพื่อ Mock-up เป็นการจำลอง ไม่ใช่ธุรกรรมจริงหรือผลทดสอบ NFR
A-06: ใช้เฉพาะ 18 แถวที่เลือก แม้ FR จาก LAB 002 จะกล่าวถึงรหัสอื่นในข้อสงสัย

## ตรวจความพร้อม

ใช้ `python3 input/validate.py --input` ตรวจเบื้องต้น แล้วทำ audit ตามขั้น 3.0
การตรวจอัตโนมัติไม่พิสูจน์ว่ากฎธุรกิจครบ ผู้เรียนต้องตรวจ FR/US และรายงาน LAB 002 เอง
ต้องมี Python 3 และแพ็กเกจ jsonschema สำหรับการตรวจ output; ทดสอบด้วย `python3 -c 'import jsonschema'`
หากไม่มีแพ็กเกจ ให้ติดตั้งในสภาพแวดล้อมเรียนที่เตรียมไว้ก่อนเริ่ม ไม่ถือว่าข้ามการตรวจได้

นับขอบเขต US จากคอลัมน์แรกเท่านั้น ตรวจจำนวนแถวและข้อความตรงต้นฉบับด้วย `python3 input/validate.py --source`
