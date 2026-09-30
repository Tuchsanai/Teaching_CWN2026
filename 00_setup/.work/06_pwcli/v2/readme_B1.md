## ส่วน B · LAB ย่อย (ง่าย → ยาก)

ทุก LAB ทำแบบเดียวกัน: เปิด Terminal ใน JupyterLab ของ container → `cd /workspace && yolo1` → คัดลอกกรอบ 💬 ทั้งกรอบไปวาง → รอจน AI ทำเสร็จ → ตรวจตาม ✅
พรอมต์ทุกอันผ่านการทดสอบจริงแล้ว โดยให้ `yolo2 -p --model sonnet "<พรอมต์>"` รันใน container ใหม่ที่ไม่มีบริบทอะไรเลย (จำลองนักศึกษา) ไล่ LAB 1 → 7 ต่อกันใน `/workspace` เดียว

### LAB 1 · เตรียม playwright-cli

🎯 **เป้าหมาย:** มีคำสั่ง `playwright-cli` และ config ที่ใช้ได้ใน container แล้วลองเปิดเว็บง่าย ๆ ครั้งแรก ได้เห็น snapshot และ ref จริงครั้งแรก

💬 **พรอมต์**

```text
{{PROMPT:lab1}}
```

📖 **คำอธิบาย**

1. **wrapper แทน alias:** ใน image มี `playwright-cli` อยู่แล้วแต่ซ่อนอยู่ใน `@playwright/mcp` AI จึงสร้างไฟล์ 2 บรรทัดที่ `/usr/local/bin` เพื่อเรียกมัน
   ใช้ไฟล์แทน `alias` เพราะ alias ใช้ได้เฉพาะ shell ที่พิมพ์เอง ถ้าโค้ด Python เรียกผ่าน `subprocess` (LAB 5–7) จะมองไม่เห็น alias
2. **config:** CLI อ่าน `.playwright/cli.config.json` จากโฟลเดอร์ที่รันคำสั่ง

   | ค่า | เหตุผล |
   |---|---|
   | `chromiumSandbox: false` | container รันเป็น root ซึ่ง sandbox ของ Chromium ไม่ยอมให้เปิด |
   | viewport 1920×1080, `deviceScaleFactor: 2` | `screenshot --hires` ได้ภาพ 3840×2160 คมชัด (A3: box ×2) |
   | `locale: en-US` | ข้อความบนเว็บเป็นภาษาอังกฤษตรงกับที่โค้ดใช้ verify |
   | `outputDir` | ไฟล์ที่ CLI สร้างอัตโนมัติ (snapshot ทุกครั้งที่ open/click) ไปอยู่ใน `pwcli-out/` ไม่รก `/workspace` |
   | (ไม่ตั้ง `headless`) | ค่าเริ่มต้นเป็น headless ซึ่งเหมาะกับ container ที่ไม่มีจอ |

3. **ทดสอบทีละคำสั่ง:** `open` เปิดเบราว์เซอร์ค้างไว้เป็น session → `snapshot` / `screenshot` ใช้ session เดิม → `list` เห็นว่าเปิดอยู่ → `close` แล้ว `list` ต้องว่าง (A10)

🔍 **snapshot เทียบหน้าเว็บจริง**

![ซ้าย: หน้า example.com จริงมีกรอบสีตาม box ของ paragraph สองอัน และลิงก์ Learn more; ขวา: บรรทัด YAML เดียวกัน](img/lab1-compare.png)

```yaml
- paragraph [ref=e7] [box=752,419,416,77]: This domain is for use in documentation examples without needing permission. ...  # ①
- paragraph [ref=e10] [box=752,406,416,102]: L’usage de ce domaine est réservé à des exemples de documentation, ...     # ②
- link "Learn more" [ref=e13] [cursor=pointer] [box=919,537,83,26]:                                                       # ③
    - /url: https://iana.org/help/example-domains
```

- ① `paragraph` = role ย่อหน้า ไม่มีชื่อในเครื่องหมายคำพูด ข้อความหลัง `:` คือเนื้อหา box ตรงกับข้อความภาษาอังกฤษบนจอพอดี
- ② ข้อสังเกตจริง: example.com มีย่อหน้าภาษาอื่นซ้อนอยู่ในตำแหน่งเดียวกันแต่มองไม่เห็นบนจอ snapshot ก็ยังแสดง → **สิ่งที่อยู่ใน snapshot ไม่จำเป็นต้องมองเห็นบนจอ** นี่คือเหตุผลที่เราต้องมีทั้ง snapshot และ screenshot
- ③ `link` มีชื่อ `"Learn more"`, ref `e13`, `[cursor=pointer]` = กดได้, บรรทัดลูก `/url:` = ปลายทางของลิงก์

✅ **ผลที่ควรได้** (สรุปจริงจาก AI + ตัดตอน `lab1/lab1.txt`)

```text
- เวอร์ชัน: playwright-cli 1.64.0-alpha-1790635538000
- ลิงก์ "Learn more": อยู่บรรทัดที่ 8 ของ example.yml (link "Learn more" [ref=e13], box=919,537,83,26)
- ขนาดภาพ example.png: 3840×2160 px (viewport 1920×1080 คูณ deviceScaleFactor 2)

$ playwright-cli list
### Browsers
- default:
  - status: open
  - browser-type: chromium
  - user-data-dir: <in-memory>
  - headed: false

$ playwright-cli close
Browser 'default' closed

$ playwright-cli list
  (no browsers)
```

**วิธีตรวจ:** `playwright-cli --version` ได้เลขเวอร์ชัน · `cat /workspace/.playwright/cli.config.json` มี `"chromiumSandbox": false` · `lab1/example.png` กว้าง 3840 px · `playwright-cli list` ตอนจบได้ `(no browsers)`

---

### LAB 2 · "ตา" อ่านหน้าเว็บเป็น snapshot

🎯 **เป้าหมาย:** เห็นว่า agent "มองเห็น" Google Flights อย่างไร จับคู่บรรทัด YAML กับช่องบนจอ และลองเครื่องมือช่วยอ่าน snapshot ยาว ๆ (`grep`, `find`, partial snapshot)

💬 **พรอมต์**

```text
{{PROMPT:lab2}}
```

📖 **คำอธิบาย**

1. `open` แล้วเช็กหน้าคุกกี้ก่อน (ในการรันของเราจาก Thailand ไม่มีหน้าคุกกี้)
2. ถ่าย `snapshot --boxes` และ `screenshot --hires` **ต่อกันทันที** เพื่อให้ภาพกับ YAML เป็นหน้าสถานะเดียวกัน ถ้าหน้าเปลี่ยนระหว่างนั้น box จะไม่ตรงภาพ
3. `grep -n` ดึงเฉพาะบรรทัดช่องกรอก พร้อมเลขบรรทัด ใช้อ้างอิงได้ (A8: หลักฐานต้องชี้บรรทัดได้)
4. `find "ticket type"` ให้ CLI ค้นใน snapshot แล้วตอบเฉพาะกิ่งที่เกี่ยว พร้อมพ่อแม่ของมัน
5. **partial snapshot** `snapshot <ref>` เอาเฉพาะใต้ element หนึ่งตัว AI หา `search "Flight"` ที่ครอบฟอร์ม แล้ว snapshot เฉพาะส่วนนั้น → สั้นลงมาก เป็นวิธีหนึ่งของการ "ตัด snapshot" (A6)

🔍 **snapshot เทียบหน้าเว็บจริง**

![ซ้าย: ฟอร์มค้นหาของ Google Flights มีกรอบสี 7 กรอบ; ขวา: บรรทัด YAML 7 บรรทัดสีและเลขตรงกัน](img/lab2-compare.png)

```yaml
- combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer] [box=480,400,138,36]:   # ① ประเภทตั๋ว
- button "1 passenger, change number of passengers." [ref=e113] [box=622,400,80,36]:          # ② จำนวนผู้โดยสาร
- combobox "Change seating class. Economy" [ref=e126] [cursor=pointer] [box=707,400,103,36]:   # ③ ชั้นโดยสาร
    - combobox "Where from?" [ref=e136] [box=480,444,282,56]: Bangkok                          # ④ ต้นทาง ค่า = Bangkok
  - combobox "Where to?" [active] [ref=e149] [box=770,444,282,56]                              # ⑤ ปลายทาง กำลังโฟกัส
  - textbox "Departure" [ref=e168] [box=1116,445,138,54]                                       # ⑥ วันไป
  - textbox "Return" [ref=e172] [box=1285,445,138,54]                                          # ⑦ วันกลับ
```

- ①③ เป็น `combobox` (กดแล้วมีรายการให้เลือก) ชื่อรวมค่าปัจจุบันไว้ด้วย: `Round trip`, `Economy`
- ② บนจอเห็นแค่ไอคอนคนกับเลข 1 แต่ name ยาวกว่ามาก เพราะมาจาก `aria-label` ที่เขียนให้โปรแกรมอ่านหน้าจอ
- ④ ค่า `Bangkok` อยู่หลัง `:` เป็น value (Google เดาจากตำแหน่งของเครื่อง) ⑤ `[active]` = เคอร์เซอร์อยู่ที่ช่องนี้
- ⑥⑦ box ของ textbox เริ่มที่ x=1116 ไม่รวมไอคอนปฏิทิน เพราะไอคอนไม่ใช่ส่วนของช่องพิมพ์

✅ **ผลที่ควรได้** (สรุปจริงจาก AI)

```text
| ไฟล์ | บรรทัด |
| flights.yml (ทั้งหน้า) | 252 |
| form-partial.yml (snapshot e99) | 23 |

partial snapshot เล็กลงประมาณ 11 เท่า ref ที่ใช้คือ e99 เป็น search "Flight" ซึ่งเป็นบรรพบุรุษที่ครอบฟอร์มค้นหา

ข้อสังเกต
- pattern button "(Search|... ไม่พบปุ่ม Search เพราะยังไม่ได้กรอกปลายทาง ตอนนี้มีแค่ปุ่ม "Explore destinations" (e176)
  กับปุ่ม "Swap origin and destination." (disabled)
- element ที่เป็นแค่ตกแต่งจะไม่มี ref เช่น generic [aria-hidden]
```

`lab2/find.txt` (จริง):

```text
### Result
Found 1 match for "ticket type":

- generic [ref=e1]:
  - generic [ref=e93]:
    - generic [ref=e97]:
      - search "Flight" [ref=e99]:
        - generic [ref=e101]:
          - generic [ref=e102]:
            - combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer]:
              - generic [aria-hidden]:
                - generic: Round trip
            - button "1 passenger, change number of passengers." [ref=e113]:
```

**สังเกต:** ปุ่ม Search **ยังไม่มี** ในหน้าแรก (จะโผล่หลังเลือกปลายทาง) และ `button "Swap origin and destination." [disabled]` ไม่มี ref เลย (ข้อสังเกต: element ที่ disabled ไม่ได้ ref เพราะกดไม่ได้)
agent จึงต้องอ่านหน้าจริงทุกรอบ ไม่ใช่จำหน้าตาเว็บไว้ล่วงหน้า

**วิธีตรวจ:** เปิด `lab2/flights.png` คู่กับ `lab2/form.txt` แล้วหา element ตาม box ได้ · `wc -l lab2/*.yml` partial สั้นกว่าทั้งหน้ามาก

---

### LAB 3 · "มือ" กดและกรอกด้วย ref

🎯 **เป้าหมาย:** สั่ง click / fill ด้วย ref ทีละคำสั่ง และ **verify ด้วย snapshot ใหม่ทุกครั้ง** (ยังไม่มี LLM ผู้ตัดสินใจ AI ใน yolo1 ทำตามขั้นที่เราเขียนไว้)

💬 **พรอมต์**

```text
{{PROMPT:lab3}}
```

📖 **คำอธิบาย**

1. ทุกครั้งที่จะกด AI ต้องอ่าน ref จาก snapshot **ล่าสุด** ก่อน (A4) พรอมต์จึงสั่งให้ snapshot หลังทุก action
2. ลำดับที่เกิดขึ้นจริงและ ref ที่ใช้ (จากการรันทดสอบ):

   | ขั้น | คำสั่ง | ref มาจาก | Playwright ที่รันจริง |
   |---|---|---|---|
   | เปิดรายการประเภทตั๋ว | `click e107` | s1 | `getByRole('combobox', { name: 'Change ticket type. Round trip' }).click()` |
   | เลือก One way | `click e541` | s2 | `getByRole('option', { name: 'One way' }).click()` |
   | เปิดช่องต้นทาง | `click e637` | s3 | `getByRole('combobox', { name: 'Where from?' }).click()` |
   | พิมพ์ BKK | `fill e735 BKK` | s4 | `getByRole('combobox', { name: 'Where else?' }).fill('BKK')` |
   | เลือกสนามบิน | `click e852` | s5 | `getByRole('option', { name: 'Suvarnabhumi Airport (BKK)' }).click()` |

3. **เรื่องที่เจอจริง:** คลิก `Where from?` แล้ว ช่องที่พิมพ์ได้กลายเป็น **อีก element หนึ่ง** ชื่อ `combobox "Where else?" [expanded]` ถ้า AI ใช้ ref `e637` เดิมพิมพ์ จะพิมพ์ผิดช่องหรือ error ต้องอ่าน snapshot ใหม่จึงรู้
4. ref ของ option `Suvarnabhumi Airport (BKK)` ก่อนพิมพ์คือ `e759` หลังพิมพ์ BKK รายการถูกสร้างใหม่กลายเป็น `e852` อีกตัวอย่างของ A4

🔍 **snapshot เทียบหน้าเว็บจริง** (`lab3/final.yml` + `lab3/final.png` หลังทำครบ)

![ซ้าย: ฟอร์มหลังเลือก One way และต้นทาง Bangkok BKK มีกรอบสี 4 กรอบ; ขวา: บรรทัด YAML ที่พิสูจน์ผล](img/lab3-compare.png)

```yaml
- combobox "Change ticket type. One way" [ref=e873] [cursor=pointer] [box=480,400,127,36]:   # ① ชื่อเปลี่ยนเป็น One way
    - combobox "Where from? Bangkok BKK" [active] [ref=e876] [box=480,444,282,56]: Bangkok   # ② ชื่อมี BKK แล้ว
  - combobox "Where to?" [ref=e878] [box=770,444,282,56]                                     # ③ ยังว่าง
- textbox "Departure" [ref=e879] [box=1116,445,308,54]                                       # ④ ไม่มีช่อง Return แล้ว
```

- ① ② คือ "หลักฐาน" ของการกด: ชื่อ element เปลี่ยนตามสถานะ (`Round trip` → `One way`, `Where from?` → `Where from? Bangkok BKK`)
- ④ ช่อง `Return` หายไปเพราะเลือก One way แล้ว และ box ของ Departure กว้างขึ้น (138 → 308)
- ref ทุกตัวเปลี่ยนหมดเทียบกับ LAB 2 (`e107` → `e873`) เพราะฟอร์มถูก render ใหม่

✅ **ผลที่ควรได้** (สรุปจริงจาก AI)

```text
บรรทัดที่พิสูจน์ใน lab3/final.yml
- บรรทัด 31: combobox "Change ticket type. One way" [ref=e873]
- บรรทัด 42: combobox "Where from? Bangkok BKK" [active] [ref=e876]: Bangkok

- ชื่อช่องต้นทาง: หลังคลิก "Where from?" ช่องที่ [expanded] ถูกเปลี่ยนชื่อเป็น "Where else?" (ref=e735)
  ผมจึง fill BKK ที่ ref นั้น ตาม snapshot ล่าสุด
```

**วิธีตรวจ:** `grep -n 'One way\|BKK' lab3/final.yml` เจอสองบรรทัดข้างบน · `grep -c "await page" lab3/actions.txt` นับคำสั่งที่รันจริงได้ · ใน `actions.txt` ไม่มี `Error`

---

### LAB 4 · ref เก่าใช้ไม่ได้

🎯 **เป้าหมาย:** เห็น error จริงเมื่อใช้ ref จาก snapshot เก่า และเห็นว่าแก้ได้ด้วยการ snapshot ใหม่ (A4)

💬 **พรอมต์**

```text
{{PROMPT:lab4}}
```

📖 **คำอธิบาย**

1. AI จด ref ของ combobox ประเภทตั๋วจาก `old.yml` ได้ `e107` แล้วใช้มันเปิด dropdown ได้ปกติ (ตอนนั้นยังเป็น snapshot ล่าสุด)
2. หลังเลือก One way หน้า render ใหม่ พอสั่ง `click e107` อีกครั้ง CLI ปฏิเสธทันทีและคืน exit code 1 **โดยไม่กดอะไรบนหน้าเลย** นี่คือ fail-closed ของตัว CLI เอง
3. snapshot ใหม่พบว่า combobox ตัวเดิม (ตำแหน่งเดิมบนจอ) ตอนนี้คือ `e634` และชื่อเปลี่ยนเป็น `One way` คลิก `e634` ได้ตามปกติ
4. บทเรียนสำหรับ agent: ถ้า CLI คืน exit ≠ 0 โค้ดต้องไม่เดาต่อ ให้ observe ใหม่แล้วถาม LLM ใหม่

🔍 **snapshot เทียบหน้าเว็บจริง** (`lab4/new.yml` + `lab4/new.png`)

![ซ้าย: ฟอร์มหลังเลือก One way combobox ประเภทตั๋วมีกรอบแดงหมายเลข 1; ขวา: บรรทัด YAML ที่มี ref ใหม่ e634](img/lab4-compare.png)

```yaml
# old.yml บรรทัด 31 (ก่อนเลือก)
- combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer]:
# new.yml (หลังเลือก One way)
- combobox "Change ticket type. One way" [active] [ref=e634] [cursor=pointer] [box=480,400,127,36]:   # ① ตัวเดิมบนจอ ref ใหม่
- combobox "Change seating class. Economy" [ref=e636] [cursor=pointer] [box=695,400,103,36]:           # ② เดิม e126
    - combobox "Where from?" [ref=e637] [box=480,444,282,56]: Bangkok                                  # ③ เดิม e136
```

ไม่ใช่แค่ตัวที่กดเท่านั้นที่ ref เปลี่ยน ②③ ที่เราไม่ได้แตะก็ได้ ref ใหม่ด้วย เพราะทั้งฟอร์มถูกสร้างใหม่ และ ② ขยับซ้ายเล็กน้อย (x 707 → 695) เพราะ ① แคบลง

✅ **ผลที่ควรได้** (ตัดตอนจริงจาก `lab4/stale.txt`)

```text
$ playwright-cli click e541
### Ran Playwright code
await page.getByRole('option', { name: 'One way' }).click();
[exit code: 0]
$ playwright-cli click e107
### Error
Error: Ref e107 not found in the current page snapshot. Try capturing new snapshot.
[exit code: 1]
$ playwright-cli snapshot --boxes --filename=lab4/new.yml
[exit code: 0]
$ playwright-cli click e634
### Ran Playwright code
await page.getByRole('combobox', { name: 'Change ticket type. One way' }).click();
[exit code: 0]
```

**วิธีตรวจ:** `grep -n "not found" lab4/stale.txt` เจอ error 1 บรรทัด ตามด้วย `[exit code: 1]` · `grep -n "ticket type" lab4/old.yml lab4/new.yml` ref ต่างกัน

---

### LAB 5 · ผู้ตัดสินใจ 1 ครั้ง (1 step ครบ 4 ช่วง)

🎯 **เป้าหมาย:** เขียนโค้ด Python ที่ทำ 1 step แบบ code-in-control ครบ: Observe → Decide (LLM) → Validate → Act → Verify และเก็บหลักฐานทุกช่วง
นี่คือ "อิฐก้อนแรก" ของ agent เต็มใน LAB 6

💬 **พรอมต์**

```text
{{PROMPT:lab5}}
```

📖 **คำอธิบาย**

| ช่วง | โค้ดทำอะไร | ทำไม (โยงทฤษฎี) |
|---|---|---|
| ① Observe | `open` → `snapshot --boxes` → `screenshot --hires` | ได้ทั้ง YAML (ให้ LLM อ่าน) และ box (ไว้วาดวงแดง) ของหน้าสถานะเดียวกัน (A3) |
| ② Decide | กรองเหลือ 30 บรรทัด → เขียน `prompt.txt` → ส่งทาง stdin ให้ `yolo1 -p ... --json-schema ... --tools ""` | plain text อ่านง่าย · schema ทำให้ตรวจได้ · ไม่มี tool = LLM กดเองไม่ได้ (A6) |
| ③ Validate → Act | ตรวจ allowlist / ref มีจริง / denylist → วาดวงรี + callout → `click` | กติกาอยู่ในโค้ด ไม่ใช่ใน prompt (A7) · มีภาพหลักฐานก่อนกด (A8) |
| ④ Verify | `snapshot` ใหม่ → หา `option "One way"` → เช็กว่า ref เดิมยังอยู่ไหม | โค้ดเป็นผู้ตัดสินว่าผ่าน ไม่ใช่ LLM (A5) · ref หมดอายุหรือไม่ (A4) |

**ทำไมสั่งให้ LLM "เปิดรายการ" ไม่ใช่ "เลือก One way" เลย?** เพราะ option `One way` ยังไม่อยู่ในหน้าจนกว่าจะเปิด dropdown LLM เห็นได้แค่สิ่งที่อยู่ใน snapshot ตอนนั้น (LAB 6 จะให้โค้ดวนหลายรอบจนถึงเป้าหมาย)

🔍 **snapshot เทียบหน้าเว็บจริง** (`lab5/step/snapshot.yml` + `observe.png` = สิ่งที่โค้ดเห็นในช่วง Observe)

![ซ้าย: หน้าแรกของ Google Flights มีกรอบสี 5 กรอบ; ขวา: 5 บรรทัดที่ถูกส่งให้ LLM ใน prompt.txt](img/lab5-compare.png)

```yaml
- combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer] [box=480,400,138,36]:   # ① LLM เลือกตัวนี้
- button "1 passenger, change number of passengers." [ref=e113] [box=622,400,80,36]:          # ②
- combobox "Change seating class. Economy" [ref=e126] [cursor=pointer] [box=707,400,103,36]:   # ③
    - combobox "Where from?" [ref=e136] [box=480,444,282,56]: Bangkok                          # ④
  - combobox "Where to?" [active] [ref=e149] [box=770,444,282,56]                              # ⑤
```

ใน `prompt.txt` บรรทัดเหล่านี้ถูกตัด `[box=...]` ออกและตัดย่อหน้า เพราะ LLM ไม่ต้องรู้ตำแหน่ง box มีไว้ให้ **โค้ด** วาดภาพเท่านั้น

✅ **ผลที่ควรได้** (ไฟล์จริงจาก `lab5/step/`)

`prompt.txt` (ตัดตอน):

```text
เป้าหมาย: เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way

รายการ element บนหน้าเว็บ (button/combobox/textbox/option) พร้อม ref:
- button "Main menu" [ref=e6] [cursor=pointer]
...
- combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer]:
- button "1 passenger, change number of passengers." [ref=e113]:
- combobox "Change seating class. Economy" [ref=e126] [cursor=pointer]:
- combobox "Where from?" [ref=e136]: Bangkok
...   (รวม 30 element)

กติกา:
- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง
- action ต้องเป็น click, fill, press หรือ stop เท่านั้น
...
รูปแบบคำตอบ JSON: {"action": "...", "ref": "...", "value": "...", "reason": "..."}
```

`decision.json`:

```json
{
  "llm_answer": {"action": "click", "ref": "e107", "value": "",
                 "reason": "คลิกที่ combobox 'Change ticket type' เพื่อเปิดรายการและเลือก One way"},
  "element": {"role": "combobox", "name": "Change ticket type. Round trip", "box": [480.0, 400.0, 138.0, 36.0]},
  "checks": {"action_in_allowlist": "pass", "ref_in_snapshot": "pass", "name_not_denylisted": "pass",
             "action_is_executable_click": "pass", "has_box": "pass"},
  "result": "pass"
}
```

`page.png` (ภาพจริงก่อนกด ตัดมาเฉพาะส่วนฟอร์ม · [ภาพเต็ม](img/lab5-page.png)):

![ภาพจริงของ Google Flights วงรีแดงล้อม combobox Round trip พร้อมกล่องข้อความ Step 1 click e107 อยู่ด้านบน ไม่บังช่อง](img/lab5-page-crop.png)

`act.txt`:

```text
คำสั่งที่รัน: playwright-cli click e107  (exit=0)
output ย่อ: await page.getByRole('combobox', { name: 'Change ticket type. Round trip' }).click();
ผล verify: PASS — พบ option "One way" ใน verify.yml
  หลักฐาน verify.yml:37: - option "One way" [ref=e541] [cursor=pointer] [box=480,492,138,48]
ref เดิม e107 ใน snapshot ใหม่: ไม่อยู่แล้ว
```

รูปแบบ JSON และชื่อ field ของคุณอาจต่างจากนี้ (AI เขียนโค้ดเองทุกครั้ง) สิ่งที่ต้องมีครบคือ คำตอบ LLM + ผลตรวจทีละข้อ + คำสั่งที่รัน + หลักฐาน verify

**วิธีตรวจ:** `ls lab5/step/` มีครบ 7 ไฟล์ (`snapshot.yml observe.png prompt.txt decision.json page.png act.txt verify.yml`) · `grep -c innerHTML lab5/one_step.py` ต้องได้ 0 · `grep -n "One way" lab5/step/verify.yml` เจอ option

---
