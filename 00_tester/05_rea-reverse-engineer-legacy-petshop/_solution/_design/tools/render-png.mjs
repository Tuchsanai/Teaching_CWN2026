#!/usr/bin/env node
// render-png.mjs · เรนเดอร์ไดอะแกรม HTML → PNG แบบ headless (สไตล์บ้านของคอร์ส 00_tester)
//
// ใช้:   node render-png.mjs <in.html> <out.png> [--dsf 2] [--width 1280]
// ค่าเริ่มต้น: กว้าง 1280 CSS px · deviceScaleFactor 2 (ไฟล์จริง 2560 px) · สูงเต็มหน้า (full page)
// ฟอนต์: HTML ต้องลิงก์ Noto Sans Thai จาก Google Fonts · สคริปต์รอ document.fonts.ready
//        ถ้าโหลดไม่ได้ (ออฟไลน์) จะเตือนและใช้ฟอนต์สำรองใน CSS (Leelawadee UI / Tahoma)
// ขนาดไฟล์: ถ้า > 600 KB จะเรนเดอร์ใหม่ที่ DSF 1.5 อัตโนมัติ และพิมพ์บอก
//
// หา playwright จาก: env PLAYWRIGHT_DIR → node_modules ข้างสคริปต์ → C:/t/work/a9/node_modules
// (ติดตั้ง: npm i playwright@1.63.0 ในโฟลเดอร์ทำงานนอก repo · ไม่ commit node_modules ลงบทเรียน)

import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const LIMIT = 600 * 1024;
const here = path.dirname(fileURLToPath(import.meta.url));

function loadPlaywright() {
  const bases = [process.env.PLAYWRIGHT_DIR, here, 'C:/t/work/a9'].filter(Boolean);
  for (const b of bases) {
    try {
      return createRequire(path.join(path.resolve(b), 'noop.js'))('playwright');
    } catch { /* ลองที่ถัดไป */ }
  }
  console.error('หา playwright ไม่เจอ · ติดตั้งด้วย: npm i playwright@1.63.0 แล้วตั้ง PLAYWRIGHT_DIR=<โฟลเดอร์นั้น>');
  process.exit(2);
}

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(name);
  if (i < 0) return def;
  const v = Number(args[i + 1]);
  args.splice(i, 2);
  return v;
};
let dsf = opt('--dsf', 2);
const width = opt('--width', 1280);
const [inHtml, outPng] = args;
if (!inHtml || !outPng) {
  console.error('ใช้: node render-png.mjs <in.html> <out.png> [--dsf 2] [--width 1280]');
  process.exit(1);
}

const { chromium } = loadPlaywright();
const browser = await chromium.launch({ headless: true });

async function render(scale) {
  const ctx = await browser.newContext({ viewport: { width, height: 800 }, deviceScaleFactor: scale });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(path.resolve(inHtml)).href, { waitUntil: 'networkidle', timeout: 30000 })
    .catch(() => page.waitForLoadState('load'));
  await page.evaluate(() => document.fonts.ready);
  const thaiOk = await page.evaluate(() => document.fonts.check('700 20px "Noto Sans Thai"'));
  if (!thaiOk) console.warn('⚠️  โหลด Noto Sans Thai ไม่ได้ · ใช้ฟอนต์สำรองแทน (ตรวจภาพอีกครั้ง)');
  // เตือนถ้ามีอะไรล้นแนวนอน
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (overflow > 0) console.warn(`⚠️  เนื้อหาล้นแนวนอน ${overflow}px`);
  fs.mkdirSync(path.dirname(path.resolve(outPng)), { recursive: true });
  await page.screenshot({ path: outPng, fullPage: true });
  await ctx.close();
  return fs.statSync(outPng).size;
}

let size = await render(dsf);
if (size > LIMIT && dsf > 1.5) {
  console.warn(`ไฟล์ ${(size / 1024).toFixed(0)} KB > 600 KB ที่ DSF ${dsf} → เรนเดอร์ใหม่ที่ DSF 1.5`);
  dsf = 1.5;
  size = await render(dsf);
}
await browser.close();
const kb = (size / 1024).toFixed(0);
console.log(`${outPng} · ${Math.round(width * dsf)} px กว้าง · DSF ${dsf} · ${kb} KB${size > LIMIT ? ' ⚠️ ยังเกิน 600 KB' : ''}`);
