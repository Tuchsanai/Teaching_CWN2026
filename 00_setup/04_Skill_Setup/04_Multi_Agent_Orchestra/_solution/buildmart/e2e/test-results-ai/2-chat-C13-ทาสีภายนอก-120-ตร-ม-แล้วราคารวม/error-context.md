# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 2-chat.spec.ts >> C13 ทาสีภายนอก 120 ตร.ม. แล้วราคารวม
- Location: tests\_bm.ts:298:3

# Error details

```
Error: คำตอบควรตรง /(^|\D)8\s*(?:แกลลอน|gal)|แปดแกลลอน/i

expect(received).toMatch(expected)

Expected pattern: /(^|\D)8\s*(?:แกลลอน|gal)|แปดแกลลอน/i
Received string:  "[TAG]{\"type\":\"paint\",\"area\":120,\"coats\":2,\"paintType\":\"exterior\"}"
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]: เปิด จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00 · LINE @buildmart-demo
  - banner [ref=e4]:
    - generic [ref=e5]:
      - link "บ้านช่าง BuildMart หน้าแรก" [ref=e6] [cursor=pointer]:
        - /url: /
        - generic [ref=e11]: บ้านช่าง BuildMart
      - search [ref=e12]:
        - textbox "ค้นหาสินค้า" [ref=e13]:
          - /placeholder: ค้นหาสินค้า เช่น ปูน, DB12, สี
        - button "ค้นหา" [ref=e14] [cursor=pointer]
      - navigation "เมนูหลัก" [ref=e15]:
        - link "สินค้า" [ref=e16] [cursor=pointer]:
          - /url: /products
        - link "คำนวณวัสดุ" [ref=e17] [cursor=pointer]:
          - /url: /calculator
        - link "🛒 ตะกร้า 0" [ref=e18] [cursor=pointer]:
          - /url: /cart
          - text: 🛒 ตะกร้า
          - generic [ref=e19]: "0"
        - link "ติดตามคำสั่งซื้อ" [ref=e20] [cursor=pointer]:
          - /url: /track
        - link "หลังร้าน" [ref=e21] [cursor=pointer]:
          - /url: /admin
  - main [ref=e22]:
    - region "บ้านช่าง BuildMart" [ref=e23]:
      - generic [ref=e28]:
        - generic [ref=e29]:
          - generic [ref=e30]: ใหม่
          - text: ถามน้องช่างด้วยเสียง · ตอบพร้อมอ้างอิงเอกสาร
        - heading "วัสดุก่อสร้างครบ จบที่บ้านช่าง" [level=1] [ref=e31]: วัสดุก่อสร้างครบจบที่บ้านช่าง
        - paragraph [ref=e32]: ปูน เหล็ก อิฐ กระเบื้อง สี ประปา ไฟฟ้า — ซื้อเยอะยิ่งถูก (50 ชิ้นขึ้นไปลด 5% · 200 ชิ้นขึ้นไปลด 10%) ส่งจาก 3 สาขา ลาดกระบัง · บางนา · รังสิต
        - generic [ref=e33]:
          - link "ดูสินค้าทั้งหมด →" [ref=e34] [cursor=pointer]:
            - /url: /products
          - link "🧮 คำนวณวัสดุ" [ref=e35] [cursor=pointer]:
            - /url: /calculator
          - button "🎙 คุยกับน้องช่าง" [ref=e36] [cursor=pointer]
        - generic [ref=e37]:
          - generic [ref=e38]:
            - generic [ref=e39]: "11"
            - generic [ref=e40]: หมวดวัสดุ
          - generic [ref=e41]:
            - generic [ref=e42]: "3"
            - generic [ref=e43]: สาขาพร้อมส่ง
          - generic [ref=e44]:
            - generic [ref=e45]: −10%
            - generic [ref=e46]: ราคาส่งสูงสุด
          - generic [ref=e47]:
            - generic [ref=e48]: 24 ชม.
            - generic [ref=e49]: ผู้ช่วย AI
      - generic [aria-hidden] [ref=e50]: SCROLL
    - heading "หมวดสินค้า" [level=2] [ref=e51]
    - paragraph [ref=e52]: เลือกหมวดเพื่อดูสินค้า ราคาส่ง และสต็อกแต่ละสาขา
    - generic [ref=e53]:
      - link "ปูน ดูสินค้า →" [ref=e54] [cursor=pointer]:
        - /url: /products?category=%E0%B8%9B%E0%B8%B9%E0%B8%99
        - generic [aria-hidden] [ref=e56]: 🪣
        - generic [ref=e57]: ปูน
        - generic [ref=e58]: ดูสินค้า →
      - link "หิน-ทราย ดูสินค้า →" [ref=e59] [cursor=pointer]:
        - /url: /products?category=%E0%B8%AB%E0%B8%B4%E0%B8%99-%E0%B8%97%E0%B8%A3%E0%B8%B2%E0%B8%A2
        - generic [aria-hidden] [ref=e61]: ⛰️
        - generic [ref=e62]: หิน-ทราย
        - generic [ref=e63]: ดูสินค้า →
      - link "เหล็ก ดูสินค้า →" [ref=e64] [cursor=pointer]:
        - /url: /products?category=%E0%B9%80%E0%B8%AB%E0%B8%A5%E0%B9%87%E0%B8%81
        - generic [aria-hidden] [ref=e66]: 🔩
        - generic [ref=e67]: เหล็ก
        - generic [ref=e68]: ดูสินค้า →
      - link "อิฐ-บล็อก ดูสินค้า →" [ref=e69] [cursor=pointer]:
        - /url: /products?category=%E0%B8%AD%E0%B8%B4%E0%B8%90-%E0%B8%9A%E0%B8%A5%E0%B9%87%E0%B8%AD%E0%B8%81
        - generic [aria-hidden] [ref=e71]: 🧱
        - generic [ref=e72]: อิฐ-บล็อก
        - generic [ref=e73]: ดูสินค้า →
      - link "กระเบื้อง ดูสินค้า →" [ref=e74] [cursor=pointer]:
        - /url: /products?category=%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%9A%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%87
        - generic [aria-hidden] [ref=e76]: 🔲
        - generic [ref=e77]: กระเบื้อง
        - generic [ref=e78]: ดูสินค้า →
      - link "สี ดูสินค้า →" [ref=e79] [cursor=pointer]:
        - /url: /products?category=%E0%B8%AA%E0%B8%B5
        - generic [aria-hidden] [ref=e81]: 🎨
        - generic [ref=e82]: สี
        - generic [ref=e83]: ดูสินค้า →
      - link "ประปา ดูสินค้า →" [ref=e84] [cursor=pointer]:
        - /url: /products?category=%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%9B%E0%B8%B2
        - generic [aria-hidden] [ref=e86]: 🚰
        - generic [ref=e87]: ประปา
        - generic [ref=e88]: ดูสินค้า →
      - link "ไฟฟ้า ดูสินค้า →" [ref=e89] [cursor=pointer]:
        - /url: /products?category=%E0%B9%84%E0%B8%9F%E0%B8%9F%E0%B9%89%E0%B8%B2
        - generic [aria-hidden] [ref=e91]: 💡
        - generic [ref=e92]: ไฟฟ้า
        - generic [ref=e93]: ดูสินค้า →
      - link "หลังคา ดูสินค้า →" [ref=e94] [cursor=pointer]:
        - /url: /products?category=%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%84%E0%B8%B2
        - generic [aria-hidden] [ref=e96]: 🏠
        - generic [ref=e97]: หลังคา
        - generic [ref=e98]: ดูสินค้า →
      - link "ไม้ ดูสินค้า →" [ref=e99] [cursor=pointer]:
        - /url: /products?category=%E0%B9%84%E0%B8%A1%E0%B9%89
        - generic [aria-hidden] [ref=e101]: 🪵
        - generic [ref=e102]: ไม้
        - generic [ref=e103]: ดูสินค้า →
      - link "เครื่องมือ ดูสินค้า →" [ref=e104] [cursor=pointer]:
        - /url: /products?category=%E0%B9%80%E0%B8%84%E0%B8%A3%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%A1%E0%B8%B7%E0%B8%AD
        - generic [aria-hidden] [ref=e106]: 🔨
        - generic [ref=e107]: เครื่องมือ
        - generic [ref=e108]: ดูสินค้า →
    - heading "ทำไมช่างเลือกบ้านช่าง" [level=2] [ref=e109]
    - generic [ref=e110]:
      - generic [ref=e111]:
        - generic [aria-hidden] [ref=e112]: 🏷️
        - heading "ยิ่งซื้อเยอะ ยิ่งถูก" [level=3] [ref=e113]
        - paragraph [ref=e114]: 50 ชิ้นขึ้นไปลด 5% · 200 ชิ้นขึ้นไปลด 10% คิดแยกต่อรายการอัตโนมัติ
      - generic [ref=e115]:
        - generic [aria-hidden] [ref=e116]: 🚚
        - heading "ส่งถึงหน้างาน" [level=3] [ref=e117]
        - paragraph [ref=e118]: เลือกรถให้ตามน้ำหนัก กระบะ · 6 ล้อ · 10 ล้อ ส่งฟรีเมื่อยอดถึง 20,000 บาท
      - generic [ref=e119]:
        - generic [aria-hidden] [ref=e120]: 🏬
        - heading "3 สาขา สต็อกเรียลไทม์" [level=3] [ref=e121]
        - paragraph [ref=e122]: ลาดกระบัง · บางนา · รังสิต ดูของคงเหลือแต่ละสาขาก่อนสั่ง
      - generic [ref=e123]:
        - generic [aria-hidden] [ref=e124]: 🧮
        - heading "คำนวณวัสดุให้" [level=3] [ref=e125]
        - paragraph [ref=e126]: คอนกรีต ผนัง กระเบื้อง สี เหล็กเส้น — ได้จำนวนแล้วใส่ตะกร้าได้ทันที
    - region "น้องช่าง ผู้ช่วย AI" [ref=e127]:
      - generic [ref=e128]:
        - generic [ref=e129]:
          - generic [ref=e130]: AI
          - text: น้องช่าง · ผู้ช่วยหน้าร้าน
        - heading "ถามด้วยเสียงได้เลย น้องช่างฟัง คิด แล้วตอบเป็นเสียง" [level=2] [ref=e131]
        - paragraph [ref=e132]: ถามราคา สต็อก 3 สาขา วิธีใช้งานจากเอกสารสเปก ให้คำนวณวัสดุ ใส่ตะกร้า หรือออกใบเสนอราคา — ทุกคำตอบจากเอกสารมีป้ายอ้างอิงหน้า PDF ให้กดเปิดดูได้
        - generic [ref=e133]:
          - generic [ref=e134]: 🎙 พูดถามได้ (Whisper)
          - generic [ref=e135]: 🔊 ตอบเป็นเสียง
          - generic [ref=e136]: 📄 อ้างอิงเอกสาร (RAG + rerank)
          - generic [ref=e137]: 🛒 ใส่ตะกร้าให้
        - button "💬 เริ่มคุยกับน้องช่าง" [ref=e139] [cursor=pointer]
  - contentinfo [ref=e142]:
    - generic [ref=e143]:
      - generic [ref=e144]: บ้านช่าง BuildMart · ราคาสินค้ายังไม่รวม VAT 7%
      - generic [ref=e145]: ลาดกระบัง 02-111-0001 · บางนา 02-111-0002 · รังสิต 02-111-0003
  - dialog "แชทกับน้องช่าง" [ref=e147]:
    - banner [ref=e148]:
      - generic:
        - img "น้องช่าง (idle)"
      - generic [ref=e152]:
        - generic [ref=e153]: น้องช่าง 🤖 BuildMart
        - generic [ref=e154]: ผู้ช่วยเรื่องวัสดุก่อสร้าง · ตอบทันที 24 ชม.
      - button "ปิดแชท" [ref=e156] [cursor=pointer]: ✕
      - generic [ref=e157]:
        - generic "ตอบเสร็จแล้วน้องช่างพูดคำตอบให้ฟังอัตโนมัติ" [ref=e158] [cursor=pointer]:
          - checkbox "คุยด้วยเสียง" [ref=e159]
          - generic: คุยด้วยเสียง
        - generic "อ่านออกเสียงคำตอบอัตโนมัติ" [ref=e160] [cursor=pointer]:
          - checkbox "อ่านออกเสียงอัตโนมัติ" [ref=e161]
          - generic: อ่านออกเสียงอัตโนมัติ
    - generic [ref=e162]:
      - generic [ref=e163]: สวัสดีครับ ผม น้องช่าง 👷 ถามได้ทั้งราคา สต็อก 3 สาขา คำนวณวัสดุ ใส่ตะกร้า หรือขอใบเสนอราคาครับ · กด 🎙 แล้วพูดถามได้เลย
      - generic [ref=e164]: ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน
      - generic [ref=e166]:
        - paragraph [ref=e168]: "[TAG]{\"type\":\"paint\",\"area\":120,\"coats\":2,\"paintType\":\"exterior\"}"
        - generic [ref=e169]:
          - link "PNT-001" [ref=e170] [cursor=pointer]:
            - /url: /products/PNT-001
          - link "PNT-002" [ref=e173] [cursor=pointer]:
            - /url: /products/PNT-002
          - link "PNT-003" [ref=e176] [cursor=pointer]:
            - /url: /products/PNT-003
          - link "PNT-004" [ref=e179] [cursor=pointer]:
            - /url: /products/PNT-004
          - button "ฟัง" [ref=e182] [cursor=pointer]:
            - generic [aria-hidden] [ref=e183]: 🔊
            - text: ฟัง
    - generic [ref=e184]:
      - button "ร้านเปิดกี่โมง" [ref=e185] [cursor=pointer]
      - button "เทคอนกรีต 3 คิวใช้ปูนกี่ถุง" [ref=e186] [cursor=pointer]
      - button "ปูนเก็บได้นานแค่ไหน" [ref=e187] [cursor=pointer]
    - generic [ref=e188]:
      - button "กดแล้วพูดถาม" [ref=e189] [cursor=pointer]
      - textbox "พิมพ์คำถาม หรือกด 🎙 แล้วพูด" [active] [ref=e194]
      - button "ส่ง" [disabled] [ref=e195]: ➤
  - alert [ref=e196]
```

# Test source

```ts
  94  |       try {
  95  |         sessionStorage.setItem('__bm_caption', t);
  96  |       } catch {}
  97  |       const c = document.getElementById('__bm_caption');
  98  |       if (c) {
  99  |         c.textContent = t;
  100 |         c.style.display = t ? 'block' : 'none';
  101 |       }
  102 |     }, text)
  103 |     .catch(() => {});
  104 | }
  105 | 
  106 | /** การ์ดเปิดเคส: บอกว่าทำอะไร และผ่านเมื่อไร (ค้าง ~3 วิ) */
  107 | export async function intro(page: Page, item: PlayItem, ms = 3000) {
  108 |   await page.evaluate(
  109 |     ({ it }) => {
  110 |       const d = document.createElement('div');
  111 |       d.id = '__bm_intro';
  112 |       d.style.cssText =
  113 |         'position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;' +
  114 |         'background:rgba(20,20,24,.78);pointer-events:none;font-family:Sarabun,"Noto Sans Thai",Tahoma,sans-serif';
  115 |       const esc = (s: string) => s.replace(/[&<>]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[ch] as string);
  116 |       d.innerHTML = `<div style="background:#fff;border-radius:18px;padding:28px 36px;max-width:820px;box-shadow:0 20px 60px rgba(0,0,0,.4);border-top:8px solid #F26B1D">
  117 |         <div style="color:#F26B1D;font-weight:700;font-size:16px">${esc(it.group)}</div>
  118 |         <div style="font-size:34px;font-weight:800;color:#222;margin:4px 0 14px">${esc(it.id)} · ${esc(it.title)}</div>
  119 |         <div style="font-size:19px;color:#333;margin-bottom:8px"><b>ทำอะไร:</b> ${esc(it.what)}</div>
  120 |         <div style="font-size:19px;color:#333"><b>ผ่านเมื่อ:</b> ${esc(it.expect)}</div></div>`;
  121 |       document.documentElement.appendChild(d);
  122 |     },
  123 |     { it: item },
  124 |   );
  125 |   await page.waitForTimeout(ms);
  126 |   await page.evaluate(() => document.getElementById('__bm_intro')?.remove()).catch(() => {});
  127 | }
  128 | 
  129 | export async function hold(page: Page, ms = HOLD) {
  130 |   await page.waitForTimeout(ms);
  131 | }
  132 | 
  133 | /** พิมพ์ทีละตัว (delay 60 ms) ให้คนดูทัน */
  134 | export async function typeHuman(locator: Locator, text: string, opts: { clear?: boolean } = {}) {
  135 |   await locator.click();
  136 |   if (opts.clear !== false) await locator.fill('');
  137 |   await locator.pressSequentially(text, { delay: 60 });
  138 | }
  139 | 
  140 | /** ใส่ outline สีส้มชั่วคราวให้ element ที่กำลังตรวจ */
  141 | export async function highlight(locator: Locator, ms = 4500) {
  142 |   await locator.first().scrollIntoViewIfNeeded().catch(() => {});
  143 |   await locator
  144 |     .evaluateAll((els, ms) => {
  145 |       for (const el of els as HTMLElement[]) {
  146 |         const prev = [el.style.outline, el.style.outlineOffset, el.style.boxShadow];
  147 |         el.style.outline = '4px solid #ff8c00';
  148 |         el.style.outlineOffset = '2px';
  149 |         el.style.boxShadow = '0 0 0 8px rgba(255,140,0,.25)';
  150 |         setTimeout(() => {
  151 |           [el.style.outline, el.style.outlineOffset, el.style.boxShadow] = prev;
  152 |         }, ms);
  153 |       }
  154 |     }, ms)
  155 |     .catch(() => {});
  156 | }
  157 | 
  158 | /** ไฮไลต์แล้วค้างภาพ (ใช้หลังได้ผลแต่ละขั้น ก่อน assert ถัดไป) */
  159 | export async function show(page: Page, locator: Locator, ms = HOLD) {
  160 |   await highlight(locator, ms + 500);
  161 |   await hold(page, ms);
  162 | }
  163 | 
  164 | export async function attachText(info: TestInfo, name: string, body: string) {
  165 |   await info.attach(name, { body, contentType: 'text/plain' });
  166 | }
  167 | export async function attachJson(info: TestInfo, name: string, data: unknown) {
  168 |   await info.attach(name, { body: JSON.stringify(data, null, 2), contentType: 'application/json' });
  169 | }
  170 | 
  171 | // ---------------- ตรวจคำตอบแบบยืดหยุ่น ----------------
  172 | /** เลขไทย → อารบิก · ตัด comma คั่นหลักพัน (7,120 → 7120) · ตัด zero-width · ช่องว่างซ้ำ → ช่องเดียว (ใช้ทั้งคำตอบและคำที่ค้น) */
  173 | export const norm = (s: string) =>
  174 |   s
  175 |     .replace(/[๐-๙]/g, (d) => String(d.charCodeAt(0) - 0x0e50))
  176 |     .replace(/[\u200b\u200c\u200d\ufeff]/g, '')
  177 |     .replace(/(\d),(?=\d{3}(?!\d))/g, '$1')
  178 |     .replace(/\s+/g, ' ')
  179 |     .trim();
  180 | 
  181 | export type Check = string | RegExp | { mock: string | RegExp; ai: string | RegExp };
  182 | 
  183 | /** mock: ต้องมีคำนั้นตรงตัว (ยอม comma) · ai: ใช้ regex ยืดหยุ่นถ้าให้มา
  184 |  *  ตรวจบนข้อความที่ผ่าน norm() แล้วทุกโหมด → regex ไม่ต้องเผื่อ comma / เลขไทย / ช่องว่างซ้ำ */
  185 | export function expectAnswer(answer: string, checks: Check[], opts: { soft?: boolean; label?: string } = {}) {
  186 |   const a = norm(answer);
  187 |   const ex = opts.soft ? expect.soft : expect;
  188 |   const pre = opts.label ? `${opts.label}: ` : '';
  189 |   let ok = true;
  190 |   for (const c of checks) {
  191 |     const pick = typeof c === 'object' && !(c instanceof RegExp) ? (MODE === 'ai' ? c.ai : c.mock) : c;
  192 |     const hit = pick instanceof RegExp ? pick.test(a) : a.includes(norm(pick));
  193 |     ok &&= hit;
> 194 |     if (pick instanceof RegExp) ex(a, `${pre}คำตอบควรตรง ${pick}`).toMatch(pick);
      |                                                                    ^ Error: คำตอบควรตรง /(^|\D)8\s*(?:แกลลอน|gal)|แปดแกลลอน/i
  195 |     else ex(a, `${pre}คำตอบควรมี "${pick}"`).toContain(norm(pick));
  196 |   }
  197 |   return ok;
  198 | }
  199 | 
  200 | // ---------------- API helper (ใช้ cookie session เดียวกับหน้าเว็บ) ----------------
  201 | export async function apiJson(req: APIRequestContext, method: string, url: string, data?: unknown) {
  202 |   const r = await req.fetch(url, { method, data, headers: data ? { 'Content-Type': 'application/json' } : undefined });
  203 |   const t = await r.text();
  204 |   let j: any = null;
  205 |   try {
  206 |     j = JSON.parse(t);
  207 |   } catch {
  208 |     j = { raw: t };
  209 |   }
  210 |   if (!r.ok()) throw new Error(`${method} ${url} → ${r.status()} ${t.slice(0, 200)}`);
  211 |   return j;
  212 | }
  213 | 
  214 | export async function getStock(req: APIRequestContext, sku: string): Promise<Record<string, number>> {
  215 |   const p = await apiJson(req, 'GET', `/api/products/${sku}`);
  216 |   return Object.fromEntries((p.stock || []).map((s: any) => [s.branch, Number(s.qty)]));
  217 | }
  218 | 
  219 | export async function adminLogin(page: Page) {
  220 |   await page.goto('/admin');
  221 |   const pw = page.getByTestId('admin-password');
  222 |   if (await pw.isVisible().catch(() => false)) {
  223 |     await say(page, 'ล็อกอินหลังร้าน (รหัส dev)');
  224 |     await typeHuman(pw, ADMIN_PASSWORD);
  225 |     await page.getByTestId('admin-login').click();
  226 |     await expect(page.getByTestId('admin-password')).toHaveCount(0, { timeout: 20_000 });
  227 |   }
  228 | }
  229 | 
  230 | // ---------------- แชท ----------------
  231 | export type Answer = { text: string; cites: string[]; citeLabels: string[] };
  232 | 
  233 | export async function openChat(page: Page) {
  234 |   if (!(await page.getByTestId('chat-panel').isVisible().catch(() => false))) {
  235 |     await highlight(page.getByTestId('chat-open'), 1500);
  236 |     await page.waitForTimeout(800);
  237 |     await page.getByTestId('chat-open').click();
  238 |   }
  239 |   await expect(page.getByTestId('chat-panel')).toBeVisible();
  240 |   await page.waitForTimeout(800); // ให้ประวัติแชทโหลดก่อนนับข้อความ
  241 | }
  242 | 
  243 | /** พิมพ์คำถาม → ส่ง → รอคำตอบเสร็จ (data-done) → ไฮไลต์ + ค้างภาพ → attach คำตอบ */
  244 | export async function ask(
  245 |   page: Page,
  246 |   info: TestInfo,
  247 |   question: string,
  248 |   opts: { timeout?: number; holdMs?: number; attachName?: string; waitDone?: boolean } = {},
  249 | ): Promise<Answer> {
  250 |   await openChat(page);
  251 |   const bots = page.getByTestId('chat-msg-bot');
  252 |   const before = await bots.count();
  253 |   await say(page, `พิมพ์ถามน้องช่าง: “${question}”`);
  254 |   await typeHuman(page.getByTestId('chat-input'), question);
  255 |   await page.getByTestId('chat-send').click();
  256 |   const bot = bots.nth(before);
  257 |   await expect(bot).toHaveAttribute('data-done', 'true', { timeout: opts.timeout ?? ANSWER_TIMEOUT });
  258 |   const ans = await readAnswer(page, bot);
  259 |   await info.attach(opts.attachName ?? 'answer', { body: ans.text, contentType: 'text/plain' });
  260 |   if (ans.cites.length) await attachJson(info, 'cites', ans.citeLabels);
  261 |   await say(page, ans.cites.length ? `ได้คำตอบ + ป้ายอ้างอิง ${ans.cites.join(', ')}` : 'ได้คำตอบแล้ว');
  262 |   await highlight(bot, (opts.holdMs ?? HOLD) + 500);
  263 |   const citeLoc = page.getByTestId('chat-cite');
  264 |   if (ans.cites.length) await highlight(citeLoc, (opts.holdMs ?? HOLD) + 500);
  265 |   await hold(page, opts.holdMs ?? HOLD);
  266 |   return ans;
  267 | }
  268 | 
  269 | /** อ่านข้อความ + cites ของ bubble บอท (cites อยู่ใน row เดียวกัน) */
  270 | export async function readAnswer(page: Page, bot: Locator): Promise<Answer> {
  271 |   const text = (await bot.innerText()).trim();
  272 |   const row = bot.locator('xpath=..');
  273 |   const cites = row.getByTestId('chat-cite');
  274 |   const n = await cites.count();
  275 |   const files: string[] = [];
  276 |   const labels: string[] = [];
  277 |   for (let i = 0; i < n; i++) {
  278 |     const href = (await cites.nth(i).getAttribute('href')) || '';
  279 |     const m = href.match(/\/api\/docs\/([^#?]+)/);
  280 |     if (m) files.push(decodeURIComponent(m[1]));
  281 |     labels.push((await cites.nth(i).innerText()).trim());
  282 |   }
  283 |   return { text, cites: [...new Set(files)], citeLabels: labels };
  284 | }
  285 | 
  286 | export function expectCite(ans: Answer, filename: string) {
  287 |   expect(ans.cites, `ควรมีป้ายอ้างอิง ${filename}`).toContain(filename);
  288 | }
  289 | 
  290 | /** สร้าง test 1 เคสจาก playlist (ชื่อ test ขึ้นต้นด้วย id) */
  291 | export function bmCase(
  292 |   id: string,
  293 |   fn: (args: { page: Page; item: PlayItem; browser: import('@playwright/test').Browser; context: import('@playwright/test').BrowserContext }, info: TestInfo) => Promise<void>,
  294 |   opts: { timeout?: number; skip?: () => string | false } = {},
```