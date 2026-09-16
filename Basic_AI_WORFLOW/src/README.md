# สัญญาการเขียนสไลด์

เขียน fragment UTF-8 ใน `src/slides/` เช่น `00-cover.html`, `10-theory.html` และ `20-workflows.html` ตัว build อ่าน `.html`/`.htm` ระดับเดียวเรียงตามชื่อ แต่ละไฟล์มีหลาย section ได้ ไม่ต้องใส่ `<html>`, `<head>` หรือ engine script เอง

```sh
python3 src/build_deck.py --slides src/slides --root . --out AI_Workflow_Engineering.html
python3 tests/test_slides.py --html AI_Workflow_Engineering.html --out tests/results.json --shots tests/screenshots
```

ต้องมี Python packages `beautifulsoup4`, `markdown-it-py`, `playwright` และ Chromium ของ Playwright ใช้ `tools/render_md.py` render Markdown และ Mermaid ตอน build ตั้ง `MERMAID_JS` เป็นไฟล์ Mermaid JavaScript ในเครื่องได้ ไม่มีการโหลด CDN ระหว่างเปิด deck

## รูปแบบ section และความสูง

ทุกหน้าต้องเป็น `<section class="slide …" data-chapter="เลขบท ชื่อบท" data-title="ชื่อหน้า">` และมี `.body` สำหรับเนื้อหา พื้นที่อ้างอิง **1280×720 px** engine ใช้ `--s` ย่อขยายตามหน้าต่าง ห้ามเพิ่มความสูง `.slide` หรือย่อทั้งหน้าด้วย CSS เพื่อหลบการตรวจ overflow

หัวข้ออยู่ใน `.head` ส่วนท้าย `.foot` สูง 38px ตัว build เติมส่วนท้ายให้หน้าที่ไม่มี โดยซ้ายเป็น `data-chapter` และขวาเป็น `.pg` รูปแบบ `N / total` ถ้ามีส่วนท้ายเอง engine จะอัปเดตหรือเติม `.pg` ปุ่ม Overview อยู่บน controls ของทุกหน้า

`.body` มีพื้นที่ใช้งานลดลงตามหัวข้อและ padding เว้นที่ส่วนท้ายเสมอ กล่องยาวต้องเลื่อนภายใน ใช้ `style="--h:360px"` หรือ `max-height` กับ `.copybox`, `.mdbox`, `.trace`; `--h` ของ `.ui-frame` เป็นความสูง iframe ไม่รวม toolbar; ของ `.threebox` เป็นความสูง `.boxbody` ไม่รวมหัว; ของ `.tabs` เป็นความสูง pane ไม่รวม tabbar ต้องบวกพื้นที่หัวและช่องว่างด้วย ค่าปริยายเป็นเพียงจุดเริ่มต้น ไม่รับประกันว่าจะวางซ้อนหลายกล่องแล้วพอดี

เกณฑ์ overflow คือ `.slide.scrollHeight > 720` หรือ `.body.scrollHeight > .body.clientHeight + 2` ลดเนื้อหาหรือแบ่งหน้าเมื่อเกิน ห้ามใช้ `overflow:hidden` ตัด prompt/ผลลัพธ์ ตัวเลขผลการทดลองต้องอ้างข้อมูลจริง หากไม่มีให้เขียน “ไม่มีข้อมูล”

## Directive ของ build

ทุก path อ้างจาก `--root` ไม่ใช่ที่อยู่ fragment ใช้ path สัมพัทธ์ ไม่มี path เฉพาะเครื่อง

| Directive | ผลลัพธ์และเงื่อนไข |
| --- | --- |
| `<img data-svg="img/x.svg" class="…" style="…" alt="…">` | ฝัง SVG โดยตัด XML declaration, doctype และ comments คง class/style; ถ้าไม่มี `viewBox` สร้างจาก width/height แบบตัวเลขหรือ px แล้วลบ width/height ของ SVG |
| `<img data-png="img/x.png" alt="…">` | แปลง PNG เป็น `data:image/png;base64,…` |
| `<iframe data-inline-src="experiments/งาน/workflow/output.html" title="ผลงาน">` | ฝังเนื้อหาเต็มใน `srcdoc` escape `&`, `"`, `<`, `>` พร้อม sandbox `allow-scripts allow-same-origin allow-forms allow-modals` |
| `<div data-md="experiments/งาน/workflow/output.md" style="--h:420px"></div>` | เรียก `render_markdown()` เติมคลาส `.mdbox`; Mermaid เป็น inline SVG ใน `.mermaid-svg` ตอน build; code fence มีปุ่ม copy |
| `<pre data-file="experiments/งาน/workflow/prompt.md" style="--h:380px"></pre>` | อ่านข้อความเต็ม escape เป็น `.copybox > pre.code + button.copy`; หากอยู่ใน `.copybox` แล้วจะไม่ครอบซ้ำ; style บน pre ใหม่ย้ายไปกล่อง |
| `<section class="slide" data-auto="toc"></section>` | สร้างสารบัญจาก `data-chapter` ตามลำดับที่พบ แต่ละบทลิงก์ไปหน้าแรก ถ้าไม่ใส่จะแทรกหลังหน้าแรกอัตโนมัติ |
| `data-goto-title="<data-title>"` | build เติมหรือเขียนทับ `data-goto` ให้ตรงเลขหน้าของ `data-title` หลังสร้างสารบัญและกำหนดเลขหน้า; exit **4** เมื่อไม่พบชื่อปลายทางหรือชื่อปลายทางซ้ำหลายหน้า พร้อมรายการใน stderr |

แนะนำให้ใส่เลข `data-goto` ไว้ด้วยเพื่อ fallback เช่น `<button type="button" data-goto="2" data-goto-title="สารบัญ">สารบัญ</button>` ตัว build ใช้ชื่อปลายทางเป็นหลัก จึงยังลิงก์ถูกเมื่อแทรกหรือย้ายหน้า และพิมพ์จำนวนรายการที่ resolve ลง stdout ชื่อต้องตรง `data-title` ทุกตัวอักษร; หน้าสารบัญอัตโนมัติใช้ชื่อ `สารบัญ`

Mermaid หรือ asset ผิดพลาด: exit **2** พร้อมชื่อไฟล์ section และบล็อกที่ผิด ตรวจแหล่งข้อมูลใน DOM สไลด์: `src`, `href`, `xlink:href`, `srcset`, CSS `url(...)` และ `@import` ที่อ้าง HTTP(S) ทำให้ exit **3** พร้อมรายการ ไม่ตรวจข้อความ prompt ใน copybox และเนื้อหาใน `srcdoc` อย่างไรก็ตามผลงานที่จะฝังควรทำงาน offline ด้วย ห้ามใส่ external script/link ใน fragment การตรวจนี้ไม่ใช่ sandbox สำหรับ JavaScript จากแหล่งที่ไม่น่าเชื่อถือ

## คลาสที่ใช้ได้

- โครงหน้า: `.slide`, `.head`, `.eye`, `h2`, `.sub`, `.body`, `.foot`, `.pg`, `.cover`, `.section`, `.subsection`
- Layout: `.grid2`, `.grid3`, `.grid4`, `.split`, `.split.rev`
- เนื้อหา: `.card` และ `.card.g/.a/.r`, `.bul`, `.big`, `.quote`, `.callout` และ `.callout.warn/.danger`, `.table`, `pre.code`, `.steps`, `.flow`, `.chips`, `.chip`, `.metric`, `.caption`, `.toc`, `.diagram`
- Interactive: `.copybox`, `.threebox`, `.tabs`, `.tabbar`, `.tabpane`, `.ui-frame`, `figure.figure`, `.mdbox`, `.trace`; `.overview` เป็นสถานะที่ engine ใส่ให้ body

CSS variables เดิม: `--s`, `--navy`, `--teal`, `--green`, `--mint`, `--amber`, `--cream`, `--red`, `--rose`, `--ink`, `--muted`, `--line`, `--code` และ `--h` สำหรับขนาดกล่อง ห้ามแก้ `--s` ใน fragment

## ตัวอย่างหน้าทฤษฎี

```html
<section class="slide" data-chapter="1 แนวคิด" data-title="ตรวจผลงานก่อนส่งต่อ">
  <header class="head"><span class="eye">แนวคิด</span><h2>ตรวจผลงานก่อนส่งต่อ</h2>
    <p class="sub">กำหนดเกณฑ์รับงานให้ชัดเจน</p></header>
  <div class="body"><div class="grid2">
    <article class="card g"><h3>สิ่งที่ต้องทำ</h3><p>สร้างผลงานตามข้อกำหนด</p></article>
    <article class="card a"><h3>หลักฐาน</h3><p>ตรวจผลจากไฟล์จริง</p></article>
  </div></div>
</section>
```

## ตัวอย่าง threebox

หัวต้องใช้ลำดับ ① PROMPT ② PROCESS ③ OUTPUT แต่ละช่องเป็น `div > h3 + div.boxbody` มีลูกศรและพื้นที่เลื่อนของตนเอง

```html
<section class="slide" data-chapter="2 วิธีทำงาน" data-title="จากคำสั่งสู่ผลงาน">
  <header class="head"><h2>จากคำสั่งสู่ผลงาน</h2></header>
  <div class="body"><div class="threebox" style="--h:350px">
    <div><h3>① PROMPT</h3><div class="boxbody">
      <pre data-file="experiments/งาน/loop/prompt.md" style="--h:320px"></pre>
    </div></div>
    <div><h3>② PROCESS</h3><div class="boxbody"><ol class="steps">
      <li>สร้างผลงาน</li><li>ตรวจเกณฑ์</li><li>แก้ตามหลักฐาน</li>
    </ol></div></div>
    <div><h3>③ OUTPUT</h3><div class="boxbody">ไม่มีข้อมูล</div></div>
  </div></div>
</section>
```

## ตัวอย่าง tabs เปรียบเทียบ workflow

ปุ่มกับ pane จับคู่ด้วย `data-tab` ภายใน `.tabs` เดียวกัน ปุ่มแรก active อัตโนมัติ ใช้ data-tab ชื่อซ้ำต่างกล่องได้

```html
<section class="slide" data-chapter="2 วิธีทำงาน" data-title="เลือก workflow">
  <header class="head"><h2>เลือก workflow</h2></header>
  <div class="body"><div class="tabs" style="--h:350px">
    <nav class="tabbar"><button data-tab="loop">Loop</button>
      <button data-tab="graph">Graph</button><button data-tab="dynamic">Dynamic</button></nav>
    <div class="tabpane" data-tab="loop">วนตรวจและแก้ตามเกณฑ์</div>
    <div class="tabpane" data-tab="graph">ส่งต่องานตามเส้นทางที่กำหนด</div>
    <div class="tabpane" data-tab="dynamic">ปรับแผนตามข้อมูลใหม่</div>
  </div></div>
</section>
```

## ตัวอย่าง mdbox และ copybox

```html
<section class="slide" data-chapter="3 หลักฐาน" data-title="อ่านผลงาน Markdown">
  <header class="head"><h2>อ่านผลงาน Markdown</h2></header>
  <div class="body"><div data-md="experiments/งาน/graph/output.md" style="--h:420px"></div></div>
</section>
<section class="slide" data-chapter="3 หลักฐาน" data-title="คำสั่งฉบับเต็ม">
  <header class="head"><h2>คำสั่งฉบับเต็ม</h2></header>
  <div class="body"><pre data-file="experiments/งาน/graph/prompt.md" style="--h:440px"></pre></div>
</section>
```

Template ที่เขียนตรงใน fragment ต้องเป็นภาษาไทยและ escape เครื่องหมาย HTML ใช้โครงนี้ (ตัว build เติมปุ่มให้ได้):

```html
<div class="copybox" style="--h:360px"><pre class="code">อ่านข้อกำหนดต่อไปนี้ แล้วเสนอแผนการทำงาน
ระบุเกณฑ์รับงานและหลักฐานที่ต้องตรวจ
หากข้อมูลไม่พอ ให้เขียนว่า “ไม่มีข้อมูล”</pre><button class="copy" type="button">Copy</button></div>
```

Copy ใช้ `navigator.clipboard.writeText(pre.textContent)` และ fallback textarea กับ `execCommand('copy')` แสดง “Copied” นาน 1.2 วินาที ไม่ตัดข้อความที่เลื่อนพ้นกล่อง

## ตัวอย่างเว็บ ภาพ และ log

```html
<div class="ui-frame" style="--h:360px">
  <iframe title="เว็บผลงาน" data-inline-src="experiments/งาน/loop/output.html"></iframe>
</div>
<figure class="figure" style="--h:380px"><img data-svg="img/workflow.svg" alt="กระบวนการทำงาน"></figure>
<div class="trace" style="--h:320px"><table class="table">
  <thead><tr><th>เหตุการณ์</th><th>หลักฐาน</th></tr></thead>
  <tbody><tr><td>ไม่มีข้อมูล</td><td>ไม่มีข้อมูล</td></tr></tbody>
</table></div>
```

`.ui-frame` เติมปุ่มเปิดเต็มหน้าต่างด้วย Blob URL และโหลดใหม่ด้วยการรีเซ็ต srcdoc; `.figure` เติมปุ่มขยายเป็น overlay กด Esc หรือคลิกเพื่อปิด

## การนำทางและการตรวจรับ

←/→, Space, PageUp/PageDown, Home/End เปลี่ยนหน้า; `o` เปิด Overview แล้วคลิกเลือกหน้า; Esc ปิด overlay หรือ Overview; hash `#pN` เปลี่ยนหน้าสองทาง คลิกพื้นที่ซ้าย/ขวาหนึ่งในสี่ของสไลด์เพื่อเปลี่ยนหน้า controls, iframe และกล่อง interactive/พื้นที่เลื่อนไม่กระตุ้นการเปลี่ยนหน้า

`tests/test_slides.py` เปิด `file://` ที่ viewport 1600×900, เดินทุกหน้าด้วย ArrowRight, ถ่าย `slide-NNN.png` และ `overview.png` รายงาน JSON มี `html`, `checked_at`, `slides`, `ok`, `overflow`, `console_errors`, `copy_ok`, `iframes:{count,loaded}`, `mermaid_svg`, `tabs_ok`, `pages:[{index,title,chapter,screenshot}]` โดย screenshot เป็น path สัมพัทธ์จาก cwd `ok` เท่ากับไม่มี overflow ไม่มี console error/pageerror และ copy ผ่าน ต้องมี copybox อย่างน้อยหนึ่งกล่องจึงผ่าน `tabs_ok` เป็น null เมื่อไม่มีคู่แท็บให้ทดสอบ

ชุด sample ใช้ตรวจ engine ไม่ใช่ข้อมูลผลการทดลอง รันได้ด้วย:

```sh
python3 src/build_deck.py --slides .work/router/exp/sample-deck/slides --root .work/router/exp/sample-deck --out .work/router/exp/sample-deck/deck.html
python3 tests/test_slides.py --html .work/router/exp/sample-deck/deck.html --out .work/router/exp/sample-deck/results.json --shots .work/router/exp/sample-deck/shots
```
