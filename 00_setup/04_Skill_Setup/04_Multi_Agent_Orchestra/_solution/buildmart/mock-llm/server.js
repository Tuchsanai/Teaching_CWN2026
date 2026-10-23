// mock-llm ของ "บ้านช่าง BuildMart" — LLM จำลองแบบ OpenAI-compatible (ไม่ต้องใช้ GPU)
// รองรับ: GET /health · GET /v1/models · POST /v1/chat/completions (stream SSE และ non-stream)
// ไม่มี dependency (ใช้ http ของ Node ล้วน)
//
// หลักการ: ทำตัวเหมือน LLM ที่ "รู้เฉพาะสิ่งที่ chat-worker ใส่มาใน messages" เท่านั้น
//   - ข้อมูลร้าน / ตารางสินค้า (## สินค้าที่เกี่ยวข้อง) / เอกสารอ้างอิง (## เอกสารอ้างอิง) อ่านจาก system prompt
//   - ไม่เปิดอ่าน PDF หรือ DB เอง (พิสูจน์ว่า RAG ทำงานจริง)
//   - ผลของ tag มาเป็นข้อความที่ขึ้นต้นด้วย "ผลคำนวณ:" / "ผลคำสั่ง:" ตามด้วย JSON
// รูปแบบ input ทั้งหมดอธิบายไว้ใน CONTRACT.md หัวข้อ "Notes from C3 (mock input format)"
'use strict';
const http = require('http');

const PORT = Number(process.env.PORT || 8000);
const MODEL = process.env.MOCK_MODEL || 'mock-buildmart';
const DELAY_MS = Number(process.env.MOCK_DELAY_MS ?? 15); // หน่วงระหว่าง delta (ให้ดูเหมือนพิมพ์)
const CHUNK = Number(process.env.MOCK_CHUNK || 6); // จำนวนตัวอักษรต่อ delta

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

const STOP = ['ครับ', 'ค่ะ', 'คะ', 'นะ', 'ไหม', 'มั้ย', 'หรือเปล่า', 'แค่ไหน', 'เท่าไร', 'เท่าไหร่', 'อะไร', 'อย่างไร', 'ยังไง', 'ได้', 'กี่', 'ต้อง', 'หน่อย', 'ช่วย', 'บ้าง', 'แล้ว', 'และ', 'กับ', 'ของ', 'ที่', 'จะ', 'ให้', 'เป็น', 'คือ', 'หรือ', 'ขอ', 'ถ้า', 'อยาก', 'ทราบ', 'สอบถาม', 'ผม', 'ฉัน', 'เรา', 'ไป'];
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
function lastItems(messages, beforeIdx) {
  for (let k = beforeIdx - 1; k >= 0; k--) {
    const m = messages[k];
    const c = text(m.content);
    if (/^\s*ผลคำนวณ\s*[:：]/.test(c)) {
      const j = parseJsonAfter(c);
      if (j && Array.isArray(j.rows) && j.rows.length) return j.rows.map((r) => ({ sku: r.sku, qty: Number(r.qty), unit: r.unit || '', label: r.label || '' }));
    }
    if (m.role === 'assistant') {
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
    : `${p.name} (${p.sku}) มีของ ${have.length} สาขา จาก ${codesList.length} สาขา (${detail})`;
}
function qtyIn(q) {
  const m = q.match(/(\d[\d,]*)\s*(เส้น|ถุง|ก้อน|กล่อง|แกลลอน|ชิ้น|อัน|ม้วน|แผ่น|ตัว|ตู้|เครื่อง|กระป๋อง|pcs|pieces|bags|bars|units)/i);
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
  const couponQ = /โค้ดส่วนลด|โค้ดลด|คูปอง|ส่วนลด|โปรโมชั่นโค้ด|coupon|discount|promo code/i.test(q);
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
      const top = rankProducts(q, products)[0];
      if (top && top.s >= 3) items = [{ sku: top.p.sku, qty, label: top.p.name, unit: top.p.unit }];
    }
    if (!items.length) items = lastItems(messages, qIdx);
    items = items.filter((it) => it.qty > 0);
    if (!items.length) return out(en ? 'Which product and how many would you like to add?' : 'ต้องการใส่สินค้าอะไร จำนวนเท่าไรครับ เช่น "ใส่ตะกร้า CEM-001 10 ถุง"');
    const list = items.map((it) => `- ${it.sku} ${it.label || ''} × ${it.qty} ${it.unit || ''}`.replace(/\s+$/, '')).join('\n');
    const tags = items.map((it) => `[ADD_TO_CART]${JSON.stringify({ sku: it.sku, qty: it.qty })}`).join('\n');
    return (en ? `Done, I added these to your cart:\n${list}` : endKrub(`เรียบร้อยครับ ใส่ตะกร้าให้แล้ว\n${list}\nไปที่หน้าตะกร้าเพื่อสั่งซื้อหรือขอใบเสนอราคาได้เลยครับ`)) + '\n' + tags;
  }

  // 5) คำนวณวัสดุ → [CALC]
  const ct = calcTag(q);
  if (ct) return (en ? 'Let me calculate that for you.' : 'ขอคำนวณให้สักครู่นะครับ') + '\n[CALC]' + JSON.stringify(ct);

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
  if (/เบอร์|โทร|ติดต่อ|phone|call|contact|สาขา.*(ไหน|อะไร|ที่ไหน)|branch/i.test(q) && !/สต็อก|สต๊อก|มีของ|กี่สาขาที่มี|ราคา|stock/i.test(q)) {
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

  const priceQ = /ราคา|กี่บาท|ละเท่า|how much|price|cost/i.test(q);
  const stockQ = /สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|ของหมด|in stock|stock|available at/i.test(q);

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
    const clauses = q0.split(/\s*(?:แล้วก็|แล้ว|และ|,|\?|และก็|\band\b|\balso\b)\s*/).filter((c) => c.trim().length > 1);
    const pClause = clauses.filter((c) => /ราคา|กี่บาท|ละเท่า|how much|price|cost|สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|stock/i.test(c)).join(' ') || q;
    const other = clauses.filter((c) => !/ราคา|กี่บาท|ละเท่า|how much|price|cost|สต็อก|สต๊อก|มีของ|กี่สาขา|เหลือ|stock/i.test(c)).join(' ');
    let ranked = rankProducts(enrich(pClause), products);
    if (!ranked.length) ranked = rankProducts(q, products);
    const parts = [];
    if (other && docs.length) {
      const d = searchDocs(enrich(other), docs, products);
      if (d && d.coverage >= 0.3) parts.push((en ? `According to ${d.doc.filename}: ` : `จากเอกสาร ${d.doc.filename} หน้า ${d.doc.page}: `) + `${d.sentence} [${d.doc.n}]`);
    }
    if (ranked.length && ranked[0].s >= 2) {
      const p = ranked[0].p;
      const qty = qtyIn(pClause);
      if (priceQ) parts.push(priceLine(p, qty, en));
      if (stockQ) parts.push(stockLine(p, shop, en));
      return out(parts.join('\n'));
    }
    if (parts.length) return out(parts.join('\n'));
    return out(en ? "Sorry, I couldn't find that product in our catalogue, so I can't give a price." : 'ขออภัยครับ ไม่พบสินค้านี้ในรายการของร้าน จึงยังบอกราคาไม่ได้ ลองพิมพ์ชื่อหรือรหัสสินค้าอีกครั้งได้ครับ');
  }

  // 11) มีขายไหม
  const availQ = /ขายไหม|ขายมั้ย|มีขาย|ขายด้วย|ขาย.*ไหม|มี.+ไหม|do you (sell|have)|available/i.test(q);
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

  // 12) ตอบจากเอกสารอ้างอิง (RAG)
  if (docs.length) {
    const d = searchDocs(q, docs, products);
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

// ---------------------------------------------------------------- HTTP
function send(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(body) });
  res.end(body);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function handleChat(req, res, body) {
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

module.exports = { buildReply, createServer, parseProducts, parseDocs, parseShop, searchDocs };

if (require.main === module) {
  createServer().listen(PORT, '0.0.0.0', () => console.log(`[mock-llm] listening on :${PORT} model=${MODEL}`));
}
