// ตรวจคำตอบของบอทตามเงื่อนไขใน cases.json (คืนรายการ "เหตุผลที่ไม่ผ่าน" เป็นภาษาไทย)

export type Check = {
  turn: number | "last"; // คำตอบที่เท่าไหร่ (เริ่มที่ 1) หรือ "last"
  has?: (string | string[])[]; // ต้องมีทุกรายการ ([a, b] = มีอย่างใดอย่างหนึ่ง)
  not?: string[]; // ห้ามมี
  lang?: "th" | "en"; // ภาษาของคำตอบ
};

/** ข้อความ text มี token หรือไม่ */
export function contains(text: string, token: string): boolean {
  if (token.startsWith("re:")) return new RegExp(token.slice(3), "i").test(text);
  // เบอร์โทร เช่น 053-123-456 -> เทียบเฉพาะตัวเลข (บอทอาจเขียน 053 123 456)
  if (/^[\d-]{9,}$/.test(token)) return text.replace(/[^\d]/g, "").includes(token.replace(/-/g, ""));
  // ตัวเลข เช่น 4, 600, 15% -> ต้องไม่เป็นส่วนหนึ่งของเลขอื่น (4 ไม่ตรงกับ 14, 45, 4.5)
  if (/^\d+%?$/.test(token)) return new RegExp(`(?<![\\d.,])${token}(?!\\d)`).test(text);
  return text.toLowerCase().includes(token.toLowerCase());
}

/** เดาภาษาจากสัดส่วนตัวอักษรไทย/อังกฤษ */
export function isLang(text: string, lang: "th" | "en"): boolean {
  const thai = (text.match(/[฀-๿]/g) || []).length;
  const latin = (text.match(/[A-Za-z]/g) || []).length;
  if (thai + latin === 0) return false;
  const thaiShare = thai / (thai + latin);
  return lang === "th" ? thaiShare > 0.5 : thaiShare < 0.2;
}

export function runChecks(checks: Check[], answers: string[]): string[] {
  const fails: string[] = [];
  for (const c of checks) {
    const idx = c.turn === "last" ? answers.length - 1 : c.turn - 1;
    const label = c.turn === "last" ? "คำตอบสุดท้าย" : `คำตอบที่ ${c.turn}`;
    const text = answers[idx];
    if (!text) {
      fails.push(`${label}: ไม่มีคำตอบ`);
      continue;
    }
    for (const item of c.has ?? []) {
      const options = Array.isArray(item) ? item : [item];
      if (!options.some((t) => contains(text, t))) fails.push(`${label}: ไม่มี ${options.join(" หรือ ")}`);
    }
    for (const t of c.not ?? []) {
      if (contains(text, t)) fails.push(`${label}: มีสิ่งที่ห้ามมี (${t.replace(/^re:/, "")})`);
    }
    if (c.lang && !isLang(text, c.lang)) {
      fails.push(`${label}: ไม่ใช่ภาษา${c.lang === "th" ? "ไทย" : "อังกฤษ"}`);
    }
  }
  return fails;
}
