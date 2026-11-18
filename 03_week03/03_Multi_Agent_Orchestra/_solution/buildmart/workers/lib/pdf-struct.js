// workers/lib/pdf-struct.js — อ่าน "Tagged PDF" (PDF ที่มีโครงสร้าง) แล้วแปลงเป็นหน่วยเนื้อหา: หัวข้อ · ย่อหน้า · ตาราง
//
// ทำไมต้องใช้โครงสร้าง: ข้อความดิบจาก PDF ไม่รู้ว่าตัวเลข "5.5" อยู่ใต้หัวคอลัมน์ไหน แถวไหน
//   Tagged PDF (เช่น ที่ Chromium/Word/LibreOffice export) เก็บ structure tree ไว้ในไฟล์:
//   Document → H1/H2/P/L/LI/Table → TR → TH/TD (+ แอตทริบิวต์ RowSpan / ColSpan / Scope)
//   แต่ละ element ชี้ไปที่ "marked content" (MCID) บนหน้า → เราต้องหาว่าข้อความของ MCID นั้นคืออะไร
//
// ดึงข้อความ 3 ขั้น (ทุกขั้นทำจาก bytes ของ PDF เท่านั้น):
//   1) pdf-lib   : เดิน structure tree → ต้นไม้ {role, attrs, kids:[element | {page, mcid}]}
//   2) pdfjs-dist: หา "กรอบ" (bounding box) ของแต่ละ MCID บนหน้า จากตำแหน่งข้อความ
//      (ข้อความจาก pdfjs เองใช้ไม่ได้กับไทย — วรรณยุกต์บางตัวหาย จึงใช้แค่ตำแหน่ง)
//   3) poppler   : `pdftotext -bbox-layout` ให้คำไทยที่ถูกต้องพร้อมพิกัด → จับคู่คำเข้ากรอบ MCID
// แล้วประกอบเป็นหน่วยเนื้อหา และแปลงตาราง (รวมเซลล์ rowspan/colspan, หัวตารางหลายชั้น, หัวซ้ำข้ามหน้า)
import { PDFDocument, PDFName, PDFDict, PDFArray, PDFRef, PDFNumber } from 'pdf-lib';

const THAI = /[฀-๿]/;
const NOTE_RE = /^[¹²³⁴⁵⁶⁷⁸⁹⁰*]+\s*|^หมายเหตุ/;
const TOC_RE = /^(สารบัญ|contents|table of contents)$/i;
const BLOCK_ROLES = new Set(['P', 'H', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI', 'Lbl', 'LBody', 'Caption', 'BlockQuote', 'Note', 'TOCI', 'Table', 'TR', 'TH', 'TD']);
const nfc = (s) => s.normalize('NFC').replace(/ํา/g, 'ำ'); // นิคหิต+สระอา → สระอำ

/** ต่อข้อความหลายบรรทัด: ไทย-ไทย ชิดกัน · อื่น ๆ เว้นวรรค */
export function joinLines(lines) {
  let out = '';
  for (const l of lines) {
    if (!l) continue;
    if (!out) out = l;
    else out += THAI.test(out.at(-1)) && THAI.test(l[0]) ? l : ` ${l}`;
  }
  return out;
}

// ---------------------------------------------------------------- 1) structure tree (pdf-lib)
export async function readStructTree(bytes) {
  const doc = await PDFDocument.load(bytes, { ignoreEncryption: true, updateMetadata: false });
  const ctx = doc.context;
  const pageIdx = new Map(doc.getPages().map((p, i) => [p.ref.toString(), i]));
  const rootDict = doc.catalog.lookup(PDFName.of('StructTreeRoot'));
  if (!(rootDict instanceof PDFDict)) return { root: null, pages: doc.getPageCount() };
  const roleMap = new Map();
  const rm = rootDict.lookup(PDFName.of('RoleMap'));
  if (rm instanceof PDFDict) for (const [k, v] of rm.entries()) roleMap.set(k.decodeText?.() ?? k.toString().slice(1), v.toString().slice(1));
  const look = (o) => (o instanceof PDFRef ? ctx.lookup(o) : o);
  const name = (o) => (o ? o.toString().replace(/^\//, '') : '');
  const seen = new Set();

  const attrsOf = (d) => {
    const out = {};
    let a = look(d.get(PDFName.of('A')));
    const list = a instanceof PDFArray ? a.asArray().map(look) : a ? [a] : [];
    for (const x of list) {
      if (!(x instanceof PDFDict)) continue;
      for (const k of ['RowSpan', 'ColSpan']) {
        const v = look(x.get(PDFName.of(k)));
        if (v instanceof PDFNumber) out[k] = v.asNumber();
      }
      const sc = x.get(PDFName.of('Scope'));
      if (sc) out.Scope = name(sc);
    }
    return out;
  };
  const walk = (o, pg) => {
    const ref = o instanceof PDFRef ? o.toString() : null;
    if (ref) {
      if (seen.has(ref)) return null;
      seen.add(ref);
    }
    o = look(o);
    if (o instanceof PDFNumber) return pg != null ? { page: pg, mcid: o.asNumber() } : null;
    if (!(o instanceof PDFDict)) return null;
    const pgRef = o.get(PDFName.of('Pg'));
    const page = pgRef ? pageIdx.get(pgRef.toString()) : pg;
    const type = name(o.get(PDFName.of('Type')));
    if (type === 'MCR') {
      const m = look(o.get(PDFName.of('MCID')));
      return m instanceof PDFNumber && page != null ? { page, mcid: m.asNumber() } : null;
    }
    if (type === 'OBJR') return null;
    let role = name(o.get(PDFName.of('S')));
    role = roleMap.get(role) || role;
    const node = { role, attrs: attrsOf(o), kids: [] };
    const k = o.get(PDFName.of('K'));
    const ks = k == null ? [] : look(k) instanceof PDFArray ? look(k).asArray() : [k];
    for (const c of ks) {
      const n = walk(c, page);
      if (n) node.kids.push(n);
    }
    return node;
  };
  const root = { role: 'Root', attrs: {}, kids: [] };
  const k = rootDict.get(PDFName.of('K'));
  const ks = k == null ? [] : look(k) instanceof PDFArray ? look(k).asArray() : [k];
  for (const c of ks) {
    const n = walk(c, null);
    if (n) root.kids.push(n);
  }
  return { root, pages: doc.getPageCount() };
}

// ---------------------------------------------------------------- 2) กรอบของแต่ละ MCID (pdfjs)
let pdfjsP = null;
async function loadPdfjs() {
  if (!pdfjsP) pdfjsP = import('pdfjs-dist/legacy/build/pdf.mjs');
  return pdfjsP;
}
/** → [ Map(mcid → {x0,y0,x1,y1}) ต่อหน้า ] (พิกัดแบบ "บนลงล่าง" หน่วย pt เหมือน poppler) */
export async function mcidBoxes(bytes) {
  const pdfjs = await loadPdfjs();
  const doc = await pdfjs.getDocument({ data: new Uint8Array(bytes), verbosity: 0, isEvalSupported: false }).promise;
  const out = [];
  try {
    for (let i = 1; i <= doc.numPages; i++) {
      const page = await doc.getPage(i);
      const [vx0, vy0, , vy1] = page.view;
      const H = vy1 - vy0;
      const tc = await page.getTextContent({ includeMarkedContent: true, disableNormalization: true });
      const boxes = new Map();
      const stack = [];
      for (const it of tc.items) {
        if (it.type === 'beginMarkedContentProps' || it.type === 'beginMarkedContent') {
          const m = /_mc(\d+)$/.exec(it.id || '');
          stack.push(m ? Number(m[1]) : null);
          continue;
        }
        if (it.type === 'endMarkedContent') {
          stack.pop();
          continue;
        }
        const mcid = [...stack].reverse().find((x) => x != null);
        if (mcid == null || !(it.width > 0)) continue;
        const [, , , , e, f] = it.transform;
        const h = it.height || Math.abs(it.transform[3]) || 10;
        const b = { x0: e - vx0, x1: e - vx0 + it.width, y0: H - (f - vy0) - h, y1: H - (f - vy0) + 0.3 * h };
        const cur = boxes.get(mcid);
        boxes.set(mcid, cur ? { x0: Math.min(cur.x0, b.x0), y0: Math.min(cur.y0, b.y0), x1: Math.max(cur.x1, b.x1), y1: Math.max(cur.y1, b.y1) } : b);
      }
      out.push(boxes);
      page.cleanup();
    }
  } finally {
    await doc.destroy();
  }
  return out;
}

// ---------------------------------------------------------------- 3) คำจาก poppler → ข้อความของแต่ละ MCID
const decode = (s) =>
  s
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&amp;/g, '&');
const num = (attrs, k) => Number(new RegExp(`${k}="([0-9.]+)"`).exec(attrs)?.[1] || 0);

/** ผล `pdftotext -bbox-layout` → [ [ {text, x0,y0,x1,y1, line} ] ต่อหน้า ] */
export function popplerWords(xml) {
  const pages = [];
  let lineNo = 0;
  for (const pm of xml.matchAll(/<page\b[^>]*>([\s\S]*?)<\/page>/g)) {
    const words = [];
    for (const lm of pm[1].matchAll(/<line\b[^>]*>([\s\S]*?)<\/line>/g)) {
      lineNo++;
      for (const w of lm[1].matchAll(/<word\b([^>]*)>([\s\S]*?)<\/word>/g)) {
        const text = nfc(decode(w[2]).trim());
        if (text) words.push({ text, x0: num(w[1], 'xMin'), y0: num(w[1], 'yMin'), x1: num(w[1], 'xMax'), y1: num(w[1], 'yMax'), line: lineNo });
      }
    }
    pages.push(words);
  }
  return pages;
}

/** จับคู่คำ (poppler) เข้ากรอบ MCID (pdfjs) → Map("page:mcid" → ข้อความ) */
export function mcidTexts(wordsByPage, boxesByPage) {
  const out = new Map();
  wordsByPage.forEach((words, p) => {
    const boxes = [...(boxesByPage[p] || new Map())].map(([mcid, b]) => ({ mcid, ...b, area: (b.x1 - b.x0) * (b.y1 - b.y0) }));
    if (!boxes.length) return;
    const acc = new Map(); // mcid → [{text,line}]
    for (const w of words) {
      const cx = (w.x0 + w.x1) / 2;
      const cy = (w.y0 + w.y1) / 2;
      let best = null;
      for (const b of boxes) {
        if (cx >= b.x0 - 1.5 && cx <= b.x1 + 1.5 && cy >= b.y0 - 1.5 && cy <= b.y1 + 1.5 && (!best || b.area < best.area)) best = b;
      }
      if (!best) continue; // ไม่อยู่ในเนื้อหาที่มีโครงสร้าง = หัว/ท้ายกระดาษ (artifact) → ทิ้ง
      if (!acc.has(best.mcid)) acc.set(best.mcid, []);
      acc.get(best.mcid).push(w);
    }
    for (const [mcid, ws] of acc) {
      const lines = [];
      let cur = null;
      for (const w of ws) {
        if (!cur || cur.line !== w.line) lines.push((cur = { line: w.line, parts: [] }));
        cur.parts.push(w.text);
      }
      out.set(`${p}:${mcid}`, joinLines(lines.map((l) => l.parts.join(' '))));
    }
  });
  return out;
}

// ---------------------------------------------------------------- ประกอบหน่วยเนื้อหา
/** ข้อความทั้งหมดใต้ element (ตัดข้อความซ้ำ — เช่น หัวตารางที่ถูกพิมพ์ซ้ำบนหน้าถัดไปจะชี้ MCID ใหม่ที่ข้อความเหมือนเดิม) */
function textOf(node, texts) {
  const parts = [];
  let page = null;
  const seen = new Set();
  const rec = (n) => {
    if ('mcid' in n) {
      const t = texts.get(`${n.page}:${n.mcid}`);
      if (t && !seen.has(t)) {
        seen.add(t);
        parts.push(t);
        if (page == null) page = n.page;
      }
      return;
    }
    n.kids.forEach(rec);
  };
  rec(node);
  return { text: joinLines(parts).replace(/\s+/g, ' ').trim(), page };
}
const hasBlockDesc = (n) => n.kids.some((k) => !('mcid' in k) && (BLOCK_ROLES.has(k.role) || hasBlockDesc(k)));

/** ตาราง → {caption, page, rows:[{page, text}]} — รวมเซลล์ที่ span, หัวตารางหลายชั้น, หัวแถว */
function buildTable(node, texts) {
  let caption = '';
  const trs = [];
  const collect = (n) => {
    for (const k of n.kids) {
      if ('mcid' in k) continue;
      if (k.role === 'Caption') caption = textOf(k, texts).text;
      else if (k.role === 'TR') trs.push(k);
      else if (k.role !== 'Table') collect(k); // THead/TBody/TFoot
    }
  };
  collect(node);
  // วางเซลล์ลงกริด (เซลล์ rowspan/colspan ถูกอ้างซ้ำทุกช่องที่มันครอบ = "propagate" ค่า)
  const grid = [];
  trs.forEach((tr, r) => {
    grid[r] = grid[r] || [];
    let c = 0;
    for (const k of tr.kids) {
      if ('mcid' in k || (k.role !== 'TH' && k.role !== 'TD')) continue;
      while (grid[r][c]) c++;
      const t = textOf(k, texts);
      const cell = { text: t.text, page: t.page, th: k.role === 'TH', scope: k.attrs.Scope || '', row: r };
      const rs = Math.max(1, k.attrs.RowSpan || 1);
      const cs = Math.max(1, k.attrs.ColSpan || 1);
      for (let i = 0; i < rs; i++) for (let j = 0; j < cs; j++) (grid[r + i] = grid[r + i] || [])[c + j] = cell;
      c += cs;
    }
  });
  const nCols = Math.max(0, ...grid.map((row) => row.length));
  // แถวหัวตาราง = แถวบนสุดที่ทุกเซลล์เป็น TH และไม่ใช่หัวแถว (Scope=Row)
  let nHead = 0;
  while (nHead < grid.length && grid[nHead].length && grid[nHead].every((c) => c && c.th && c.scope !== 'Row')) nHead++;
  if (nHead === grid.length) nHead = Math.min(1, grid.length); // ตารางที่มีแต่ TH → ถือแถวแรกเป็นหัว
  const colPath = [];
  for (let j = 0; j < nCols; j++) {
    const labels = [];
    for (let i = 0; i < nHead; i++) {
      const t = grid[i][j]?.text;
      if (t && t !== '–' && labels.at(-1) !== t) labels.push(t);
    }
    colPath[j] = labels.join(' › ');
  }
  const rows = [];
  for (let r = nHead; r < grid.length; r++) {
    const row = grid[r] || [];
    const parts = [];
    const labels = []; // หัวแถว (TH scope=Row) ที่ไม่มีหัวคอลัมน์ → ใช้เป็นป้ายนำหน้าแถว
    let page = null;
    for (let j = 0; j < nCols; j++) {
      const cell = row[j];
      if (!cell || (j > 0 && row[j - 1] === cell)) continue; // colspan: ใช้ครั้งเดียว
      if (cell.row === r && page == null) page = cell.page;
      const v = cell.text;
      if (!v) continue;
      const h = colPath[j];
      if (!h && cell.th && !parts.length) labels.push(v);
      else parts.push(h && h !== v ? `${h}: ${v}` : v);
    }
    const text = labels.length ? `${labels.join(' › ')}: ${parts.join(', ')}` : parts.join(', ');
    if (parts.length || labels.length) rows.push({ page: page ?? row.find(Boolean)?.page ?? null, text });
  }
  const page = rows[0]?.page ?? grid[0]?.find(Boolean)?.page ?? null;
  return { caption, page, header: colPath.filter(Boolean), rows };
}

/**
 * structure tree → หน่วยเนื้อหาเรียงตามลำดับเอกสาร
 *   {type:'heading', level, text, page} · {type:'para', text, page} · {type:'table', caption, page, rows, notes}
 * ตัดสารบัญ (ทุกอย่างใต้หัวข้อ "สารบัญ" จนถึงหัวข้อระดับเดียวกันถัดไป)
 */
export function structToUnits(root, texts) {
  const units = [];
  const visit = (n) => {
    if ('mcid' in n) {
      const t = texts.get(`${n.page}:${n.mcid}`);
      if (t) units.push({ type: 'para', text: t, page: n.page });
      return;
    }
    const m = /^H([1-6])?$/.exec(n.role);
    if (m) {
      const t = textOf(n, texts);
      if (t.text) units.push({ type: 'heading', level: Number(m[1] || 2), text: t.text, page: t.page });
      return;
    }
    if (n.role === 'Table') {
      units.push({ type: 'table', ...buildTable(n, texts), notes: [] });
      return;
    }
    if (n.role === 'Artifact') return;
    if ((BLOCK_ROLES.has(n.role) && n.role !== 'L') || !hasBlockDesc(n)) {
      const t = textOf(n, texts);
      if (t.text) units.push({ type: 'para', text: t.text, page: t.page });
      return;
    }
    n.kids.forEach(visit);
  };
  visit(root);
  // ตัดสารบัญ + ผูกเชิงอรรถ (ย่อหน้าที่ขึ้นต้น ¹ ² … ต่อจากตาราง) เข้ากับตาราง
  const out = [];
  let skipLevel = 0;
  for (const u of units) {
    if (u.type === 'heading') {
      if (skipLevel && u.level <= skipLevel) skipLevel = 0;
      if (TOC_RE.test(u.text)) {
        skipLevel = u.level;
        continue;
      }
    }
    if (skipLevel) continue;
    const last = out.at(-1);
    if (u.type === 'para' && last?.type === 'table' && NOTE_RE.test(u.text)) {
      last.notes.push(u.text);
      continue;
    }
    out.push(u);
  }
  return out;
}
