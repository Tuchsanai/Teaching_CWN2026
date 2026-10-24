# rea/ — เครื่องมือส่องระบบด้วย REA (รันจากรากบทใน PowerShell)

| ไฟล์ | ทำอะไร |
|---|---|
| `Dockerfile` | image `rea-lab:6.4.0` = REA 6.4.0 + Chromium (build ครั้งเดียวก่อนเข้าคลาส: `docker build -t rea-lab:6.4.0 rea`) |
| `rea.ps1` | เรียก REA ใน container · mount รากบทเป็น `/work` · path ที่ส่งให้ REA ต้องขึ้นต้น `/work/` · เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 …` · ทิ้งบรรทัด progress (`rea_progress`) ที่ REA พ่นลง stderr ให้เอง (error อื่นและ exit code ยังอยู่ · อยากเห็น progress ใส่ `-Progress`) |
| `rea-input.mjs` | ห่อผล REA เป็น input ของคำสั่งถัดไป (`trace` `s2b` `compare` `view`) |
| `rea-summarize.mjs` | ย่อผล REA ก้อนใหญ่ให้อ่านได้ (`--md` ตาราง · `--all` ทุกแถว · `--samples` body ตัวอย่างแบบย่อของ API ใน HAR/scenario · `--png` ภาพสุดท้ายของ scenario · `--s2b-table` ตาราง 4 ทิศ) · key ของ HAR แสดง 2 ชั้น (`order{…,giftWrap}`) · ผล analyze มีคอลัมน์ method ที่ helper อ่านจาก bundle ตรงตำแหน่งที่ REA ชี้ (REA ไม่บันทึก method เอง) และตาราง `electron-renderer` = ไฟล์ HTML ที่ REA ตีความ ไม่ใช่แอป Electron |
| `record-har.mjs` | เดินเส้นทางหลักของร้านแบบ headless แล้วเก็บ HAR (`--out <โฟลเดอร์>` · ค่าเริ่มต้น `out\`) |
| `scenario-coupon.json` | สคริปต์ให้ REA ขับเบราว์เซอร์ (ใช้กับ `-Network pawpantry05_default`) |
| `scratch/` | ที่วางสคริปต์ Playwright ชั่วคราว (ใช้ playwright ของโฟลเดอร์นี้ · ไม่ถูก commit) |

- ทำไมต้อง `-Out`: `>` ของ PowerShell 5.1 ได้ไฟล์ UTF-16/มี BOM ซึ่ง REA ไม่รับเป็น input
- ผลใน `out\` ใหญ่หลายสิบ MB **ห้ามให้ AI เปิดตรง ๆ** ให้ย่อด้วย `node rea\rea-summarize.mjs` เท่านั้น
- ไฟล์ `.har` มีรหัสผ่าน/cookie จริง ห้ามส่งต่อหรือ commit
