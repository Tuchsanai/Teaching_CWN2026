สร้าง [input-audit.md](../baseline-filtered-v2/input-audit.md) แล้ว

ผล **INPUT_READY เฉพาะการวางแผนเอกสารและ offline mock**

- SHA-256 ตรงครบ 10/10 ไฟล์ มีผลตรวจ upstream ครบ
- US ตั้งต้นครบ 18 แถว ไม่พบการขยายเนื้อหานอกขอบเขต
- คงข้อค้างหมายเหตุ ก./ค./ช. และ mapping; UI ยังไม่มี ETA ของ US-07
- ยังไม่ตรวจ Flow หลังกรองครบทุกเกณฑ์ ไม่รัน browser หรือทดสอบระบบจริง

สร้างเฉพาะไฟล์ audit และไม่แก้ baseline เดิม