# ที่มาชุดตรวจร่วม

สร้างจาก 006_LAB_Test_Scenarios_Traceability/input/ui-scenarios.json ตามตัวอย่างใน README ขั้น 7.3; คง regression นอก US-21 ทั้งหมด และแยก N-1/N จำนวน 3 รอบ reset อิสระ
วันที่ตรึง UTC 2026-09-14T15:20:18.187609+00:00
SHA-256 0143e20088b966a958fc2dd496a9afa3d3ec11d706d07861c0ff0ee374a8f8ed
ตรึงหลังเริ่มการเรียก AI แต่ก่อนอ่านชิ้นงานผลของทั้งสองวิธี จึงไม่ตรงเงื่อนไขตรึงก่อนเรียกทั้งหมด; เป็นข้อจำกัดการทดลอง ไม่ใช่การทดลองควบคุมสมบูรณ์
Baseline ui-scenarios.json ที่ให้ทั้งสองวิธีเป็นดัชนี scenario-set-round-0.json ไม่ใช่ action array จึงไม่เหมาะรันโดยตรง; คงต้นฉบับที่ส่งไว้ ไม่สับเปลี่ยนกลางการเรียก
manifest มี path docs/ui-contract.md ที่ไม่มีจริง: สัญญา v2 จริงอยู่ change-baseline/ui-contract-v2.md; ถือเป็นข้อผิดพลาดการเตรียม input ร่วม ไม่ใช่ประสิทธิภาพ workflow
runner เดิมรองรับ click/fill/expect_* แต่ไม่มี clock advance ด้วย CSS; ชุดนี้ยังไม่พิสูจน์รอยต่อ 00/15/30/45 ทั้งหมดหรือเวลา server/LAN

## รุ่นที่ใช้รันจริง: shared-tests-v2.json

พบ fixture เดิมอ้าง rush-start/rush-end และข้าม nav-capacity ซึ่งไม่ตรง DOM baseline ตาม shared-test-baseline-dom.json จึงแก้ส่วน setup ร่วมเป็น capacity-start/capacity-end และเข้า nav-capacity ก่อนกรอก ไม่เปลี่ยนผลคาดหวัง และไม่แก้ regression นอก US-21
เก็บ shared-tests.json รุ่นแรกไว้ ยังไม่ได้รันชุดรุ่นแรก; ทั้งสองวิธีใช้รุ่น v2 เดียวกัน
ตรึง UTC 2026-09-14T15:25:55.743727+00:00; SHA-256 85cb7472f75ab962e7ea156d4b8fa220f397eb1cf5c635d77c669c5fcec21abc
