# ASSETS · รูปและเสียงของเว็บ สบายใจ สปา

- ไม่มีรูปหรือเสียงจากอินเทอร์เน็ต · รูปทั้งหมดอยู่ที่ `public/assets/` ยกเว้นรูปสัดส่วนร่างกาย before/after ที่อยู่ `private/photos/` (นอก public เสิร์ฟผ่าน `/api/photos/:id` ที่ตรวจเจ้าของ · NFR-11)
- รูปจาก Codex: สั่ง `codex exec "..."` ให้ใช้เครื่องมือสร้างรูปในตัวทีละรูป (โทนไทยร่วมสมัย เขียวใบตอง ครีม ทอง) → คัดลอกจาก `~/.codex/generated_images` → ย่อด้วย `node scripts/resize.mjs <โฟลเดอร์รูป>` (sharp: กว้าง ≤ 1600px · panorama ≤ 4096px · webp)
- Codex สร้างสำเร็จครบทุกรูป (23 รูป) จึงไม่มีรูปไหนต้องใช้ SVG แทน · ลวดลายไทย ไอคอน และกราฟวาดด้วย SVG/CSS ตามที่ออกแบบไว้
- ใบหน้าตัวอย่างและนักบำบัดเป็นภาพวาด ไม่ใช่คนจริง · รูปร่างกาย before/after ไม่มีใบหน้า

| ไฟล์ | ใช้ที่หน้าไหน | สร้างด้วย |
|---|---|---|
| `public/assets/hero.webp` | `/` hero | Codex |
| `public/assets/svc-s01.webp` | `/`, `/services` (S01 นวดไทย 60) | Codex |
| `public/assets/svc-s02.webp` | `/services` (S02 นวดไทย 90) | Codex |
| `public/assets/svc-s03.webp` | `/services` (S03 ประคบสมุนไพร) | Codex |
| `public/assets/svc-s04.webp` | `/`, `/services` (S04 นวดน้ำมันอโรมา) | Codex |
| `public/assets/svc-s05.webp` | `/services` (S05 นวดเท้า) | Codex |
| `public/assets/svc-s06.webp` | `/services` (S06 ขัดผิวสมุนไพร) | Codex |
| `public/assets/svc-s07.webp` | `/services`, `/quiz` (S07 ทรีตเมนต์หน้า) | Codex |
| `public/assets/svc-p01.webp` | `/`, `/services`, `/package`, `/quiz` (P01 Bangkok Relax) | Codex |
| `public/assets/svc-k01.webp` | `/services`, `/quiz` (K01 คอร์สกระชับสัดส่วน) | Codex |
| `public/assets/thr-t01.webp` … `thr-t06.webp` (6 ไฟล์) | `/therapists` (ภาพวาดนักบำบัด T01–T06) | Codex |
| `public/assets/gc-orchid.webp` | `/giftcard` ลายกล้วยไม้ | Codex |
| `public/assets/gc-lotus.webp` | `/giftcard` ลายบัว | Codex |
| `public/assets/gc-gold.webp` | `/giftcard` ลายทอง | Codex |
| `public/assets/pano-couple.webp` | `/book` (จองคู่) ปุ่ม "ดูห้อง 360°" — panorama 2:1 | Codex |
| `public/assets/face-sample.webp` | `/skin` ใบหน้าตัวอย่างแบบภาพวาด (วิเคราะห์ผิว + ภาพจำลองก่อน/หลัง) | Codex |
| `private/photos/c01-before.webp` | `/wallet` ผ่าน `/api/photos/1` (เฉพาะเจ้าของ C01) | Codex |
| `private/photos/c01-after.webp` | `/wallet` ผ่าน `/api/photos/2` (เฉพาะเจ้าของ C01) | Codex |
| `public/favicon.svg` | ไอคอนแท็บทุกหน้า (ดอกบัว) | SVG |
| `components/ThaiOrnament.tsx` (Lotus, Orchid, GoldDivider) | ลายบัว/กล้วยไม้ที่หน้าแรก หน้าจอง และหัวทุกหน้า (FR-32) | SVG |
| `app/globals.css` (ลายจุดทองพื้นหลัง, แถบกนกใต้ header, เส้นทอง) | ทุกหน้า | CSS |
| `components/WaistChart.tsx` | `/wallet` กราฟรอบเอว | SVG |
| ไอคอนแชทลอย (ในเลย์เอาต์) | ทุกหน้า | SVG |
| เพลงสปา (`components/MusicToggle.tsx`) | ปุ่มเปิด/ปิดเพลงที่ header ทุกหน้า — สร้างเสียงสดด้วย Web Audio API (คอร์ดเพนทาโทนิก + ระฆังลำดับตายตัว) ไม่มีไฟล์เสียง ไม่ autoplay | Web Audio (โค้ด) |

รวม: รูปจาก Codex **23 รูป** (public 21 + private 2) · SVG/CSS **0 รูปแทนที่** (มีเฉพาะลวดลาย/ไอคอน/กราฟ 5 รายการที่ออกแบบเป็น SVG/CSS ตั้งแต่แรก)
