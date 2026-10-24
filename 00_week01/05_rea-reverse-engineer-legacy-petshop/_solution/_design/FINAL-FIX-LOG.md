# FINAL-FIX-LOG · บท 05 (FIX5 · 12 ต.ค. 2026)

ใช้ FINAL-REVIEW-V1/V2/V3 · ไม่รันเว็บ · ไม่แตะ git · README ตัดเป็น 4 chunk ให้ trimmer A–D ทำขนาน แล้วประกอบด้วย `C:/Users/oishi/AppData/Local/Temp/claude/fix5/assemble.sh` (ตรวจ: code block ตรง PROMPTS.md · หัวข้อเดิมทุกบรรทัด · รูปครบลำดับเดิม · alt ≤ 300 ตัวอักษร · ลิงก์ไม่หาย)

**ขนาด README: 308,763 → 250,399 B** (ยังไม่ถึง ~200 KB · ส่วนที่ตัดไม่ได้: พรอมต์ ~75 KB + พรอมต์ในตาราง ~11 KB) · ลิงก์/anchor README + fast_track + _solution/README = 128 ลิงก์ เสีย 0 · พรอมต์ README = PROMPTS.md ทุกตัวอักษร (15/15)
⚠️ ตอนประกอบ trimmer B C ยังไม่ส่งรายงานปิดงาน (A D เสร็จ) (ไฟล์ chunk ผ่านตัวตรวจแล้ว) → ถ้า chunk ถูกแก้ต่อ ให้รัน `sh .../fix5/assemble.sh` ซ้ำ

## D15 · กันเฉลยรั่ว
| รายการ | ผล |
|---|---|
| พรอมต์ LAB 1–10 (11 จุด) ใน PROMPTS.md = README | ✅ "ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)" |
| LAB 1 settings.json + CLAUDE.md | ✅ deny `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` + ข้อห้ามใน CLAUDE.md |
| **เบี่ยงจาก BRIEF D15** | `Read(./README.md)` ทดสอบจริง (`claude -p` sonnet · `C:/t/work/fix5deny-*`) **กัน petshop/README.md ด้วย** (pattern ไม่มี / = ทุกระดับ) → ใช้ `Read(/README.md)` · ชุดรวม Edit 5 + Read 3: 3 เป้าถูกปฏิเสธทั้ง Read/Grep · petshop/README.md อ่านได้ · **บท 06 ต้องใช้แบบเดียวกัน** |
| fast_track 🅰️ 🅱️ | ✅ ขั้น 1 เพิ่ม Read deny + ข้อห้ามใน CLAUDE.md (ข้อ 3 เดิมห้ามอยู่แล้ว) |
| `_solution/.claude/settings.json` · `_solution/CLAUDE.md` · `_solution/README.md` | ✅ อัปเดตสถานะปลายทาง + หมายเหตุว่าเพิ่มหลังรอบจริง |
| LAB 2 ข้อ 6(3) ที่สั่งเปิด README | ✅ อ้างประโยค skill ของ REA แทน |
| 🔁 prompt PR-2/PR-3/หยุดก่อน · แถว "เทียบกับเฉลย" | ✅ (D) ขยายข้อห้าม · แถวเทียบเฉลยบอกให้ลบ rule `_solution` ก่อน |

## V1
| ID | ผล |
|---|---|
| N1 HAR 2,447 entries | ✅ (B) ติด "รอบจริงก่อนแก้พรอมต์ · ไม่กรอง ~40 MB" |
| N2 test:all 46/231 | ✅ (C) ติด "รอบจริงก่อนแก้พรอมต์" + ยังไม่ยืนยัน |
| N3 N4 N5 N6 N7 | ✅ (B/C) |
| 👀 29 bullet | ✅ M ทั้ง 7 + m ที่เหลือตามเพดาน ≤ 4 ใหม่ต่อ LAB (LAB 3 +ethics · LAB 7 +trace) · รวมกับ bullet เดิมที่ซ้ำ |

## V2
| ID | ผล |
|---|---|
| 01–04 GIF | ✅ GIFFX render ใหม่ · alt README sync จาก IMAGES-NOTES (≤ 300) |
| 05 / V3 F7 fast_track placeholder | ❌ ไม่ทำ: รอผลรอบ fast track ที่กำลังรัน |
| 06 LAB 7/10 คำตอบซ่อนแต่ ✅ เห็น | ✅ (C) ตัดคำตอบซ้ำใน ✅ + บรรทัดเตือน "อ่าน ✅ หลังทำเสร็จ" (ภาพ lab7-impact/lab10-solo ยังมีคำตอบ) |
| 07 08 09 | ยอมรับตามรีวิว |
| 10 / V3 F17 concept .py | ✅ แก้ทาง caption เท่านั้น (ไม่สร้างภาพใหม่) |
| 11 | ❌ ไม่บังคับ |
| 12 13 | ✅ alt concept-08 · safe-change-loop.html ขั้น 5 แก้ + render PNG ใหม่ |
| 14 ส่งปกติ ในภาพ lab9 | ❌ ต้อง render ภาพผลใหม่ |

## V3
| ID | ผล |
|---|---|
| F1 | ✅ (ดู D15) |
| F2 | ✅ บรรทัด "อ่านก่อน LAB 0" |
| F3 / D16 | ⚠️ alt ทุกรูป ≤ 300 · README 251 KB (ยังสูงกว่าเป้า ~200 KB) |
| F4 boilerplate shell | ❌ เปลี่ยนพรอมต์มาก ต้องรัน LAB ซ้ำยืนยัน |
| F5 | ✅ (D) +2 แถว · รวมแถวหยุดก่อน |
| F6 | ✅ 🧰 แถว git + LAB 9 ทางสำรองถ้าไม่ใช่ git repo |
| F8 trace ใน impact | ✅ LAB 7 ข้อ 2 · seed ทดสอบจริงกับ `out\v1-server.json` ของ RUN05 (9.5 s · 26 node · source_files = 2 route.ts + chunk CheckoutForm · ไม่เห็น lib/*) · ยังไม่รัน LAB 7 ทั้งพรอมต์ |
| F9 จริยธรรม | ✅ LAB 3 ข้อ 5 "ขอบเขตที่ได้รับอนุญาต" + รูบริกข้อ 5 |
| F10 | ✅ LAB 9 คอลัมน์ "ที่มาของผลคาดหวัง [D]/[R]/[E]" |
| F11 | ✅ 📖 +8 ศัพท์ · ร้อยแก้ว/พรอมต์ test → เทสต์ (ตามบท 06 · คงในโค้ด หัวข้อ alt และคำผสมอังกฤษ) |
| F12 F13 F14 F18 F19 F20 F21 F22 F23 | ✅ (F23: oracle-badges-e.html แก้ [A] + render ใหม่ · concept-12 ภาพยังเขียน "[A] AI" แก้ทาง alt) |
| F15 ลำดับ concept | ✅ rename 13→12 14→13 15→14 12→15 18→16 16→17 17→18 · อัปเดตอ้างอิงใน 05 (README fast_track _design) และ 06 (README-PART-A LESSON-PLAN REVIEW-PLAN-V1) · ตรวจ path บท 06 → ครบ |
| F16 | ✅ §17 ใช้ `../06_.../img/concept-10-impact-ripple.jpg` (ภาพมีอยู่แล้ว ฉากสปา · ระบุใน alt) · concept-23 ย้ายไป LAB 9 |
| §6 ข้อที่ "แก้ที่บท 06" (อ้างข้อ 3/4/7 · ตาราง 📦) | ❌ นอกขอบเขต → ส่งผู้ดูแลบท 06 |
