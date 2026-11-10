#!/usr/bin/env node
// web-builder verifier: เปิดไฟล์ HTML ด้วย Playwright (Chromium --no-sandbox) แล้วตรวจว่าใช้งานได้จริง
// Usage: node verify.cjs [path/to/index.html] [--steps steps.json] [--out dir]
// steps รันทั้งจอ desktop และ mobile (เริ่มจากข้อมูลว่างทั้งสองรอบ) แล้วตรวจ error และจอล้นซ้ำหลังรัน
// Exit code 0 = PASS, 1 = FAIL, 2 = setup error
'use strict';
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function parseArgs(argv) {
  const a = { file: 'site/index.html', steps: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--steps') a.steps = argv[++i];
    else if (v === '--out') a.out = argv[++i];
    else if (v === '-h' || v === '--help') a.help = true;
    else a.file = v;
  }
  return a;
}

function loadPlaywright() {
  const tried = [];
  const candidates = [];
  if (process.env.PLAYWRIGHT_PATH) candidates.push(process.env.PLAYWRIGHT_PATH);
  candidates.push('playwright', 'playwright-core');
  try {
    const root = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    candidates.push(
      path.join(root, '@playwright/mcp/node_modules/playwright'),
      path.join(root, 'playwright'),
      path.join(root, '@playwright/test/node_modules/playwright'),
      path.join(root, 'playwright-core'),
    );
  } catch (_) { /* npm not available */ }
  for (const c of candidates) {
    try { return require(c); } catch (e) { tried.push(c); }
  }
  console.error('ERROR: หา playwright ไม่เจอ ลองตั้ง PLAYWRIGHT_PATH=/path/to/node_modules/playwright\nTried:\n  ' + tried.join('\n  '));
  process.exit(2);
}

// ข้อความยาวไม่มีช่องว่าง ใช้ทดสอบว่าเนื้อหาที่ผู้ใช้พิมพ์ไม่ดันหน้าจอให้ล้น
const LONG = 'ก'.repeat(60) + 'W'.repeat(60);

async function runSteps(page, steps, fails, tag) {
  for (const [i, s] of steps.entries()) {
    const label = `${tag} step ${i + 1} ${s.action}${s.selector ? ' ' + s.selector : ''}${s.value !== undefined && s.action.startsWith('expect') ? ' "' + String(s.value).slice(0, 40) + '"' : ''}`;
    try {
      const loc = s.selector ? page.locator(s.selector).first() : null;
      switch (s.action) {
        case 'click': await loc.click({ timeout: 3000 }); break;
        case 'fill': await loc.fill(String(s.value ?? ''), { timeout: 3000 }); break;
        case 'press': await (loc ? loc.press(s.value) : page.keyboard.press(s.value)); break;
        case 'select': await loc.selectOption(s.value, { timeout: 3000 }); break;
        case 'wait': await page.waitForTimeout(Number(s.value) || 300); break;
        case 'reload': await page.reload({ waitUntil: 'load' }); await page.waitForTimeout(300); break;
        case 'fillLong': await loc.fill(LONG, { timeout: 3000 }); break;
        case 'expectInvalid': {
          // ช่องที่กรอกผิด: ต้องมี aria-invalid="true" และข้อความเตือนต้องผูกกับช่อง หรืออยู่ใน role=alert / aria-live
          const r = await loc.evaluate(e => {
            const ids = ((e.getAttribute('aria-describedby') || '') + ' ' + (e.getAttribute('aria-errormessage') || '')).split(/\s+/).filter(Boolean);
            const tied = ids.map(i => document.getElementById(i)).filter(Boolean).some(n => n.innerText.trim());
            const live = [...document.querySelectorAll('[role=alert],[role=status],[aria-live=polite],[aria-live=assertive]')].some(n => n.innerText.trim());
            return { inv: e.getAttribute('aria-invalid') === 'true', said: tied || live };
          });
          if (!r.inv) throw new Error('ช่องนี้ไม่มี aria-invalid="true" ตอนกรอกผิด');
          if (!r.said) throw new Error('ข้อความเตือนไม่ได้ผูกกับช่อง (aria-describedby) และไม่อยู่ใน role=alert / aria-live');
          break;
        }
        case 'expectBodyText': case 'expectNoBodyText': {
          const t = await page.evaluate(() => document.body.innerText);
          const has = t.includes(String(s.value));
          if (has !== (s.action === 'expectBodyText')) throw new Error(`page text ${has ? 'contains' : 'does not contain'} "${s.value}"`);
          break;
        }
        case 'expectVisible': await loc.waitFor({ state: 'visible', timeout: 3000 }); break;
        case 'expectHidden': await loc.waitFor({ state: 'hidden', timeout: 3000 }); break;
        case 'expectText': {
          const t = await loc.innerText({ timeout: 3000 });
          if (!t.includes(String(s.value))) throw new Error(`text "${t.slice(0, 80)}" does not contain "${s.value}"`);
          break;
        }
        case 'expectCount': {
          const n = await page.locator(s.selector).count();
          if (n !== Number(s.value)) throw new Error(`count ${n} != ${s.value}`);
          break;
        }
        case 'eval': {
          const r = await page.evaluate(s.value);
          if (!r) throw new Error(`expression returned falsy: ${s.value}`);
          break;
        }
        default: throw new Error('unknown action');
      }
      console.log(`  ok   ${label}`);
    } catch (e) {
      fails.push(`${label}: ${e.message.split('\n')[0]}`);
      console.log(`  FAIL ${label}: ${e.message.split('\n')[0]}`);
    }
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log('Usage: node verify.cjs [site/index.html] [--steps steps.json] [--out dir]');
    return 0;
  }
  const file = path.resolve(args.file);
  if (!fs.existsSync(file)) { console.error(`ERROR: ไม่พบไฟล์ ${file}`); return 2; }
  const outDir = path.resolve(args.out || path.join(path.dirname(file), '..', '.verify'));
  fs.mkdirSync(outDir, { recursive: true });
  const steps = args.steps ? JSON.parse(fs.readFileSync(args.steps, 'utf8')) : [];

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const fails = [];
  const warns = [];
  const url = 'file://' + file;

  try {
    for (const vp of [{ name: 'desktop', width: 1280, height: 800 }, { name: 'mobile', width: 375, height: 740 }]) {
      console.log(`\n[${vp.name} ${vp.width}x${vp.height}]`);
      const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const page = await ctx.newPage();
      const errs = [];
      page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
      page.on('pageerror', e => errs.push('pageerror: ' + e.message));
      page.on('requestfailed', r => {
        const u = r.url();
        // external resources may be offline; local missing files are real errors
        (u.startsWith('file:') ? errs : warns).push(`requestfailed: ${u} (${r.failure()?.errorText})`);
      });

      await page.goto(url, { waitUntil: 'load', timeout: 15000 });
      await page.waitForTimeout(500);

      const info = await page.evaluate(() => {
        const doc = document.documentElement;
        const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
        const badAnchors = [...document.querySelectorAll('a[href^="#"]')]
          .map(a => a.getAttribute('href')).filter(h => h.length > 1 && !ids.has(decodeURIComponent(h.slice(1))));
        const brokenImgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src);
        const noAlt = [...document.images].filter(i => !i.hasAttribute('alt')).length;
        return {
          title: document.title,
          lang: doc.getAttribute('lang'),
          viewportMeta: !!document.querySelector('meta[name="viewport"]'),
          textLen: (document.body?.innerText || '').trim().length,
          overflowX: doc.scrollWidth - doc.clientWidth,
          badAnchors, brokenImgs, noAlt,
          h1: document.querySelectorAll('h1').length,
          textInputs: document.querySelectorAll('input:not([type]), input[type=text], input[type=search], textarea').length,
          storage: (() => { try { return localStorage.length; } catch (e) { return 0; } })(),
        };
      });

      const shot = path.join(outDir, `${vp.name}.png`);
      await page.screenshot({ path: shot, fullPage: true });
      console.log(`  title="${info.title}" text=${info.textLen} chars, h1=${info.h1}, screenshot=${shot}`);

      const tag = `[${vp.name}]`;
      errs.forEach(e => fails.push(`${tag} ${e}`));
      if (info.textLen < 20) fails.push(`${tag} page looks blank (text ${info.textLen} chars)`);
      if (info.overflowX > 1) fails.push(`${tag} horizontal overflow ${info.overflowX}px`);
      info.badAnchors.forEach(h => fails.push(`${tag} anchor ${h} has no matching id`));
      info.brokenImgs.forEach(s => fails.push(`${tag} broken image ${s}`));
      if (vp.name === 'desktop') {
        if (!info.title) warns.push('missing <title>');
        if (!info.lang) warns.push('missing <html lang>');
        if (!info.viewportMeta) fails.push('missing <meta name="viewport">');
        if (info.h1 !== 1) warns.push(`expected exactly one <h1>, found ${info.h1}`);
        if (info.noAlt) warns.push(`${info.noAlt} <img> without alt`);
      }
      if (steps.length) {
        // ทุก viewport เริ่มจากข้อมูลว่าง (context ใหม่) แล้วรัน steps ชุดเดียวกัน
        console.log('  interaction steps:');
        await runSteps(page, steps, fails, tag);
        if (errs.length) errs.splice(0).forEach(e => fails.push(`${tag} after steps: ${e}`));
        const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        if (over > 1) fails.push(`${tag} horizontal overflow ${over}px after steps (เนื้อหาที่เพิ่มเข้ามาดันจอให้ล้น → ใส่ overflow-wrap:anywhere / min-width:0 ให้กล่องที่แสดงข้อความของผู้ใช้)`);
        await page.screenshot({ path: path.join(outDir, `${vp.name}-after-steps.png`), fullPage: true });
      }
      if (vp.name === 'mobile' && steps.length && !steps.some(s => s.action === 'fillLong') && info.textInputs > 0)
        warns.push('steps ไม่มี fillLong ทั้งที่หน้ามีช่องให้ผู้ใช้พิมพ์ → เพิ่ม step fillLong แล้วส่งฟอร์ม เพื่อตรวจว่าข้อความยาวไม่ทำให้จอมือถือล้น');
      if (vp.name === 'mobile' && steps.length && !steps.some(s => s.action === 'expectInvalid') && info.textInputs > 0)
        warns.push('หน้ามีช่องกรอก แต่ steps ไม่มี expectInvalid → ทำกรณีกรอกผิด 1 ครั้ง แล้วใส่ step expectInvalid ที่ช่องนั้น เพื่อตรวจ aria-invalid และการประกาศข้อความเตือน');
      if (vp.name === 'mobile' && steps.length && !steps.some(s => s.action === 'reload') && (await page.evaluate(() => { try { return localStorage.length; } catch (e) { return 0; } })) > 0)
        warns.push('หน้าใช้ localStorage แต่ steps ไม่มี reload → เพิ่ม step reload แล้ว expect ซ้ำ เพื่อตรวจว่าข้อมูลยังอยู่');
      await ctx.close();
    }
  } finally {
    await browser.close();
  }

  console.log('\n=== RESULT ===');
  warns.forEach(w => console.log('WARN ' + w));
  fails.forEach(f => console.log('FAIL ' + f));
  if (!steps.length) console.log('WARN ไม่ได้ส่ง --steps: ตรวจแค่ว่าหน้าเปิดได้ ยังไม่ได้ตรวจว่าทำงานตาม brief');
  console.log(fails.length ? `FAIL (${fails.length} problem(s))` : 'PASS');
  return fails.length ? 1 : 0;
}

main().then(c => process.exit(c), e => { console.error('ERROR:', e.message); process.exit(2); });
