#### Step 01 · เปิดรายการประเภทตั๋ว

📁 [`log/steps/01_oneway-click/`](log/steps/01_oneway-click/) · LLM ใช้เวลา 10.0 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/01_oneway-click/snapshot.yml) 253 บรรทัด · บรรทัด 31 คือ element ที่จะถูกเลือกในรอบนี้

![Step 1: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s01-compare.png)

```yaml
- combobox "Change ticket type. Round trip" [ref=e107] [cursor=pointer] [box=480,400,138,36]:   # ① บรรทัด 31 ← เป้าของ step นี้
- button "1 passenger, change number of passengers." [ref=e113] [box=622,400,80,36]:            # ② บรรทัด 34
- combobox "Change seating class. Economy" [ref=e126] [cursor=pointer] [box=707,400,103,36]:    # ③ บรรทัด 36
- combobox "Where from?" [ref=e136] [box=480,444,282,56]: Bangkok                               # ④ บรรทัด 42
- combobox "Where to?" [active] [ref=e149] [box=770,444,282,56]                                 # ⑤ บรรทัด 46
- textbox "Departure" [ref=e168] [box=1116,445,138,54]                                          # ⑥ บรรทัด 48
```

หน้าแรกของ Google Flights ค่าเริ่มต้นเป็น Round trip โค้ดเช็กก่อนว่าเป้าหมาย "One way" สำเร็จหรือยัง (ยัง) จึงต้องถาม LLM

**② Decide** — ส่ง 30 บรรทัดให้ LLM ([`prompt.txt`](log/steps/01_oneway-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ประเภทตั๋วต้องเป็น 'One way' — ถ้าเห็น option 'One way' ให้ click; ถ้าไม่เห็น ให้ click combobox ประเภทตั๋ว (Change ticket type) เพื่อเปิดรายการ

สิ่งที่ทำไปแล้วใน step นี้:
(ยังไม่มี)

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Change ticket type. Round trip" [ref=e107]:
- button "1 passenger, change number of passengers." [ref=e113]:
- combobox "Change seating class. Economy" [ref=e126]:
- combobox "Where from?" [ref=e136]: Bangkok
- combobox "Where to?" [active] [ref=e149]
- textbox "Departure" [ref=e168]
- textbox "Return" [ref=e172]
...   (รวม 30 บรรทัด)
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e107", "value": "", "reason": "Click combobox 'Change ticket type. Round trip' เพื่อเปิดรายการและแสดง option 'One way'"}
```

ยังไม่มี option "One way" ในหน้า LLM จึงเลือกทางที่กติกาใน goal บอกไว้: click combobox ประเภทตั๋วเพื่อเปิดรายการ

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/01_oneway-click/page.png" width="860" alt="Step 1 ภาพจริงก่อนกด วงแดงรอบ combobox Change ticket type. Round trip พร้อม callout">

```text
$ playwright-cli click e107
await page.getByRole('combobox', { name: 'Change ticket type. Round trip' }).click();
- Page URL: https://www.google.com/travel/flights?hl=en
exit code: 0
```

ผ่านทั้ง 4 ข้อ โค้ดวาดวงแดงรอบ combobox ตาม box `480,400,138,36` แล้วจึงสั่งกด

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/01_oneway-click/verify.yml):

```text
เป้าหมาย 'ประเภทตั๋ว' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - combobox [expanded] [aria-hidden] [ref=e537] [cursor=pointer] [box=480,400,138,36]:
ref e107 ใน snapshot ใหม่: ไม่มีแล้ว
```

dropdown เปิดแล้ว แต่ประเภทตั๋วยังไม่ใช่ One way → **ยังไม่ผ่าน** โค้ดวนกลับไป Observe ใหม่ และ ref `e107` หายไปจาก snapshot ใหม่แล้ว

#### Step 02 · เลือก One way

📁 [`log/steps/02_oneway-click/`](log/steps/02_oneway-click/) · LLM ใช้เวลา 9.5 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/02_oneway-click/snapshot.yml) 267 บรรทัด · บรรทัด 37 คือ element ที่จะถูกเลือกในรอบนี้

![Step 2: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s02-compare.png)

```yaml
- listbox "Select your ticket type." [ref=e539] [box=480,436,138,160]:                       # ① บรรทัด 35
- option "Round trip" [active] [selected] [ref=e540] [cursor=pointer] [box=480,444,138,48]   # ② บรรทัด 36
- option "One way" [ref=e541] [cursor=pointer] [box=480,492,138,48]                          # ③ บรรทัด 37 ← เป้าของ step นี้
- option "Multi-city" [ref=e542] [cursor=pointer] [box=480,540,138,48]                       # ④ บรรทัด 38
```

หน้าเปลี่ยน: มี listbox 3 option โผล่มา snapshot มี 267 บรรทัด

**② Decide** — ส่ง 3 บรรทัดให้ LLM ([`prompt.txt`](log/steps/02_oneway-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ประเภทตั๋วต้องเป็น 'One way' — ถ้าเห็น option 'One way' ให้ click; ถ้าไม่เห็น ให้ click combobox ประเภทตั๋ว (Change ticket type) เพื่อเปิดรายการ

สิ่งที่ทำไปแล้วใน step นี้:
- click e107 (combobox "Change ticket type. Round trip")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- option "Round trip" [active] [selected] [ref=e540]
- option "One way" [ref=e541]
- option "Multi-city" [ref=e542]
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e541", "value": "", "reason": "เห็น option 'One way' [ref=e541] อยู่ในรายการแล้ว จึง click เพื่อเลือกประเภทตั๋วเป็น One way"}
```

"สิ่งที่ทำไปแล้ว" บอก LLM ว่าเปิดรายการไปแล้ว และ snapshot ที่ส่งไปเหลือแค่ 3 บรรทัด (กรองด้วยคำใบ้ของ step) LLM จึงเลือกได้ง่าย

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/02_oneway-click/page.png" width="860" alt="Step 2 ภาพจริงก่อนกด วงแดงรอบ option One way พร้อม callout">

```text
$ playwright-cli click e541
await page.getByRole('option', { name: 'One way' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoOagwIAhIIL20vMGZuMmdAAUgBcAGCAQsI____________AZgB…
exit code: 0
```

ref `e541` มีอยู่ใน snapshot ล่าสุดจริง (ถ้า LLM ตอบ `e107` จากรอบก่อน ข้อ "ref exists" จะไม่ผ่าน)

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/02_oneway-click/verify.yml):

```text
เป้าหมาย 'ประเภทตั๋ว' → ผ่าน ✅
  หลักฐาน verify.yml บรรทัด 31: - combobox "Change ticket type. One way" [active] [ref=e634] [cursor=pointer] [box=480,400,127,36]:
ref e541 ใน snapshot ใหม่: ไม่มีแล้ว
```

ชื่อ combobox เปลี่ยนเป็น `Change ticket type. One way` → **ผ่าน** ไปเป้าหมายถัดไป · ก่อนถาม LLM เรื่องชั้นโดยสาร โค้ด verify ก่อนและพบว่า `Economy` + `1 passenger` เป็นค่าเริ่มต้นอยู่แล้ว จึงข้ามโดยไม่เรียก LLM

#### Step 03 · เปิดช่องต้นทาง

📁 [`log/steps/03_origin-click/`](log/steps/03_origin-click/) · LLM ใช้เวลา 9.7 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/03_origin-click/snapshot.yml) 251 บรรทัด · บรรทัด 42 คือ element ที่จะถูกเลือกในรอบนี้

```yaml
- combobox "Where from?" [ref=e637] [box=480,444,282,56]: Bangkok
```

ฟอร์มถูก render ใหม่หลังเลือก One way ทุก element ได้ ref ใหม่ (`Where from?` เป็น `e637` ไม่ใช่ `e136` แบบใน LAB 2)

**② Decide** — ส่ง 29 บรรทัดให้ LLM ([`prompt.txt`](log/steps/03_origin-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ต้นทางต้องเป็น Suvarnabhumi Airport (BKK) — ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click; ถ้าเห็นช่องต้นทางที่ [expanded] ('Where from?' หรือ 'Where else?') ให้ fill ด้วย BKK; ไม่อย่างนั้นให้ click combobox 'Where from?'

สิ่งที่ทำไปแล้วใน step นี้:
(ยังไม่มี)

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Change ticket type. One way" [active] [ref=e634]:
- button "1 passenger" [ref=e635]:
- combobox "Change seating class. Economy" [ref=e636]:
- combobox "Where from?" [ref=e637]: Bangkok
- combobox "Where to?" [ref=e638]
- textbox "Departure" [ref=e639]
- button "Explore destinations" [ref=e640]:
...   (รวม 29 บรรทัด)
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e637", "value": "", "reason": "Click the 'Where from?' combobox to expand it and see available airport options. Currently it shows 'Bangkok', but we need to select the specific option 'Suvarnabhumi Airport (BKK)' which should appear once the combobox is expanded."}
```

ต้นทางแสดง `Bangkok` แต่ยังไม่ได้ระบุสนามบิน LLM จึงเลือกเปิดช่องเพื่อดูตัวเลือก

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/03_origin-click/page.png" width="860" alt="Step 3 ภาพจริงก่อนกด วงแดงรอบ combobox Where from? พร้อม callout">

```text
$ playwright-cli click e637
await page.getByRole('combobox', { name: 'Where from?' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoOagwIAhIIL20vMGZuMmdAAUgBcAGCAQsI____________AZgB…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/03_origin-click/verify.yml):

```text
เป้าหมาย 'ต้นทาง' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - combobox "Where else?" [expanded] [active] [ref=e735] [box=532,448,344,48]: Bangkok
ref e637 ใน snapshot ใหม่: ไม่มีแล้ว
```

หน้าเปลี่ยน: ช่องที่พิมพ์ได้กลายเป็น element ใหม่ชื่อ `Where else?` [expanded] ยังไม่มี BKK ในชื่อ → **ยังไม่ผ่าน**

#### Step 04 · เลือก Suvarnabhumi (BKK)

📁 [`log/steps/04_origin-click/`](log/steps/04_origin-click/) · LLM ใช้เวลา 8.5 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/04_origin-click/snapshot.yml) 281 บรรทัด · บรรทัด 61 คือ element ที่จะถูกเลือกในรอบนี้

![Step 4: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s04-compare.png)

```yaml
- combobox "Where else?" [expanded] [active] [ref=e735] [box=532,448,344,48]: Bangkok           # ① บรรทัด 50
- option "Bangkok" [selected] [ref=e748] [box=480,505,448,48]:                                  # ② บรรทัด 56
- option "Suvarnabhumi Airport (BKK)" [selected] [ref=e759] [box=480,553,448,56]:               # ③ บรรทัด 61 ← เป้าของ step นี้
- option "Don Mueang International Airport (DMK)" [selected] [ref=e768] [box=480,609,448,56]:   # ④ บรรทัด 65
```

dropdown ต้นทางเปิดอยู่ มี option สนามบินให้เลือกทันทีโดยไม่ต้องพิมพ์

**② Decide** — ส่ง 6 บรรทัดให้ LLM ([`prompt.txt`](log/steps/04_origin-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ต้นทางต้องเป็น Suvarnabhumi Airport (BKK) — ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click; ถ้าเห็นช่องต้นทางที่ [expanded] ('Where from?' หรือ 'Where else?') ให้ fill ด้วย BKK; ไม่อย่างนั้นให้ click combobox 'Where from?'

สิ่งที่ทำไปแล้วใน step นี้:
- click e637 (combobox "Where from?")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Where else?" [expanded] [active] [ref=e735]: Bangkok
- button "Origin, Select multiple airports" [ref=e742]
- option "Bangkok" [selected] [ref=e748]:
- button "Toggle nearby airports for Bangkok" [expanded] [ref=e756]
- option "Suvarnabhumi Airport (BKK)" [selected] [ref=e759]:
- option "Don Mueang International Airport (DMK)" [selected] [ref=e768]:
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e759", "value": "", "reason": "เห็น option 'Suvarnabhumi Airport (BKK)' ในหน้าเว็บ จึงทำตามเป้าหมายโดยคลิก option นี้"}
```

goal บอกว่า "ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click" LLM เห็นจริงใน 6 บรรทัดที่ส่งไป จึงไม่ต้อง fill

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/04_origin-click/page.png" width="860" alt="Step 4 ภาพจริงก่อนกด วงแดงรอบ option Suvarnabhumi Airport (BKK) พร้อม callout">

```text
$ playwright-cli click e759
await page.getByRole('option', { name: 'Suvarnabhumi Airport (BKK)' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoJagcIARIDQktLQAFIAXABggELCP___________wGYAQI&tfu=…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/04_origin-click/verify.yml):

```text
เป้าหมาย 'ต้นทาง' → ผ่าน ✅
  หลักฐาน verify.yml บรรทัด 42: - combobox "Where from? Bangkok BKK" [active] [ref=e866] [box=480,444,282,56]: Bangkok
ref e759 ใน snapshot ใหม่: ไม่มีแล้ว
```

ชื่อช่องต้นทางเปลี่ยนเป็น `Where from? Bangkok BKK` → **ผ่าน**

#### Step 05 · เปิดช่องปลายทาง

📁 [`log/steps/05_destination-click/`](log/steps/05_destination-click/) · LLM ใช้เวลา 7.3 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/05_destination-click/snapshot.yml) 251 บรรทัด · บรรทัด 46 คือ element ที่จะถูกเลือกในรอบนี้

```yaml
- combobox "Where to?" [ref=e868] [box=770,444,282,56]
```

ต้นทางเสร็จแล้ว ช่อง `Where to?` ยังว่าง

**② Decide** — ส่ง 29 บรรทัดให้ LLM ([`prompt.txt`](log/steps/05_destination-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ปลายทางต้องเป็น 'Tokyo, Japan' — ถ้าเห็น option 'Tokyo, Japan' ให้ click; ถ้าเห็นช่อง 'Where to?' ที่ [expanded] ให้ fill ด้วย Tokyo; ไม่อย่างนั้นให้ click combobox 'Where to?'

สิ่งที่ทำไปแล้วใน step นี้:
(ยังไม่มี)

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Change ticket type. One way" [ref=e863]:
- button "1 passenger" [ref=e864]:
- combobox "Change seating class. Economy" [ref=e865]:
- combobox "Where from? Bangkok BKK" [active] [ref=e866]: Bangkok
- combobox "Where to?" [ref=e868]
- textbox "Departure" [ref=e869]
- button "Explore destinations" [ref=e870]:
...   (รวม 29 บรรทัด)
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e868", "value": "", "reason": "Clicking on the 'Where to?' combobox to expand it and search for 'Tokyo, Japan' option"}
```

ยังไม่มี option Tokyo และช่องยังไม่ [expanded] ตาม goal ต้อง click ช่องก่อน

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/05_destination-click/page.png" width="860" alt="Step 5 ภาพจริงก่อนกด วงแดงรอบ combobox Where to? พร้อม callout">

```text
$ playwright-cli click e868
await page.getByRole('combobox', { name: 'Where to?' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoJagcIARIDQktLQAFIAXABggELCP___________wGYAQI&tfu=…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/05_destination-click/verify.yml):

```text
เป้าหมาย 'ปลายทาง' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - combobox "Where to?" [expanded] [active] [ref=e965] [box=830,448,336,48]
ref e868 ใน snapshot ใหม่: ไม่มีแล้ว
```

ช่อง `Where to?` เป็น [expanded] แล้ว แต่ยังไม่มีค่า Tokyo → **ยังไม่ผ่าน**

#### Step 06 · พิมพ์ Tokyo

📁 [`log/steps/06_destination-fill/`](log/steps/06_destination-fill/) · LLM ใช้เวลา 8.2 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/06_destination-fill/snapshot.yml) 290 บรรทัด · บรรทัด 50 คือ element ที่จะถูกเลือกในรอบนี้

![Step 6: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s06-compare.png)

```yaml
- combobox "Where to?" [expanded] [active] [ref=e965] [box=830,448,336,48]   # ① บรรทัด 50 ← เป้าของ step นี้
- option "Anywhere" [ref=e979] [box=770,505,448,48]:                         # ② บรรทัด 56
- option "Europe" [ref=e987] [box=770,553,448,48]:                           # ③ บรรทัด 60
- option "Japan" [ref=e994] [box=770,601,448,48]:                            # ④ บรรทัด 64
```

dropdown ปลายทางเปิดอยู่ แต่มีแค่ปลายทางแนะนำ (Anywhere, Europe, Japan, …) ไม่มี Tokyo

**② Decide** — ส่ง 9 บรรทัดให้ LLM ([`prompt.txt`](log/steps/06_destination-fill/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ปลายทางต้องเป็น 'Tokyo, Japan' — ถ้าเห็น option 'Tokyo, Japan' ให้ click; ถ้าเห็นช่อง 'Where to?' ที่ [expanded] ให้ fill ด้วย Tokyo; ไม่อย่างนั้นให้ click combobox 'Where to?'

สิ่งที่ทำไปแล้วใน step นี้:
- click e868 (combobox "Where to?")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Where to?" [expanded] [active] [ref=e965]
- button "Destination, Select multiple airports" [ref=e973]
- option "Anywhere" [ref=e979]:
- option "Europe" [ref=e987]:
- option "Japan" [ref=e994]:
- option "Paris, France" [ref=e1001]:
- button "Toggle nearby airports for Paris, France" [ref=e1009]
- option "London, United Kingdom" [ref=e1012]:
- button "Toggle nearby airports for London, United Kingdom" [ref=e1020]
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "fill", "ref": "e965", "value": "Tokyo", "reason": "The combobox 'Where to?' is already expanded [expanded] [active]. According to the instructions, when the field is expanded, I should fill it with 'Tokyo' to search for the Tokyo, Japan destination."}
```

ไม่มี option `Tokyo, Japan` LLM จึง fill ตาม goal

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step · ✓ fill value allowed for this step → `ok`

<img src="log/steps/06_destination-fill/page.png" width="860" alt="Step 6 ภาพจริงก่อนกด วงแดงรอบ combobox Where to? พร้อม callout">

```text
$ playwright-cli fill e965 Tokyo
await page.getByRole('combobox', { name: 'Where to?' }).fill('Tokyo');
exit code: 0
```

มีข้อตรวจเพิ่ม 1 ข้อสำหรับ fill: ค่าที่กรอกต้องอยู่ในรายการที่โค้ดอนุญาต (`Tokyo`) ถ้า LLM จะพิมพ์อย่างอื่นจะไม่ผ่าน

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/06_destination-fill/verify.yml):

```text
เป้าหมาย 'ปลายทาง' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - combobox "Where to?" [expanded] [active] [ref=e965] [box=830,448,336,48]: Tokyo
ref e965 ใน snapshot ใหม่: ยังอยู่
```

ช่องมีค่า Tokyo แล้วแต่ dropdown ยัง [expanded] = ยังไม่ได้เลือกจริง → **ยังไม่ผ่าน** · น่าสนใจ: ref `e965` **ยังอยู่** เพราะการพิมพ์ไม่ได้สร้างช่องใหม่ แต่โค้ดก็ยัง observe ใหม่ตามกติกา

#### Step 07 · เลือก Tokyo, Japan

📁 [`log/steps/07_destination-click/`](log/steps/07_destination-click/) · LLM ใช้เวลา 7.9 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/07_destination-click/snapshot.yml) 290 บรรทัด · บรรทัด 56 คือ element ที่จะถูกเลือกในรอบนี้

![Step 7: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s07-compare.png)

```yaml
- combobox "Where to?" [expanded] [active] [ref=e965] [box=830,448,336,48]: Tokyo   # ① บรรทัด 50
- option "Tokyo, Japan" [ref=e1099] [box=770,505,448,48]:                           # ② บรรทัด 56 ← เป้าของ step นี้
- option "Haneda Airport (HND)" [ref=e1110] [box=770,553,448,56]:                   # ③ บรรทัด 61
- option "Narita International Airport (NRT)" [ref=e1119] [box=770,609,448,56]:     # ④ บรรทัด 65
```

รายการเปลี่ยนเป็นผลค้นหาของคำว่า Tokyo

**② Decide** — ส่ง 9 บรรทัดให้ LLM ([`prompt.txt`](log/steps/07_destination-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
ปลายทางต้องเป็น 'Tokyo, Japan' — ถ้าเห็น option 'Tokyo, Japan' ให้ click; ถ้าเห็นช่อง 'Where to?' ที่ [expanded] ให้ fill ด้วย Tokyo; ไม่อย่างนั้นให้ click combobox 'Where to?'

สิ่งที่ทำไปแล้วใน step นี้:
- click e868 (combobox "Where to?")
- fill e965 = Tokyo (combobox "Where to?")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Where to?" [expanded] [active] [ref=e965]: Tokyo
- button "Destination, Select multiple airports" [ref=e973]
- option "Tokyo, Japan" [ref=e1099]:
- button "Toggle nearby airports for Tokyo, Japan" [expanded] [ref=e1107]
- option "Haneda Airport (HND)" [ref=e1110]:
- option "Narita International Airport (NRT)" [ref=e1119]:
- option "Tokyo Station" [ref=e1128]:
- option "Tokyo Oshima Camellia Airport, Japan" [ref=e1137]:
- button "Toggle nearby airports for Tokyo Oshima Camellia Airport, Japan" [ref=e1145]
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e1099", "value": "", "reason": "Clicking 'Tokyo, Japan' option to set the destination as required by the goal"}
```

"สิ่งที่ทำไปแล้ว" มี 2 บรรทัด (click + fill) LLM เลือก option ที่ตรงชื่อเป้าหมายพอดี ไม่เลือก Haneda/Narita

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/07_destination-click/page.png" width="860" alt="Step 7 ภาพจริงก่อนกด วงแดงรอบ option Tokyo, Japan พร้อม callout">

```text
$ playwright-cli click e1099
await page.getByRole('option', { name: 'Tokyo, Japan' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDQktLcgwIAxIIL20vMDdkZmtAAUgBcAGCAQsI____…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/07_destination-click/verify.yml):

```text
เป้าหมาย 'ปลายทาง' → ผ่าน ✅
  หลักฐาน verify.yml บรรทัด 46: - combobox "Where to?" [active] [ref=e1167] [box=770,444,282,56]: Tokyo
ref e1099 ใน snapshot ใหม่: ไม่มีแล้ว
```

dropdown ปิดแล้ว และช่อง `Where to?` มีค่า Tokyo → **ผ่าน** (ต้องผ่านทั้งสองเงื่อนไข ดู A5)

#### Step 08 · เปิดปฏิทิน

📁 [`log/steps/08_date-click/`](log/steps/08_date-click/) · LLM ใช้เวลา 9.3 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/08_date-click/snapshot.yml) 252 บรรทัด · บรรทัด 48 คือ element ที่จะถูกเลือกในรอบนี้

```yaml
- textbox "Departure" [ref=e1170] [box=1116,445,308,54]
```

ฟอร์มมี One way / BKK / Tokyo ครบ เหลือวันเดินทาง โค้ดคำนวณวันที่เป้าหมาย = 15 ต.ค. 2026 ไว้แล้วตั้งแต่เริ่ม

**② Decide** — ส่ง 30 บรรทัดให้ LLM ([`prompt.txt`](log/steps/08_date-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
วันเดินทาง (Departure) ต้องเป็น October 15, 2026 — ถ้าเห็นปุ่มวันที่ October 15, 2026 ให้ click; ไม่อย่างนั้นให้ click ช่อง 'Departure' เพื่อเปิดปฏิทิน

สิ่งที่ทำไปแล้วใน step นี้:
(ยังไม่มี)

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Change ticket type. One way" [ref=e1160]:
- button "1 passenger" [ref=e1161]:
- combobox "Change seating class. Economy" [ref=e1162]:
- combobox "Where from? Bangkok BKK" [ref=e1163]: Bangkok
- button "Swap origin and destination." [ref=e1164]
- combobox "Where to?" [active] [ref=e1167]: Tokyo
- textbox "Departure" [ref=e1170]
...   (รวม 30 บรรทัด)
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e1170", "value": "", "reason": "ไม่เห็นปุ่ม October 15, 2026 ในรายการ elements ที่กำหนด จึงคลิกที่ textbox 'Departure' เพื่อเปิดปฏิทินและเลือกวันที่ October 15, 2026"}
```

ยังไม่มีปุ่มวันที่ 15 LLM จึงเปิดช่อง Departure

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/08_date-click/page.png" width="860" alt="Step 8 ภาพจริงก่อนกด วงแดงรอบ textbox Departure พร้อม callout">

```text
$ playwright-cli click e1170
await page.getByRole('textbox', { name: 'Departure' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDQktLcgwIAxIIL20vMDdkZmtAAUgBcAGCAQsI____…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/08_date-click/verify.yml):

```text
เป้าหมาย 'วันเดินทาง' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - textbox "Departure" [active] [ref=e1275] [box=1116,445,308,54]
ref e1170 ใน snapshot ใหม่: ไม่มีแล้ว
```

ปฏิทินเปิดแล้ว (snapshot ยาวขึ้นเป็น 1,5xx บรรทัด) แต่ยังไม่ได้เลือกวัน → **ยังไม่ผ่าน**

#### Step 09 · เลือกวันที่ 15 ต.ค. 2026

📁 [`log/steps/09_date-click/`](log/steps/09_date-click/) · LLM ใช้เวลา 7.3 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/09_date-click/snapshot.yml) 1,566 บรรทัด · บรรทัด 213 คือ element ที่จะถูกเลือกในรอบนี้

![Step 9: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s09-compare.png)

```yaml
- textbox "Departure" [active] [ref=e1275] [box=1116,445,308,54]                            # ① บรรทัด 55
- button "Wednesday, October 14, 2026 , 7346 Thai baht" [ref=e2780] [box=1232,722,48,48]:   # ② บรรทัด 209
- button "Thursday, October 15, 2026 , 7160 Thai baht" [ref=e2783] [box=1280,722,48,48]:    # ③ บรรทัด 213 ← เป้าของ step นี้
- button "Friday, October 16, 2026 , 7346 Thai baht" [ref=e2786] [box=1328,722,48,48]:      # ④ บรรทัด 217
- button "Done." [ref=e2656] [box=1357,946,83,32]:                                          # ⑤ บรรทัด 1353
```

ปฏิทิน 2 เดือนมีปุ่มวันหลายร้อยปุ่ม snapshot **1,566 บรรทัด**

**② Decide** — ส่ง 2 บรรทัดให้ LLM ([`prompt.txt`](log/steps/09_date-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
วันเดินทาง (Departure) ต้องเป็น October 15, 2026 — ถ้าเห็นปุ่มวันที่ October 15, 2026 ให้ click; ไม่อย่างนั้นให้ click ช่อง 'Departure' เพื่อเปิดปฏิทิน

สิ่งที่ทำไปแล้วใน step นี้:
- click e1170 (textbox "Departure")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- textbox "Departure" [active] [ref=e1275]
- button "Thursday, October 15, 2026 , 7160 Thai baht" [ref=e2783]:
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e2783", "value": "", "reason": "Found the button for Thursday, October 15, 2026 with the price 7160 Thai baht. Clicking it to set the departure date as required."}
```

โค้ดกรองด้วยคำใบ้ `Departure|October 15, 2026` เหลือส่งให้ LLM แค่ **2 บรรทัด** (A6 token budget) โอกาสกดผิดวันแทบเป็นศูนย์

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/09_date-click/page.png" width="860" alt="Step 9 ภาพจริงก่อนกด วงแดงรอบ button Thursday, October 15, 2026 , 7160 Thai b พร้อม callout">

```text
$ playwright-cli click e2783
await page.getByRole('button', { name: 'Thursday, October 15, 2026 ,' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDQktLcgwIAxIIL20vMDdkZmtAAUgBcAGCAQsI____…
exit code: 0
```

ผ่านทั้ง 4 ข้อ · ชื่อปุ่มมีราคา `7160 Thai baht` แต่ไม่ติด denylist เพราะเราห้ามแค่ "จอง/จ่าย" ไม่ได้ห้ามคำว่าราคา

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/09_date-click/verify.yml):

```text
เป้าหมาย 'วันเดินทาง' → ผ่าน ✅
  หลักฐาน verify.yml บรรทัด 56: - textbox "Departure" [active] [ref=e1275] [box=1116,445,256,54]: Thu, Oct 15
ref e2783 ใน snapshot ใหม่: ไม่มีแล้ว
```

ช่อง Departure มีค่า `Thu, Oct 15` → **ผ่าน**

#### Step 10 · กด Done ของปฏิทิน

📁 [`log/steps/10_search-click/`](log/steps/10_search-click/) · LLM ใช้เวลา 9.0 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/10_search-click/snapshot.yml) 1,571 บรรทัด · บรรทัด 1358 คือ element ที่จะถูกเลือกในรอบนี้

```yaml
- button "Done. Search for one-way flights, departing on October 15, 2026" [ref=e2864] [box=1357,947,83,32]:
```

ปฏิทินยังเปิดอยู่ ปุ่มค้นหาถูกบังอยู่ข้างหลัง

**② Decide** — ส่ง 2 บรรทัดให้ LLM ([`prompt.txt`](log/steps/10_search-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
กดค้นหาเที่ยวบิน — ถ้าเห็นปุ่ม 'Done' ของปฏิทินให้ click ก่อน; ไม่อย่างนั้นให้ click ปุ่ม 'Search'

สิ่งที่ทำไปแล้วใน step นี้:
(ยังไม่มี)

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- textbox "Departure" [active] [ref=e1275]: Thu, Oct 15
- button "Done. Search for one-way flights, departing on October 15, 2026" [ref=e2864]:
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e2864", "value": "", "reason": "เห็นปุ่ม 'Done' ของปฏิทิน (Done. Search for one-way flights, departing on October 15, 2026) ให้ click ก่อนตามคำสั่ง"}
```

goal บอกให้กด Done ก่อนถ้าเห็น LLM เห็นปุ่ม `Done. Search for one-way flights…`

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/10_search-click/page.png" width="860" alt="Step 10 ภาพจริงก่อนกด วงแดงรอบ button Done. Search for one-way flights, depart พร้อม callout">

```text
$ playwright-cli click e2864
await page.getByRole('button', { name: 'Done. Search for one-way' }).click();
- Page URL: https://www.google.com/travel/flights?tfs=CBwQARojEgoyMDI2LTEwLTE1agcIARIDQktLcgwIAxIIL20vMDdkZmtA…
exit code: 0
```

ชื่อปุ่มมีคำว่า Search แต่ไม่ติด denylist (การค้นหาอนุญาต) ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/10_search-click/verify.yml):

```text
เป้าหมาย 'ค้นหา' → ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)
  สถานะหน้าใหม่: - textbox "Departure" [active] [ref=e2883] [box=1116,445,256,54]: Thu, Oct 15
ref e2864 ใน snapshot ใหม่: ไม่มีแล้ว
```

ปฏิทินปิด แต่ URL ยังไม่ใช่ `/travel/flights/search` → **ยังไม่ผ่าน** (ปุ่ม Done แค่ปิดปฏิทิน ไม่ได้ค้นหา)

#### Step 11 · กด Search

📁 [`log/steps/11_search-click/`](log/steps/11_search-click/) · LLM ใช้เวลา 11.0 วินาที

**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/11_search-click/snapshot.yml) 254 บรรทัด · บรรทัด 52 คือ element ที่จะถูกเลือกในรอบนี้

![Step 11: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-s11-compare.png)

```yaml
- combobox "Change ticket type. One way" [ref=e2877] [cursor=pointer] [box=480,400,127,36]:   # ① บรรทัด 31
- combobox "Where from? Bangkok BKK" [ref=e2880] [box=480,444,282,56]: Bangkok                # ② บรรทัด 42
- combobox "Where to?" [ref=e2882] [box=770,444,282,56]: Tokyo                                # ③ บรรทัด 46
- textbox "Departure" [active] [ref=e2883] [box=1116,445,256,54]: Thu, Oct 15                 # ④ บรรทัด 49
- button "Search" [ref=e2899] [box=907,526,107,40]                                            # ⑤ บรรทัด 52 ← เป้าของ step นี้
```

ปุ่ม `Search` โผล่แล้ว (ใน LAB 2 ยังไม่มีปุ่มนี้)

**② Decide** — ส่ง 30 บรรทัดให้ LLM ([`prompt.txt`](log/steps/11_search-click/prompt.txt) ตัดตอน):

```text
เป้าหมายของ step นี้:
กดค้นหาเที่ยวบิน — ถ้าเห็นปุ่ม 'Done' ของปฏิทินให้ click ก่อน; ไม่อย่างนั้นให้ click ปุ่ม 'Search'

สิ่งที่ทำไปแล้วใน step นี้:
- click e2864 (button "Done. Search for one-way flights, departing on October 15, 2")

หน้าเว็บตอนนี้ (snapshot ตัดแล้ว):
- combobox "Change ticket type. One way" [ref=e2877]:
- button "1 passenger" [ref=e2878]:
- combobox "Change seating class. Economy" [ref=e2879]:
- combobox "Where from? Bangkok BKK" [ref=e2880]: Bangkok
- button "Swap origin and destination." [ref=e2881]
- combobox "Where to?" [ref=e2882]: Tokyo
- textbox "Departure" [active] [ref=e2883]: Thu, Oct 15
...   (รวม 30 บรรทัด)
```

LLM ตอบ (`decision.json` → `llm_decision`):

```json
{"action": "click", "ref": "e2899", "value": "", "reason": "ปุ่ม 'Done' ของปฏิทินได้ถูก click ไปแล้วใน step ก่อนหน้า snapshot ปัจจุบันไม่มีปุ่ม 'Done' อยู่ ต้องกด 'Search' [ref=e2899] เพื่อค้นหาเที่ยวบิน"}
```

"สิ่งที่ทำไปแล้ว" บอกว่ากด Done ไปแล้ว LLM จึงเลือก Search

**③ Validate → Act** — ✓ action in allowlist · ✓ ref exists in latest snapshot · ✓ element not in denylist · ✓ role allowed for this step → `ok`

<img src="log/steps/11_search-click/page.png" width="860" alt="Step 11 ภาพจริงก่อนกด วงแดงรอบ button Search พร้อม callout">

```text
$ playwright-cli click e2899
await page.getByRole('button', { name: 'Search' }).click();
- Page URL: https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTEwLTE1agcIARIDQktLcgwIAxIIL20vM…
exit code: 0
```

ผ่านทั้ง 4 ข้อ

**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/11_search-click/verify.yml):

```text
เป้าหมาย 'ค้นหา' → ผ่าน ✅
  หลักฐาน verify.yml บรรทัด 112: - link "From 7346 Thai baht. 1 stop flight with Vietjet. Leaves Suvarnabhumi Airport at 11:30 AM on Thursday, October 15 and arrives at Haneda Airport at 1:00 A
ref e2899 ใน snapshot ใหม่: ไม่มีแล้ว
```

URL เป็นหน้า `/travel/flights/search` และมีผลเที่ยวบิน ≥ 3 รายการ → **ผ่าน** ครบทุกเป้าหมาย

