// สร้าง PDF เอกสารสินค้า BuildMart จาก HTML ในโฟลเดอร์นี้ ด้วย headless Chromium (Playwright)
// ใช้: cd docs/docs-src && npm i && npx playwright install --only-shell chromium && node make_pdfs.mjs [ชื่อไฟล์ ...] [--png <dir>]
// ผลลัพธ์: ../BM-*.pdf (6 ไฟล์) และ ../../tests/fixtures/BM-PROMO-NOV.pdf
//
// สิ่งที่สคริปต์ทำ
//   1) ฟอนต์ Sarabun ฝังมาจาก fonts/ (OFL) → PDF เหมือนกันทุกเครื่อง และ copy/ค้นข้อความไทยได้
//   2) หัวกระดาษ BuildMart + ท้ายกระดาษ "หน้า X/Y" ด้วย headerTemplate/footerTemplate (เป็น artifact ไม่ปนเนื้อหา)
//   3) PDF แบบ "Tagged PDF" (tagged: true) → มีโครงสร้าง H1/H2/P/Table/TR/TH/TD + RowSpan/ColSpan ฝังในไฟล์
//      rag-worker อ่านโครงสร้างนี้เพื่อแปลงแถวตารางให้มีหัวคอลัมน์ติดไปด้วย
//   4) สารบัญอัตโนมัติ: สร้างรายการจาก h2/h3 → render รอบแรก → อ่านเลขหน้าของหัวข้อจาก structure tree → render รอบสอง
import { chromium } from 'playwright';
import { PDFDocument, PDFName, PDFDict, PDFArray, PDFRef, PDFNumber } from 'pdf-lib';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const here = path.dirname(fileURLToPath(import.meta.url));
const docsDir = path.resolve(here, '..');
const fixturesDir = path.resolve(here, '../../tests/fixtures');

const ALL = [
  ['BM-DS-CEM', docsDir],
  ['BM-DS-STL', docsDir],
  ['BM-DS-PNT', docsDir],
  ['BM-DS-TIL', docsDir],
  ['BM-DS-ELC-PIP', docsDir],
  ['BM-POLICY', docsDir],
  ['BM-PROMO-NOV', fixturesDir],
];
const args = process.argv.slice(2);
const pngIdx = args.indexOf('--png');
const pngDir = pngIdx >= 0 ? path.resolve(args[pngIdx + 1]) : null;
const only = args.filter((a, i) => !a.startsWith('--') && (pngIdx < 0 || i !== pngIdx + 1));
// ชื่ออื่นที่ไม่อยู่ในรายการ (เช่น _template) → เขียนไปที่ docs-src/_out/ (ไว้ลองหน้าตา ไม่ถูก ingest)
const jobs = only.length
  ? only.map((n) => ALL.find(([a]) => a === n) || [n, path.join(here, '_out')])
  : ALL;

// ---------- หัว/ท้ายกระดาษ (template ของ Chromium โหลดไฟล์ภายนอกไม่ได้ → ฝังฟอนต์เป็น base64) ----------
const b64 = (f) => fs.readFileSync(path.join(here, 'fonts', f)).toString('base64');
const FONT_CSS = `
@font-face{font-family:SarabunH;font-weight:400;src:url(data:font/ttf;base64,${b64('Sarabun-Regular.ttf')}) format('truetype')}
@font-face{font-family:SarabunH;font-weight:700;src:url(data:font/ttf;base64,${b64('Sarabun-Bold.ttf')}) format('truetype')}`;

function headerTemplate(meta) {
  return `<style>${FONT_CSS}
  .h{font-family:SarabunH,sans-serif;width:100%;margin:0 16mm;padding:0;display:flex;align-items:center;justify-content:space-between;
     -webkit-print-color-adjust:exact;border-bottom:1.2mm solid #F26B1D;padding-bottom:1.6mm;font-size:8pt;color:#3A3F44}
  .l{display:flex;align-items:center;gap:2.5mm}.logo{width:8mm;height:8mm;border-radius:1.6mm;background:#F26B1D;color:#fff;font-weight:700;
     font-size:9.5pt;display:flex;align-items:center;justify-content:center}.n{font-size:11pt;font-weight:700;line-height:1.1}
  .s{font-size:7pt;color:#6B6B6B}.r{text-align:right;line-height:1.35}.r b{color:#F26B1D;font-size:8.5pt}</style>
  <div class="h"><div class="l"><div class="logo">BM</div><div><div class="n">บ้านช่าง BuildMart</div>
  <div class="s">วัสดุก่อสร้างครบวงจร · ลาดกระบัง · บางนา · รังสิต</div></div></div>
  <div class="r"><b>${meta.doc}</b><br>${meta.title} · ${meta.rev}</div></div>`;
}
function footerTemplate(meta) {
  return `<style>${FONT_CSS}
  .f{font-family:SarabunH,sans-serif;width:100%;margin:0 16mm;border-top:0.3mm solid #D9D9D9;padding-top:1.2mm;font-size:7.5pt;color:#6B6B6B;
     display:flex;justify-content:space-between}</style>
  <div class="f"><span>${meta.doc} · ${meta.title} · บ้านช่าง BuildMart</span>
  <span>หน้า <span class="pageNumber"></span>/<span class="totalPages"></span></span></div>`;
}

// ---------- สารบัญ: สร้างรายการจาก h2/h3 (ใส่ id ให้) ----------
function buildToc() {
  const nav = document.querySelector('nav.toc');
  if (!nav) return [];
  const ol = nav.querySelector('ol') || nav.appendChild(document.createElement('ol'));
  ol.innerHTML = '';
  const heads = [...document.querySelectorAll('main h2, main h3')];
  heads.forEach((h, i) => {
    if (!h.id) h.id = `sec-${i + 1}`;
    const li = document.createElement('li');
    if (h.tagName === 'H3') li.className = 'sub';
    li.innerHTML = `<a href="#${h.id}"></a><span class="pg">–</span>`;
    li.querySelector('a').textContent = h.textContent.trim();
    ol.appendChild(li);
  });
  return heads.map((h) => h.tagName);
}
const setTocPages = (pages) =>
  document.querySelectorAll('nav.toc li .pg').forEach((s, i) => (s.textContent = pages[i] ?? '–'));

// ---------- อ่าน structure tree: หน้าแรกของแต่ละหัวข้อ H2/H3 ----------
async function headingPages(pdfBytes) {
  const doc = await PDFDocument.load(pdfBytes);
  const ctx = doc.context;
  const pageNo = new Map(doc.getPages().map((p, i) => [p.ref.toString(), i + 1]));
  const root = doc.catalog.lookup(PDFName.of('StructTreeRoot'));
  const out = []; // [{role, page}]
  const firstPage = (node, pg) => {
    node = node instanceof PDFRef ? ctx.lookup(node) : node;
    if (node instanceof PDFNumber) return pg ? pageNo.get(pg.toString()) : null;
    if (node instanceof PDFArray) {
      for (const k of node.asArray()) {
        const r = firstPage(k, pg);
        if (r) return r;
      }
      return null;
    }
    if (node instanceof PDFDict) {
      const p = node.get(PDFName.of('Pg')) || pg;
      if (node.get(PDFName.of('MCID'))) return pageNo.get(p.toString());
      const k = node.get(PDFName.of('K'));
      return k ? firstPage(k, p) : null;
    }
    return null;
  };
  const walk = (node) => {
    node = node instanceof PDFRef ? ctx.lookup(node) : node;
    if (node instanceof PDFArray) return node.asArray().forEach(walk);
    if (!(node instanceof PDFDict)) return;
    const s = node.get(PDFName.of('S'))?.toString();
    if (s === '/H2' || s === '/H3') out.push({ role: s.slice(1), page: firstPage(node, node.get(PDFName.of('Pg'))) });
    const k = node.get(PDFName.of('K'));
    if (k) walk(k);
  };
  if (root) walk(root.get(PDFName.of('K')));
  return { pages: doc.getPageCount(), heads: out };
}

for (const [, d] of jobs) fs.mkdirSync(d, { recursive: true });
if (pngDir) fs.mkdirSync(pngDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
for (const [name, outDir] of jobs) {
  await page.goto(pathToFileURL(path.join(here, `${name}.html`)).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const meta = await page.evaluate(() => ({ ...document.body.dataset }));
  const opts = {
    format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true, outline: true,
    displayHeaderFooter: true, headerTemplate: headerTemplate(meta), footerTemplate: footerTemplate(meta),
  };
  const roles = await page.evaluate(buildToc);
  let pdf = await page.pdf(opts);
  let info = await headingPages(pdf);
  if (roles.length) {
    // structure tree มี H2 ของหัว "สารบัญ" ด้วย (อยู่ใน nav ไม่ใช่ main) → ข้ามรายการที่อยู่ก่อนหัวข้อแรกของ main
    const heads = info.heads.slice(info.heads.length - roles.length);
    await page.evaluate(setTocPages, heads.map((h) => h.page));
    pdf = await page.pdf(opts);
    const again = await headingPages(pdf);
    const h2 = again.heads.slice(again.heads.length - roles.length).map((h) => h.page);
    if (h2.join() !== heads.map((h) => h.page).join()) {
      await page.evaluate(setTocPages, h2); // เลขหน้าขยับหลังเติมสารบัญ → เติมใหม่อีกรอบ
      pdf = await page.pdf(opts);
    }
    info = await headingPages(pdf);
  }
  const out = path.join(outDir, `${name}.pdf`);
  fs.writeFileSync(out, pdf);
  if (pngDir) {
    await page.emulateMedia({ media: 'print' });
    await page.screenshot({ path: path.join(pngDir, `${name}.png`), fullPage: true });
    await page.emulateMedia({ media: 'screen' });
  }
  console.log('wrote', path.relative(path.resolve(here, '../..'), out), `${info.pages} หน้า`, `${pdf.length} bytes`);
}
await browser.close();
