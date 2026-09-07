## สรุปขั้นนี้

อ่าน `requirements.md` แล้ว (v1.1, ป้าย `SIMULATION`, B01–B09 + UAT-01–09 ครบ) — **ไม่ได้แต่งข้อกำหนดเอง**

**หมายเหตุสำคัญ:** ในโฟลเดอร์มี `index.html` อยู่ก่อนแล้ว (สร้างเมื่อ 10:30 วันนี้ ตรงตาม requirements.md และมีป้าย `SIMULATION`) ผมจึง**ไม่เขียนทับทั้งไฟล์** แต่ตรวจเทียบ B01–B09 ทีละข้อ แล้วแก้เพิ่มเพียง 1 บรรทัด (favicon แบบ inline `data:,` เพื่อกำจัด 404 ใน console) — ทุกไฟล์อยู่ใน `/root/workspace/sa-work/006/` ไม่แตะ `/root/workspace/sa-labs/` และไม่อ่าน README ของ LAB

### ไฟล์ในขั้นนี้ (ตามเพดานที่กำหนด)

| ไฟล์ | ขนาด | สถานะ |
|---|---|---|
| `index.html` | 24,123 ไบต์ | ไฟล์เดียวรวม HTML+CSS+JS, ไม่มีการอ้างภายนอก (`http(s)://` / `src=` / `CSS import` / `url()` = 0 จุด) |
| `preview.md` | ≈13 KB | สร้างใหม่ — URL/พอร์ต/ไฟล์/ขอบเขต/สถานะ ไม่มีคำสั่ง shell หรือ PID |

### ฟังก์ชันสำคัญใน `index.html` (ไม่แสดงโค้ดทั้งไฟล์)

| กลุ่ม | ฟังก์ชัน | หน้าที่ |
|---|---|---|
| ค่าคงตัว | `WORKSHOP_NAME`, `TOTAL_SEATS=3`, `STORAGE_KEY="aiDesignWorkshop.bookings.v1"` | ชื่อเวิร์กช็อป, จำนวนที่นั่ง, คีย์ localStorage |
| คำนวณ | `remainingSeats()` | เหลือ = 3 − จำนวนรายการ |
| ตรวจรหัส | `normalizeCode()`, `sameCode()`, `indexOfCode()` | ตัดช่องว่าง/space ล้วน (B03), กันรหัสซ้ำไม่แบ่งตัวพิมพ์ (B03) |
| ที่นั่ง | `lowestFreeSeat()`, `findBySeat()` | จ่ายเลขที่นั่ง 1–3 ที่ว่างต่ำสุด |
| storage | `probeStorage()`, `load()`, `save()`, `showStorageWarning()` | ทดสอบว่าใช้ได้, อ่านกลับ+ทำความสะอาดข้อมูล (กันเกิน 3/ซ้ำ), บันทึก, **แจ้งเมื่อใช้ไม่ได้** (B06/B07) |
| แสดงผล | `render()`, `renderSeats()`, `renderList()`, `setStatus()` | อัปเดตตัวเลข/การ์ดที่นั่ง/รายการ+ปุ่มยกเลิก/ข้อความไทย `role="status"` `aria-live="polite"` (B09) |
| เหตุการณ์ | `book()`, `cancel(code)`, `resetAll()` | จอง (ปฏิเสธเมื่อว่าง/ซ้ำ/เต็มพร้อมเลข 0), ยกเลิกคืนที่ทันที, เริ่มใหม่ล้าง storage (B03–B05, B07) |
| keyboard | `keepFocus()`, `findByKey()` | คืน focus ให้ปุ่มหลัง re-render; ปุ่มจองเป็น `type="submit"` → **Enter จองได้**; ลำดับ Tab = ช่องกรอก → จอง → ยกเลิก → เริ่มใหม่ (B08) |

### ส่วนติดต่อผู้ใช้ (id ที่ใช้อ้างอิงตอนตรวจ)

`#workshop-title` · `#seat-total`/`#seat-booked`/`#seat-left` · `#state-line` · `#seats .seat` (3 ใบ) · `<label for="learner-code">` + `#learner-code` (ช่องเดียว ไม่มีชื่อ/อีเมล/เบอร์โทร) · `#code-hint` · `#book-btn` · `#status` (live) · `#booking-list` + ปุ่ม `[data-cancel]` · `#list-count`/`#empty-note` · `#reset-btn` · `#storage-warn` (`role="alert"`, ซ่อนเมื่อ storage ใช้ได้)

### เซิร์ฟเวอร์และการตรวจหน้า (ไม่รอ process)

| หัวข้อ | ผล |
|---|---|
| URL / พอร์ต | `http://0.0.0.0:8080/index.html` (หรือ `http://127.0.0.1:8080/index.html`) — bind `0.0.0.0`, พอร์ต 8080 ว่างจึง**ไม่ต้อง**ใช้พอร์ตสำรอง |
| โหมด | background, ให้บริการโฟลเดอร์ `/root/workspace/sa-work/006/` |
| HTTP | `200`, 24,123 ไบต์ |
| viewport 375×812 | `scrollWidth − clientWidth = 0`, ชิ้นส่วนเลยกรอบ = 0 |
| ค่าเริ่มต้น | 3 / 0 / 3, การ์ดที่นั่ง 3 ใบ, label 1 + input 1 (text), ปุ่มคงที่ 2 ตัว |
| console / page error | ไม่มี |
| syntax JS | ผ่าน |
| localStorage | ใช้งานได้ → แถบเตือนยังซ่อน (คีย์เกิดเมื่อจองครั้งแรก) |

**สิ่งที่ไม่ได้ทำ (ตั้งใจ):** ไม่ได้รัน UAT-01–UAT-09 (การจอง/ปฏิเสธ/ยกเลิก/refresh/keyboard/ขาวดำ) จึงยังไม่มีผลผ่าน-ไม่ผ่าน และไม่สร้างสคริปต์ UAT/ไฟล์ผล/ภาพ ตามคำสั่ง — ตรวจเฉพาะ sanity check ของการโหลดและเลย์เอาต์ โดยใช้ Chromium ที่มีอยู่ในเครื่อง (ไม่ดาวน์โหลดอะไรเพิ่ม)

หยุดรอที่ขั้นนี้ครับ ไม่ทำขั้นถัดไปเอง
