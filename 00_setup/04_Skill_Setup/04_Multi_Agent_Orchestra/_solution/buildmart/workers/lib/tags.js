// workers/lib/tags.js — tag คำสั่งในคำตอบของโมเดล (BUILDMART ข้อ 4.4) + ทำความสะอาดข้อความก่อนแสดง
//
//   [CALC]{"type":"concrete","volume":3}     → คำนวณวัสดุ (shared/calc.js) แล้วเรียกโมเดลอีกรอบ
//   [ADD_TO_CART]{"sku":"CEM-001","qty":21}  → เพิ่มลงตะกร้าจริง (หลายบรรทัดได้)
//   [QUOTE]{}                                 → สร้างใบเสนอราคาจากตะกร้า แล้วเรียกโมเดลอีกรอบ
//
// parseTags(raw)      → [{name, args, start, end}]   (JSON อ่านแบบนับวงเล็บ รองรับช่องว่าง/``` ครอบ)
// cleanText(raw)      → ข้อความสำหรับผู้ใช้: ตัด <think> · tag · [n] · tag ที่ยังพิมพ์ไม่จบท้าย stream
// citeRefs(raw)       → เลข [n] ที่โมเดลอ้าง (ตามลำดับที่เจอ ไม่ซ้ำ)
import { stripThink } from './llm.js';

export const TAG_NAMES = ['CALC', 'ADD_TO_CART', 'QUOTE'];
// v3: โมเดลจริงบางครั้งสะกด tag เพี้ยน ([TAG] [CALCULATE] [ADD-TO-CART] [Quote] ...) → รับทุก "[ชื่ออังกฤษ]" แล้วจัดเข้า 3 ชนิดจากชื่อหรือจาก JSON
//   JSON มี type เป็นงานคำนวณ → CALC · มี sku/items → ADD_TO_CART · ชื่อขึ้นต้น QUOT → QUOTE · อื่น ๆ ที่มี JSON → UNKNOWN (ไม่ทำงาน แต่ตัดออกจากข้อความ)
const TAG_RE = /\[\s*([A-Za-z][A-Za-z_ -]{0,30}?)\s*\]/g;
export const CALC_TYPES = ['concrete', 'wall', 'tile', 'paint', 'rebar'];
const NAME_ALIAS = [
  [/^(CALC|CALCULATE|CALCULATION|CALCULATOR|COMPUTE|ESTIMATE)$/, 'CALC'],
  [/^(ADD_?TO_?CART|ADD_?CART|CART_?ADD|ADD|CART|ADD_?ITEMS?)$/, 'ADD_TO_CART'],
  [/^(QUOTE|QUOTATION|CREATE_?QUOTE|QUOTE_?REQUEST)$/, 'QUOTE'],
];
/** ชื่อ tag ที่โมเดลเขียน + JSON → ชนิดที่ระบบรู้จัก (หรือ null = ไม่ใช่ tag) */
export function canonicalTag(rawName, args, hasJson) {
  const n = String(rawName).trim().toUpperCase().replace(/[\s-]+/g, '_');
  const a = args && typeof args === 'object' ? args : null;
  if (a && CALC_TYPES.includes(String(a.type || '').toLowerCase())) return 'CALC';
  if (a && (a.sku || Array.isArray(a.items) || (Array.isArray(a) && a.some((x) => x?.sku)))) return 'ADD_TO_CART';
  for (const [re, name] of NAME_ALIAS) if (re.test(n)) return name === 'QUOTE' || hasJson ? name : null;
  return hasJson ? 'UNKNOWN' : null; // "[หมายเหตุ]" / "[Link]" ที่ไม่มี JSON ตาม = ข้อความธรรมดา
}

/** อ่าน JSON object ที่เริ่มที่ตำแหน่ง i (ข้ามช่องว่าง/`:`) → {value, end} หรือ null */
function readJsonObject(s, i) {
  let k = i;
  while (k < s.length && /[\s:`]/.test(s[k]) && s[k] !== '\n') k++;
  if (s[k] !== '{') return null;
  let depth = 0;
  let inStr = false;
  for (let j = k; j < s.length; j++) {
    const c = s[j];
    if (inStr) {
      if (c === '\\') j++;
      else if (c === '"') inStr = false;
      continue;
    }
    if (c === '"') inStr = true;
    else if (c === '{') depth++;
    else if (c === '}' && --depth === 0) {
      const txt = s.slice(k, j + 1);
      try {
        return { value: JSON.parse(txt), end: j + 1 };
      } catch {
        try {
          return { value: JSON.parse(txt.replace(/'/g, '"').replace(/,\s*}/g, '}')), end: j + 1 };
        } catch {
          return { value: null, end: j + 1 };
        }
      }
    }
  }
  return { value: null, end: s.length, open: true }; // ยังไม่ปิดวงเล็บ (stream ยังไม่จบ)
}

export function parseTags(raw) {
  const s = stripThink(raw);
  const out = [];
  TAG_RE.lastIndex = 0;
  let m;
  while ((m = TAG_RE.exec(s))) {
    const j = readJsonObject(s, m.index + m[0].length);
    const name = canonicalTag(m[1], j?.value, !!j);
    if (!name) continue;
    if (name === 'CALC' && j?.value && j.value.type) j.value.type = String(j.value.type).toLowerCase();
    out.push({ name, rawName: m[1], args: j?.value ?? {}, start: m.index, end: j ? j.end : m.index + m[0].length, open: !!j?.open });
    if (j) TAG_RE.lastIndex = j.end;
  }
  // JSON งานคำนวณที่ไม่มีชื่อ tag เลย (เช่น ```json {"type":"paint",...}```) → CALC
  if (!out.some((t) => t.name === 'CALC')) {
    const re = /\{\s*"type"\s*:\s*"(concrete|wall|tile|paint|rebar)"/gi;
    let k;
    while ((k = re.exec(s))) {
      if (out.some((t) => k.index >= t.start && k.index < t.end)) continue;
      const j = readJsonObject(s, k.index);
      if (!j || !j.value) continue;
      j.value.type = String(j.value.type).toLowerCase();
      let start = k.index;
      const before = s.slice(0, start).match(/```(?:json)?\s*$/i);
      if (before) start -= before[0].length;
      out.push({ name: 'CALC', rawName: '', args: j.value, start, end: j.end, open: false });
      break;
    }
    out.sort((x, y) => x.start - y.start);
  }
  return out;
}

/** เลข [n] / [1, 2] / [1][2] ที่โมเดลใส่ (ไม่นับ tag) */
export function citeRefs(raw) {
  const s = stripThink(raw);
  const seen = [];
  const re = /\[(\d{1,2}(?:\s*[,،、]\s*\d{1,2})*)\]/g;
  let m;
  while ((m = re.exec(s))) for (const n of m[1].split(/\s*[,،、]\s*/).map(Number)) if (n > 0 && !seen.includes(n)) seen.push(n);
  return seen;
}

/** ข้อความที่แสดงให้ผู้ใช้ (ใช้ได้ทั้งระหว่าง stream และตอนจบ) */
export function cleanText(raw, { final = false } = {}) {
  let s = stripThink(raw);
  // ตัด tag + JSON (รวม ``` ที่ครอบ)
  const tags = parseTags(s);
  for (let i = tags.length - 1; i >= 0; i--) s = s.slice(0, tags[i].start) + s.slice(tags[i].end);
  s = s.replace(/```(?:json)?\s*```/g, '');
  if ((s.match(/```/g) || []).length % 2 === 1 || tags.length) s = s.replace(/^[ \t]*```(?:json)?[ \t]*$/gim, ''); // รั้ว code block ที่เหลือหลังตัด tag
  // ตกค้าง: "[ชื่อ]{...}" ที่ JSON พัง / "[TAG]" ลอย ๆ ท้ายข้อความ (ตอนจบ)
  s = s.replace(/\[\s*[A-Z][A-Z_ -]{0,30}\s*\]\s*\{[^\n]*\}?/g, '');
  if (final) s = s.replace(/\[\s*(?:TAG|CALC|ADD_TO_CART|QUOTE|ADD|CART)\s*\]\s*$/gi, '');
  // tag ที่ยังพิมพ์ไม่ครบท้ายข้อความ เช่น "[CA" "[ADD_TO"
  if (!final) {
    const i = s.lastIndexOf('[');
    if (i !== -1) {
      const tail = s.slice(i);
      if (/^\[\s*[A-Za-z_ -]*\]?\s*$/.test(tail) || /^\[\d{0,2}(\s*,\s*\d{0,2})*$/.test(tail)) s = s.slice(0, i); // "[CA" "[TAG]" "[1" ยังไม่ปิด/ยังไม่มี JSON
    }
  }
  // ตัดเลขอ้างอิง [n]
  s = s.replace(/[ \t]*\[(\d{1,2}(?:\s*[,،、]\s*\d{1,2})*)\]/g, '');
  // ตัดหัวข้อ/คำที่โมเดลบางตัวชอบเติม
  s = s.replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n');
  return final ? s.trim() : s.replace(/^\s+/, '');
}

/** มีอักษรไทยไหม */
export const hasThai = (s) => /[฀-๿]/.test(String(s || ''));
