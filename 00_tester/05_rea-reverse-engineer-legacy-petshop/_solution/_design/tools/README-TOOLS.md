# เครื่องมือทำรูปผล LAB (ใช้ร่วมกันบท 05 และ 06)

แปลงผลจริงใน `results/LABn_RESULT.md` และวิดีโอ Playwright เป็นรูปใน `img/` ตามสไตล์บท 04 (`STYLE-GUIDE.md` §4)

| ไฟล์ | ทำอะไร | ได้ |
|---|---|---|
| `md-table-to-spec.mjs` | ดึงตาราง markdown ตัวที่ N จากไฟล์ .md → spec JSON | `labN-<slug>.json` |
| `render-result.mjs` | spec JSON → ตาราง PNG ธีมมืด (แบบ `04/img/lab0-checklist.png`) | `labN-<slug>.png` กว้าง 2560 px · < 600 KB |
| `webm-to-gif.mjs` | วิดีโอ .webm/.mp4 → GIF ด้วย ffmpeg 2 รอบ (palettegen → paletteuse) | `gif-TC-…gif` กว้าง 960 px · 8 fps · ≤ 3 MB |
| `render-png.mjs` | ไดอะแกรม HTML → PNG (พื้นขาว) | ไดอะแกรม/การ์ด |

ต้องมี: Node 20+ · Playwright 1.63 (หาที่ `PLAYWRIGHT_DIR` → `node_modules` ข้างสคริปต์ → `C:/t/work/a9`) · ffmpeg ใน PATH · อินเทอร์เน็ต (โหลดฟอนต์ Noto Sans Thai จาก Google Fonts ถ้าออฟไลน์จะเตือนและใช้ Leelawadee UI)

> ⚠️ รูปใน `img/` ต้องมาจากผลรันจริงเท่านั้น · ไฟล์ทดลองให้เขียนไว้ใน `C:/t/work/<งาน>/` ก่อน แล้วค่อยคัดลงมา

## 1. ตารางผล → PNG (3 ขั้น)

```powershell
$T = "05_rea-reverse-engineer-legacy-petshop/_solution/_design/tools"
$R = "06_sabai-spa-legacy-change-request/_solution/_design/results"

# ① ดูว่าไฟล์มีกี่ตาราง แล้วเลือกตัวที่ต้องการ
node $T/md-table-to-spec.mjs $R/LAB0_RESULT.md --list

# ② ดึงตารางที่ 1 เป็น spec (เลือกคอลัมน์/แถวได้) · ใช้ --out แทน > เพื่อได้ UTF-8 ไม่มี BOM
node $T/md-table-to-spec.mjs $R/LAB0_RESULT.md 1 --theme 06 `
  --title "LAB 0 · ตรวจเครื่อง" --summary "สรุป: พร้อม 9/9 รายการ" `
  --cols 0,1,2,3 --rows 0-8 --out C:/t/work/img06/lab0-checklist.json

# ③ แก้ JSON ถ้าต้องการ (ตัดคำยาว ใส่ highlight) แล้วเรนเดอร์ · เปิดดูด้วยตาทุกรูปก่อนคัดลง img/
node $T/render-result.mjs C:/t/work/img06/lab0-checklist.json C:/t/work/img06/lab0-checklist.png
```

ผลที่พิมพ์: `lab0-checklist.png · 2560×1600 px · DSF 2 · 159 KB` (ถ้า > 600 KB จะเรนเดอร์ใหม่ที่ DSF 1.5 ให้เอง)

### spec JSON

```json
{
  "title": "LAB 4 · ทดสอบ CR-01",
  "subtitle": "รันจริง 12 ต.ค. 2026 · WEB_PORT 4000",
  "theme": "06",
  "columns": ["#", "กรณี", "ผลที่คาดหวัง", "ผลจริง", "ผ่าน?"],
  "rows": [
    ["E01", "จองปกติ", "฿1,000 − 10% (฿100) = **฿900**", "฿900", "✅"],
    ["E02", "ยกเลิก", "สถานะ `cancelled`", "ไม่เปลี่ยน", "❌"]
  ],
  "highlight": [{ "row": 1, "col": 3, "color": "red" }],
  "summary": ["สรุป: ผ่าน 1/2", "บรรทัดที่ 2 (ถ้ามี)"]
}
```

| ช่อง | ความหมาย |
|---|---|
| `title` | หัวเรื่องสีส้ม · ถ้าไม่มี `—` จะต่อท้ายชื่อระบบตาม theme ให้ (`— PawPantry` / `— สบายใจ สปา`) · ใส่ `"suffix": "…"` เปลี่ยนได้ หรือ `false` ไม่ต่อท้าย |
| `theme` | `"05"` (ค่าเริ่มต้น) หรือ `"06"` · สีเหมือนกันทุกบท (พื้น `#1e1e1e` · หัวเรื่อง `#e8b86d` · หัวคอลัมน์ `#9cdcfe` บนพื้น `#2d2d2d` · เส้น `#444` · สรุป `#88aa88` วัดจากพิกเซลรูปบท 04) ต่างกันแค่ชื่อระบบท้ายหัวเรื่อง |
| `rows` | ใช้ `` `code` `` · `**ตัวหนา**` · `<br>` ได้ · ข้อความยาวตัดบรรทัดเอง (คำไทยตัดด้วย Chromium) |
| `highlight` | `row`/`col` นับจาก 0 (ไม่รวมหัวตาราง) · ไม่ใส่ `col` = ทั้งแถว · สี `red` `green` `yellow` `blue` `orange` `gray` หรือ `#hex` → ตัวอักษรสีนั้น + พื้นจาง |
| `widths` | เช่น `["10%", "30%", …]` เมื่อคอลัมน์ออกมาไม่สวย |
| `align` | ไม่ใส่ = คอลัมน์ที่ทุกช่อง ≤ 4 ตัว (✅ ❌ ตัวเลข) จัดกลาง · คอลัมน์ที่ทุกช่อง ≤ 12 ตัว (`✅ พร้อม` `38/42`) ไม่ตัดบรรทัด |
| `mono` / `monoAuto` | monospace อัตโนมัติ (ยกเว้นคอลัมน์แรก) เมื่อทั้งช่องเป็น `` `code` `` หรือมี `/ . _` ไม่มีอักษรไทยและ ≤ 3 คำ (path, URL, เวอร์ชัน) · `"mono": [2]` บังคับคอลัมน์ · `"monoAuto": false` ปิด หรือ `[1,2]` เลือกคอลัมน์ |

ตัวเลือกเพิ่ม: `--min-height 800` (ค่าเริ่มต้น = กรอบ 1280×800 เหมือนบท 04 ตารางยาวกว่านั้นยืดลงเอง · `0` = ครอปพอดีตาราง) · `--dsf 2` · `--html out.html` (เก็บ HTML ไว้ตรวจ)

ข้อแนะนำ: ตารางเกิน ~15 แถวให้เลือกแถวเด่นด้วย `--rows` แล้วเพิ่มแถว `["…", "อีก 27 แถว (ดู TEST-PLAN.md)", "", ""]` · ห้ามใส่คำเฉลยบั๊กในรูปก่อน LAB ล่าบั๊ก (STYLE-GUIDE §4.3)

## 2. วิดีโอ → GIF

```powershell
ffmpeg -version   # ต้องมี (บท 04 ใช้ 8.0.1)
node $T/webm-to-gif.mjs test-results/booking-chromium/video.webm C:/t/work/img06/gif-TC-CR1-01.gif --ss 1 --to 9
```

- `--ss` / `--to` (หรือ `--t` ความยาว) ตัดช่วง · `--width 960` · `--fps 8` · `--colors 128` · `--max-mb 3`
- ถ้าเกิน 3 MB จะลองใหม่เอง: 96 สี → 64 สี → 6 fps → 800 px → 5 fps · ยังเกินอีก = exit 4 ให้ตัดคลิปสั้นลง
- วงแดงจุดคลิกและป้ายชื่อ test มุมซ้ายล่าง (STYLE-GUIDE §4.1) ต้องใส่ในหน้าเว็บตอนอัดวิดีโอ (fixture ของ Playwright) สคริปต์นี้ไม่วาดเพิ่ม

### 2.1 GIF สไตล์บ้าน (การ์ดไตเติล · ป้ายชื่อ test · เฟรมค้าง + วงแดง · ภาพนิ่งปิดท้าย) → `gif-fx/`

```powershell
node $T/gif-fx/gif-fx.mjs $T/gif-fx/bug01.json        # ตัวอย่าง: img/gif-bug-BUG-01.gif
node $T/gif-fx/gif-fx.mjs $T/gif-fx/gift-03-04.json   # ตัวอย่าง: img/gif-TC-GIFT-03-04.gif
```

- spec JSON: `video` `out` `title{kick,text,sub,foot,dur}` `label` `masks[]` `segments[]` (`clip` ss/to/speed · `hold` at/dur · `still` image/dur · ทุกแบบรับ `caption` `caption_x` `caption_y` `rings[{x,y,w,h,n}]`) · พิกัดเป็นพิกัดวิดีโอต้นฉบับ (1280×800) · รายละเอียดหัวไฟล์ `gif-fx.mjs`
- ข้อความไทยทุกชิ้น (การ์ด ป้าย แถบคำอธิบาย เลขวงแดง) เรนเดอร์ด้วย Chromium headless เป็น PNG โปร่งใสแล้ว ffmpeg ซ้อน — **ห้ามใช้ ffmpeg drawtext / PIL วาดไทย** (วรรณยุกต์พัง)
- หาพิกัดวงแดง: `ffmpeg -ss <t> -i video.webm -frames:v 1 f.png` แล้วเปิดดู · เกิน `max_mb` จะลด 96 สี → 6 fps → 64 สี → 880 → 800 px เอง · `"dither": "none"` ไฟล์เล็กและตัวหนังสือคมกว่า bayer สำหรับหน้าเว็บสีเรียบ

## 3. ทดสอบแล้ว (12 ต.ค. 2026)

ข้อมูลสมมติที่ติดป้าย "ตัวอย่าง" ใน `C:/t/work/tpl/` (ไม่ได้ลง `img/`): `sample-05.json` → PNG 2560×1600 159 KB · `sample-06.json` → 151 KB · แปลง `04/_solution/_design/results/LAB0_RESULT.md` ตารางที่ 1 → 229 KB · วิดีโอ Playwright 1280×800 ~5 วินาที → GIF 960×600 36 เฟรม 0.32 MB · เทียบด้วยตากับ `04/img/lab0-checklist.png` แล้ว สี ระยะ ขนาดตัวอักษรตรงกัน (ไฟล์ใหม่ละเอียดกว่า 2 เท่า)
