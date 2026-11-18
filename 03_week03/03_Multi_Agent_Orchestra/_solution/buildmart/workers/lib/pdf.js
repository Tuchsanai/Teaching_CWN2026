// workers/lib/pdf.js — ดึงข้อความจาก PDF ทีละหน้า + ตัดเป็น chunk (ใช้โดย rag-worker)
//
// ดึงข้อความ: ใช้ `pdftotext -bbox-layout` (poppler-utils ติดตั้งใน workers image) แบบ UTF-8
//   - ได้ทุกบรรทัด (line → word) พร้อมพิกัด → ใช้พิกัดหาว่าบรรทัดไหนถูกตัดเพราะสุดความกว้าง → ต่อกลับเป็นย่อหน้าเดียว
//     ไทย-ไทย ต่อชิดกัน (Chromium ตัดบรรทัดไทยตรงรอยคำโดยไม่มีช่องว่าง เช่น "ต้อง|ใช้" → "ต้องใช้")
//     กรณีอื่น (ตัวเลข/อังกฤษ) ต่อด้วยช่องว่าง
//   - 1 ย่อหน้า = 1 บรรทัดในข้อความผลลัพธ์ → ประโยคไม่ขาดกลางทาง (ดีต่อทั้ง embedding และการอ้างอิง)
//   - PDF ที่สร้างจาก Chromium + ฟอนต์ Sarabun มี ToUnicode ครบ → สระ/วรรณยุกต์ไทยออกมาถูกต้อง
// ตัด chunk: ~500 ตัวอักษร ซ้อนกัน 80 · ภาษาไทยไม่มีช่องว่างระหว่างคำ จึงไม่ตัดคำ (word segmentation)
//   แต่พยายามตัดที่ "ขึ้นบรรทัด" หรือ "ช่องว่าง" (ไทยใช้ช่องว่างคั่นวลี/ประโยค) ที่อยู่ใกล้ขอบ chunk ที่สุด
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { readStructTree, mcidBoxes, popplerWords, mcidTexts, structToUnits } from './pdf-struct.js';

const run = promisify(execFile);
const THAI = /[\u0E00-\u0E7F]/;

const decode = (s) =>
  s
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&amp;/g, '&');

/** ต่อบรรทัดของย่อหน้าเดียวกัน (ไทย-ไทย ชิดกัน · อื่น ๆ เว้นวรรค) */
export function joinLines(lines) {
  let out = '';
  for (const l of lines) {
    if (!l) continue;
    if (!out) out = l;
    else out += THAI.test(out.at(-1)) && THAI.test(l[0]) ? l : ` ${l}`;
  }
  return out;
}

/**
 * แปลงผล -bbox-layout (XHTML) → { title, pages: [ [ย่อหน้า, ...], ... ] }
 * poppler มักแยกแต่ละบรรทัดเป็น block ของตัวเอง จึงต่อบรรทัดกลับเป็นย่อหน้าด้วยพิกัด:
 *   บรรทัดนี้ยาวเกือบถึงขอบขวาของหน้า (ถูกตัดเพราะเต็มบรรทัด) + บรรทัดถัดไปชิดซ้ายตรงกัน + ระยะห่างแนวตั้งแคบ
 *   (ช่องตาราง/หัวข้อ/รายการ มีระยะห่างมากกว่า จึงไม่ถูกต่อ)
 */
export function parseBboxLayout(xml) {
  const title = decode(/<title>([\s\S]*?)<\/title>/.exec(xml)?.[1] || '').trim();
  const num = (attrs, k) => Number(new RegExp(`${k}="([0-9.]+)"`).exec(attrs)?.[1] || 0);
  const pages = [];
  for (const pm of xml.matchAll(/<page\b([^>]*)>([\s\S]*?)<\/page>/g)) {
    // หัว/ท้ายกระดาษ (running header/footer): บรรทัดในแถบบน 8% หรือแถบล่าง 4% ของความสูงหน้า → ข้าม
    const H = num(pm[1], 'height') || 842;
    const lines = [];
    for (const lm of pm[2].matchAll(/<line\b([^>]*)>([\s\S]*?)<\/line>/g)) {
      const text = [...lm[2].matchAll(/<word\b[^>]*>([\s\S]*?)<\/word>/g)]
        .map((w) => decode(w[1]).trim())
        .filter(Boolean)
        .join(' ');
      const y0 = num(lm[1], 'yMin');
      const y1 = num(lm[1], 'yMax');
      if (!text || y1 < 0.08 * H || y0 > 0.96 * H) continue;
      lines.push({ text, x0: num(lm[1], 'xMin'), x1: num(lm[1], 'xMax'), y0, y1 });
    }
    // แถวตาราง: บรรทัดที่อยู่ระดับเดียวกัน (y ใกล้กัน) และเรียงไปทางขวา → รวมเป็นบรรทัดเดียวคั่นด้วย " | "
    for (let i = lines.length - 1; i > 0; i--) {
      const a = lines[i - 1];
      const b = lines[i];
      if (Math.abs(a.y0 - b.y0) < 2 && b.x0 > a.x1) {
        a.text = `${a.text} | ${b.text}`;
        a.x1 = b.x1;
        lines.splice(i, 1);
      }
    }
    const right = Math.max(0, ...lines.map((l) => l.x1));
    const paras = [];
    let cur = null; // { parts:[], last: line, x0 }
    for (const l of lines) {
      const h = cur ? cur.last.y1 - cur.last.y0 : 0;
      const wrapped =
        cur &&
        cur.last.x1 >= right - 70 && // บรรทัดก่อนหน้าเต็มเกือบถึงขอบขวา
        Math.abs(l.x0 - cur.x0) < 3 && // ชิดซ้ายตรงกัน
        l.y0 - cur.last.y1 >= -1 &&
        l.y0 - cur.last.y1 < 0.3 * h; // ระยะห่างแนวตั้งแคบ (บรรทัดในย่อหน้าเดียวกัน)
      if (wrapped) {
        cur.parts.push(l.text);
        cur.last = l;
      } else {
        if (cur) paras.push(joinLines(cur.parts));
        cur = { parts: [l.text], last: l, x0: l.x0 };
      }
    }
    if (cur) paras.push(joinLines(cur.parts));
    pages.push(paras.map((t) => t.replace(/\s+/g, ' ').trim()).filter(Boolean));
  }
  return { title, pages };
}

/**
 * ดึงเนื้อหาจาก PDF (Buffer) → { pages, title, tagged, units }
 *   units = หน่วยเนื้อหาเรียงตามเอกสาร: {type:'heading'|'para'|'table', ..., page (เริ่ม 0)}
 *   - PDF มีโครงสร้าง (Tagged PDF) → ใช้ structure tree (lib/pdf-struct.js) ได้ตารางพร้อมหัวคอลัมน์
 *   - PDF ไม่มีโครงสร้าง (สแกน/โปรแกรมเก่า) → ย่อหน้าจากพิกัดบรรทัด (parseBboxLayout) แถวตารางคั่นด้วย " | "
 */
export async function extractDocument(bytes) {
  const dir = await mkdtemp(path.join(tmpdir(), 'bm-pdf-'));
  const file = path.join(dir, 'in.pdf');
  try {
    await writeFile(file, bytes);
    const { stdout: xml } = await run('pdftotext', ['-enc', 'UTF-8', '-bbox-layout', file, '-'], { maxBuffer: 64 << 20 });
    const { title, pages } = parseBboxLayout(xml);
    if (!pages.length) throw new Error('PDF ไม่มีหน้า หรืออ่านไม่ได้');
    try {
      const st = await readStructTree(bytes);
      if (st.root && st.root.kids.length) {
        const texts = mcidTexts(popplerWords(xml), await mcidBoxes(bytes));
        const units = structToUnits(st.root, texts);
        const chars = units.reduce((n, u) => n + (u.text?.length || 0) + (u.rows?.length || 0) * 20, 0);
        if (chars > 100) return { pages: pages.length, title, tagged: true, units };
      }
    } catch (e) {
      console.warn('[pdf] อ่านโครงสร้าง (Tagged PDF) ไม่สำเร็จ ใช้วิธีพิกัดแทน:', e.message);
    }
    const units = [];
    stripRepeated(pages).forEach((paras, p) => paras.forEach((text) => units.push({ type: 'para', text, page: p })));
    return { pages: pages.length, title, tagged: false, units };
  } finally {
    await rm(dir, { recursive: true, force: true }).catch(() => {});
  }
}

/** (ใช้กับ PDF ไม่มีโครงสร้าง / เข้ากันได้กับโค้ดเดิม) → { pages, title, texts: ['ข้อความหน้า 1', ...] } */
export async function extractPdf(bytes) {
  const d = await extractDocument(bytes);
  const texts = Array.from({ length: d.pages }, () => []);
  for (const u of d.units) texts[u.page ?? 0]?.push(u.text ?? [u.caption, ...(u.rows || []).map((r) => r.text)].join('\n'));
  return { pages: d.pages, title: d.title, texts: texts.map((t) => t.join('\n')) };
}

const MARKS = /[¹²³⁴⁵⁶⁷⁸⁹]/g;

/**
 * หน่วยเนื้อหา → chunk [{page (เริ่ม 1), content}]
 *   ย่อหน้า: รวมตามหัวข้อระดับ 2 (หัวข้อย่อยแทรกเป็นบรรทัด) → ตัด ~size ตัวอักษร ซ้อน overlap · บรรทัดแรกของ chunk = ชื่อหัวข้อ
 *   ตาราง : บรรทัดแรก = ชื่อตาราง (caption) แล้วตามด้วยแถว "หัวคอลัมน์: ค่า, ..." ทีละกลุ่มแถว (~size) ไม่ตัดกลางแถว
 *           + เชิงอรรถ (¹ ²) ที่แถวใน chunk อ้างถึง
 */
export function buildChunks(units, { size = 500, overlap = 80, tableSize = Math.round(size * 1.4) } = {}) {
  const chunks = [];
  let section = '';
  let buf = []; // [{text, page}]
  const flush = (force = false) => {
    if (!buf.length) return false;
    // ข้อความสั้นมาก (เช่น บรรทัดบนปก) ไม่แยกเป็น chunk เดี่ยว → ยกไปรวมกับหัวข้อถัดไป
    if (!force && !chunks.length && buf.reduce((n, b) => n + b.text.length, 0) < 120) return false;
    const prefix = section ? `${section}\n` : '';
    // ตำแหน่งเริ่มของแต่ละบรรทัด → หาเลขหน้าของ chunk
    const starts = [];
    let pos = 0;
    for (const b of buf) {
      starts.push({ pos, page: b.page });
      pos += b.text.length + 1;
    }
    const text = buf.map((b) => b.text).join('\n');
    let cursor = 0;
    for (const piece of chunkText(text, { size: Math.max(200, size - prefix.length), overlap })) {
      const at = text.indexOf(piece, Math.max(0, cursor - overlap - 5));
      if (at >= 0) cursor = at + 1;
      const s = [...starts].reverse().find((x) => x.pos <= Math.max(0, at));
      chunks.push({ page: (s?.page ?? buf[0].page ?? 0) + 1, content: prefix + piece });
    }
    buf = [];
    return true;
  };
  for (const u of units) {
    if (u.type === 'heading') {
      if (u.level <= 2) {
        if (!flush() && buf.length && section) buf.unshift({ text: section, page: buf[0].page });
        section = u.text;
      } else buf.push({ text: u.text, page: u.page });
      continue;
    }
    if (u.type === 'para') {
      buf.push({ text: u.text, page: u.page });
      continue;
    }
    if (u.type === 'table') {
      flush(true);
      const head = u.caption || (section ? `ตารางในหัวข้อ ${section}` : 'ตาราง');
      let rows = [];
      let len = 0;
      let part = 0;
      const emit = () => {
        if (!rows.length) return;
        const marks = new Set(rows.flatMap((r) => r.text.match(MARKS) || []));
        const notes = u.notes.filter((n) => {
          const m = n.match(/^[¹²³⁴⁵⁶⁷⁸⁹]/);
          return !m || marks.has(m[0]);
        });
        const content = [`${head}${part ? ' (ต่อ)' : ''}`, ...rows.map((r) => r.text), ...notes].join('\n');
        chunks.push({ page: (rows[0].page ?? u.page ?? 0) + 1, content });
        part++;
        rows = [];
        len = 0;
      };
      for (const r of u.rows) {
        if (rows.length && len + r.text.length > tableSize) emit();
        rows.push(r);
        len += r.text.length + 1;
      }
      emit();
    }
  }
  flush(true);
  return chunks;
}

/** block ที่ปรากฏทุกหน้า (หัว/ท้ายกระดาษ) หรือเป็นเลขหน้า → ตัดออก (การเทียบทุกหน้าทำเมื่อมี ≥ 2 หน้า) */
function stripRepeated(pages) {
  // ตัดเลขหน้า (ทั้งบรรทัดเดี่ยว "หน้า 1/2" และที่ต่อท้ายบรรทัดท้ายกระดาษ "... | หน้า 1/2")
  const pageNo = /\s*\|?\s*(หน้า|page)\s*\d+(\s*(\/|of)\s*\d+)?\s*$/i;
  const norm = pages.map((b) => b.map((l) => l.replace(pageNo, '').trim()).filter(Boolean));
  let drop = new Set();
  if (norm.length >= 2) {
    const sets = norm.map((b) => new Set(b));
    drop = new Set([...sets[0]].filter((l) => sets.every((s) => s.has(l))));
  }
  return norm.map((b) => b.filter((l) => !drop.has(l)));
}

/**
 * ตัดข้อความเป็น chunk ขนาด ~size ตัวอักษร ซ้อนกัน overlap ตัวอักษร
 * - หาจุดตัดที่ขึ้นบรรทัดก่อน (ช่วง 60%–100% ของ size) ถ้าไม่มีใช้ช่องว่าง ถ้าไม่มีอีกก็ตัดตรง size
 * - จุดเริ่ม chunk ถัดไป = end - overlap แล้วเลื่อนไปข้างหน้าให้ตรงช่องว่าง/ขึ้นบรรทัด (ไม่เริ่มกลางคำ)
 */
export function chunkText(text, { size = 500, overlap = 80 } = {}) {
  const t = text.trim();
  if (!t) return [];
  if (t.length <= size) return [t];
  const chunks = [];
  let start = 0;
  while (start < t.length) {
    let end = Math.min(start + size, t.length);
    if (end < t.length) {
      const minEnd = start + Math.floor(size * 0.6);
      const nl = t.lastIndexOf('\n', end);
      const sp = t.lastIndexOf(' ', end);
      if (nl > minEnd) end = nl;
      else if (sp > minEnd) end = sp;
    }
    const piece = t.slice(start, end).trim();
    if (piece) chunks.push(piece);
    if (end >= t.length) break;
    let next = Math.max(end - overlap, start + 1);
    // เลื่อนจุดเริ่มไปหลังช่องว่าง/ขึ้นบรรทัดถัดไป (ภายใน overlap) เพื่อไม่เริ่มกลางวลี
    const m = t.slice(next, end).search(/[\s]/);
    if (m >= 0) next = next + m + 1;
    start = next;
  }
  return chunks;
}
