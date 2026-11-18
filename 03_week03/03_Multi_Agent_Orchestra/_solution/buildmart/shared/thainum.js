// shared/thainum.js — ตัวเลขที่สะกดเป็นคำไทย → ตัวเลข (ข้อความจาก Whisper / คนพิมพ์ เช่น "ร้อยถุง" "ห้าสิบเส้น" "หกสิบคูณหกสิบ" "สองจุดห้า")
//   thaiWordsToNumber('สองร้อยห้าสิบ') → 250 · ไม่ใช่ตัวเลข → null
//   digitsForThaiNumbers('ซื้อร้อยถุง') → 'ซื้อ 100 ถุง' · 'หกสิบคูณหกสิบ' → '60x60' · 'THW สองจุดห้า' → 'THW 2.5'
//   (แทนเฉพาะคำตัวเลขที่ตามด้วยหน่วยสินค้า / คูณ / จุด — ไม่แตะ "สองตัวนี้" "หนึ่งในนั้น")
const DIGIT = { ศูนย์: 0, หนึ่ง: 1, เอ็ด: 1, สอง: 2, ยี่: 2, สาม: 3, สี่: 4, ห้า: 5, หก: 6, เจ็ด: 7, แปด: 8, เก้า: 9 };
const MULT = { สิบ: 10, ร้อย: 100, พัน: 1000, หมื่น: 10000, แสน: 100000 };
const WORDS = 'ศูนย์|หนึ่ง|เอ็ด|สอง|ยี่|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า|สิบ|ร้อย|พัน|หมื่น|แสน';
const TOKEN_RE = new RegExp(WORDS, 'g');

export function thaiWordsToNumber(s) {
  const toks = String(s || '').match(TOKEN_RE);
  if (!toks || toks.join('') !== String(s).replace(/\s+/g, '')) return null;
  let total = 0;
  let cur = null;
  for (const t of toks) {
    if (t in DIGIT) cur = DIGIT[t];
    else {
      total += (cur ?? 1) * MULT[t];
      cur = null;
    }
  }
  return total + (cur ?? 0);
}

const UNITS = 'ถุง|เส้น|ก้อน|กล่อง|แกลลอน|ชิ้น|อัน|ม้วน|แผ่น|ตัว|ตู้|เครื่อง|กระป๋อง|ลูก|คิว|ตร\\.?ม\\.?|ตารางเมตร|เมตร|บาท|กก\\.?|กิโล|แอมป์|มิล|ซม\\.?|เซน';
const NUM = `((?:${WORDS})+)`;
const DIM_RE = new RegExp(`${NUM}\\s*คูณ\\s*${NUM}`, 'g');
const DEC_RE = new RegExp(`${NUM}\\s*จุด\\s*((?:${WORDS})+)`, 'g');
// "สองตัวนี้" "สามอันนั้น" = ชี้สินค้า ไม่ใช่จำนวน
const PHRASE_RE = new RegExp(`${NUM}\\s*(${UNITS})(?!\\s*(?:นี้|นั้น|นั่น|เมื่อกี้|ที่ว่า))`, 'g');

export function digitsForThaiNumbers(text) {
  return String(text || '')
    // คำที่ Whisper ถอดเป็นเสียงอ่าน: "ดีบี 12" → DB12 · "อาร์บี 9" → RB9 · "CEM001" → CEM-001
    .replace(/ดีบี\s*(\d+)/g, 'DB$1')
    .replace(/อาร์บี\s*(\d+)/g, 'RB$1')
    .replace(/\b(CEM|AGG|STL|BRK|TIL|PNT|PIP|ELC|ROF|WOD|TOL)\s*-?\s*(\d{3})\b/gi, (m, a, b) => `${a.toUpperCase()}-${b}`)
    .replace(DIM_RE, (m, a, b) => {
      const x = thaiWordsToNumber(a);
      const y = thaiWordsToNumber(b);
      return x == null || y == null ? m : ` ${x}x${y} `;
    })
    .replace(DEC_RE, (m, a, b) => {
      const x = thaiWordsToNumber(a);
      const d = (b.match(TOKEN_RE) || []).map((t) => DIGIT[t]);
      return x == null || d.some((v) => v == null) ? m : ` ${x}.${d.join('')} `;
    })
    .replace(PHRASE_RE, (m, words, unit) => {
      const n = thaiWordsToNumber(words);
      return n == null ? m : ` ${n} ${unit}`;
    });
}
