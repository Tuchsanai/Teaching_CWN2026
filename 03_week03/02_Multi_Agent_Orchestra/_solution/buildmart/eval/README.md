# eval/ — ประเมิน RAG + คำถามปกติ + บทสนทนาหลายรอบ (BuildMart v3)

ตาม BUILDMART ข้อ 8 · CONTRACT_V3 §6–§7 · ไม่มีการเรียก API ของ LLM ในสคริปต์ใด ๆ — ผู้ตัดสินคือ **Claude ที่รันพรอมต์** (อ่าน judge batch แล้วเขียน JSON)

```
parts/*.json ──merge.mjs──► qa.json ──run_eval.mjs──► runs/<label>/answers.json + pages/ + judge_batches/*.md
                                                        │ Claude ตัดสิน → judge_batches/batch-NN.judgments.json (หรือ judgments.json)
                                                        └─score.mjs──► runs/<label>/results.json ──POST /api/admin/eval──► /admin/eval
```

| ไฟล์ | หน้าที่ |
|---|---|
| `parts/rag-*.json` | set `rag` (จาก PDF) `{id, set, question, expected, key_facts, sources:[{filename,page}], type, difficulty}` |
| `parts/qa.json` | set `qa` (DB/ร้าน) `{id, set, question, expected, expected_values, sql, category, needs_products, volatile?}` |
| `parts/conv.json` | set `conv` 12 บท × 4–6 รอบ `{id, set, title, voice, turns:[{text, audio?, lang?, refers_to?, expected, key_facts?, expected_values?, sources?, needs_products?, expect_state?, volatile?}]}` |
| `merge.mjs` | รวม parts → `qa.json` · ตรวจ JSON/id ซ้ำ/ฟิลด์/จำนวนต่อ set (`--strict` = exit 1 ถ้าไม่ผ่าน) |
| `run_eval.mjs` | ถามผ่าน web API จริง · คิด metric โค้ด · เขียน judge batch |
| `score.mjs` | รวม metric โค้ด + คำตัดสิน → `results.json` · `--post` ส่งเข้า dashboard |

## ใช้งาน

```bash
cd eval
node merge.mjs                                                      # → qa.json (rag 169 · qa 79 · conv 12)
node run_eval.mjs --label ai-rerank-on  --mode ai --rerank on       # ทุก set · concurrency 2
node run_eval.mjs --label mock-smoke --mode mock --limit 2          # ทดสอบสคริปต์ 2 ข้อต่อ set
#   --set rag,qa,conv (หรือ --sets) · --ids CV-01,Q-05 · --concurrency 2 · --timeout 240000
#   --no-voice (รอบเสียงใช้ข้อความอ้างอิง) · --fixtures <dir> · --docs <LAB/documents> · --pdf-engine auto|pymupdf|pdfjs
#   --llm/--stt/--tts <ชื่อ> ใส่ใน config ของ run (dashboard แสดงเป็นป้าย · rerank=off ใช้เทียบ)
# … Claude ตัดสินทุก runs/<label>/judge_batches/batch-NN.md …
node score.mjs --label ai-rerank-on --post http://localhost:3400    # --as <ชื่อ> = label ที่ POST
node run_eval.mjs --label ai-rerank-on --rescore-cer                # คิด stt_cer ใหม่จาก transcript ที่บันทึกไว้ (ไม่ถาม API)
node make_report.mjs                                                # → RESULTS.md · results.html · SAMPLES.md    # header x-eval-token = $EVAL_TOKEN หรือ bm-eval (--token)
```

- **session ใหม่ต่อข้อ/บท**: คำขอแรกไม่ส่ง cookie เลย → web สร้าง `bm_sid` ใหม่ → รอบถัดไปในบทเดียวกันส่ง cookie นั้นต่อ (ตะกร้า/ประวัติ 10 ข้อความเป็นของบทนั้นเท่านั้น)
- **รอบเสียง** (`audio: "V0x.wav"`): `POST /api/voice` (multipart `audio`) ด้วยไฟล์ใน `e2e/voice-fixtures/` → ข้อความที่ถอดได้ไปถาม `/api/chat` · คิด `stt_cer` เทียบ `text` (+ `accept` ถ้ามี) · ไม่พบไฟล์/voice ปิด → ใช้ `text` ถามแทน (`stt_cer` = null) · ถอดได้ว่าง → ใช้ `text` ถามแทนแต่ `stt_cer` = 1
- **หลักฐานให้ผู้ตัดสิน**: API ส่งแค่ `retrieved:[{filename,page,score}]` → run_eval ดึงข้อความหน้านั้นจาก `LAB/documents/*.pdf` (PyMuPDF ผ่าน `python -I` ถ้ามี · ไม่งั้น pdfjs-dist จาก `eval/node_modules` หรือ `workers/node_modules`) เขียน `pages/<ไฟล์>-p<N>.txt` และใส่ excerpt (~1,400 ตัวอักษรที่ตรงคำถาม/คำตอบที่สุด) ใน batch
- API ไม่มีฟิลด์ `retrieved`/`products` (worker รุ่นเก่า) → metric ที่ต้องใช้ฟิลด์นั้นเป็น `null` (ไม่นับ) และมีคำเตือนใน `answers.json.meta.warnings`

## metric

| metric | set | คิดโดย | นิยาม |
|---|---|---|---|
| `hit_at_4` | rag (+conv รอบที่มี `sources`) | โค้ด | 1 ถ้า `retrieved[0..3]` มี (filename, page) ∈ `sources` · ข้อ `negative` ไม่นับ |
| `mrr` | rag | โค้ด | 1/อันดับแรกที่ตรง (1–4) · ไม่เจอ = 0 |
| `citation_acc` | rag | โค้ด | 1 ถ้ามี cite ≥ 1 ที่ตรง `sources` **และ**ไม่มี cite จากไฟล์นอก `sources` |
| `exact_value` | qa (+conv) | โค้ด | 1 ถ้า **ทุก**ค่าใน `expected_values` อยู่ในคำตอบ · ค่าตัวเลขล้วนเทียบเชิงตัวเลขหลัง normalize (ตัด `,` · เลขไทย→อารบิก · `137.75` = `137.750` · `"13,775"` = `13775`) · ค่าข้อความ/มีหน่วยเทียบแบบ substring หลังตัดช่องว่าง · ค่าที่เป็น array = รูปเขียนที่ยอมรับ (ตรงตัวใดตัวหนึ่งพอ) |
| `sql_correct` | qa (+conv) | โค้ด | 1 ถ้า `products` ⊇ SKU ใน `needs_products` ∪ SKU ใน `sql` · ข้อคูปอง/ค่าส่ง/ยอดรวมที่ไม่มี SKU = `exact_value` |
| `stt_cer` | conv เสียง | โค้ด | CER = (S+D+I)/N ระดับตัวอักษร (Levenshtein) หลังแปลงคำตัวเลขไทยเป็นตัวเลขทั้งสองฝั่ง (`shared/thainum.js`: สองจุดห้า→2.5 · ร้อยถุง→100 ถุง · หกสิบคูณหกสิบ→60x60 · ดีบี 12→DB12) แล้วตัดช่องว่าง/เครื่องหมาย · ตัวพิมพ์เล็ก · เลขไทย→อารบิก · ต่ำสุดของข้อความหลัก/`accept` · **ยิ่งต่ำยิ่งดี** |
| `key_fact_recall` | rag/conv | โค้ด (ช่วยผู้ตัดสิน) | สัดส่วน `key_facts` ที่ match ในคำตอบ (กติกาเดียวกับ exact_value) |
| `state_ok` | conv | โค้ด | รอบที่มี `expect_state`: `cartCount` ใน SSE done ตรง และ/หรือมี `quoteNo` |
| `faithfulness` | rag | ผู้ตัดสิน | ดู rubric |
| `correctness` | ทุก set | ผู้ตัดสิน | ดู rubric · conv = เฉลี่ยทุกรอบ |
| `context_retention` | conv | ผู้ตัดสิน | เฉลี่ยรอบที่ 2 ขึ้นไป |

**pass ต่อข้อ** (= "ผ่าน/ไม่ผ่าน ต่อข้อ" ใน `METRICS.md`): rag = `correctness` ≥ 0.5 และ `faithfulness` ≥ 0.5 · qa = `correctness` ≥ 0.5 และ (`exact_value` = 1 หรือไม่มี `expected_values`) · conv = **ทุกรอบ** `correctness` ≥ 0.5 (+ `exact_value` ≠ 0 · `state_ok` ≠ 0) และ `context_retention` ≥ 0.5 · ข้อที่ยังไม่ได้ตัดสิน → pass คิดจาก metric โค้ด (`key_fact_recall`/`exact_value` = 1) และ `reason` ขึ้นต้นด้วย "(ยังไม่ได้ตัดสิน …)" · ค่าเฉลี่ยของ metric ผู้ตัดสินคิดเฉพาะข้อที่ตัดสินแล้ว (`summary.<set>.judged`)

`results.json` = `{label, config:{llm, rerank, stt, tts, mode, …}, summary, items, meta}`
- `summary.rag|qa|conv` = `{<metric>: 0..1, n, judged, pass_rate}` (conv มี `turns` `voice_turns` เพิ่ม)
- `summary.sql` = สำเนาของ `summary.qa` (`alias_of:"qa"`) เพราะการ์ด B ของ `/admin/eval` ตอนนี้อ่าน key `sql` · ปิดได้ด้วย `--no-sql-alias`
- `summary.by_doc` (rag ต่อไฟล์) · `summary.by_type` (rag ต่อ `type` · qa ต่อ `category` · conv เสียง/ข้อความ) · `summary.by_difficulty.rag` · `summary.latency` (ttft/total p50/p95 ms)
- `items[]` = `{id, set, doc?, qtype, difficulty?, question, turns? (conv: {q, a, audio?, transcript?, refers_to, expected, metrics, reason}), expected:{answer, sources|values, key_facts|sql}, answer, retrieved, cites, products, metrics, pass, judged, reason}`

## Rubric ผู้ตัดสิน

คุณคือผู้ตัดสิน (Claude) — ตัดสินจาก**เนื้อหาจริง**เทียบ "คำตอบที่คาด" และ "ย่อหน้าที่ค้นได้" · metric โค้ดใน batch แสดงไว้ช่วยดูเท่านั้น (เช่น `exact_value` อาจเป็น 1 เพราะบอทลอกตารางค่าส่งทั้งตาราง ทั้งที่ไม่ได้ตอบค่าส่งของตะกร้านี้) · คะแนนใช้ได้แค่ **0 · 0.5 · 1** · `reason` ภาษาไทยสั้น ๆ บังคับเมื่อคะแนน < 1 และควรระบุสิ่งที่ผิดชัด ๆ ("ตอบ 64 แทน 48", "ไม่ได้บอกว่าห้ามปูพื้น", "ลืมว่าคุยเรื่อง CEM-003")

### correctness (rag · qa · conv ทุกรอบ)
| คะแนน | เมื่อ |
|---|---|
| **1** | ข้อเท็จจริงหลัก/ตัวเลขทุกตัวใน "คำตอบที่คาด" (`key_facts`/`expected_values`) ครบและถูก · ถ้อยคำต่างได้ หน่วยเทียบเท่าได้ (10 มม. = 10 มิล) · มีข้อมูลเสริมที่ถูกได้ · ข้อ `negative`/`off_topic`: บอกว่าไม่มีข้อมูลในเอกสาร/ปฏิเสธสุภาพโดย**ไม่แต่ง** · ข้อ `ambiguous`: ถามกลับหรือเสนอตัวเลือกที่ถูก · ถามอังกฤษต้องตอบอังกฤษ |
| **0.5** | ถูกบางส่วน: ขาดค่าบางตัว (ให้ราคาต่อหน่วยถูกแต่ไม่ให้ยอดรวม) · ปัดเศษ/คำนวณคลาดเล็กน้อย · ประเด็นหลักถูกแต่มีข้อมูลผิดประกอบ · ตอบผิดภาษา |
| **0** | ค่าหลักผิด · ไม่ตอบ/ตอบคนละเรื่อง · แต่งข้อมูลในข้อ negative · error/timeout · ปฏิเสธทั้งที่เอกสาร/DB มีคำตอบ |

ข้อ `volatile` (สต็อก): ถ้าตัวเลขต่างจากที่คาดแต่สอดคล้องกับข้อมูลใน DB ตอนรัน (มีการตัดสต็อกระหว่างทดสอบ) ให้ถือว่าถูก

### faithfulness (rag)
แยกคำตอบเป็นข้อกล่าวอ้าง (ตัวเลข ข้อกำหนด ขั้นตอน) → ตรวจทีละข้อว่ามีใน "ย่อหน้าที่ค้นได้" (excerpt หรือหน้าเต็มใน `../pages/`)
| คะแนน | เมื่อ |
|---|---|
| **1** | ทุกข้อกล่าวอ้างมีหลักฐานในหน้าที่ค้นได้ · หรือคำตอบบอกว่าไม่มีข้อมูล · ราคา/สต็อก/ข้อมูลร้าน (มาจาก DB/system prompt) ไม่ต้องมีหลักฐานใน PDF |
| **0.5** | ประเด็นหลักมีหลักฐาน แต่มีบางข้อกล่าวอ้างที่ไม่มีหลักฐาน |
| **0** | ประเด็นหลักไม่มีหลักฐาน (แต่ง/มาจากความรู้ทั่วไป) แม้บังเอิญถูก |

### context_retention (conv · รอบที่ 2 ขึ้นไป)
ให้คะแนน**การตีความสิ่งที่อ้างถึง** (`refers_to`) ไม่ใช่ความถูกของตัวเลข
| คะแนน | เมื่อ |
|---|---|
| **1** | เข้าใจว่า "อันนั้น/ตัวนี้/ตัวเมื่อกี้/แล้วถ้า…ล่ะ/ใส่ตะกร้า/ขอใบเสนอราคา" หมายถึงสินค้า/จำนวน/หัวข้อตาม `refers_to` (เช่น "แล้วถ้า 200 ถุงล่ะ" → สินค้าเดิม 200 ถุง) · การกระทำ (ใส่ตะกร้า) ทำกับสินค้า/จำนวนที่ถูก |
| **0.5** | ถูกครึ่งเดียว: ถูกสินค้าแต่ผิดจำนวน · ถามยืนยันทั้งที่บริบทชัด แต่ระบุสินค้าที่ถูก |
| **0** | ตีความผิดสินค้า/หัวข้อ · ลืมบริบทแล้วตอบกว้าง ๆ · ถามกลับว่า "สินค้าอะไร" ทั้งที่เพิ่งคุยกัน |

### รูปแบบไฟล์คำตัดสิน
คัดลอก `batch-NN.template.json` → `batch-NN.judgments.json` แล้วเติมค่า (หรือรวมทุกข้อไว้ใน `runs/<label>/judgments.json` ซึ่งจะทับไฟล์ batch):
```json
{
  "R-CEM-07": { "faithfulness": 1, "correctness": 0.5, "reason": "ให้ 5.5 กก. แต่ไม่บอกเกรียง 10 มม." },
  "Q-12":     { "correctness": 1, "reason": "" },
  "CV-03": {
    "turns": [
      { "correctness": 1, "reason": "" },
      { "correctness": 1, "context_retention": 1, "reason": "" },
      { "correctness": 0, "context_retention": 0, "reason": "ตอบระยะทาบของ RB9 แทน DB12" }
    ],
    "reason": "รอบ 3 ลืมว่าคุยเรื่อง DB12"
  }
}
```
ไม่อยากตัดสินรายรอบ ให้ใส่ `correctness`/`context_retention` ระดับบทแทน `turns` ได้ (แต่ pass ของ conv จะใช้ค่าระดับบท = 1)

## ชุด conv (parts/conv.json)
12 บท · 60 รอบ · 5 บทใช้เสียง (V01–V10 ครบทุกไฟล์) · ผสม PDF (6 ไฟล์) + DB (ราคา ราคาส่ง สต็อก) + ตะกร้า (`expect_state.cartCount`) + ใบเสนอราคา (`quoteNo`) + คูปอง + ค่าส่ง + เครื่องคำนวณ · ทุกตัวเลขคำนวณด้วย `shared/pricing.js` + `shared/calc.js` + seed (`db/init/02_seed.sql`) · เลขหน้าตรวจจาก PDF จริง

| บท | เรื่อง | เสียง |
|---|---|---|
| CV-01 | CEM-001 อายุเก็บ → ราคาส่ง 100 ถุง → ใส่ตะกร้า → รถ/ค่าส่ง → ใบเสนอราคา | V01 V02 V03 V09 V10 |
| CV-02 | เกรียง 60x60 → อัตราปูนกาว → 20 ตร.ม. กี่กิโล → กี่ถุง → ตะกร้า → ยอดรวม VAT | V04 V05 |
| CV-03 | DB12 สต็อกรังสิต → สาขามากสุด → ระยะทาบ → "แล้วถ้า DB16 ล่ะ" → ราคาส่ง 200 เส้น | V06 |
| CV-04 | THW 2.5 คู่เบรกเกอร์ → ราคา/ประกัน ELC-002 → ตะกร้า → ยอดรวม → คูปอง BUILD5 | V07 |
| CV-05 | ประกันสีภายนอก (อังกฤษ) → ภายใน → ราคา → ทา 120 ตร.ม. → ทาเที่ยว 2 | V08 |
| CV-06 | TIL-002 ปูพื้นได้ไหม → TIL-001 → 12 ตร.ม. กี่กล่อง → ยาแนว → ราคา | – |
| CV-07 | ปูนเปิดถุงคืนได้ไหม → ยังไม่เปิด → เหล็กสั่งตัด → แต้ม Pro → แลกได้ไหม | – |
| CV-08 | คอนกรีต 3 คิว → บ่ม → มาตรฐานปูน → ใส่ตะกร้าทั้งหมด → BUILD5 + รถ 10 ล้อ | – |
| CV-09 | PVC 8.5 น้ำดีได้ไหม → ท่อน้ำดี 60 เส้น → ข้องอ → รอกาว | – |
| CV-10 | อิฐมวลเบา 30 ตร.ม. → ปูนก่อที่รังสิต (หมด) → ถ้าอิฐมอญ → ราคาส่ง → รถส่ง | – |
| CV-11 | (อังกฤษ) DB16 ราคา → มาตรฐาน → 150 เส้น → CONTRACTOR10 → เปิดวันอาทิตย์ | – |
| CV-12 | "ปูนถุงละเท่าไร" (คลุมเครือ) → ตัวที่ใช้ฉาบ → 50 ถุง → "แล้วถ้า 200 ถุงล่ะ" → ฉาบหนาเกิน 1.5 ซม. | – |

รอบสต็อก (`volatile:true`) ใช้ค่า seed — ถ้ามีการตัดสต็อกก่อนรัน ให้ผู้ตัดสินเทียบกับ DB ตอนรัน
