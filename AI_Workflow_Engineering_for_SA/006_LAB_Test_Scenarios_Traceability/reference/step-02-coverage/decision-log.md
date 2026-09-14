# บันทึกการตัดสินใจ Loop

วันที่ UTC: 2026-09-14T14:42:21.437735+00:00

- การตรวจตั้งต้น: [round-1/coverage-round-1.md](round-1/coverage-round-1.md) มี GAPS; ส่งรายงานเต็มเข้า prompt แก้ coverage โดยแทนช่อง MISSING
- อนุญาตแก้สูงสุด 2 รอบตามบทเรียน และให้ผู้ตรวจอิสระตรวจหลังแก้ทุกครั้ง; ไม่แก้ผล AI ด้วยมือ
- snapshot ต้นทางคงเดิม; mapping ที่ไม่มีต้องคง MISSING ไม่สร้างข้อมูลใหม่แทน
- manifest ตั้งต้นเก็บ path สัมพันธ์กับตำแหน่ง manifest; ระบุฐาน path จริงใน prompt ที่ใช้ตรวจและแก้ โดยเก็บไฟล์เดิม

- รอบแก้ที่ 1: เพิ่มกรณีตาม D01–D07; ผลและ regression อยู่ใน [fix-1/coverage-fixes-round-1.md](fix-1/coverage-fixes-round-1.md)
- ตรวจหลังแก้: [round-2/coverage-round-2.md](round-2/coverage-round-2.md); ผ่านเงื่อนไขส่งรวมขั้นต่ำ 26 จาก 26 US
- หยุดแก้เมื่อเหลือข้อค้าง upstream/fixture/ข้อมูลธุรกิจที่อยู่นอกขอบเขตการแก้ scenario ในรอบนี้; ไม่ใช้รอบแก้ที่ 2 เพื่อแต่ง mapping หรือคำตอบธุรกิจ
- เลือก [selected-set.md](selected-set.md) และรักษารายงานที่ยังมีช่องว่างไปขั้น merge
