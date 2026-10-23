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
const TAG_RE = /\[\s*(CALC|ADD_TO_CART|QUOTE)\s*\]/g;

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
    out.push({ name: m[1], args: j?.value ?? {}, start: m.index, end: j ? j.end : m.index + m[0].length, open: !!j?.open });
    if (j) TAG_RE.lastIndex = j.end;
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
  // tag ที่ยังพิมพ์ไม่ครบท้ายข้อความ เช่น "[CA" "[ADD_TO"
  if (!final) {
    const i = s.lastIndexOf('[');
    if (i !== -1) {
      const tail = s.slice(i);
      if (/^\[\s*[A-Z_]*\s*$/.test(tail) || /^\[\d{0,2}(\s*,\s*\d{0,2})*$/.test(tail)) s = s.slice(0, i); // "[CA" "[1" ยังไม่ปิด
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
