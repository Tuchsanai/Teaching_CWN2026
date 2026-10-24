#!/usr/bin/env node
// render-result.mjs · ตารางผลของ LAB (spec JSON) → PNG ธีมมืด ตามสไตล์ img/lab0-checklist.png ของบท 04
//
// ใช้:   node render-result.mjs <spec.json> <out.png> [--dsf 2] [--min-height 800] [--html out.html]
//
// spec = {
//   "title":     "LAB 0 · ตรวจเครื่อง",            // ไม่มี "—" → เติมชื่อระบบตาม theme ให้ (— PawPantry / — สบายใจ สปา)
//   "subtitle":  "รันจริง 12 ต.ค. 2026 · …",       // ไม่บังคับ · ตัวเทาใต้หัวเรื่อง
//   "theme":     "05" | "06",                       // ไม่บังคับ · ค่าเริ่มต้น "05"
//   "columns":   ["รายการ", "ผล", "พร้อมไหม"],
//   "rows":      [["Docker", "29.5.2", "✅"], …],   // ข้อความในช่องใช้ `code` **ตัวหนา** และ <br> / \n ขึ้นบรรทัดใหม่ได้
//   "summary":   "สรุป: พร้อม 9/9 รายการ",          // หรือ array หลายบรรทัด · สีเขียวใต้ตาราง
//   "highlight": [{ "row": 2, "col": 1, "color": "red" }],  // row/col นับจาก 0 · ไม่ใส่ col = ทั้งแถว
//                                                   // สี: red green yellow blue orange gray หรือ "#hex"
//   "widths":    ["22%", "38%", "12%", "28%"],     // ไม่บังคับ · ไม่ใส่ = ให้เบราว์เซอร์จัดเอง
//   "align":     ["left", "left", "center"],       // ไม่บังคับ · ไม่ใส่ = คอลัมน์ที่ทุกช่องสั้น ≤ 4 ตัว (✅ ❌ 12) จัดกลาง
//   "mono":      [1],                               // ไม่บังคับ · บังคับให้คอลัมน์นี้เป็น monospace
//   "monoAuto":  true                               // ค่าเริ่มต้น true = ทุกคอลัมน์ยกเว้นคอลัมน์แรก (ชื่อรายการ เช่น "Node.js")
//                                                   // ช่องที่ทั้งช่องเป็น `code` หรือมี / . _ และไม่มีอักษรไทย (≤ 3 คำ) → monospace
//                                                   // false = ปิด · [1, 2] = เฉพาะคอลัมน์ที่ระบุ
// }
//
// ผล: กว้าง 1280 CSS px × DSF 2 = ไฟล์ 2560 px · สูงอย่างน้อย 800 CSS px (เหมือนบท 04) และยืดตามตาราง
//     ถ้าไฟล์ > 600 KB จะเรนเดอร์ใหม่ที่ DSF 1.5 · ฟอนต์ Noto Sans Thai (Google Fonts) ตัดคำไทยด้วย Chromium
// หา playwright จาก: env PLAYWRIGHT_DIR → node_modules ข้างสคริปต์ → C:/t/work/a9/node_modules

import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const LIMIT = 600 * 1024;
const WIDTH = 1280;
const here = path.dirname(fileURLToPath(import.meta.url));

// ---------- ธีม (สีตรงกับ 04/img/lab0-checklist.png ที่วัดจากพิกเซล) ----------
const BASE = {
  bg: '#1e1e1e', text: '#dddddd', title: '#e8b86d', head: '#9cdcfe', headBg: '#2d2d2d',
  border: '#444444', summary: '#88aa88', sub: '#9d9d9d', code: '#ce9178', codeBg: '#2a2a2a',
};
const THEMES = {
  '05': { ...BASE, suffix: 'PawPantry' },
  '06': { ...BASE, suffix: 'สบายใจ สปา' },
};
const COLORS = {
  red: '#f48771', green: '#89d185', yellow: '#dcdcaa', blue: '#9cdcfe', orange: '#e8b86d', gray: '#8a8a8a',
};

// ---------- อาร์กิวเมนต์ ----------
const args = process.argv.slice(2);
const takeOpt = (name, def) => {
  const i = args.indexOf(name);
  if (i < 0) return def;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
let dsf = Number(takeOpt('--dsf', 2));
const minHeight = Number(takeOpt('--min-height', 800));
const htmlOut = takeOpt('--html', null);
const [specPath, outPng] = args;
if (!specPath || !outPng) {
  console.error('ใช้: node render-result.mjs <spec.json> <out.png> [--dsf 2] [--min-height 800] [--html out.html]');
  process.exit(1);
}
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8').replace(/^\uFEFF/, ''));
for (const k of ['title', 'columns', 'rows']) {
  if (!spec[k]) { console.error(`spec ต้องมี "${k}"`); process.exit(1); }
}
const theme = THEMES[String(spec.theme ?? '05')] ?? THEMES['05'];
const ncol = spec.columns.length;
spec.rows.forEach((r, i) => {
  if (r.length !== ncol) console.warn(`⚠️  แถว ${i} มี ${r.length} ช่อง แต่หัวตารางมี ${ncol} คอลัมน์`);
});

// ---------- แปลงข้อความในช่อง ----------
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const THAI = /[\u0E00-\u0E7F]/;
function inline(raw) {
  // แยก `code` ก่อน แล้วค่อยแปลง **bold** และขึ้นบรรทัดใหม่ในส่วนที่ไม่ใช่ code
  const s = String(raw ?? '');
  const parts = s.split(/(`[^`]+`)/g);
  return parts.map((p) => {
    if (/^`[^`]+`$/.test(p)) return `<code${p.length <= 26 ? ' class="short"' : ''}>${esc(p.slice(1, -1))}</code>`;
    return esc(p)
      .replace(/&lt;br\s*\/?&gt;/gi, '<br>')
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  }).join('');
}
const plain = (s) => String(s ?? '').replace(/[`*]/g, '').replace(/<br\s*\/?>/gi, ' ');
const autoCols = Array.isArray(spec.monoAuto) ? new Set(spec.monoAuto) : null;
function isMonoCell(raw, ci) {
  const s = String(raw ?? '').trim();
  if (!s) return false;
  if (/^`[^`]+`$/.test(s)) return true;                 // ทั้งช่องเป็น code → mono ทั้งช่อง (ไม่มีพื้นหลัง pill)
  if (spec.monoAuto === false) return false;
  if (autoCols ? !autoCols.has(ci) : ci === 0) return false;
  if (s.startsWith('`')) return false;                   // มี code บางส่วน → จัดการด้วย <code> แทน
  // มี / . _ และไม่มีอักษรไทย และไม่เกิน 3 คำ → ถือว่าเป็น path / URL / ชื่อไฟล์ / เวอร์ชัน
  return /[/._]/.test(s) && !THAI.test(s) && s.split(/\s+/).length <= 3;
}
const glyphLen = (s) => [...new Intl.Segmenter('th', { granularity: 'grapheme' }).segment(plain(s).trim())].length;

const align = spec.align ?? spec.columns.map((_, c) =>
  spec.rows.length && spec.rows.every((r) => glyphLen(r[c]) <= 4) ? 'center' : 'left');
// คอลัมน์สั้น (ทุกช่อง ≤ 12 ตัว เช่น "✅ พร้อม" "38/42") → ไม่ตัดบรรทัด ทั้งหัวและช่อง
const nowrap = spec.columns.map((_, c) =>
  spec.rows.length > 0 && spec.rows.every((r) => glyphLen(r[c]) <= 12) && glyphLen(spec.columns[c]) <= 12);
const monoCols = new Set(spec.mono ?? []);
const hl = new Map();
for (const h of spec.highlight ?? []) {
  const color = COLORS[h.color] ?? h.color ?? COLORS.red;
  if (h.col === undefined || h.col === null) for (let c = 0; c < ncol; c++) hl.set(`${h.row},${c}`, color);
  else hl.set(`${h.row},${h.col}`, color);
}

let title = spec.title;
if (!title.includes('—') && theme.suffix && spec.suffix !== false) title += ` — ${spec.suffix ?? theme.suffix}`;
const summary = [].concat(spec.summary ?? []);

const colgroup = spec.widths ? `<colgroup>${spec.widths.map((w) => `<col style="width:${w}">`).join('')}</colgroup>` : '';
const thead = `<tr>${spec.columns.map((c, i) => `<th style="text-align:${align[i]}${nowrap[i] ? ';white-space:nowrap' : ''}">${inline(c)}</th>`).join('')}</tr>`;
const tbody = spec.rows.map((r, ri) => `<tr>${r.map((cell, ci) => {
  const cls = [];
  if (monoCols.has(ci) || isMonoCell(cell, ci)) cls.push('mono');
  const color = hl.get(`${ri},${ci}`);
  const style = [`text-align:${align[ci] ?? 'left'}`];
  if (nowrap[ci]) style.push('white-space:nowrap');
  if (color) style.push(`color:${color}`, `background:${color}1f`, 'font-weight:600');
  let body = inline(cell);
  if (cls.includes('mono')) {
    // ตัดบรรทัดที่ / . _ - ก่อน (ไม่ตัดกลางคำ) · ตัดกลางคำเฉพาะเมื่อยาวเกินช่องจริง ๆ
    body = body.replace(/^<code(?: class="short")?>(.*)<\/code>$/s, '$1')
      .split(/(<[^>]+>)/g).map((t) => (t.startsWith('<') ? t : t.replace(/([/._-])(?=[^\s])/g, '$1<wbr>'))).join('');
  }
  return `<td class="${cls.join(' ')}" style="${style.join(';')}">${body === '' ? '&nbsp;' : body}</td>`;
}).join('')}</tr>`).join('\n');

const html = `<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700&family=Noto+Sans:wght@400;600;700&family=Noto+Sans+Mono:wght@400;600&display=block" rel="stylesheet">
<style>
  :root { color-scheme: dark; }
  html, body { margin: 0; background: ${theme.bg}; }
  body { width: ${WIDTH}px; min-height: ${minHeight}px; box-sizing: border-box; padding: 40px 40px 36px;
         font-family: "Noto Sans", "Noto Sans Thai", "Leelawadee UI", Tahoma, "Segoe UI Emoji", sans-serif;
         font-size: 17px; line-height: 1.4; color: ${theme.text}; }
  h1 { margin: 0 0 ${spec.subtitle ? 6 : 16}px; font-size: 22px; line-height: 1.4; font-weight: 700; color: ${theme.title}; }
  .sub { margin: 0 0 14px; font-size: 14px; color: ${theme.sub}; }
  table { width: 100%; border-collapse: collapse; table-layout: ${spec.widths ? 'fixed' : 'auto'}; }
  th, td { border: 1px solid ${theme.border}; padding: 10px 14px; vertical-align: top;
           overflow-wrap: break-word; word-break: normal; }
  th { background: ${theme.headBg}; color: ${theme.head}; font-weight: 700; text-align: left; vertical-align: middle; }
  td.mono, code { font-family: "Cascadia Mono", Consolas, "Noto Sans Mono", "Noto Sans Thai", monospace; }
  td.mono { font-size: 15.5px; overflow-wrap: break-word; }
  code.short { white-space: nowrap; }
  code { font-size: 0.92em; color: ${theme.code}; background: ${theme.codeBg}; padding: 1px 4px; margin: 0 1px; border-radius: 4px; }
  td[style*="background"] code { color: inherit; }
  b { font-weight: 700; color: #ffffff; }
  .summary { margin: 18px 0 0; font-size: 15px; color: ${theme.summary}; }
  .summary + .summary { margin-top: 4px; }
</style></head>
<body>
  <h1>${inline(title)}</h1>
  ${spec.subtitle ? `<p class="sub">${inline(spec.subtitle)}</p>` : ''}
  <table>${colgroup}<thead>${thead}</thead><tbody>
${tbody}
  </tbody></table>
  ${summary.map((s) => `<p class="summary">${inline(s)}</p>`).join('\n  ')}
</body></html>`;

if (htmlOut) fs.writeFileSync(htmlOut, html);

// ---------- เรนเดอร์ ----------
function loadPlaywright() {
  const bases = [process.env.PLAYWRIGHT_DIR, here, 'C:/t/work/a9'].filter(Boolean);
  for (const b of bases) {
    try { return createRequire(path.join(path.resolve(b), 'noop.js'))('playwright'); } catch { /* ถัดไป */ }
  }
  console.error('หา playwright ไม่เจอ · ติดตั้งด้วย: npm i playwright@1.63.0 แล้วตั้ง PLAYWRIGHT_DIR=<โฟลเดอร์นั้น>');
  process.exit(2);
}
const { chromium } = loadPlaywright();
const browser = await chromium.launch({ headless: true });

async function render(scale) {
  const ctx = await browser.newContext({ viewport: { width: WIDTH, height: minHeight }, deviceScaleFactor: scale });
  const page = await ctx.newPage();
  await page.setContent(html, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.evaluate(() => document.fonts.ready);
  const thaiOk = await page.evaluate(() => document.fonts.check('400 17px "Noto Sans Thai"', 'ก'));
  if (!thaiOk) console.warn('⚠️  โหลด Noto Sans Thai ไม่ได้ (ออฟไลน์?) · ใช้ Leelawadee UI แทน (ตรวจภาพอีกครั้ง)');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (overflow > 0) console.warn(`⚠️  ตารางล้นแนวนอน ${overflow}px · ลดข้อความหรือกำหนด "widths"`);
  fs.mkdirSync(path.dirname(path.resolve(outPng)), { recursive: true });
  await page.screenshot({ path: outPng, fullPage: true });
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  await ctx.close();
  return { size: fs.statSync(outPng).size, h };
}

let { size, h } = await render(dsf);
if (size > LIMIT && dsf > 1.5) {
  console.warn(`ไฟล์ ${(size / 1024).toFixed(0)} KB > 600 KB ที่ DSF ${dsf} → เรนเดอร์ใหม่ที่ DSF 1.5`);
  dsf = 1.5;
  ({ size, h } = await render(dsf));
}
await browser.close();
console.log(`${outPng} · ${Math.round(WIDTH * dsf)}×${Math.round(h * dsf)} px · DSF ${dsf} · ${(size / 1024).toFixed(0)} KB` +
  `${size > LIMIT ? ' ⚠️ ยังเกิน 600 KB (ตัดแถวหรือแบ่งเป็น 2 ภาพ)' : ''}`);
