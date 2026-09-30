# เพิ่มเติมจากผู้ใช้ (สำคัญ — ปรับงานต่อจากที่ทำไว้ ไม่ต้องเริ่มใหม่)
ช่วงทดลองค้นหาตั๋ว (agent run) ต้องให้ นศ เห็นทุกขั้นแบบโปร่งใส:
1. ใช้ snapshot จริงของหน้าเว็บในแต่ละ step (ไม่ใช่ตัวอย่างแต่ง)
2. page.png = ภาพจริงของเว็บที่ "วงกลมแดง" รอบ element ที่จะ action + กล่องคำอธิบาย (callout) บนภาพ เช่น
   "Step 3 · fill f1e21 = Bangkok (ช่อง Where from?)" — ทำโดย inject overlay HTML/SVG เข้าไปในหน้าด้วย `eval`
   ตาม box จาก `snapshot --boxes` แล้ว `screenshot --hires` แล้วลบ overlay ออก (PIL วาดภาษาไทยไม่ครบ จึงใช้ overlay HTML)
   วาง callout ในที่ว่าง ไม่บังของที่กำลังอธิบาย
3. แสดง process ส่งให้ LLM ตัดสินใจ: ทุก step เก็บ
   - prompt.txt = ข้อความ plain text ที่ส่งให้ LLM จริงทั้งก้อน (เป้าหมาย step + snapshot ที่ตัดแล้ว + กติกา + รูปแบบคำตอบ)
   - decision.json = คำตอบ LLM ดิบ + ผล validate ของโค้ด (allowlist/ref มีจริง/denylist) 
   - act.txt = คำสั่ง playwright-cli ที่โค้ดรันจริง + output ย่อ + ผล verify
4. ทั้งหมดต้องขับด้วย prompt plain text: การคุยกับ LLM เป็น plain text prompt (อ่านรู้เรื่อง ไม่ใช่ JSON ซ้อนยาก ๆ) ตอบกลับเป็น JSON ตาม schema;
   และใน README ส่วนทดลอง นศ แค่ copy พรอมต์ plain text สั้น ๆ ไปวางใน yolo1 ก็ได้ผลเดียวกัน
5. README: แต่ละ step แสดงเป็นชุด  [ภาพ page.png วงกลม+callout] → [ตัดตอน prompt.txt ที่ส่ง LLM] → [decision.json] → [คำสั่ง Act + ผล verify]
   (ตัดตอนให้สั้นอ่านง่าย ลิงก์ไปไฟล์เต็มใน log/steps/)
6. ภาพแนวคิดสร้างเสร็จแล้ว 6 ภาพที่ $W/img_gen/concept-0{1..6}-*.png (architecture, loop, snapshot-ref, stale-ref, guardrail, decision-json)
   ให้เปิดดู แล้วคัดลอกภาพที่ใช้ไป 06_Playwright_CLI_Trip/img/ และใส่ในตำแหน่งที่เหมาะ ไม่ต้องทำ imagegen_todo.md
7. (เพิ่มล่าสุด) ผู้ใช้ต้องการเห็น process "ทีละ step อย่างละเอียด" เพื่อให้ นศ เข้าใจ:
   ทุก step ของ agent run ใน README ต้องมีหัวข้อย่อยของตัวเอง แยกเป็น 4 ช่วงชัดเจน
   ① Observe (คำสั่ง snapshot จริง + ตัดตอน YAML บรรทัดที่เกี่ยว พร้อม ref)
   ② Decide (prompt plain text ที่ส่ง LLM + JSON ที่ตอบกลับ + เหตุผล)
   ③ Validate→Act (ผลตรวจของโค้ดทีละข้อ ✓/✗ + คำสั่ง playwright-cli ที่รันจริง + ภาพวงกลม+callout)
   ④ Verify (snapshot ใหม่ บรรทัดที่พิสูจน์ว่าสถานะเปลี่ยน + ทำไม ref เก่าใช้ต่อไม่ได้)
   ห้ามข้ามหรือรวบ step; อธิบายเป็นภาษาไทยสั้นใต้แต่ละช่วงว่า "เกิดอะไรขึ้น/ทำไม"
8. (เพิ่มล่าสุด) ผู้ใช้ต้องการ "ทฤษฎีเพิ่มขึ้นอีก" — ส่วนทฤษฎีใน README ให้ลึกขึ้น (ภาษาไทย กระชับ มีตัวอย่างจากงานจริงนี้ประกอบ) หัวข้อที่ควรมี:
   - 3 แบบของ web automation: scripted (selector ตายตัว) / LLM-in-control (agent ถือ tool เอง) / code-in-control — ตารางเทียบ ข้อดี ข้อเสีย ความเสี่ยง เมื่อไรควรใช้
   - ตาของ agent: DOM/selector vs screenshot+vision vs accessibility tree (role, name, state, ref) — ทำไม snapshot YAML เหมาะกับ LLM
   - วงจรชีวิตของ ref (สร้างตอน snapshot → ใช้ได้จนหน้าเปลี่ยน) และ box (css px, viewport-relative)
   - Structured output / JSON schema: ทำไมต้องบังคับ schema, validate แบบ fail-closed
   - Guardrail แบบ defense-in-depth: allowlist/denylist, max steps, human-in-the-loop, และ **prompt injection จากเนื้อหาหน้าเว็บ** (ข้อความบนเว็บพยายามสั่ง LLM) → เหตุผลที่กติกาต้องอยู่ในโค้ด
   - Context/token budget: ตัด snapshot, ทำไมส่งเฉพาะส่วนที่เกี่ยว
   - Verify / oracle: ตรวจผลด้วยโค้ดจาก snapshot ใหม่ ไม่เชื่อคำพูด LLM; ไม่เดาข้อมูล (ราคาต้องมี ref ที่มา)
   - Failure modes ของเว็บจริง: UI เปลี่ยน, dropdown/async/timing, consent, CAPTCHA/bot detection → หยุดและรายงาน ไม่พยายามเลี่ยง
   - Auditability/evidence และจริยธรรม (ToS, rate, ไม่ทำธุรกรรมแทนคน)
   ภาพแนวคิดชุดใหม่ (ละเอียดกว่า) กำลังสร้างที่ $W/img_gen/v2/ (01–11 รวม 09 llm-vs-code-control, 10 trim-snapshot, 11 red-circle) — ถ้ามีแล้วให้ใช้ v2 แทน v1 ชื่อไฟล์เดียวกัน วางประกอบทฤษฎีแต่ละหัวข้อ
9. (เพิ่มล่าสุด) **ทุก LAB** ต้องมี "accessibility snapshot เทียบกับหน้าเว็บจริง" ให้ นศ เห็นว่า YAML แต่ละบรรทัดคือ element ไหนบนจอ:
   - ภาพ compare.png ต่อ LAB (และต่อ step สำคัญของ agent run): ซ้าย = screenshot จริง (--hires) ที่ inject overlay กรอบสี + ป้ายเลข ①②③… 
     ตาม [box=...] ของ element ที่เกี่ยวข้อง 4–8 ตัว; ขวา = ตัดตอน snapshot YAML จริงบรรทัดเดียวกัน ระบายสี/เลขตรงกัน
     (ประกอบด้วย PIL: ข้อความ YAML เป็น ASCII ใช้ฟอนต์ monospace ได้; ป้ายภาษาไทยให้อยู่ใน overlay HTML บนหน้าเว็บเท่านั้น)
   - ใต้ภาพใน README ใส่ code block ```yaml ของบรรทัดเดียวกันจริง (copy ได้) พร้อมคอมเมนต์ # ① ... ให้ตรงกับภาพ
   - อธิบายสั้น: role / name / state (เช่น [expanded], [checked], value) / [ref] / [box] ของแต่ละบรรทัดตรงกับอะไรบนจอ
   - LAB ที่ไม่ได้ใช้เว็บ (ถ้ามี เช่น ตั้ง alias) ข้ามได้ นอกนั้นต้องมีทุก LAB
10. (เพิ่มล่าสุด) ต้องมีส่วน "อธิบายเทคนิค" (ก่อน LAB หรือเป็นกล่องอธิบายตอนใช้ครั้งแรก) — แต่ละหัวข้อ: คืออะไร · หน้าตาจริง (ตัวอย่างจาก snapshot ของงานนี้) · ใช้ทำอะไรใน loop · ข้อควรระวัง
   - Accessibility tree / accessibility snapshot: browser สร้างจาก DOM + ARIA อย่างไร, ทำไมเห็นแค่ element ที่มีความหมาย, รูปแบบ YAML (ย่อหน้า = parent/child)
   - role / name / state & value (เช่น [expanded], [checked], [disabled], [active], [cursor=pointer], /url:)
   - ref: รูปแบบจริง `f1e21` (ตรวจจริงว่า prefix f/เลขหมายถึงอะไร เช่น frame/รุ่น snapshot — ทดลองให้เห็น ห้ามเดา), ขอบเขตอายุ, ทำไมไม่ใช้ CSS selector
   - box: `snapshot --boxes` → [box=x,y,w,h] css px เทียบ viewport, ใช้วาดวงกลม/กรอบ, ผลของ deviceScaleFactor 2 (ภาพ --hires พิกัด ×2)
   - partial snapshot (`snapshot <ref>` / `--depth`), `find` ค้นใน snapshot, `eval` บนหน้า/บน element
   - session/daemon ของ playwright-cli (browser ค้างอยู่ระหว่างคำสั่ง, `-s=<name>`, `close`), config .playwright/cli.config.json, headless vs headed
   - structured output (`--json-schema`), fail-closed validation, allowlist/denylist, snapshot trimming, overlay injection
   ทุกข้ออ้างอิงเฉพาะที่ตรวจจริงแล้ว (--help หรือรันทดลอง) ถ้าไม่แน่ใจให้เขียนตามที่สังเกตได้และบอกว่าเป็นข้อสังเกต
11. (เพิ่มล่าสุด) **ทุก LAB ย่อย เป็น prompt-based**: นศ copy พรอมต์ plain text 1 กรอบ (```text) ไปวางใน yolo1 (container LAB 03, cwd /workspace) แล้วทำงานได้ทันทีจนได้ผล
   ไม่ต้องพิมพ์ shell เอง (ถ้ามีคำสั่ง shell ให้อยู่ในพรอมต์ให้ AI รัน) — พรอมต์ต้องครบในตัว (self-contained): เตรียม alias/config เองถ้ายังไม่มี, บอกไฟล์ output ที่ต้องได้
   โครงของแต่ละ LAB ย่อย:
   - 🎯 เป้าหมาย / แนวคิดที่ได้เรียน (2–3 บรรทัด)
   - 💬 พรอมต์ (สั้น กระชับ copy-วางได้เลย)
   - 📖 คำอธิบาย: พรอมต์นี้ทำให้ AI ทำอะไรทีละขั้น, ทำไมต้องเขียนแบบนี้ (เชื่อมกับทฤษฎี)
   - ✅ ผลที่ควรได้ (output จริงจากการรันพรอมต์นั้นจริงบนเครื่องนี้ + ภาพ compare/page จริง) และ วิธีตรวจว่าถูก
   **ต้องทดสอบทุกพรอมต์จริง**: รัน `yolo2 -p --model sonnet "<พรอมต์>"` ในโฟลเดอร์ scratch ใน .work (จำลอง นศ ที่ไม่มีบริบท) ให้ทำงานได้จนจบ
   ถ้าไม่ผ่านให้แก้พรอมต์แล้วรันซ้ำ; บันทึกผลทดสอบย่อไว้ใน $W/prompt_tests.md
