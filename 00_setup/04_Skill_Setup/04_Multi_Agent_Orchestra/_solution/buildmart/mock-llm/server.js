// mock-llm ของ "บ้านช่าง BuildMart" — LLM จำลองแบบ OpenAI-compatible (ไม่ต้องใช้ GPU)
// รองรับ: GET /health · GET /v1/models · POST /v1/chat/completions (stream SSE และ non-stream)
// v3 (API เดียวกับ ai-box · CONTRACT_V3 §3):
//   POST /v1/audio/transcriptions  multipart `file` → sha256 → ข้อความจาก e2e/voice-fixtures/index.json (ไม่รู้จัก → text '')
//   POST /v1/rerank                {query, documents, top_n} → ลำดับเดิม (score ลดหลั่น)
//   POST /v1/audio/speech          {input} → e2e/voice-fixtures/tts-cache/<sha256(input)>.wav (อัดจาก VoxCPM2 จริง)
//                                  ไม่มี → tts-cache/generic.wav → ไม่มีอีก → เสียงสังเคราะห์สั้น ๆ (header x-tts-engine: mock)
// หน่วงเวลาให้ใกล้ของจริง (load test): MOCK_TTFT_MS (ก่อน token แรก) · MOCK_DELAY_MS (ต่อ delta) · MOCK_STT_MS · MOCK_TTS_MS
//   MOCK_RERANK_MS · MOCK_LLM_SLOTS (>0 = รับแชทพร้อมกันได้เท่านี้ ที่เหลือรอคิว เหมือน KV cache ของ GPU เต็ม)
// บทสนทนาหลายรอบ: อ่านหัวข้อ "## บริบทบทสนทนา" (สินค้าที่กำลังคุยถึง + จำนวนล่าสุด) ที่ chat-worker ใส่มา
//   → "อันนั้นราคาเท่าไร" / "แล้วราคาส่ง 100 ถุงล่ะ" / "ใส่ตะกร้าให้หน่อย" ใช้สินค้านั้นต่อได้
// ไม่มี dependency (ใช้ http ของ Node ล้วน)
//
// หลักการ: ทำตัวเหมือน LLM ที่ "รู้เฉพาะสิ่งที่ chat-worker ใส่มาใน messages" เท่านั้น
//   - ข้อมูลร้าน / ตารางสินค้า (## สินค้าที่เกี่ยวข้อง) / เอกสารอ้างอิง (## เอกสารอ้างอิง) อ่านจาก system prompt
//   - ไม่เปิดอ่าน PDF หรือ DB เอง (พิสูจน์ว่า RAG ทำงานจริง)
//   - ผลของ tag มาเป็นข้อความที่ขึ้นต้นด้วย "ผลคำนวณ:" / "ผลคำสั่ง:" ตามด้วย JSON
// รูปแบบ input ทั้งหมดอธิบายไว้ใน CONTRACT.md หัวข้อ "Notes from C3 (mock input format)"
'use strict';
const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 8000);
const MODEL = process.env.MOCK_MODEL || 'mock-buildmart';
const DELAY_MS = Number(process.env.MOCK_DELAY_MS ?? 15); // หน่วงระหว่าง delta (ให้ดูเหมือนพิมพ์)
const CHUNK = Number(process.env.MOCK_CHUNK || 6); // จำนวนตัวอักษรต่อ delta
const TTFT_MS = Number(process.env.MOCK_TTFT_MS || 0);
const STT_MS = Number(process.env.MOCK_STT_MS || 0);
const TTS_MS = Number(process.env.MOCK_TTS_MS || 0);
const RERANK_MS = Number(process.env.MOCK_RERANK_MS || 0);
const LLM_SLOTS = Number(process.env.MOCK_LLM_SLOTS || 0);

// ---------------------------------------------------------------- utils
const THAI = /[฀-๿]/;
const SKU_RE = /\b([A-Z]{3}-\d{3})\b/g;

function text(c) {
  if (typeof c === 'string') return c;
  if (Array.isArray(c)) return c.map((p) => (typeof p === 'string' ? p : p?.text || '')).join('');
  return c == null ? '' : String(c);
}
function num(s) {
  return Number(String(s).replace(/,/g, ''));
}
function fmt(n) {
  const r = Math.round(n * 100) / 100;
  return Number.isInteger(r)
    ? r.toLocaleString('en-US')
    : r.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function tierPrice(price, qty) {
  if (qty >= 200) return Math.round(price * 0.9 * 100) / 100;
  if (qty >= 50) return Math.round(price * 0.95 * 100) / 100;
  return price;
}
function tierLabel(qty) {
  return qty >= 200 ? 'ราคาส่งลด 10%' : qty >= 50 ? 'ราคาส่งลด 5%' : 'ราคาปกติ';
}
function endKrub(s) {
  const t = s.trimEnd();
  return /ครับ[\s.!)]*$/.test(t) ? t : t + ' ครับ';
}

// ---------------------------------------------------------------- parse context
function section(system, title) {
  const i = system.indexOf('## ' + title);
  if (i < 0) return '';
  const rest = system.slice(i + title.length + 3);
  const j = rest.search(/\n#{1,2} /);
  return j < 0 ? rest : rest.slice(0, j);
}

// "- CEM-001 | ปูนซีเมนต์... | 145 บาท/ถุง | สต็อก LKB 800 · BNA 500 · RST 300"
function parseProducts(system) {
  const out = [];
  const re = /^\s*-\s*([A-Z]{3}-\d{3})\s*\|\s*([^|\n]+?)\s*\|\s*([\d,]+(?:\.\d+)?)\s*บาท\s*\/\s*([^|\n]+?)\s*(?:\|\s*([^\n]*))?$/gm;
  let m;
  while ((m = re.exec(system))) {
    const stock = {};
    const sre = /\b([A-Z]{3})\s+(-?[\d,]+)/g;
    let s;
    while ((s = sre.exec(m[5] || ''))) stock[s[1]] = num(s[2]);
    out.push({ sku: m[1], name: m[2].trim(), price: num(m[3]), unit: m[4].trim(), stock });
  }
  return out;
}

// "[1] BM-DS-CEM.pdf หน้า 1: <chunk>"  (chunk ยาวได้หลายบรรทัด จนถึง [n] ถัดไป หรือหัวข้อ ##)
function parseDocs(system) {
  const sec = section(system, 'เอกสารอ้างอิง');
  const out = [];
  const re = /^\[(\d+)\]\s*(\S+?)\s+(?:หน้า|page|p\.)\s*(\d+)\s*[:：]\s*/gm;
  const heads = [];
  let m;
  while ((m = re.exec(sec))) heads.push({ n: Number(m[1]), filename: m[2], page: Number(m[3]), start: m.index, body: re.lastIndex });
  heads.forEach((h, i) => {
    const end = i + 1 < heads.length ? heads[i + 1].start : sec.length;
    out.push({ n: h.n, filename: h.filename, page: h.page, content: sec.slice(h.body, end).trim() });
  });
  return out;
}

// "## บริบทบทสนทนา" (chat-worker v3) → { skus:[...], qty:number|null }
//   สินค้าที่กำลังคุยถึง: CEM-001 ปูนซีเมนต์... · CEM-004 ...
//   จำนวนล่าสุดที่ลูกค้าพูดถึง: 100 ถุง
function parseFocus(system) {
  const sec = section(system, 'บริบทบทสนทนา');
  if (!sec) return { skus: [], qty: null };
  const line = (sec.match(/สินค้าที่กำลังคุยถึง\s*[:：]([^\n]*)/) || [])[1] || '';
  const skus = [...new Set(line.toUpperCase().match(SKU_RE) || [])];
  const q = (sec.match(/จำนวนล่าสุด[^:：\n]*[:：]\s*([\d,]+)/) || [])[1];
  return { skus, qty: q ? num(q) : null };
}
// คำที่ชี้กลับไปยังสินค้าที่คุยก่อนหน้า
const REFER = /(?:ตัว|อัน|ชิ้น|สินค้า|ล็อต|รายการ|แบบ)(?:นั้น|นี้|นั่น|นี่|เมื่อกี้|เดิม|ที่ว่า)|ที่ว่า|นั่น|that one|this one|\bit\b|\bthem\b|\bthat\b/i;
const PLURAL = /สองตัว|สองอย่าง|สองรายการ|ทั้งสอง|ทั้งคู่|ทั้ง 2|both|these two|the two/i;

// "## ยอดเงินที่คำนวณแล้ว" (chat-worker v3 · shared/pricing.js computeTotals ของตะกร้าจริง หรือสินค้าที่คุยถึง × จำนวน)
function parseEstimate(system) {
  const sec = section(system, 'ยอดเงินที่คำนวณแล้ว');
  if (!sec) return null;
  const n = (re) => {
    const m = sec.match(re);
    return m ? num(m[1]) : null;
  };
  const est = {
    cart: /ที่มา:\s*ตะกร้า/.test(sec),
    lines: (sec.match(/^- .+$/gm) || []).map((l) => l.slice(2)),
    subtotal: n(/ยอดสินค้า\s*([\d,.]+)/),
    weight: n(/น้ำหนักรวม\s*([\d,.]+)/),
    vehicle: (sec.match(/กก\.\s*·\s*(กระบะ|รถ 6 ล้อ|รถ 10 ล้อ)/) || [])[1] || '',
    shipping: n(/ค่าส่ง\s*([\d,.]+)/),
    vat: n(/VAT\s*([\d,.]+)/),
    total: n(/ยอดสุทธิ\s*([\d,.]+)/),
    coupons: {},
  };
  for (const m of sec.matchAll(/^คูปอง\s+([A-Z0-9]+):\s*(.+)$/gm)) {
    const body = m[2];
    if (/ใช้ไม่ได้/.test(body)) est.coupons[m[1]] = { ok: false, error: (body.match(/\((.+)\)/) || [])[1] || '' };
    else {
      const g = (re) => num((body.match(re) || [])[1] || 'NaN');
      est.coupons[m[1]] = { ok: true, discount: g(/ส่วนลด\s*([\d,.]+)/), after: g(/หลังส่วนลด\s*([\d,.]+)/), shipping: g(/ค่าส่ง\s*([\d,.]+)/), vat: g(/VAT\s*([\d,.]+)/), total: g(/ยอดสุทธิ\s*([\d,.]+)/) };
    }
  }
  return est.total != null ? est : null;
}
const VEH_EN = { กระบะ: 'pickup truck', 'รถ 6 ล้อ': '6-wheel truck', 'รถ 10 ล้อ': '10-wheel truck' };

function parseShop(system) {
  const shop = {};
  shop.name = (system.match(/ชื่อร้าน\s*[:：]?\s*([^\n|·]+)/) || [])[1]?.trim() || 'บ้านช่าง BuildMart';
  const wk = system.match(/จันทร์\s*[–-]\s*เสาร์\s*(\d{1,2}[:.]\d{2})\s*[–-]\s*(\d{1,2}[:.]\d{2})/);
  const sun = system.match(/อาทิตย์\s*(\d{1,2}[:.]\d{2})\s*[–-]\s*(\d{1,2}[:.]\d{2})/);
  shop.weekday = wk ? [wk[1], wk[2]] : null;
  shop.sunday = sun ? [sun[1], sun[2]] : null;
  shop.branches = [];
  const bre = /`?\b([A-Z]{3})\b`?\s+([^\s·|`]+)\s+โทร\.?\s*([0-9][0-9-]{7,})/g;
  let m;
  while ((m = bre.exec(system))) if (!shop.branches.find((b) => b.code === m[1])) shop.branches.push({ code: m[1], name: m[2], phone: m[3] });
  shop.coupons = [];
  const cre = /`?\b([A-Z]{3,}\d+)\b`?\s*ลด\s*(\d+(?:\.\d+)?)\s*%[^\d\n]*([\d,]+)/g;
  while ((m = cre.exec(system))) if (!shop.coupons.find((c) => c.code === m[1])) shop.coupons.push({ code: m[1], percent: num(m[2]), min: num(m[3]) });
  shop.line = (system.match(/LINE\s*[:：]?\s*(@[\w-]+)/) || [])[1] || null;
  return shop;
}

// ---------------------------------------------------------------- matching helpers
const EN2TH = [
  [/portland/i, 'ปอร์ตแลนด์'], [/cement/i, 'ปูนซีเมนต์'], [/mortar/i, 'ปูนก่อ'], [/plaster/i, 'ปูนฉาบ'],
  [/adhesive|tile glue/i, 'ปูนกาว'], [/coarse sand/i, 'ทรายหยาบ'], [/fine sand/i, 'ทรายละเอียด'], [/sand/i, 'ทราย'],
  [/gravel|stone/i, 'หิน'], [/deformed/i, 'ข้ออ้อย'], [/rebar|steel|iron bar/i, 'เหล็ก'], [/tie wire/i, 'ลวดผูกเหล็ก'],
  [/aac|lightweight brick/i, 'อิฐมวลเบา'], [/brick/i, 'อิฐ'], [/block/i, 'บล็อก'], [/floor tile/i, 'กระเบื้องพื้น'],
  [/wall tile/i, 'กระเบื้องผนัง'], [/roof/i, 'หลังคา'], [/tile/i, 'กระเบื้อง'], [/grout/i, 'ยาแนว'], [/primer/i, 'รองพื้น'],
  [/exterior|outdoor/i, 'ภายนอก'], [/interior|indoor/i, 'ภายใน'], [/paint/i, 'สี'], [/brush/i, 'แปรงทาสี'],
  [/pipe glue|pvc glue/i, 'กาวทาท่อ'], [/elbow/i, 'ข้องอ'], [/pipe/i, 'ท่อ'], [/breaker/i, 'เบรกเกอร์'],
  [/cable|wire/i, 'สายไฟ'], [/consumer unit|load center/i, 'ตู้คอนซูเมอร์'], [/metal sheet/i, 'เมทัลชีท'],
  [/plywood/i, 'ไม้อัด'], [/timber|wood/i, 'ไม้'], [/hammer/i, 'ค้อน'], [/drill/i, 'สว่าน'], [/tape measure/i, 'ตลับเมตร'],
];
function enrich(q) {
  if (THAI.test(q)) return q;
  let extra = '';
  for (const [re, th] of EN2TH) if (re.test(q)) extra += ' ' + th;
  return q + extra;
}

const STOP = ['ครับ', 'ค่ะ', 'คะ', 'นะ', 'ไหม', 'มั้ย', 'หรือเปล่า', 'แค่ไหน', 'เท่าไร', 'เท่าไหร่', 'อะไร', 'อย่างไร', 'ยังไง', 'ได้', 'กี่', 'ต้อง', 'หน่อย', 'ช่วย', 'บ้าง', 'แล้ว', 'และ', 'กับ', 'ของ', 'ที่', 'จะ', 'ให้', 'เป็น', 'คือ', 'หรือ', 'ขอ', 'ถ้า', 'อยาก', 'ทราบ', 'สอบถาม', 'ผม', 'ฉัน', 'เรา', 'ไป', 'ซื้อ'];
function thaiRuns(s) {
  let t = s;
  for (const w of STOP) t = t.split(w).join(' ');
  return (t.match(/[฀-๿]+/g) || []).filter((r) => r.length >= 2);
}
function grams(s) {
  const set = new Set();
  for (const run of thaiRuns(s)) {
    const cs = Array.from(run);
    if (cs.length < 3) set.add(run);
    for (let i = 0; i + 3 <= cs.length; i++) set.add(cs.slice(i, i + 3).join(''));
  }
  return set;
}
function codes(s) {
  // รหัส/คำเฉพาะภาษาอังกฤษ-ตัวเลข เช่น DB12 TIL-001 THW 16A 2.5
  // (D) เพิ่ม \d+x\d+ (ขนาด เช่น 60x60) ให้จับทั้งก้อน
  return new Set((s.match(/\d+[xX×]\d+|[A-Za-z]+[A-Za-z0-9.\-]*\d[A-Za-z0-9.\-]*|[A-Z]{2,}|\d+[A-Za-z]+/g) || []).map((x) => x.toUpperCase().replace(/[.\-]+$/, '')));
}

function scoreProduct(q, p) {
  const Q = q.toUpperCase();
  let s = 0;
  if (Q.includes(p.sku)) s += 100;
  for (const c of codes(p.name)) if (c.length >= 2 && new RegExp('(^|[^A-Z0-9])' + c.replace(/[.\-]/g, '\\$&') + '($|[^A-Z0-9])').test(Q)) s += 12;
  const qg = grams(q);
  for (const g of grams(p.name)) if (qg.has(g)) s += 1;
  return s;
}
function rankProducts(q, products) {
  return products
    .map((p, i) => ({ p, s: scoreProduct(q, p), i }))
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s || a.i - b.i);
}

// ---------------------------------------------------------------- document (RAG) search
const HINTS = [
  [/นาน|อายุ|เก็บ|shelf|store|last/i, ['เก็บ', 'เดือน', 'อายุ']],
  [/ประกัน|warrant/i, ['รับประกัน', 'ปี']],
  [/คืน|return|refund/i, ['คืน']],
  [/ทาบ|lap/i, ['ทาบ', 'เท่า', 'ซม']],
  [/แอมป์|amp|เบรกเกอร์/i, ['เบรกเกอร์', 'กระแส']],
  [/โปร|promo|แถม/i, ['โปร', 'แถม']],
  [/นอกบ้าน|ภายนอก|outdoor|exterior/i, ['ภายนอก']],
  [/ปูพื้น|floor/i, ['ปูพื้น', 'พื้น']],
  [/บ่ม|cur/i, ['บ่ม']],
  [/แต้ม|สมาชิก|member|point/i, ['แต้ม', 'สมาชิก']],
  [/มาตรฐาน|มอก|standard/i, ['มาตรฐาน', 'มอก']],
  [/ผสม|mix/i, ['ผสม']],
  [/รอ|กี่ชั่วโมง|กี่วัน|wait/i, ['รอ', 'ชั่วโมง', 'วัน']],
];

function splitPieces(content) {
  // แยกเป็น segment (ขอบแข็ง: ขึ้นบรรทัด · • | ;) แล้วแต่ละ segment แยกเป็นชิ้นตามช่องว่าง
  const segs = content
    // (D) ไม่ตัดหลังคำย่อไทยที่ลงท้ายด้วยจุด (มม. ซม. กก. ตร.มม. มอก.) — ตัดเฉพาะจุดหลังอักษรที่ไม่ใช่ไทย
    .split(/\n+|\s*[·•|;]\s*|(?<=(?<![\u0E00-\u0E7F])\.|[!?。])\s+(?=[^\d])/)
    .map((s) => s.trim())
    .filter(Boolean);
  return segs.map((s) => s.split(/\s+/));
}

function questionTerms(q) {
  const terms = new Map(); // term -> {kind}
  for (const g of grams(q)) terms.set(g, 'g');
  for (const c of codes(q)) terms.set(c, 'c');
  for (const [re, words] of HINTS) if (re.test(q)) for (const w of words) if (!terms.has(w)) terms.set(w, 'h');
  return terms;
}
function hasTerm(textUpper, raw, term, kind) {
  if (kind === 'c') return new RegExp('(^|[^A-Z0-9])' + term.replace(/[.\-]/g, '\\$&') + '($|[^A-Z0-9.])').test(textUpper);
  return raw.includes(term);
}

function searchDocs(q, docs, products = []) {
  if (!docs.length) return null;
  const terms = questionTerms(q);
  // คำที่เป็น "ชื่อสินค้า" (ประธาน) ให้น้ำหนักน้อย — คำที่บอกว่าถามเรื่องอะไร (เก็บ/รับประกัน/คืน) สำคัญกว่า
  const subj = new Set();
  for (const p of products) for (const g of grams(p.name)) subj.add(g);
  if (!terms.size) return null;
  const qSkus = new Set(q.toUpperCase().match(SKU_RE) || []);
  // segment ทั้งหมด (ไว้คิด IDF)
  const all = [];
  for (const d of docs) for (const seg of splitPieces(d.content)) all.push({ d, seg, raw: seg.join(' ') });
  const N = all.length;
  const df = new Map();
  for (const [t, k] of terms) {
    let c = 0;
    for (const a of all) if (hasTerm(a.raw.toUpperCase(), a.raw, t, k)) c++;
    df.set(t, c);
  }
  const weight = (t, k) => {
    const c = df.get(t) || 0;
    if (!c) return 0;
    const base = Math.log(1 + N / c);
    return k === 'c' ? base * 3 : k === 'h' ? base * 2 : subj.has(t) ? base * 0.3 : base;
  };
  let denom = 0;
  for (const [t, k] of terms) denom += df.get(t) ? weight(t, k) : k === 'h' ? 0 : 0.6;
  let best = null;
  for (const a of all) {
    const P = a.seg;
    for (let i = 0; i < P.length; i++) {
      let len = 0;
      for (let j = i; j < P.length; j++) {
        len += P[j].length + 1;
        if (len > 150 && j > i) break;
        const raw = P.slice(i, j + 1).join(' ');
        // ห้ามข้ามไปปนสินค้ารหัสอื่นที่ไม่ได้ถาม
        const sk = raw.match(SKU_RE) || [];
        if (qSkus.size && sk.some((x) => !qSkus.has(x))) break;
        let s = 0;
        const U = raw.toUpperCase();
        for (const [t, k] of terms) if (hasTerm(U, raw, t, k)) s += weight(t, k);
        // (D) เอกสารยาวมี "คำถาม FAQ" และ "ชื่อตาราง" ที่มีคำตรงคำถามแต่ไม่มีคำตอบ → ลดคะแนน · คะแนนเท่ากันให้ช่วงที่มีตัวเลข (ข้อเท็จจริง) ชนะ
        if (/กี่|ไหม|มั้ย|อย่างไร|ยังไง|เท่าไร|เท่าไหร่|\?/.test(raw)) s *= 0.8;
        if (/^ตารางที่\s*\d+/.test(raw)) s *= 0.8;
        // (v3) เอกสารยาว 20 หน้ามี "ตัวอย่างคำนวณ" ที่มีคำตรงคำถามปนอยู่ → เชื่ออันดับของ retriever/reranker ด้วย ([1] ดีสุด)
        s *= 1 - 0.12 * Math.min(4, Math.max(0, (a.d.n || 1) - 1));
        const dig = /\d/.test(raw.replace(/[A-Z]{2,3}-\d{3}|ตารางที่\s*\d+/g, ''));
        const tie = best && Math.abs(s - best.s) < 1e-9;
        if (!best || s > best.s + 1e-9 || (tie && dig && !best.dig) || (tie && dig === best.dig && raw.length < best.raw.length)) best = { s, a, i, j, raw, dig };
      }
    }
  }
  if (!best || best.s <= 0) return null;
  // ขยายไปทางขวาให้ได้ตัวเลข/ข้อเท็จจริงที่ตามหลังคำสำคัญ
  const P = best.a.seg;
  let { i, j } = best;
  let added = 0;
  while (j + 1 < P.length && added < 45) {
    const nxt = P[j + 1];
    const sk = nxt.match(SKU_RE) || [];
    if (sk.some((x) => !qSkus.has(x))) break;
    j++;
    added += nxt.length + 1;
  }
  if (i > 0 && /^[A-Z]{3}-\d{3}$/.test(P[i - 1]) && (!qSkus.size || qSkus.has(P[i - 1]))) i--;
  const sentence = P.slice(i, j + 1).join(' ').replace(/\s+/g, ' ').trim();
  return { score: best.s, coverage: denom ? best.s / denom : 0, sentence, doc: best.a.d };
}

// ---------------------------------------------------------------- history helpers
// รายการสินค้าล่าสุดในบทสนทนา: จาก "ผลคำนวณ:" JSON หรือจากบรรทัด "- SKU ชื่อ : N หน่วย" ในคำตอบก่อนหน้า
function lastItems(messages, beforeIdx, { onlyLatest = false } = {}) {
  let seenAssistant = false;
  for (let k = beforeIdx - 1; k >= 0; k--) {
    if (onlyLatest && seenAssistant) break;
    const m = messages[k];
    const c = text(m.content);
    if (/^\s*ผลคำนวณ\s*[:：]/.test(c)) {
      const j = parseJsonAfter(c);
      if (j && Array.isArray(j.rows) && j.rows.length) return j.rows.map((r) => ({ sku: r.sku, qty: Number(r.qty), unit: r.unit || '', label: r.label || '' }));
    }
    if (m.role === 'assistant') {
      seenAssistant = true;
      const items = [];
      const re = /^\s*[-•*]\s*\**([A-Z]{3}-\d{3})\**\s*([^\n:]*?)\s*[:：]\s*([\d,]+)\s*([^\s\n(]*)/gm;
      let x;
      while ((x = re.exec(c))) items.push({ sku: x[1], label: x[2].trim(), qty: num(x[3]), unit: x[4] });
      if (items.length) return items;
    }
  }
  return [];
}
function parseJsonAfter(c) {
  const i = c.indexOf('{');
  const k = c.indexOf('[');
  const start = i < 0 ? k : k < 0 ? i : Math.min(i, k);
  if (start < 0) return null;
  try {
    return JSON.parse(c.slice(start).trim());
  } catch {
    const end = Math.max(c.lastIndexOf('}'), c.lastIndexOf(']'));
    try {
      return JSON.parse(c.slice(start, end + 1));
    } catch {
      return null;
    }
  }
}

// ---------------------------------------------------------------- answers
function answerCalcResult(res, en) {
  const rows = Array.isArray(res?.rows) ? res.rows : [];
  if (res?.error || !rows.length) {
    return en
      ? `Sorry, I couldn't calculate that (${res?.error || 'no result'}). Please tell me the size again, e.g. "concrete 3 cubic meters".`
      : `ขออภัยครับ คำนวณไม่สำเร็จ (${res?.error || 'ไม่มีผลลัพธ์'}) รบกวนบอกขนาดงานอีกครั้ง เช่น "เทคอนกรีต 3 คิว" ครับ`;
  }
  const type = res.type || res.input?.type;
  const inp = { ...(res.extra || {}), ...(res.input || {}) };
  const list = rows.map((r) => `- ${r.sku} ${r.label || ''} : ${r.qty} ${r.unit || ''}`.replace(/\s+$/, '')).join('\n');
  if (en) return `Here is the material estimate:\n${list}\nType "add to cart" if you want me to put these in your cart.`;
  let head = 'ผลคำนวณวัสดุที่ต้องใช้ครับ';
  const r0 = rows[0];
  if (type === 'concrete') head = `เทคอนกรีต ${inp.volume ?? ''} ลบ.ม. (ส่วนผสม 1:2:4) ต้องใช้ปูนซีเมนต์ ${r0.qty} ${r0.unit} พร้อมทรายและหินดังนี้ครับ`;
  else if (type === 'paint') {
    const kind = inp.paintType === 'exterior' ? 'ภายนอก' : 'ภายใน';
    head = `ทาสี${kind} ${inp.area ?? ''} ตร.ม. ${inp.coats ?? 2} เที่ยว ต้องใช้สี ${r0.qty} ${r0.unit}` + (rows[1] ? ` และสีรองพื้น ${rows[1].qty} ${rows[1].unit}` : '') + ' ครับ';
  } else if (type === 'tile') head = `ปูกระเบื้อง ${inp.area ?? ''} ตร.ม. (เผื่อเศษ 10%) ต้องใช้กระเบื้อง ${r0.qty} ${r0.unit} ครับ`;
  else if (type === 'wall') head = `ก่อผนัง ${inp.area ?? ''} ตร.ม. ต้องใช้${r0.label || 'อิฐ'} ${r0.qty} ${r0.unit} ครับ`;
  else if (type === 'rebar') {
    const w = res.weightKg ?? inp.weightKg;
    head = `เหล็ก ${inp.size ?? ''} ยาวรวม ${inp.length ?? ''} เมตร ใช้ ${res.bars ?? r0.qty} เส้น` + (w != null ? ` น้ำหนักประมาณ ${fmt(w)} กก.` : '') + ' ครับ';
  }
  return `${head}\n${list}\nถ้าต้องการ พิมพ์ "ใส่ตะกร้าให้เลย" ได้เลยครับ`;
}

function answerCommandResult(res, en) {
  if (res?.quoteNo) {
    const tot = res.total != null ? (en ? ` Total ${fmt(res.total)} baht.` : ` ยอดรวม ${fmt(res.total)} บาท`) : '';
    return en
      ? `Your quotation ${res.quoteNo} is ready (valid 7 days): /quote/${res.quoteNo}.${tot}`
      : `สร้างใบเสนอราคาเรียบร้อยแล้วครับ เลขที่ ${res.quoteNo}${tot} ดูและพิมพ์ได้ที่ /quote/${res.quoteNo} (มีอายุ 7 วัน) ครับ`;
  }
  if (res?.error) {
    const empty = /empty|ว่าง/i.test(String(res.error));
    return en
      ? empty ? 'Your cart is empty. Please add some items first, then ask me for a quotation again.' : `Sorry, that did not work (${res.error}).`
      : empty ? 'ตะกร้ายังว่างอยู่ครับ เพิ่มสินค้าลงตะกร้าก่อน แล้วค่อยขอใบเสนอราคาอีกครั้งนะครับ' : `ขออภัยครับ ทำรายการไม่สำเร็จ (${res.error}) ครับ`;
  }
  if (res?.cartCount != null) return en ? `Done. Your cart now has ${res.cartCount} item(s).` : `เรียบร้อยครับ ตอนนี้ในตะกร้ามี ${res.cartCount} รายการครับ`;
  return en ? 'Done.' : 'เรียบร้อยครับ';
}

const UNIT_EN = { ถุง: 'bag', เส้น: 'bar', ก้อน: 'piece', กล่อง: 'box', แกลลอน: 'gallon', ชิ้น: 'piece', อัน: 'piece', ม้วน: 'roll', แผ่น: 'sheet', ตัว: 'unit', ตู้: 'unit', เครื่อง: 'unit', กระป๋อง: 'can', 'ลบ.ม.': 'cubic meter' };
const TH2EN = [
  ['ปูนซีเมนต์ปอร์ตแลนด์', 'Portland cement'], ['ปูนกาวซีเมนต์', 'tile adhesive cement'], ['ปูนก่อ', 'masonry mortar'], ['ปูนฉาบ', 'plaster mortar'],
  ['ปูกระเบื้อง', ''], ['สำเร็จรูป', 'ready-mixed'], ['ประเภท', 'Type'], ['กก.', 'kg'], ['ทรายหยาบ', 'coarse sand'], ['ทรายละเอียด', 'fine sand'],
  ['หินเบอร์', 'stone no.'], ['หิน', 'crushed stone'], ['เหล็กข้ออ้อย', 'deformed bar'], ['เหล็กเส้นกลม', 'round bar'], ['ลวดผูกเหล็ก', 'tie wire'],
  ['ยาว', 'length'], ['ม.', 'm'], ['อิฐมอญ', 'clay brick'], ['อิฐมวลเบา', 'AAC block'], ['บล็อกประสาน', 'interlocking block'], ['ก้อน', 'piece'],
  ['กระเบื้องพื้น', 'floor tile'], ['กระเบื้องผนัง', 'wall tile'], ['กระเบื้องหลังคาลอนคู่', 'roof tile'], ['ลายหินอ่อน', 'marble pattern'],
  ['ขาวเงา', 'glossy white'], ['ยาแนว', 'grout'], ['สีเทา', 'grey'], ['สีแดง', 'red'], ['สีน้ำอะคริลิก', 'acrylic paint'], ['ภายนอก', 'exterior'],
  ['ภายใน', 'interior'], ['สีขาว', 'white'], ['สีรองพื้นปูนใหม่', 'primer for new plaster'], ['แปรงทาสี', 'paint brush'], ['นิ้ว', 'inch'],
  ['ท่อ', 'pipe'], ['ชั้น', 'class'], ['ข้องอ', 'elbow'], ['กาวทาท่อ', 'PVC glue'], ['กรัม', 'g'], ['สายไฟ', 'cable'], ['ตร.มม.', 'sq.mm'],
  ['เบรกเกอร์ลูกย่อย', 'circuit breaker'], ['ตู้คอนซูเมอร์', 'consumer unit'], ['ช่อง', 'way'], ['เมทัลชีท', 'metal sheet'], ['มม.', 'mm'],
  ['ไม้อัด', 'plywood'], ['ฟุต', 'ft'], ['ไม้แบบ', 'formwork board'], ['ค้อนหงอน', 'claw hammer'], ['สว่านกระแทกไร้สาย', 'cordless impact drill'],
  ['ตลับเมตร', 'tape measure'], ['แกลลอน', 'gallon'], ['ล.', 'L'], ['กล่อง', 'box'], ['แผ่น', 'sheets'], ['ม้วน', 'roll'], ['ตร.ม.', 'sq.m'],
];
function nameEn(name) {
  let n = name;
  for (const [th, e] of TH2EN) n = n.split(th).join(' ' + e + ' ');
  n = n.replace(/[฀-๿]+/g, ' ').replace(/\(\s*\)/g, '').replace(/\s+/g, ' ').replace(/\s+([),])/g, '$1').replace(/\(\s+/g, '(').trim();
  return n || 'this item';
}
const unitEn = (u) => UNIT_EN[u] || u.replace(/[฀-๿.]+/g, '').trim() || 'unit';

function priceLine(p, qty, en) {
  if (en) p = { ...p, name: nameEn(p.name), unit: unitEn(p.unit) };
  if (qty && qty > 1) {
    const unit = tierPrice(p.price, qty);
    return en
      ? `${p.name} (${p.sku}) x ${qty} ${p.unit}: ${fmt(unit)} baht per ${p.unit} (${qty >= 50 ? 'bulk discount' : 'normal price'}), total ${fmt(unit * qty)} baht (excl. VAT).`
      : `${p.name} (${p.sku}) ซื้อ ${qty} ${p.unit} ได้${tierLabel(qty)} ราคา ${fmt(unit)} บาท/${p.unit} รวม ${fmt(unit * qty)} บาท (ยังไม่รวม VAT)`;
  }
  return en
    ? `${p.name} (${p.sku}) costs ${fmt(p.price)} baht per ${p.unit} (excluding 7% VAT).`
    : `${p.name} (${p.sku}) ราคา ${fmt(p.price)} บาท/${p.unit} (ยังไม่รวม VAT 7%)`;
}
function stockLine(p, shop, en) {
  if (en) p = { ...p, name: nameEn(p.name) };
  const name = (c) => (en ? c : shop.branches.find((b) => b.code === c)?.name || c);
  const codesList = Object.keys(p.stock);
  const have = codesList.filter((c) => p.stock[c] > 0);
  const detail = codesList.map((c) => `${name(c)} ${p.stock[c] > 0 ? fmt(p.stock[c]) : en ? 'out of stock' : 'หมด'}`).join(' · ');
  return en
    ? `${p.name} (${p.sku}) is in stock at ${have.length} branch(es): ${detail}.`
    : `${p.name} (${p.sku}) มีของ ${have.length} สาขา จาก ${codesList.length} สาขา (${detail}) รวมทุกสาขา ${fmt(codesList.reduce((a, c) => a + (p.stock[c] || 0), 0))} ${p.unit || ''}`.trimEnd();
}
function qtyIn(q) {
  const m =
    q.match(/(\d[\d,]*)\s*(เส้น|ถุง|ก้อน|กล่อง|แกลลอน|ชิ้น|อัน|ม้วน|แผ่น|ตัว|ตู้|เครื่อง|กระป๋อง|pcs|pieces|bags|bars|units|boxes|gallons|rolls|sheets)/i) ||
    q.match(/(\d[\d,]*)\s+(?:of them|of these|of those)/i);
  return m ? num(m[1]) : null;
}

function calcTag(q) {
  const vol = q.match(/(\d+(?:\.\d+)?)\s*(คิว|ลบ\.?\s*ม\.?|ลูกบาศก์เมตร|m3|m³|cubic)/i);
  const area = q.match(/(\d+(?:\.\d+)?)\s*(ตร\.?\s*ม\.?|ตารางเมตร|m2|m²|sq\.?\s*m|square)/i);
  const coats = q.match(/(\d+)\s*(เที่ยว|รอบ|coats?)/i);
  if (vol && /คอนกรีต|เทพื้น|เทคาน|เทเสา|ปูนกี่ถุง|concrete/i.test(q)) return { type: 'concrete', volume: Number(vol[1]) };
  if (area && /ทาสี|สีทา|สีกี่|ใช้สี|paint/i.test(q)) {
    return { type: 'paint', area: Number(area[1]), coats: coats ? Number(coats[1]) : 2, paintType: /ภายนอก|นอกบ้าน|exterior|outside|outdoor/i.test(q) ? 'exterior' : 'interior' };
  }
  if (area && /กระเบื้อง|tile/i.test(q)) return { type: 'tile', area: Number(area[1]) };
  if (area && /ก่อ|ผนัง|อิฐ|wall|brick/i.test(q)) return { type: 'wall', area: Number(area[1]), wallType: /มวลเบา|light|aac/i.test(q) ? 'light' : 'brick' };
  const size = q.toUpperCase().match(/\b(RB6|RB9|DB12|DB16)\b/);
  const len = q.match(/(\d+(?:\.\d+)?)\s*(เมตร|ม\.(?!\S*ม)|m\b|meters?)/i);
  if (size && len && /เหล็ก|rebar|กี่เส้น|น้ำหนัก|ยาวรวม/i.test(q)) return { type: 'rebar', size: size[1], length: Number(len[1]) };
  return null;
}

function buildReply(messages) {
  messages = Array.isArray(messages) ? messages : [];
  const system = messages.filter((m) => m.role === 'system').map((m) => text(m.content)).join('\n');
  const shop = parseShop(system);
  const products = parseProducts(system);
  const docs = parseDocs(system);
  const focus = parseFocus(system);
  const focusProducts = focus.skus.map((s) => products.find((p) => p.sku === s)).filter(Boolean);

  // ข้อความสุดท้าย (อาจเป็นผลของ tag)
  let lastIdx = messages.length - 1;
  while (lastIdx >= 0 && messages[lastIdx].role === 'system' && !/^\s*ผล(คำนวณ|คำสั่ง)/.test(text(messages[lastIdx].content))) lastIdx--;
  const lastC = lastIdx >= 0 ? text(messages[lastIdx].content) : '';
  // คำถามจริงของผู้ใช้ (user ล่าสุดที่ไม่ใช่ผล tag)
  let qIdx = messages.length - 1;
  while (qIdx >= 0 && !(messages[qIdx].role === 'user' && !/^\s*ผล(คำนวณ|คำสั่ง)/.test(text(messages[qIdx].content)))) qIdx--;
  const q0 = qIdx >= 0 ? text(messages[qIdx].content).trim() : '';
  const en = q0 ? !THAI.test(q0) : /ตอบเป็นภาษาอังกฤษ|answer in english/i.test(system);
  const out = (s) => (en ? s : endKrub(s));

  if (/^\s*ผลคำนวณ\s*[:：]/.test(lastC)) return out(answerCalcResult(parseJsonAfter(lastC) || {}, en));
  if (/^\s*ผลคำสั่ง\s*[:：]/.test(lastC)) return out(answerCommandResult(parseJsonAfter(lastC) || {}, en));

  const q = enrich(q0);
  if (!q0) return out(en ? 'Hello! How can I help you?' : `สวัสดีครับ ผม "น้องช่าง" ผู้ช่วยของร้าน ${shop.name} มีอะไรให้ช่วยครับ`);

  // 1) นอกเรื่อง: เขียนโค้ด การบ้าน การเมือง
  const shopCodes = shop.coupons.map((c) => c.code);
  const couponQ = (/โค้ดส่วนลด|โค้ดลด|คูปอง|ส่วนลด|โปรโมชั่นโค้ด|โค้ด(ไหน|อะไร)|coupon|discount|promo code/i.test(q) || shopCodes.some((c) => q.toUpperCase().includes(c))) && !/แต้ม|point/i.test(q);
  const est = parseEstimate(system);
  const prevUser = (() => {
    for (let k = qIdx - 1; k >= 0; k--) if (messages[k].role === 'user' && !/^\s*ผล(คำนวณ|คำสั่ง)/.test(text(messages[k].content))) return text(messages[k].content);
    return '';
  })();

  // 1.5) (v3) ค่าส่ง / น้ำหนัก / ยอดรวม VAT / คูปอง ของ "ตะกร้าจริง" หรือ "สินค้าที่คุยถึง × จำนวน" — ใช้ตัวเลขที่ chat-worker คำนวณแล้ว
  const explicitWeight = /(\d[\d,.]*)\s*(ตัน|ton|กก\.?|กิโล|kg)/i.test(q0) && !/ต่อ|\//.test(q0);
  const codeAsked = Object.keys(est?.coupons || {}).find((c) => q.toUpperCase().includes(c));
  const wantShip = /ค่าส่ง|ค่าขนส่ง|ส่งฟรี|รถอะไร|ส่งด้วยรถ|ใช้รถ|delivery|shipping|truck/i.test(q);
  const bestCoupon = /คุ้ม|โค้ดไหน|ใช้โค้ด|คูปองไหน|best coupon|which coupon/i.test(q);
  const wantWeight = /หนักเท่า|น้ำหนัก|หนักกี่|weigh/i.test(q);
  const wantTotal = /vat|ภาษี|สุทธิ|ต้องจ่าย|รวมทั้งหมด|ทั้งหมดรวม|รวมเป็นเงินทั้งหมด|เหลือเท่า|final total|grand total|in total/i.test(q);
  if (est && !explicitWeight && !/แต้ม|point/i.test(q) && (wantShip || wantWeight || wantTotal || codeAsked || (bestCoupon && couponQ))) {
    const items = est.lines.map((l) => l.replace(/\s*\(น้ำหนัก.*\)$/, '')).join(' · ');
    const veh = en ? VEH_EN[est.vehicle] || est.vehicle : est.vehicle;
    const parts = [];
    parts.push(en ? `For ${items}:` : `${est.cart ? 'ตะกร้าของคุณ' : 'รายการนี้'}: ${items}`);
    if (codeAsked) {
      const c = est.coupons[codeAsked];
      if (c.ok) {
        parts.push(
          en
            ? `Coupon ${codeAsked} can be used: discount ${fmt(c.discount)} baht → ${fmt(c.after)} + delivery ${fmt(c.shipping)} (${veh}) + VAT ${fmt(c.vat)} = final total ${fmt(c.total)} baht.`
            : `ใช้คูปอง ${codeAsked} ได้ครับ ลด ${fmt(c.discount)} บาท → ยอดหลังส่วนลด ${fmt(c.after)} + ค่าส่ง ${fmt(c.shipping)} บาท (${veh} น้ำหนัก ${fmt(est.weight)} กก.) + VAT ${fmt(c.vat)} = ยอดสุทธิ ${fmt(c.total)} บาท`,
        );
      } else {
        parts.push(
          en
            ? `Coupon ${codeAsked} cannot be used (${c.error}). Final total without coupon ${fmt(est.total)} baht.`
            : `ใช้คูปอง ${codeAsked} ไม่ได้ครับ (${c.error}) ยอดสุทธิไม่ใช้คูปอง ${fmt(est.total)} บาท`,
        );
        // ใช้ไม่ได้ → แนะนำคูปองอื่นที่ใช้ได้
        for (const [code, o] of Object.entries(est.coupons)) {
          if (code !== codeAsked && o.ok) parts.push(en ? `You can use ${code} instead: discount ${fmt(o.discount)} baht, final total ${fmt(o.total)} baht.` : `ใช้ ${code} แทนได้ครับ ลด ${fmt(o.discount)} บาท ยอดสุทธิ ${fmt(o.total)} บาท`);
        }
      }
    } else if (bestCoupon && couponQ) {
      const ok = Object.entries(est.coupons).filter(([, o]) => o.ok).sort((a, b) => b[1].discount - a[1].discount);
      if (ok.length) {
        const [code, o] = ok[0];
        parts.push(en ? `${code} saves the most: discount ${fmt(o.discount)} baht, final total ${fmt(o.total)} baht.` : `ใช้ ${code} คุ้มที่สุดครับ ลด ${fmt(o.discount)} บาท ยอดสุทธิ ${fmt(o.total)} บาท`);
      }
      for (const [code, o] of Object.entries(est.coupons)) if (!o.ok) parts.push(en ? `${code}: not applicable (${o.error}).` : `${code}: ใช้ไม่ได้ (${o.error})`);
    } else {
      if (wantWeight || wantShip) {
        parts.push(
          en
            ? `Total weight ${fmt(est.weight)} kg → ${veh}, delivery fee ${fmt(est.shipping)} baht.`
            : `น้ำหนักรวม ${fmt(est.weight)} กก. ใช้${est.vehicle} ค่าส่ง ${est.shipping ? fmt(est.shipping) + ' บาท' : '0 บาท (ส่งฟรี เพราะยอดหลังส่วนลดตั้งแต่ 20,000 บาท)'}`,
        );
      }
      if (wantTotal || !(wantWeight || wantShip)) {
        parts.push(
          en
            ? `Subtotal ${fmt(est.subtotal)} + delivery ${fmt(est.shipping)} + VAT 7% ${fmt(est.vat)} = total ${fmt(est.total)} baht.`
            : `ยอดสินค้า ${fmt(est.subtotal)} + ค่าส่ง ${fmt(est.shipping)} (${est.vehicle}) + VAT 7% ${fmt(est.vat)} = ยอดสุทธิ ${fmt(est.total)} บาท`,
        );
        // ถามแค่ "รวม VAT" ไม่ได้ถามค่าส่ง → บอกราคาสินค้ารวม VAT (ไม่รวมค่าส่ง) ด้วย
        if (!wantShip && /vat|ภาษี/i.test(q)) {
          const withVat = Math.round(est.subtotal * 1.07 * 100) / 100;
          parts.push(en ? `(Goods only incl. VAT, without delivery: ${fmt(withVat)} baht.)` : `(ถ้าไม่รวมค่าส่ง: ราคาสินค้ารวม VAT ${fmt(withVat)} บาท)`);
        }
      }
    }
    return out(parts.join('\n'));
  }

  // 1.6) (v3) แต้มสมาชิก: "ซื้อของ 5,000 บาท จะได้กี่แต้ม" → อัตราแต้มจากเอกสารอ้างอิง
  const amt = q0.match(/([\d,]+(?:\.\d+)?)\s*บาท/);
  if (/แต้ม|point/i.test(q) && /กี่แต้ม|ได้แต้ม|how many points/i.test(q) && amt) {
    for (const d of docs) {
      const r = d.content.match(/(\d+)\s*แต้ม\s*ต่อ\s*(?:ทุก\s*)?([\d,]+)\s*บาท/);
      if (r) {
        const pts = Math.floor(num(amt[1]) / num(r[2])) * Number(r[1]);
        return out(
          en
            ? `You earn ${r[1]} point per ${r[2]} baht, so ${amt[1]} baht gives ${fmt(pts)} points. [${d.n}]`
            : `สมาชิกได้ ${r[1]} แต้มต่อทุก ${r[2]} บาท ซื้อ ${amt[1]} บาท จะได้ ${fmt(pts)} แต้ม [${d.n}]`,
        );
      }
    }
  }
  if (!couponQ && /เขียนโค้ด|โค้ด|โปรแกรม|python|javascript|code|coding|program|การบ้าน|homework|การเมือง|เลือกตั้ง|นายก|politic/i.test(q)) {
    return out(
      en
        ? `Sorry, I can't help with that — I'm the assistant of ${shop.name} and only answer questions about construction materials, prices, stock, delivery and material estimates. Is there anything you need for your building project?`
        : `ขออภัยครับ เรื่องนี้ผมช่วยไม่ได้ ผมเป็นผู้ช่วยของร้าน ${shop.name} ตอบได้เฉพาะเรื่องวัสดุก่อสร้าง ราคา สต็อก การจัดส่ง และคำนวณวัสดุครับ มีงานก่อสร้างหรือวัสดุอะไรให้ช่วยดูไหมครับ`
    );
  }

  // 2) คูปอง
  if (couponQ) {
    const cs = shop.coupons.length ? shop.coupons : [];
    if (!cs.length) return out(en ? 'There are no coupon codes listed right now.' : 'ตอนนี้ยังไม่มีข้อมูลโค้ดส่วนลดครับ');
    const list = cs.map((c) => (en ? `- ${c.code}: ${c.percent}% off when subtotal before VAT ≥ ${fmt(c.min)} baht` : `- ${c.code} ลด ${c.percent}% เมื่อยอดก่อน VAT ตั้งแต่ ${fmt(c.min)} บาท`)).join('\n');
    return out(en ? `We have these coupon codes (one per order):\n${list}` : `มีโค้ดส่วนลดดังนี้ครับ (ใช้ได้ทีละ 1 ใบ ลดจากยอดหลังราคาส่ง)\n${list}\nใส่โค้ดได้ที่หน้าตะกร้าครับ`);
  }

  // 3) ใบเสนอราคา
  if (/ใบเสนอราคา|เสนอราคา|quotation|\bquote\b/i.test(q)) {
    return (en ? 'Sure, I will create a quotation from your cart.' : 'ได้เลยครับ กำลังสร้างใบเสนอราคาจากสินค้าในตะกร้าให้ครับ') + '\n[QUOTE]{}';
  }

  // 4) ใส่ตะกร้า
  if (/ใส่ตะกร้า|เพิ่มลงตะกร้า|เพิ่มในตะกร้า|หยิบใส่|add (it |them |these )?to (my |the )?cart|add to cart/i.test(q)) {
    let items = [];
    const skus = q.toUpperCase().match(SKU_RE) || [];
    const qty = qtyIn(q);
    if (skus.length) items = skus.map((s) => ({ sku: s, qty: qty || 1, label: products.find((p) => p.sku === s)?.name || '' }));
    else if (qty) {
      // หลายรายการในประโยคเดียว: "เอาสายไฟนั่น 3 ม้วน กับเบรกเกอร์ 4 ตัว ใส่ตะกร้าให้หน่อย"
      const segs = q0.split(/\s*(?:กับ|และ|,(?!\d)|\band\b|&)\s*/).filter((x) => qtyIn(x));
      for (const seg of segs) {
        const top = rankProducts(enrich(seg), products)[0];
        const p = top && top.s >= 2 ? top.p : REFER.test(seg) && focusProducts[0] ? focusProducts[0] : null;
        if (p && !items.find((x) => x.sku === p.sku)) items.push({ sku: p.sku, qty: qtyIn(seg), label: p.name, unit: p.unit });
      }
      if (items.length < segs.length) items = [];
      if (!items.length) {
        const top = rankProducts(q, products)[0];
        if (top && top.s >= 3) items = [{ sku: top.p.sku, qty, label: top.p.name, unit: top.p.unit }];
      }
    }
    // "ใส่ตะกร้าตามที่คำนวณไว้ทั้งหมด" → รายการจากผลคำนวณล่าสุดในประวัติ
    if (!items.length && /คำนวณ|ทั้งหมด|ทุกรายการ|ทุกอย่าง|everything|all of/i.test(q0)) items = lastItems(messages, qIdx);
    // ไม่ระบุสินค้า: ① รายการในคำตอบล่าสุด (เช่นผลคำนวณ) ② สินค้าที่กำลังคุยถึง (บริบทบทสนทนา) ③ รายการเก่ากว่าในประวัติ
    if (!items.length) items = lastItems(messages, qIdx, { onlyLatest: true });
    if (!items.length && focusProducts.length) {
      const n = qty || focus.qty;
      if (!n) {
        const names = focusProducts.slice(0, 1).map((p) => `${p.sku} ${p.name}`).join(', ');
        return out(en ? `How many ${names} would you like to add?` : `ต้องการใส่ ${names} จำนวนเท่าไรครับ`);
      }
      items = focusProducts.slice(0, 1).map((p) => ({ sku: p.sku, qty: n, label: p.name, unit: p.unit }));
    }
    if (!items.length) items = lastItems(messages, qIdx);
    items = items.filter((it) => it.qty > 0);
    if (!items.length) return out(en ? 'Which product and how many would you like to add?' : 'ต้องการใส่สินค้าอะไร จำนวนเท่าไรครับ เช่น "ใส่ตะกร้า CEM-001 10 ถุง"');
    const list = items.map((it) => `- ${it.sku} ${it.label || ''} × ${it.qty} ${it.unit || ''}`.replace(/\s+$/, '')).join('\n');
    const tags = items.map((it) => `[ADD_TO_CART]${JSON.stringify({ sku: it.sku, qty: it.qty })}`).join('\n');
    return (en ? `Done, I added these to your cart:\n${list}` : endKrub(`เรียบร้อยครับ ใส่ตะกร้าให้แล้ว\n${list}\nไปที่หน้าตะกร้าเพื่อสั่งซื้อหรือขอใบเสนอราคาได้เลยครับ`)) + '\n' + tags;
  }

  // 4.5) (v3) อัตราใช้ × พื้นที่: "ถ้าพื้นห้อง 20 ตร.ม. ต้องใช้ปูนกาวทั้งหมดกี่กิโล" (อัตรา กก./ตร.ม. จากคำตอบก่อนหน้า/เอกสาร)
  const areaM = q.match(/(\d+(?:\.\d+)?)\s*(ตร\.?\s*ม\.?|ตารางเมตร|m2|m²|sq\.?\s*m)/i);
  const history = messages.slice(0, qIdx).filter((m) => m.role === 'assistant').map((m) => text(m.content)).reverse();
  if (areaM && /กี่กิโล|กี่ กก|กี่กก|กี่ kg|how many kg/i.test(q)) {
    const src = [...history, ...docs.map((d) => d.content)];
    for (const h of src) {
      const r = h.match(/([\d.]+)\s*กก\.?\s*\/\s*ตร\.?\s*ม/);
      if (r) {
        const kg = Math.round(Number(r[1]) * Number(areaM[1]) * 100) / 100;
        return out(en ? `${r[1]} kg/sq.m × ${areaM[1]} sq.m = ${fmt(kg)} kg in total.` : `ใช้ ${r[1]} กก./ตร.ม. × ${areaM[1]} ตร.ม. = ทั้งหมด ${fmt(kg)} กก.`);
      }
    }
  }
  // "คิดเป็นกี่ถุง" → น้ำหนักรวมจากคำตอบก่อนหน้า ÷ น้ำหนักต่อถุงในชื่อสินค้า (ปัดขึ้น)
  if (/กี่ถุง|how many bags/i.test(q) && !areaM && !/คิว|ลบ/.test(q)) {
    const kgM = (history[0] || '').match(/ทั้งหมด\s*([\d,.]+)\s*กก/);
    const p = focusProducts.find((x) => /\(([\d.]+)\s*กก\.?\)/.test(x.name)) || products.find((x) => /\(([\d.]+)\s*กก\.?\)/.test(x.name) && rankProducts(q, [x]).length);
    if (kgM && p) {
      const per = Number(p.name.match(/\(([\d.]+)\s*กก\.?\)/)[1]);
      const bags = Math.ceil(num(kgM[1]) / per);
      return out(en ? `${kgM[1]} kg ÷ ${per} kg per bag = ${bags} bags of ${nameEn(p.name)} (${p.sku}).` : `${kgM[1]} กก. ÷ ${per} กก./ถุง ต้องใช้ ${p.name} (${p.sku}) ${bags} ถุง (ปัดขึ้น)`);
    }
  }

  // 5) คำนวณวัสดุ → [CALC]
  let ct = calcTag(q);
  // พื้นที่/ปริมาตรในคำถาม แต่ไม่บอกงาน ("ห้องน้ำ 12 ตร.ม. ต้องซื้อกี่กล่อง") → งานของสินค้าที่กำลังคุยถึง
  if (!ct && focusProducts.length && /(ตร\.?\s*ม|ตารางเมตร|คิว|ลบ\.?\s*ม)/.test(q) && /กี่|เท่าไร|how many|how much/i.test(q)) ct = calcTag(q + ' ' + focusProducts.map((p) => p.name).join(' '));
  // ไม่มีขนาดในคำถาม แต่เปลี่ยนวัสดุ ("ถ้าเปลี่ยนเป็นอิฐมอญล่ะ ต้องใช้เท่าไร") → ขนาดจากคำถามคำนวณก่อนหน้า
  if (!ct && /เปลี่ยนเป็น|ถ้าเป็น|แทน|instead/i.test(q) && /ต้องใช้|กี่|เท่าไร|how many|how much/i.test(q)) {
    let prevCt = null;
    for (let k = qIdx - 1; k >= 0 && !prevCt; k--) if (messages[k].role === 'user') prevCt = calcTag(enrich(text(messages[k].content)));
    if (prevCt) {
      const size = prevCt.area != null ? `${prevCt.area} ตร.ม.` : prevCt.volume != null ? `${prevCt.volume} คิว` : prevCt.length != null ? `${prevCt.length} เมตร` : '';
      const kind = { wall: 'ก่อผนัง', paint: 'ทาสี', tile: 'กระเบื้อง', concrete: 'คอนกรีต', rebar: 'เหล็ก' }[prevCt.type] || '';
      ct = calcTag(`${q} ${size} ${kind}`);
    }
  }
  if (ct) return (en ? 'Let me calculate that for you.' : 'ขอคำนวณให้สักครู่นะครับ') + '\n[CALC]' + JSON.stringify(ct);

  // 5.5) LINE ของร้าน
  if (/\bline\b|ไลน์|แอดไลน์/i.test(q) && shop.line) return out(en ? `Our LINE is ${shop.line}.` : `แอด LINE ของร้านได้ที่ ${shop.line} ครับ`);
  // 5.6) ขั้นราคาส่ง: "มีราคาส่งกี่ขั้น ขั้นละเท่าไร" · "ต้องซื้อกี่แผ่นถึงจะได้ลด 10%"
  if (/กี่ขั้น|ขั้นละ|ถึงจะได้ลด|ได้ลด\s*\d+\s*%|ราคาส่ง.*(ขั้น|ระดับ)|price tiers?/i.test(q)) {
    const top = rankProducts(q, products)[0] || (focusProducts[0] && { p: focusProducts[0], s: 99 });
    if (top && top.s >= 2) {
      const p = top.p;
      const t2 = tierPrice(p.price, 50);
      const t3 = tierPrice(p.price, 200);
      return out(
        en
          ? `${nameEn(p.name)} (${p.sku}) has 3 price tiers: 1–49 ${unitEn(p.unit)} ${fmt(p.price)} baht · 50–199 ${fmt(t2)} baht (5% off) · 200+ ${fmt(t3)} baht (10% off).`
          : `${p.name} (${p.sku}) มีราคาส่ง 3 ขั้นครับ\n- 1–49 ${p.unit}: ${fmt(p.price)} บาท/${p.unit}\n- 50–199 ${p.unit}: ${fmt(t2)} บาท/${p.unit} (ลด 5%)\n- 200 ${p.unit}ขึ้นไป: ${fmt(t3)} บาท/${p.unit} (ลด 10%)`,
      );
    }
  }

  // 6) เวลาเปิด-ปิด
  const wk = shop.weekday || ['07:00', '18:00'];
  const sun = shop.sunday || ['08:00', '12:00'];
  if (/อาทิตย์|sunday/i.test(q) && /เปิด|ปิด|หยุด|ทำการ|open|close|hour/i.test(q)) {
    return out(en ? `Yes, we are open on Sunday from ${sun[0]} to ${sun[1]}. (Mon–Sat ${wk[0]}–${wk[1]})` : `วันอาทิตย์ร้านเปิดครับ เวลา ${sun[0]}–${sun[1]} น. (จันทร์–เสาร์ ${wk[0]}–${wk[1]} น.)`);
  }
  if (/เปิดกี่โมง|ปิดกี่โมง|เวลาเปิด|เวลาทำการ|เปิดกี่|ปิดกี่|เปิดวันไหน|เปิดทุกวัน|opening|open hours|what time|when .*open|hours/i.test(q)) {
    return out(en ? `We are open Monday–Saturday ${wk[0]}–${wk[1]} and Sunday ${sun[0]}–${sun[1]}.` : `ร้านเปิดวันจันทร์–เสาร์ ${wk[0]}–${wk[1]} น. และวันอาทิตย์ ${sun[0]}–${sun[1]} น.`);
  }

  // 7) เบอร์โทร / สาขา
  if (/เบอร์|โทร|ติดต่อ|phone|call|contact|สาขา.*(ไหน|อะไร|ที่ไหน)|branch/i.test(q) && !/สต็อก|สต๊อก|มีของ|กี่สาขาที่มี|ราคา|stock|เยอะ|มากที่สุด|มากสุด|เหลือ|most/i.test(q) && !(focusProducts.length && /สาขาไหน.*มี|which branch/i.test(q))) {
    const hit = shop.branches.filter((b) => q.includes(b.name) || q.toUpperCase().includes(b.code));
    const bs = hit.length ? hit : shop.branches;
    if (!bs.length) return out(en ? 'Sorry, I do not have the branch contact details.' : 'ขออภัยครับ ผมไม่มีข้อมูลเบอร์โทรสาขาครับ');
    const list = bs.map((b) => (en ? `${b.code} ${b.name}: ${b.phone}` : `สาขา${b.name} (${b.code}) โทร ${b.phone}`)).join('\n');
    const line = shop.line ? (en ? `\nLINE: ${shop.line}` : `\nหรือทัก LINE ${shop.line}`) : '';
    return out(hit.length === 1 ? (en ? list : `${list}`) + line : (en ? `Our branches:\n${list}` : `ติดต่อสาขาต่าง ๆ ได้ที่\n${list}`) + line);
  }

  // 8) ค่าส่ง / รถ
  if (/ค่าส่ง|ค่าขนส่ง|รถอะไร|ใช้รถ|จัดส่ง|ส่งของ|ขนส่ง|shipping|delivery|truck/i.test(q)) {
    const t = q.match(/(\d+(?:[.,]\d+)?)\s*(ตัน|ton)/i);
    const k = q.match(/(\d[\d,]*(?:\.\d+)?)\s*(กก\.?|กิโล|kg)/i);
    const w = t ? num(t[1]) * 1000 : k ? num(k[1]) : null;
    if (w != null) {
      const [v, ve, fee] = w <= 1000 ? ['กระบะ', 'pickup truck', 500] : w <= 6000 ? ['รถ 6 ล้อ', '6-wheel truck', 1500] : ['รถ 10 ล้อ', '10-wheel truck', 3500];
      const free = w <= 1000 ? (en ? ' (free if the order after discount is ≥ 20,000 baht before VAT)' : ' (ส่งฟรีถ้ายอดก่อน VAT หลังส่วนลดตั้งแต่ 20,000 บาท)') : '';
      return out(en ? `For ${fmt(w)} kg we use a ${ve}; the delivery fee is ${fmt(fee)} baht${free}.` : `น้ำหนัก ${fmt(w)} กก. ใช้${v} ค่าส่ง ${fmt(fee)} บาท${free}`);
    }
    return out(
      en
        ? 'Delivery fee by total weight: ≤ 1,000 kg pickup 500 baht (free if ≥ 20,000 baht), 1,000.01–6,000 kg 6-wheel truck 1,500 baht, > 6,000 kg 10-wheel truck 3,500 baht.'
        : 'ค่าส่งคิดตามน้ำหนักรวมครับ\n- ไม่เกิน 1,000 กก. กระบะ 500 บาท (ฟรีถ้ายอดก่อน VAT หลังส่วนลดตั้งแต่ 20,000 บาท)\n- 1,000.01–6,000 กก. รถ 6 ล้อ 1,500 บาท\n- เกิน 6,000 กก. รถ 10 ล้อ 3,500 บาท'
    );
  }

  // คำถามที่ไม่ได้เอ่ยชื่อสินค้า + มีสินค้าที่กำลังคุยถึง → เติม SKU/ชื่อสินค้านั้นเข้าไปตอนค้นเอกสาร
  function withFocus(s) {
    if (!focusProducts.length || (s.toUpperCase().match(SKU_RE) || []).length) return s;
    const top = rankProducts(s, products)[0];
    if (top && top.s >= 4 && !REFER.test(s)) return s;
    // คำสั้น ๆ แทนสินค้า (รหัสในชื่อ เช่น DB12 · ไม่มี → คำแรกของชื่อ) ไม่ให้ชื่อยาวกลบคำถาม
    const short = (p) => {
      const c = [...codes(p.name)].filter((x) => /[A-Z]/.test(x));
      if (c.length) return c.join(' ');
      const w = p.name.replace(/\(.*?\)/g, ' ').split(/\s+/).filter(Boolean);
      return w.slice(0, w[1] && /^(ภายนอก|ภายใน)/.test(w[1]) ? 2 : 1).join(' ');
    };
    return s + ' ' + focusProducts.map(short).join(' ');
  }

  // ต่อเนื่อง: "ถ้าซื้อ 60 แกลลอนล่ะ" (มีจำนวน ไม่มีคำว่าราคา) = ถามราคาของสินค้าที่กำลังคุยถึง
  const qtyFollow = focusProducts.length > 0 && qtyIn(q0) != null && /ซื้อ|ล่ะ|เอา|สั่ง|buy|order|take/i.test(q0) && !/ตะกร้า|cart/i.test(q0);
  // "ปูนถุงละเท่าไร" → "เอาตัวที่ใช้ฉาบผนัง" = ยังถามราคาอยู่
  const pickFollow = /^\s*(เอา|ขอ|งั้น)(ตัว|แบบ|อัน)ที่/.test(q0) && /ราคา|เท่าไร|เท่าไหร่|กี่บาท|how much|price/i.test(prevUser);
  const priceQ = qtyFollow || pickFollow || /เป็นเงิน|ราคา|กี่บาท|ละเท่า|how much|price|cost/i.test(q);
  const stockQ = /สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|ของหมด|in stock|stock|available at|มีที่สาขา|ที่สาขา\S*(ไหม|มั้ย|บ้าง)|สาขาไหนมี|มีกี่สาขา|which branch/i.test(q) || (!!shop.branches.find((b) => q0.includes(b.name)) && /มี.*(ไหม|มั้ย|บ้าง|กี่|เท่าไร)|เหลือ/.test(q0)) || /ทุกสาขา|รวมกัน.*มี|มีมากกว่า|ที่ไหนมี/.test(q0);
  // สาขาที่ถามเจาะจง ("มีที่สาขารังสิตไหม")
  const askedBranch = shop.branches.find((b) => q0.includes(b.name) || new RegExp(`\\b${b.code}\\b`, 'i').test(q0));

  // 9) ราคารวมของรายการล่าสุด (เช่น ต่อจากผลคำนวณ)
  if (priceQ && /รวม|ทั้งหมด|total|altogether/i.test(q) && !(q.toUpperCase().match(SKU_RE) || []).length) {
    const items = lastItems(messages, qIdx);
    if (items.length) {
      let sum = 0;
      const lines = [];
      const missing = [];
      for (const it of items) {
        const p = products.find((x) => x.sku === it.sku);
        if (!p) {
          missing.push(it.sku);
          continue;
        }
        const u = tierPrice(p.price, it.qty);
        sum += u * it.qty;
        lines.push(en ? `- ${p.sku} ${p.name}: ${it.qty} × ${fmt(u)} = ${fmt(u * it.qty)} baht` : `- ${p.sku} ${p.name}: ${it.qty} × ${fmt(u)} = ${fmt(u * it.qty)} บาท`);
      }
      if (lines.length) {
        const miss = missing.length ? (en ? `\n(No price data for ${missing.join(', ')})` : `\n(ไม่มีข้อมูลราคา ${missing.join(', ')})`) : '';
        return out(en ? `Price breakdown (excl. VAT):\n${lines.join('\n')}\nTotal ${fmt(sum)} baht${miss}` : `สรุปราคา (ยังไม่รวม VAT 7%)\n${lines.join('\n')}\nรวมทั้งหมด ${fmt(sum)} บาท${miss}`);
      }
    }
  }

  // 10) ราคา / สต็อก (+ Hybrid: ส่วนที่ถามสเปกตอบจากเอกสาร)
  if (priceQ || stockQ) {
    const clauses = q0.split(/\s*(?:แล้วก็|แล้ว|และ|,(?!\d)|\?|และก็|\band\b|\balso\b)\s*/).filter((c) => c.trim().length > 1);
    const pClause = clauses.filter((c) => /ราคา|กี่บาท|ละเท่า|how much|price|cost|สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|stock/i.test(c)).join(' ') || q;
    const other = qtyFollow || askedBranch ? '' : clauses.filter((c) => !/ราคา|กี่บาท|ละเท่า|how much|price|cost|สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|stock/i.test(c)).join(' ');
    let ranked = rankProducts(enrich(pClause), products);
    if (!ranked.length) ranked = rankProducts(q, products);
    // ไม่ได้ระบุสินค้าชัด ๆ ("แล้วราคาส่ง 100 ถุงล่ะ" · "อันนั้นมีกี่สาขา") → สินค้าที่กำลังคุยถึง
    const namedSku = (q.toUpperCase().match(SKU_RE) || []).length > 0;
    if (focusProducts.length && !namedSku && (REFER.test(q0) || PLURAL.test(q0) || !ranked.length || ranked[0].s < 2)) {
      ranked = focusProducts.map((p) => ({ p, s: 99 }));
    } else if ((!ranked.length || ranked[0].s < 2) && products.length && !namedSku && priceQ) {
      // ไม่มีสินค้าที่คุยถึง + คำถามกว้าง ("ปูนถุงละเท่าไร") → ตัวแรกของตาราง (chat-worker เรียงตามความเกี่ยวข้องแล้ว)
      ranked = [{ p: products[0], s: 2 }];
    }
    // "สาขาไหนมีเยอะที่สุด"
    if (ranked.length && ranked[0].s >= 2 && /เยอะ|มากที่สุด|มากสุด|most/i.test(q)) {
      const p = ranked[0].p;
      const best = Object.entries(p.stock).sort((a, b) => b[1] - a[1])[0];
      if (best) {
        const b = shop.branches.find((x) => x.code === best[0]);
        return out(en ? `${best[0]} branch has the most ${nameEn(p.name)} (${p.sku}): ${fmt(best[1])} ${unitEn(p.unit)}.` : `สาขา${b ? b.name : best[0]} (${best[0]}) มี ${p.name} (${p.sku}) เยอะที่สุด ${fmt(best[1])} ${p.unit} (${Object.entries(p.stock).map(([c, n]) => `${c} ${fmt(n)}`).join(' · ')})`);
      }
    }
    // เทียบ 2 สินค้า: "สีรองพื้นปูนใหม่กับสีภายในขาว ราคาต่างกันกี่บาท"
    if (priceQ && /ต่างกัน|ถูกกว่า|แพงกว่า|เทียบ|difference|cheaper/i.test(q0)) {
      const pick = q0.split(/\s*(?:กับ|และ|\bvs\b|\band\b)\s*/).map((seg) => rankProducts(enrich(seg), products)[0]).filter((x) => x && x.s >= 2).map((x) => x.p);
      const two = [...new Map(pick.map((x) => [x.sku, x])).values()].slice(0, 2);
      if (two.length === 2) {
        const d = Math.abs(two[0].price - two[1].price);
        return out(two.map((x) => priceLine(x, null, en)).join('\n') + (en ? `\nDifference: ${fmt(d)} baht per unit.` : `\nต่างกัน ${fmt(d)} บาท/${two[0].unit}`));
      }
    }
    // "สองตัวนี้ราคาเท่าไร" → ทุกตัวที่กำลังคุยถึง
    if (priceQ && PLURAL.test(q0) && focusProducts.length >= 2) return out(focusProducts.map((p) => priceLine(p, qtyIn(pClause), en)).join('\n'));
    const parts = [];
    if (other && docs.length) {
      const d = searchDocs(withFocus(enrich(other)), docs, products);
      if (d && d.coverage >= 0.3) parts.push((en ? `According to ${d.doc.filename}: ` : `จากเอกสาร ${d.doc.filename} หน้า ${d.doc.page}: `) + `${d.sentence} [${d.doc.n}]`);
    }
    if (ranked.length && ranked[0].s >= 2) {
      const p = ranked[0].p;
      const qty = qtyIn(pClause);
      if (priceQ) parts.push(priceLine(p, qty, en));
      if (stockQ && askedBranch && p.stock[askedBranch.code] != null) {
        const n = p.stock[askedBranch.code];
        // หมดที่สาขาที่ถาม → บอกสาขาอื่นที่มีของ
        const others = Object.entries(p.stock).filter(([c, v]) => c !== askedBranch.code && v > 0);
        const alt = n > 0 || !others.length ? '' : en
          ? ` Available at ${others.map(([c, v]) => `${c} ${fmt(v)}`).join(' · ')}.`
          : ` แต่มีที่${others.map(([c, v]) => `สาขา${shop.branches.find((b) => b.code === c)?.name || c} ${fmt(v)} ${p.unit}`).join(' และ')}`;
        parts.push(
          en
            ? `${askedBranch.code} branch ${n > 0 ? `has ${fmt(n)} ${unitEn(p.unit)} of ${nameEn(p.name)} (${p.sku}) in stock` : `is out of ${nameEn(p.name)} (${p.sku})`}.${alt}`
            : `สาขา${askedBranch.name} (${askedBranch.code}) ${n > 0 ? `มี ${p.name} (${p.sku}) ${fmt(n)} ${p.unit}` : `${p.name} (${p.sku}) หมด (เหลือ 0)`}${alt}`,
        );
      } else if (stockQ) parts.push(stockLine(p, shop, en));
      return out(parts.join('\n'));
    }
    if (parts.length) return out(parts.join('\n'));
    return out(en ? "Sorry, I couldn't find that product in our catalogue, so I can't give a price." : 'ขออภัยครับ ไม่พบสินค้านี้ในรายการของร้าน จึงยังบอกราคาไม่ได้ ลองพิมพ์ชื่อหรือรหัสสินค้าอีกครั้งได้ครับ');
  }

  // 11) มีขายไหม
  const availQ = /ขายไหม|ขายมั้ย|มีขาย|ขายด้วย|ขาย.*ไหม|มี.+ไหม|do you (sell|have)|available/i.test(q) && !/เท่าไร|เท่าไหร่|กี่|อย่างไร|ยังไง/.test(q0);
  if (availQ) {
    let phrase = q0;
    for (const w of ['ขายไหม', 'ขายมั้ย', 'มีขาย', 'ขายด้วย', 'ขาย', 'ไหม', 'มั้ย', 'ครับ', 'ค่ะ', 'บ้าง', 'หรือเปล่า', 'ที่ร้าน', 'ร้าน', 'มี']) phrase = phrase.split(w).join(' ');
    phrase = phrase.replace(/\s+/g, ' ').trim();
    const flat = phrase.replace(/\s+/g, '');
    const exact = products.filter((p) => flat && (p.name.replace(/\s+/g, '').includes(flat) || p.sku === flat.toUpperCase()));
    if (exact.length) {
      const list = exact.slice(0, 5).map((p) => `- ${p.sku} ${p.name} ${fmt(p.price)} บาท/${p.unit}`).join('\n');
      return out(en ? `Yes, we have:\n${list}` : `มีครับ\n${list}`);
    }
    if (THAI.test(flat) || en) {
      const near = rankProducts(enrich(phrase), products).filter((x) => x.s >= 2).slice(0, 3);
      const sug = near.length
        ? en
          ? `\nRelated items we do carry:\n${near.map((x) => `- ${x.p.sku} ${x.p.name}`).join('\n')}`
          : `\nสินค้าใกล้เคียงที่ร้านมี:\n${near.map((x) => `- ${x.p.sku} ${x.p.name} ${fmt(x.p.price)} บาท/${x.p.unit}`).join('\n')}`
        : '';
      return out(en ? `Sorry, we don't carry "${phrase}" at the moment.${sug}` : `ขออภัยครับ ตอนนี้ร้านไม่มี "${phrase}" ขายครับ${sug}`);
    }
  }

  // 12) ตอบจากเอกสารอ้างอิง (RAG) — คำถามต่อเนื่อง ("อันนั้นเก็บได้นานแค่ไหน") เติมสินค้าที่กำลังคุยถึงเข้าไปในคำค้น
  if (docs.length) {
    const d = searchDocs(withFocus(q), docs, products);
    if (d && d.coverage >= 0.3) {
      let lead = '';
      if (/ได้ไหม|ได้มั้ย|ได้หรือไม่|ได้หรือเปล่า|\bcan\b|\bis it\b/i.test(q)) {
        const neg = /ไม่ได้|ห้าม|ไม่ควร|ไม่รับ|not allowed|cannot/.test(d.sentence);
        lead = en ? (neg ? 'No. ' : 'Yes. ') : neg ? 'ไม่ได้ครับ ' : 'ได้ครับ ';
      }
      return out(en ? `${lead}According to ${d.doc.filename} (page ${d.doc.page}): ${d.sentence} [${d.doc.n}]` : `${lead}จากเอกสาร ${d.doc.filename} หน้า ${d.doc.page}: ${d.sentence} [${d.doc.n}]`);
    }
  }

  // 13) พูดถึงสินค้าโดยตรง → ข้อมูลสั้น ๆ
  const top = rankProducts(q, products)[0];
  if (top && top.s >= 4) return out(priceLine(top.p, null, en) + '\n' + stockLine(top.p, shop, en));
  if (focusProducts.length && REFER.test(q0)) {
    const p = focusProducts[0];
    return out(priceLine(p, null, en) + '\n' + stockLine(p, shop, en));
  }

  // 14) ทั่วไป
  if (/สวัสดี|hello|hi\b|ขอบคุณ|thank/i.test(q)) {
    if (/ขอบคุณ|thank/i.test(q)) return out(en ? 'You are welcome! Happy building.' : 'ยินดีครับ ขอให้งานก่อสร้างราบรื่นครับ');
  }
  return out(
    en
      ? `Hello! I'm "Nong Chang", the assistant of ${shop.name}. I can help with product prices, stock at our 3 branches, delivery fees, coupons and material estimates (concrete, walls, tiles, paint, rebar). What do you need?`
      : `สวัสดีครับ ผม "น้องช่าง" ผู้ช่วยของร้าน ${shop.name} ช่วยตอบเรื่องราคาสินค้า สต็อก 3 สาขา ค่าส่ง โค้ดส่วนลด และคำนวณวัสดุ (คอนกรีต ก่อผนัง ปูกระเบื้อง ทาสี เหล็กเส้น) ได้ครับ สอบถามได้เลยครับ`
  );
}

// ---------------------------------------------------------------- v3: mock ai-box (STT · rerank · speech)
const VOICE_INDEX = process.env.VOICE_INDEX || path.join(__dirname, '..', 'e2e', 'voice-fixtures', 'index.json');
let voiceCache = { mtime: -1, map: {} };
/** sha256 → {text, language} (อ่านใหม่เมื่อไฟล์เปลี่ยน · ไม่มีไฟล์ → ตารางว่าง) */
function voiceIndex() {
  try {
    const st = fs.statSync(VOICE_INDEX);
    if (st.mtimeMs !== voiceCache.mtime) {
      const raw = JSON.parse(fs.readFileSync(VOICE_INDEX, 'utf8'));
      const map = {};
      for (const [k, v] of Object.entries(raw || {})) if (/^[0-9a-f]{64}$/i.test(k)) map[k.toLowerCase()] = typeof v === 'string' ? { text: v } : v || {};
      voiceCache = { mtime: st.mtimeMs, map };
    }
  } catch {
    voiceCache = { mtime: -1, map: {} };
  }
  return voiceCache.map;
}

// ---- fingerprint (CONTRACT_V3 §9): เสียงจากไมค์ปลอมของ e2e ผ่าน MediaRecorder (webm) → sha256 ไม่ตรงไฟล์ fixture
//   ถอดเสียงด้วย ffmpeg → mono 8 kHz → RMS envelope ช่องละ 50 ms → ตัดเงียบหัว/ท้าย
//   ตรงกันเมื่อ: ความยาว (หลังตัดเงียบ) ต่างกัน ≤ 0.4 วิ และ correlation ของ envelope (เลื่อนได้ ±0.5 วิ) ≥ 0.8
const { spawn } = require('child_process');
const FP_SR = 8000;
const FP_HOP = 400; // 50 ms
const FP_MIN_CORR = Number(process.env.MOCK_STT_MIN_CORR || 0.8);
const FP_MAX_DDUR = Number(process.env.MOCK_STT_MAX_DDUR || 0.4);

function decodePcm(buf) {
  return new Promise((resolve, reject) => {
    const p = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', String(FP_SR), '-f', 's16le', 'pipe:1']);
    const out = [];
    let err = '';
    p.stdout.on('data', (c) => out.push(c));
    p.stderr.on('data', (c) => (err += c));
    p.on('error', reject);
    p.on('close', (code) => {
      const b = Buffer.concat(out);
      if (!b.length) return reject(new Error(`ffmpeg decode failed (${code}): ${err.slice(0, 200)}`));
      resolve(new Int16Array(b.buffer, b.byteOffset, Math.floor(b.length / 2)));
    });
    p.stdin.on('error', () => {});
    p.stdin.end(buf);
  });
}

function envelope(pcm) {
  const n = Math.floor(pcm.length / FP_HOP);
  const env = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = i * FP_HOP; j < (i + 1) * FP_HOP; j++) s += pcm[j] * pcm[j];
    env[i] = Math.sqrt(s / FP_HOP);
  }
  // ตัดเงียบหัว/ท้าย (< 8% ของค่าสูงสุด)
  let max = 0;
  for (const v of env) if (v > max) max = v;
  const thr = max * 0.08;
  let a = 0;
  let b = n - 1;
  while (a < n && env[a] < thr) a++;
  while (b > a && env[b] < thr) b--;
  const e = Array.from(env.slice(a, b + 1));
  return { env: e, dur: (e.length * FP_HOP) / FP_SR };
}

function corrAt(x, y, lag) {
  // Pearson ของ x[i] กับ y[i+lag] ในช่วงที่ซ้อนกัน
  const xs = [];
  const ys = [];
  for (let i = 0; i < x.length; i++) {
    const j = i + lag;
    if (j >= 0 && j < y.length) {
      xs.push(x[i]);
      ys.push(y[j]);
    }
  }
  const n = xs.length;
  if (n < 5) return -1;
  const mx = xs.reduce((s, v) => s + v, 0) / n;
  const my = ys.reduce((s, v) => s + v, 0) / n;
  let sxy = 0;
  let sxx = 0;
  let syy = 0;
  for (let i = 0; i < n; i++) {
    sxy += (xs[i] - mx) * (ys[i] - my);
    sxx += (xs[i] - mx) ** 2;
    syy += (ys[i] - my) ** 2;
  }
  return sxx && syy ? sxy / Math.sqrt(sxx * syy) : -1;
}

const fpCache = new Map(); // file → {mtime, env, dur}
async function fixtureFp(file) {
  const fp = path.join(path.dirname(VOICE_INDEX), file);
  const st = fs.statSync(fp);
  const c = fpCache.get(fp);
  if (c && c.mtime === st.mtimeMs) return c;
  const v = { mtime: st.mtimeMs, ...envelope(await decodePcm(fs.readFileSync(fp))) };
  fpCache.set(fp, v);
  return v;
}

/** หา fixture ที่ใกล้ที่สุดด้วย fingerprint → {entry, corr, dDur} | null */
async function matchFingerprint(buf) {
  const entries = Object.values(voiceIndex()).filter((e) => e && e.file);
  if (!entries.length) return null;
  const q = envelope(await decodePcm(buf));
  let best = null;
  for (const e of entries) {
    let f;
    try {
      f = await fixtureFp(e.file);
    } catch (err) {
      console.warn('[mock-llm] fixture decode failed', e.file, err.message);
      continue;
    }
    const dDur = Math.abs(f.dur - q.dur);
    if (dDur > FP_MAX_DDUR) continue;
    let c = -1;
    for (let lag = -10; lag <= 10; lag++) c = Math.max(c, corrAt(q.env, f.env, lag));
    if (!best || c > best.corr) best = { entry: e, corr: c, dDur };
  }
  return best && best.corr >= FP_MIN_CORR ? best : best ? { ...best, rejected: true } : null;
}

/** multipart/form-data → { name: {filename, body:Buffer, value:string} } (ไม่มี dependency) */
function parseMultipart(buf, ctype) {
  const m = /boundary=(?:"([^"]+)"|([^;]+))/i.exec(ctype || '');
  const parts = {};
  if (!m) return parts;
  const b = Buffer.from('--' + (m[1] || m[2]).trim());
  let i = buf.indexOf(b);
  while (i >= 0) {
    const start = i + b.length;
    if (buf.slice(start, start + 2).toString() === '--') break;
    const next = buf.indexOf(b, start);
    if (next < 0) break;
    const part = buf.slice(start + 2, next - 2); // ตัด CRLF หลัง boundary และก่อน boundary ถัดไป
    const he = part.indexOf('\r\n\r\n');
    if (he >= 0) {
      const head = part.slice(0, he).toString('utf8');
      const body = part.slice(he + 4);
      const name = (/name="([^"]*)"/i.exec(head) || [])[1];
      if (name) parts[name] = { filename: (/filename="([^"]*)"/i.exec(head) || [])[1], body, value: body.toString('utf8') };
    }
    i = next;
  }
  return parts;
}

/** ความยาวเสียง (วินาที) จาก header WAV · ไม่ใช่ WAV → null */
function wavDuration(buf) {
  if (buf.length < 44 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WAVE') return null;
  let off = 12;
  let byteRate = 0;
  while (off + 8 <= buf.length) {
    const id = buf.toString('ascii', off, off + 4);
    const size = buf.readUInt32LE(off + 4);
    if (id === 'fmt ') byteRate = buf.readUInt32LE(off + 16);
    if (id === 'data') return byteRate ? Math.round((Math.min(size, buf.length - off - 8) / byteRate) * 1000) / 1000 : null;
    off += 8 + size + (size % 2);
  }
  return null;
}

async function handleTranscription(req, res, buf) {
  if (STT_MS) await sleep(STT_MS);
  const parts = parseMultipart(buf, req.headers['content-type']);
  const file = parts.file || parts.audio;
  if (!file || !file.body.length) return send(res, 400, { error: { message: 'missing multipart field "file"' } });
  const sha = crypto.createHash('sha256').update(file.body).digest('hex');
  let hit = voiceIndex()[sha];
  let match = hit ? 'sha256' : 'none';
  let fp = null;
  if (!hit) {
    try {
      fp = await matchFingerprint(file.body);
      if (fp && !fp.rejected) {
        hit = fp.entry;
        match = 'fingerprint';
      }
    } catch (e) {
      console.warn('[mock-llm] fingerprint failed:', e.message);
    }
  }
  const lang = (parts.language && parts.language.value.trim()) || '';
  console.log(`[mock-llm] stt sha256=${sha.slice(0, 12)}… ${match}${fp ? ` corr=${fp.corr.toFixed(3)} dDur=${fp.dDur.toFixed(2)}s best=${fp.entry.file}` : ''} bytes=${file.body.length}`);
  return send(res, 200, {
    text: (hit && hit.text) || '',
    language: (hit && hit.language) || lang || 'th',
    duration: wavDuration(file.body) ?? (hit && hit.durationMs ? hit.durationMs / 1000 : null),
    mock: true,
    match,
    sha256: sha,
  });
}

// ---- mock TTS: เสียง VoxCPM2 ที่อัดไว้ (sha256 ของ input) ----
const TTS_CACHE_DIR = process.env.TTS_CACHE_DIR || path.join(__dirname, '..', 'e2e', 'voice-fixtures', 'tts-cache');
/** WAV 16-bit mono 24 kHz: เสียงสั้น ๆ (ใช้เมื่อยังไม่มี tts-cache) ยาวตามความยาวข้อความ */
function synthWav(chars) {
  const sr = 24000;
  const sec = Math.min(8, Math.max(1, chars / 14));
  const n = Math.round(sr * sec);
  const buf = Buffer.alloc(44 + n * 2);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write('WAVE', 8);
  buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(sr, 24); buf.writeUInt32LE(sr * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write('data', 36); buf.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) {
    const t = i / sr;
    const env = 0.5 + 0.5 * Math.sin(2 * Math.PI * 3 * t); // "พยางค์" 3 ครั้ง/วิ ให้มาสคอตขยับปาก
    buf.writeInt16LE(Math.round(Math.sin(2 * Math.PI * 220 * t) * env * 6000), 44 + i * 2);
  }
  return buf;
}
async function handleSpeech(req, res, body) {
  let p;
  try {
    p = JSON.parse(body || '{}');
  } catch {
    return send(res, 400, { error: { message: 'invalid JSON' } });
  }
  const input = String(p.input || '');
  if (!input.trim()) return send(res, 400, { error: { message: 'empty input' } });
  if (TTS_MS) await sleep(TTS_MS);
  const sha = crypto.createHash('sha256').update(input, 'utf8').digest('hex');
  let wav = null;
  let src = 'cache';
  for (const f of [sha + '.wav', 'generic.wav']) {
    try {
      wav = fs.readFileSync(path.join(TTS_CACHE_DIR, f));
      if (f === 'generic.wav') src = 'generic';
      break;
    } catch {}
  }
  if (!wav) {
    wav = synthWav(input.length);
    src = 'synth';
  }
  console.log(`[mock-llm] tts sha256=${sha.slice(0, 12)}… ${src} bytes=${wav.length}`);
  res.writeHead(200, { 'Content-Type': 'audio/wav', 'Content-Length': wav.length, 'x-tts-engine': 'mock', 'x-tts-source': src });
  res.end(wav);
}

function handleRerank(req, res, body) {
  let p;
  try {
    p = JSON.parse(body || '{}');
  } catch {
    return send(res, 400, { error: { message: 'invalid JSON' } });
  }
  const docs = Array.isArray(p.documents) ? p.documents : [];
  const n = Math.max(0, Math.min(docs.length, Number(p.top_n) || docs.length));
  // ลำดับเดิม (identity) · score ลดหลั่น 1 → 0
  const results = docs.slice(0, n).map((_, i) => ({ index: i, relevance_score: +(1 - i / Math.max(1, docs.length)).toFixed(4) }));
  return send(res, 200, { results, mock: true });
}

// ---------------------------------------------------------------- HTTP
function send(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(body) });
  res.end(body);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// MOCK_LLM_SLOTS: จำลอง GPU ที่รับพร้อมกันได้จำกัด (เกินแล้วรอคิว)
let active = 0;
const waiters = [];
async function acquire() {
  if (!LLM_SLOTS) return () => {};
  if (active >= LLM_SLOTS) await new Promise((r) => waiters.push(r));
  active++;
  return () => {
    active--;
    const w = waiters.shift();
    if (w) w();
  };
}

async function handleChat(req, res, body) {
  const release = await acquire();
  try {
    await handleChatInner(req, res, body);
  } finally {
    release();
  }
}

async function handleChatInner(req, res, body) {
  let payload;
  try {
    payload = JSON.parse(body || '{}');
  } catch {
    return send(res, 400, { error: { message: 'invalid JSON' } });
  }
  let reply;
  try {
    reply = buildReply(payload.messages);
  } catch (e) {
    console.error('[mock-llm] buildReply error', e);
    reply = 'ขออภัยครับ ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้งครับ';
  }
  const id = 'chatcmpl-mock-' + Date.now().toString(36);
  const created = Math.floor(Date.now() / 1000);
  const model = payload.model || MODEL;
  const usage = { prompt_tokens: Math.ceil(body.length / 4), completion_tokens: Math.ceil(reply.length / 2), total_tokens: 0 };
  usage.total_tokens = usage.prompt_tokens + usage.completion_tokens;
  if (TTFT_MS) await sleep(TTFT_MS);
  if (!payload.stream) {
    return send(res, 200, { id, object: 'chat.completion', created, model, choices: [{ index: 0, message: { role: 'assistant', content: reply }, finish_reason: 'stop' }], usage });
  }
  res.writeHead(200, { 'Content-Type': 'text/event-stream; charset=utf-8', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  let closed = false;
  res.on('close', () => (closed = true));
  const write = (o) => !closed && res.write(`data: ${JSON.stringify(o)}\n\n`);
  write({ id, object: 'chat.completion.chunk', created, model, choices: [{ index: 0, delta: { role: 'assistant', content: '' }, finish_reason: null }] });
  const cps = Array.from(reply);
  for (let i = 0; i < cps.length && !closed; i += CHUNK) {
    write({ id, object: 'chat.completion.chunk', created, model, choices: [{ index: 0, delta: { content: cps.slice(i, i + CHUNK).join('') }, finish_reason: null }] });
    if (DELAY_MS) await sleep(DELAY_MS);
  }
  write({ id, object: 'chat.completion.chunk', created, model, choices: [{ index: 0, delta: {}, finish_reason: 'stop' }], usage });
  if (!closed) res.end('data: [DONE]\n\n');
}

function createServer() {
  return http.createServer((req, res) => {
    const url = (req.url || '/').split('?')[0];
    if (req.method === 'GET' && (url === '/health' || url === '/healthz')) return send(res, 200, { status: 'ok', model: MODEL });
    if (req.method === 'GET' && url === '/v1/models') return send(res, 200, { object: 'list', data: [{ id: MODEL, object: 'model', created: 0, owned_by: 'buildmart-mock' }] });
    if (req.method === 'POST' && url === '/v1/audio/transcriptions') {
      const chunks = [];
      req.on('data', (c) => chunks.push(c));
      req.on('end', () => {
        handleTranscription(req, res, Buffer.concat(chunks)).catch((e) => send(res, 500, { error: { message: String(e.message || e) } }));
      });
      return;
    }
    if (req.method === 'POST' && url === '/v1/rerank') {
      let body = '';
      req.setEncoding('utf8');
      req.on('data', (c) => (body += c));
      req.on('end', () => (RERANK_MS ? sleep(RERANK_MS) : Promise.resolve()).then(() => handleRerank(req, res, body)));
      return;
    }
    if (req.method === 'POST' && url === '/v1/audio/speech') {
      let body = '';
      req.setEncoding('utf8');
      req.on('data', (c) => (body += c));
      req.on('end', () => handleSpeech(req, res, body).catch((e) => send(res, 500, { error: { message: String(e.message || e) } })));
      return;
    }
    if (req.method === 'POST' && url === '/v1/chat/completions') {
      let body = '';
      req.setEncoding('utf8');
      req.on('data', (c) => (body += c));
      req.on('end', () => handleChat(req, res, body).catch((e) => {
        console.error('[mock-llm]', e);
        if (!res.headersSent) send(res, 500, { error: { message: String(e.message || e) } });
        else res.end();
      }));
      return;
    }
    send(res, 404, { error: { message: 'not found' } });
  });
}

module.exports = { buildReply, createServer, parseProducts, parseDocs, parseShop, parseFocus, searchDocs, parseMultipart };

if (require.main === module) {
  createServer().listen(PORT, '0.0.0.0', () => console.log(`[mock-llm] listening on :${PORT} model=${MODEL}`));
}
