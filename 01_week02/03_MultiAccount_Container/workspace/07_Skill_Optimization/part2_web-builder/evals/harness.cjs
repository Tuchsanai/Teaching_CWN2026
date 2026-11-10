// harness.cjs <sandbox> <task.json> : เปิด ./site/index.html ด้วย Playwright แล้วตรวจทีละข้อ (ชุดตรวจที่เอเจนต์ไม่เคยเห็น)
// ผล: JSON {score, checks:[{id, pass, note}]} · ข้อ g_* ตรวจทุกโจทย์ · ข้อ f_* มาจาก checks/<task>.cjs
const path = require('path'), fs = require('fs'), cp = require('child_process');
function loadPlaywright() {
  try { return require('playwright'); } catch (e) {}
  const g = cp.execSync('npm root -g').toString().trim();
  for (const p of ['playwright', '@playwright/mcp/node_modules/playwright', '@playwright/test/node_modules/playwright'])
    if (fs.existsSync(path.join(g, p))) return require(path.join(g, p));
  throw new Error('ไม่พบ playwright');
}
(async () => {
  const [sb, taskFile] = process.argv.slice(2);
  const task = JSON.parse(fs.readFileSync(taskFile, 'utf8'));
  const C = [];
  const chk = (id, pass, note = '') => C.push({ id, pass: !!pass, note: String(note).slice(0, 200) });
  const done = () => { console.log(JSON.stringify({ score: +(C.filter(c => c.pass).length / C.length).toFixed(4), checks: C })); };
  let spec = require(path.join(__dirname, 'checks', (task.kind || task.id) + '.cjs'));
  if (spec.make) spec = spec.make(task.cfg);
  const index = path.join(sb, 'site', 'index.html');
  if (!fs.existsSync(index)) {
    for (const id of ['g_clean', 'g_offline', 'g_mobile', 'g_a11y', 'g_storage', 'g_keyboard', ...(spec.addText ? ['g_escape', 'g_longtext'] : []), 'a_contrast', 'a_status', 'a_landmark', 'a_focus', 'a_reflow', 'a_target', ...(spec.invalid ? ['a_invalid'] : []), ...spec.ids]) chk(id, false, 'ไม่มี site/index.html');
    return done();
  }
  const pw = loadPlaywright();
  const browser = await pw.chromium.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
  const errors = [], external = [], failed = [];
  await ctx.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')) return r.continue();
    external.push(u); return r.abort();
  });
  const wire = p => {
    p.on('pageerror', e => errors.push('pageerror: ' + e.message));
    p.on('console', m => { if (m.type() === 'error' && !/net::ERR_FAILED|ERR_BLOCKED/.test(m.text())) errors.push('console: ' + m.text()); });
    p.on('requestfailed', q => { if (q.url().startsWith('file:')) failed.push(q.url().split('/').pop()); });
    p.on('dialog', d => d.dismiss().catch(() => {}));
    p.setDefaultTimeout(2500);
  };
  const url = 'file://' + index;
  const page = await ctx.newPage(); wire(page);
  await page.goto(url); await page.waitForTimeout(300);
  // ---- ตัวช่วยของชุดตรวจ
  const mk = page => { const h = {
    page, url,
    text: async () => (await page.evaluate(() => document.body.innerText)).replace(/ /g, ' '),
    has: async re => re.test(await h.text()),
    reload: async () => { await page.reload(); await page.waitForTimeout(300); },
    settle: () => page.waitForTimeout(150),
    // กดปุ่ม label ของการ์ดที่มีชื่อ name (การ์ด = กล่องใหญ่สุดที่มีปุ่ม label ปุ่มเดียว)
    clickInCard: async (name, label) => {
      const ok = await page.evaluate(([name, label]) => {
        const btns = [...document.querySelectorAll('button, [role=button], input[type=button]')]
          .filter(b => ((b.innerText || b.value || '') + ' ' + (b.getAttribute('aria-label') || '')).includes(label) && b.offsetParent !== null);
        for (const b of btns) {
          let card = b;
          while (card.parentElement && btns.filter(x => card.parentElement.contains(x)).length === 1) card = card.parentElement;
          if (card.innerText.includes(name)) { b.click(); return true; }
        }
        return false;
      }, [name, label]);
      await page.waitForTimeout(120);
      return ok;
    },
    button: name => page.getByRole('button', { name, exact: true }).first(),
    run: async (id, fn) => { try { const r = await fn(); chk(id, r === undefined ? true : r === true, r === true || r === undefined ? '' : r); } catch (e) { chk(id, false, e.message.split('\n')[0]); } },
  }; return h; };
  const h = mk(page);
  const fresh = async (opts, init) => { const o = Object.assign({ locale: 'th-TH', timezoneId: 'Asia/Bangkok' }, opts); delete o.count; const c = await browser.newContext(o);
    await c.route('**/*', r => /^(file|data|blob):/.test(r.request().url()) ? r.continue() : r.abort());
    if (init) await c.addInitScript(init.fn, init.arg);
    const p = await c.newPage(); const errs = []; p.on('pageerror', e => { errs.push(e.message); if (opts && opts.count) errors.push('pageerror: ' + e.message); }); p.on('dialog', d => d.dismiss().catch(() => {}));
    p.setDefaultTimeout(2500); await p.goto(url); await p.waitForTimeout(300); return { c, p, errs }; };
  // หน้าใหม่ที่ข้อมูลว่าง สำหรับข้อตรวจที่ต้องเริ่มจากศูนย์ (ข้อหนึ่งพลาดจะไม่ลามไปข้ออื่น)
  h.fresh = async () => mk((await fresh({ viewport: { width: 1280, height: 800 }, count: true })).p);
  // ---- ข้อเฉพาะของโจทย์
  try { await spec.run(h); } catch (e) { errors.push('ชุดตรวจหยุดกลางทาง: ' + e.message.split('\n')[0]); }
  for (const id of spec.ids) if (!C.find(c => c.id === id)) chk(id, false, 'ไม่ได้ตรวจ (ขั้นก่อนหน้าล้ม)');
  // ---- ข้อร่วมทุกโจทย์
  const a11y = await page.evaluate(() => {
    const bad = [];
    if (!document.documentElement.lang) bad.push('html ไม่มี lang');
    if (!document.title.trim()) bad.push('ไม่มี title');
    if (!document.querySelector('meta[name=viewport]')) bad.push('ไม่มี meta viewport');
    if (document.querySelectorAll('h1').length !== 1) bad.push('h1 ' + document.querySelectorAll('h1').length + ' ตัว');
    for (const i of document.querySelectorAll('img')) if (!i.hasAttribute('alt')) { bad.push('img ไม่มี alt'); break; }
    for (const i of document.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=submit]), select, textarea')) {
      const lab = i.labels && i.labels.length || i.getAttribute('aria-label') || i.getAttribute('aria-labelledby');
      if (!lab) { bad.push('ช่องกรอกไม่มี label: ' + (i.id || i.name || i.placeholder || i.type)); break; }
    }
    for (const b of document.querySelectorAll('button')) if (!(b.innerText.trim() || b.getAttribute('aria-label'))) { bad.push('ปุ่มไม่มีชื่อ'); break; }
    return bad;
  });
  chk('g_a11y', a11y.length === 0, a11y.join(' · '));
  // ---- ความทนทาน (ไม่ได้เขียนไว้ใน brief ทีละข้อ แต่เว็บที่ใช้งานจริงต้องผ่าน)
  const keys = await page.evaluate(() => Object.keys(localStorage));
  const sub = mk;
  // g_storage: ข้อมูลใน localStorage เสีย (JSON พัง / ชนิดผิด) หน้าเว็บต้องยังเปิดและใช้งานได้
  try {
    const bad = [];
    for (const val of ['{oops', '{"a":1}', '5']) {
      const f = await fresh({ viewport: { width: 1280, height: 800 } }, { fn: ([ks, v]) => { try { for (const k of ks) localStorage.setItem(k, v); } catch (e) {} }, arg: [keys, val] });
      const alive = await f.p.locator('h1').first().isVisible().catch(() => false);
      let usable = true;
      if (spec.smoke) usable = await spec.smoke(sub(f.p)).catch(() => false);
      if (f.errs.length || !alive || !usable) bad.push(`ค่า ${val}: ${f.errs[0] || (alive ? 'ใช้งานต่อไม่ได้' : 'หน้าไม่ขึ้น')}`);
      await f.c.close();
    }
    chk('g_storage', keys.length > 0 && bad.length === 0, keys.length ? bad.join(' | ') : 'ไม่ได้ใช้ localStorage');
  } catch (e) { chk('g_storage', false, e.message.split('\n')[0]); }
  // g_keyboard: ทุกอย่างที่กดได้ต้องโฟกัสด้วยคีย์บอร์ดได้ (เป็น button/a/input จริง หรือมี tabindex)
  const kb = await page.evaluate(() => {
    const bad = [];
    for (const e of document.querySelectorAll('body *')) {
      if (!e.offsetParent || getComputedStyle(e).cursor !== 'pointer') continue;
      if (e.closest('button, a[href], input, select, textarea, label, summary, [tabindex]:not([tabindex="-1"])')) continue;
      bad.push(e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : ''));
    }
    return [...new Set(bad)];
  });
  chk('g_keyboard', kb.length === 0, kb.length ? 'กดได้แต่โฟกัสด้วยคีย์บอร์ดไม่ได้: ' + kb.slice(0, 4).join(', ') : '');
  if (spec.addText) {
    // g_escape: ข้อความที่ผู้ใช้พิมพ์ต้องแสดงเป็นตัวหนังสือ ไม่ถูกตีความเป็น HTML
    try {
      const f = await fresh({ viewport: { width: 1280, height: 800 } });
      const evil = '<img src=x onerror="window.__xss=1"><b>หนา</b>';
      await spec.addText(sub(f.p), evil); await f.p.waitForTimeout(400);
      const r = await f.p.evaluate(() => ({ x: window.__xss === 1, t: document.body.innerText, img: document.querySelectorAll('img[src="x"]').length }));
      chk('g_escape', !r.x && r.img === 0 && r.t.includes('<b>หนา</b>'), r.x || r.img ? 'ข้อความของผู้ใช้ถูกแทรกเป็น HTML (innerHTML)' : 'ไม่แสดงข้อความตามที่พิมพ์');
      await f.c.close();
    } catch (e) { chk('g_escape', false, e.message.split('\n')[0]); }
    // g_longtext: ข้อความยาวไม่มีช่องว่าง ต้องไม่ดันหน้าจอมือถือให้ล้น
    try {
      const f = await fresh({ viewport: { width: 375, height: 740 } });
      await spec.addText(sub(f.p), 'ก'.repeat(70) + 'A'.repeat(70)); await f.p.waitForTimeout(400);
      const r = await f.p.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth, t: document.body.innerText.includes('ก'.repeat(30)) }));   // เว็บที่จำกัดความยาว (maxlength) ตัดท้ายข้อความได้ จึงดูแค่ 30 ตัวแรก
      chk('g_longtext', r.t && r.sw <= r.iw + 1, r.t ? `จอ 375px ล้นเป็น ${r.sw}px หลังเพิ่มข้อความยาว` : 'เพิ่มข้อความยาวไม่ได้');
      await f.c.close();
    } catch (e) { chk('g_longtext', false, e.message.split('\n')[0]); }
  }
  // ---- การเข้าถึงได้ตาม WCAG 2.2 AA (ตรวจด้วยโค้ด ไม่ใช้ AI ตัดสิน)
  // a_contrast (1.4.3): ตัวหนังสือทุกชิ้นที่มองเห็น ต้องตัดกับพื้นหลัง ≥ 4.5:1 (ตัวใหญ่ ≥ 3:1)
  const contrast = () => page.evaluate(() => {
    const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
    const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
    const over = (t, b) => ({ r: t.r * t.a + b.r * (1 - t.a), g: t.g * t.a + b.g * (1 - t.a), b: t.b * t.a + b.b * (1 - t.a), a: 1 });
    const bgOf = e => { const st = []; for (let n = e; n; n = n.parentElement) { const s = getComputedStyle(n); if (s.backgroundImage !== 'none') return null; const c = parse(s.backgroundColor); if (c && c.a > 0) { st.push(c); if (c.a === 1) break; } }
      let bg = { r: 255, g: 255, b: 255, a: 1 }; for (const c of st.reverse()) bg = over(c, bg); return bg; };
    const bad = [];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const txt = n.textContent.trim(); const e = n.parentElement;
      if (!txt || !e || !e.offsetParent || e.closest('[disabled], script, style, option')) continue;
      const s = getComputedStyle(e); if (s.visibility === 'hidden' || +s.opacity === 0) continue;
      const bg = bgOf(e); if (!bg) continue;
      let fg = parse(s.color); if (!fg) continue; fg = over(fg, bg);
      const L1 = lum(fg), L2 = lum(bg), r = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const px = parseFloat(s.fontSize), big = px >= 24 || (px >= 18.66 && +s.fontWeight >= 700);
      if (r < (big ? 3 : 4.5) - 0.01) bad.push(`"${txt.slice(0, 18)}" ${r.toFixed(2)}:1`);
    }
    return [...new Set(bad)];
  });
  try { const lo = await contrast(); chk('a_contrast', lo.length === 0, lo.slice(0, 3).join(' · ')); } catch (e) { chk('a_contrast', false, e.message.split('\n')[0]); }
  // a_status (4.1.3): ข้อความแจ้งผล/แจ้งเตือนที่เปลี่ยนเองต้องอยู่ในพื้นที่ที่โปรแกรมอ่านจอประกาศได้
  const live = await page.evaluate(() => document.querySelectorAll('[role=alert], [role=status], [aria-live=polite], [aria-live=assertive], output').length);
  chk('a_status', live > 0, live ? '' : 'ไม่มี role=status / role=alert / aria-live สำหรับข้อความที่เปลี่ยนเอง');
  // a_landmark (1.3.1 · 2.4.1): มี <main> หนึ่งตัว และหัวเรื่องไม่ข้ามระดับ
  const lm = await page.evaluate(() => { const bad = []; const m = document.querySelectorAll('main, [role=main]').length; if (m !== 1) bad.push('main ' + m + ' ตัว');
    let prev = 0; for (const hd of document.querySelectorAll('h1,h2,h3,h4,h5,h6')) { const l = +hd.tagName[1]; if (prev && l > prev + 1) { bad.push(`หัวเรื่องข้ามจาก h${prev} ไป h${l}`); break; } prev = l; } return bad; });
  chk('a_landmark', lm.length === 0, lm.join(' · '));
  // a_focus (2.4.7): กด Tab แล้วต้องเห็นว่าโฟกัสอยู่ที่ไหน
  try {
    const f = await fresh({ viewport: { width: 1280, height: 800 } });
    const noRing = [];
    for (let k = 0; k < 8; k++) {
      await f.p.keyboard.press('Tab');
      const r = await f.p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null;
        if (/^(date|time|datetime-local|month|week)$/.test(e.type)) return null;   // เบราว์เซอร์วาดวงโฟกัสที่ช่องย่อยข้างใน อ่านจากตัว input ไม่ได้
        const s = getComputedStyle(e); const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none';
        return { ring, name: e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') }; });
      if (r && !r.ring) noRing.push(r.name);
    }
    chk('a_focus', noRing.length === 0, noRing.length ? 'โฟกัสแล้วไม่มี outline/box-shadow: ' + [...new Set(noRing)].slice(0, 3).join(', ') : '');
    await f.c.close();
  } catch (e) { chk('a_focus', false, e.message.split('\n')[0]); }
  // a_reflow (1.4.10) + a_target (2.5.8): จอกว้าง 320px ไม่ต้องเลื่อนแนวนอน · เป้ากดทุกอันไม่เล็กกว่า 24×24px
  try {
    const f = await fresh({ viewport: { width: 320, height: 640 } });
    const r = await f.p.evaluate(() => { const small = [];
      for (const e of document.querySelectorAll('button, a[href], select, input:not([type=hidden])')) { if (!e.offsetParent) continue;
        let b = e.getBoundingClientRect();
        if (/^(checkbox|radio)$/.test(e.type)) { const l = e.closest('label') || (e.labels && e.labels[0]); if (l) { const lb = l.getBoundingClientRect(); b = { width: Math.max(b.width, lb.width), height: Math.max(b.height, lb.height) }; } }
        if (b.width < 23.5 || b.height < 23.5) small.push(`${e.tagName.toLowerCase()}${e.type ? '[' + e.type + ']' : ''} ${Math.round(b.width)}×${Math.round(b.height)}`); }
      return { sw: document.documentElement.scrollWidth, iw: window.innerWidth, small: [...new Set(small)] }; });
    chk('a_reflow', r.sw <= r.iw + 1, `จอ 320px: scrollWidth ${r.sw}`);
    chk('a_target', r.small.length === 0, r.small.slice(0, 3).join(' · '));
    await f.c.close();
  } catch (e) { chk('a_reflow', false, e.message.split('\n')[0]); chk('a_target', false, 'ไม่ได้ตรวจ'); }
  // a_invalid (3.3.1): ช่องที่กรอกผิดต้องมี aria-invalid="true" และข้อความเตือนต้องผูกกับช่อง (aria-describedby / aria-errormessage)
  // หรืออยู่ในพื้นที่ที่ประกาศเอง (role=alert / aria-live) อย่างใดอย่างหนึ่ง
  if (spec.invalid) {
    try {
      const f = await fresh({ viewport: { width: 1280, height: 800 } });
      const loc = await spec.invalid(mk(f.p)); await f.p.waitForTimeout(300);
      const r = await loc.evaluate(e => { const ids = ((e.getAttribute('aria-describedby') || '') + ' ' + (e.getAttribute('aria-errormessage') || '')).split(/\s+/).filter(Boolean);
        const tied = ids.map(i => document.getElementById(i)).filter(Boolean).some(x => x.innerText.trim().length > 0);
        const live = [...document.querySelectorAll('[role=alert], [aria-live=assertive], [aria-live=polite], [role=status]')].some(x => x.innerText.trim().length > 0);
        return { inv: e.getAttribute('aria-invalid') === 'true', said: tied || live }; });
      chk('a_invalid', r.inv && r.said, [r.inv ? '' : 'ช่องที่ผิดไม่มี aria-invalid="true"', r.said ? '' : 'ข้อความเตือนไม่ได้ผูกกับช่อง และไม่อยู่ใน role=alert / aria-live'].filter(Boolean).join(' · '));
      await f.c.close();
    } catch (e) { chk('a_invalid', false, e.message.split('\n')[0]); }
  }
  const m = await ctx.newPage(); wire(m);
  await m.setViewportSize({ width: 375, height: 740 });
  await m.goto(url); await m.waitForTimeout(300);
  const ov = await m.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth,
    small: [...document.querySelectorAll('button, a, input, select')].filter(e => e.offsetParent && e.getBoundingClientRect().right > window.innerWidth + 1).length }));
  chk('g_mobile', ov.sw <= ov.iw + 1 && ov.small === 0, `จอ 375px: scrollWidth ${ov.sw} · ปุ่ม/ช่องที่ล้นจอ ${ov.small}`);
  chk('g_clean', errors.length === 0, errors.slice(0, 2).join(' | '));
  chk('g_offline', external.length === 0 && failed.length === 0, [...new Set(external)].slice(0, 2).concat(failed.slice(0, 2)).join(' | '));
  await browser.close();
  done();
})().catch(e => { console.log(JSON.stringify({ score: 0, checks: [{ id: 'harness', pass: false, note: e.message.slice(0, 200) }] })); });
