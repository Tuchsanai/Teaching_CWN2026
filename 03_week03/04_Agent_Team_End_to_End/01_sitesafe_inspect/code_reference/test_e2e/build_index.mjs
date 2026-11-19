// Builds ./test/index.html + ./test/evidence/<TC>/... from Playwright JSON results.
// usage: node build_index.mjs <final results.json> [first-run results.json]
import fs from 'node:fs';
import path from 'node:path';

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const testDir = path.resolve(here, '..');
const evDir = path.join(testDir, 'evidence');
const finalRes = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
// argv[2] = first full run, argv[3..] = reruns (override the same TC)
const firstRes = finalRes;
const reruns = process.argv.slice(3).map(f => JSON.parse(fs.readFileSync(f, 'utf8')));
const triage = JSON.parse(fs.readFileSync(path.join(here, 'triage.json'), 'utf8'));

function collect(res) {
  const out = {};
  const walk = s => {
    for (const sp of s.specs || []) for (const t of sp.tests || []) {
      const id = (sp.title.match(/TC-\d-\d\d/) || [])[0]; if (!id) continue;
      const r = t.results[t.results.length - 1];
      out[id] = { title: sp.title, file: sp.file, status: r.status, duration: r.duration, errors: (r.errors || []).map(e => (e.message || '').replace(/\u001b\[[0-9;]*m/g, '')), attachments: r.attachments || [], annotations: t.annotations || [] };
    }
    for (const c of s.suites || []) walk(c);
  };
  for (const s of res.suites) walk(s);
  return out;
}
const first = collect(firstRes);
const fin = { ...first };
for (const rr of reruns) Object.assign(fin, collect(rr));
const rerunIds = new Set(reruns.flatMap(rr => Object.keys(collect(rr))));
const fixPath = (pth, id) => {
  if (!pth || fs.existsSync(pth)) return pth;
  if (!rerunIds.has(id)) { const alt = pth.replace(/([\\/])test-results([\\/])/, '$1results$1run1-test-results$2'); if (fs.existsSync(alt)) return alt; }
  return pth;
};

fs.rmSync(evDir, { recursive: true, force: true });
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const ids = Object.keys(fin).sort();
const rows = [];
for (const id of ids) {
  const t = fin[id]; const dir = path.join(evDir, id); fs.mkdirSync(dir, { recursive: true });
  const files = [];
  t.attachments.forEach((a, i) => {
    let name = `${String(i + 1).padStart(2, '0')}-${a.name.replace(/[^\w.\-ก-๙]+/g, '_')}`;
    const ext = a.contentType === 'image/png' ? '.png' : a.contentType === 'application/json' ? '.json' : a.contentType === 'application/zip' ? '.zip' : a.contentType?.startsWith('text/') ? '.txt' : '';
    if (!name.endsWith(ext)) name += ext;
    const dst = path.join(dir, name);
    const ap = fixPath(a.path, id);
    if (ap && fs.existsSync(ap)) fs.copyFileSync(ap, dst);
    else if (a.body) fs.writeFileSync(dst, Buffer.from(a.body, 'base64'));
    else return;
    files.push({ name, type: a.contentType, label: a.name });
  });
  const pr = (t.title.match(/\[(P\d)\]/) || [])[1] || '';
  const blocked = t.status === 'skipped';
  const st = t.status === 'passed' ? 'ผ่าน' : blocked ? 'บล็อก' : 'ล้ม';
  const tri = triage[id] || {};
  rows.push({ id, t, files, pr, st, tri, rerun: rerunIds.has(id), firstSt: first[id] ? (first[id].status === 'passed' ? 'ผ่าน' : first[id].status === 'skipped' ? 'บล็อก' : 'ล้ม') : '' });
}

const groups = { '1': '5.1 รับรูป', '2': '5.2 ผลตรวจ AI', '3': '5.3 คิว', '4': '5.4 รายงาน/แก้ผล', '5': '5.5 สิทธิ์' };
const count = f => rows.filter(f).length;
const summary = Object.entries(groups).map(([g, name]) => ({ name, pass: count(r => r.id[3] === g && r.st === 'ผ่าน'), fail: count(r => r.id[3] === g && r.st === 'ล้ม'), block: count(r => r.id[3] === g && r.st === 'บล็อก') }));

const card = r => {
  const imgs = r.files.filter(f => f.type === 'image/png').map(f => `<a href="evidence/${r.id}/${encodeURIComponent(f.name)}" target="_blank"><img src="evidence/${r.id}/${encodeURIComponent(f.name)}" alt="${esc(f.label)}"><span>${esc(f.label)}</span></a>`).join('');
  const others = r.files.filter(f => f.type !== 'image/png').map(f => `<a class="file" href="evidence/${r.id}/${encodeURIComponent(f.name)}" target="_blank">${f.type === 'application/zip' ? '🧭 trace' : '📄'} ${esc(f.label)}</a>`).join(' ');
  const err = r.t.errors.length ? `<details><summary>ข้อความที่ล้ม (${r.t.errors.length})</summary><pre>${esc(r.t.errors.join('\n\n').slice(0, 6000))}</pre></details>` : '';
  const ann = r.t.annotations.filter(a => a.description).map(a => `<li><b>${esc(a.type)}</b>: ${esc(a.description)}</li>`).join('');
  return `<section class="tc st-${r.st}" id="${r.id}" data-st="${r.st}" data-g="${r.id[3]}">
  <header><h3>${r.id} <small>${esc(r.t.title.replace(/^TC-\d-\d\d\s*/, ''))}</small></h3><span class="badge">${r.st}</span>${r.tri.cat ? `<span class="cat">${esc(r.tri.cat)}</span>` : ''}</header>
  ${r.tri.note ? `<p class="note">${esc(r.tri.note)}</p>` : ''}
  <p class="meta">${r.pr} · ${(r.t.duration / 1000).toFixed(1)} วินาที${r.rerun ? ` · รันซ้ำหลังแก้เทสต์ (รอบแรก: ${r.firstSt})` : ''} · ${esc(r.t.file)}</p>
  ${ann ? `<ul class="ann">${ann}</ul>` : ''}${err}
  <div class="shots">${imgs}</div><p class="files">${others}</p></section>`;
};

const html = `<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SiteSafe Test Evidence</title>
<style>
:root{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e2e1dc;--pass:#1f7a3a;--fail:#b3261e;--block:#8a6d00}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#161615;--fg:#ecebe6;--muted:#a3a29c;--card:#20201e;--line:#34332f;--pass:#5cc27a;--fail:#ff8a80;--block:#e6c450}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 "Sarabun","Noto Sans Thai",system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:16px}h1{margin:.2em 0}table{border-collapse:collapse;width:100%;background:var(--card)}td,th{border:1px solid var(--line);padding:6px 8px;text-align:left}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.filters button{border:1px solid var(--line);background:var(--card);color:var(--fg);padding:6px 12px;border-radius:16px;cursor:pointer}.filters button.on{outline:2px solid var(--fg)}
.tc{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--line);border-radius:8px;padding:12px 14px;margin:12px 0}
.st-ผ่าน{border-left-color:var(--pass)}.st-ล้ม{border-left-color:var(--fail)}.st-บล็อก{border-left-color:var(--block)}
.tc header{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.tc h3{margin:0;font-size:1.05em;flex:1 1 300px}.tc h3 small{font-weight:400;color:var(--muted)}
.badge,.cat{padding:2px 10px;border-radius:12px;font-size:.85em;border:1px solid currentColor}.st-ผ่าน .badge{color:var(--pass)}.st-ล้ม .badge{color:var(--fail)}.st-บล็อก .badge{color:var(--block)}
.meta,.note{color:var(--muted);margin:.3em 0}.note{color:var(--fg)}pre{white-space:pre-wrap;word-break:break-word;font-size:12px;max-height:320px;overflow:auto;background:var(--bg);padding:8px}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}.shots a{display:block;color:var(--muted);font-size:12px;text-decoration:none}.shots img{width:100%;height:120px;object-fit:cover;object-position:top;border:1px solid var(--line);border-radius:4px}
.files a{margin-right:10px}a{color:inherit}.ann{font-size:.9em;color:var(--muted)}
</style></head><body><main>
<h1>หลักฐานการทดสอบ SiteSafe Inspect</h1>
<p class="meta">Playwright Test · Chromium · 1 worker · เว็บ http://localhost:3410 (ai_mode real) · รายงาน: <a href="TEST-REPORT.md">TEST-REPORT.md</a> · แผน: <a href="TEST-PLAN.md">TEST-PLAN.md</a> · trace เปิดได้ที่ <a href="https://trace.playwright.dev" target="_blank">trace.playwright.dev</a> หรือ <code>npx playwright show-trace &lt;ไฟล์&gt;</code></p>
<table><tr><th>กลุ่ม</th><th>ผ่าน</th><th>ล้ม</th><th>บล็อก</th></tr>
${summary.map(s => `<tr><td>${s.name}</td><td>${s.pass}</td><td>${s.fail}</td><td>${s.block}</td></tr>`).join('')}
<tr><th>รวม</th><th>${count(r => r.st === 'ผ่าน')}</th><th>${count(r => r.st === 'ล้ม')}</th><th>${count(r => r.st === 'บล็อก')}</th></tr></table>
<div class="filters"><button data-f="all" class="on">ทั้งหมด</button><button data-f="ผ่าน">ผ่าน</button><button data-f="ล้ม">ล้ม</button><button data-f="บล็อก">บล็อก</button>${Object.entries(groups).map(([g, n]) => `<button data-g="${g}">${n}</button>`).join('')}</div>
<nav>${rows.map(r => `<a href="#${r.id}">${r.id}</a>`).join(' · ')}</nav>
${rows.map(card).join('\n')}
</main><script>
document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filters button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
const f=b.dataset.f,g=b.dataset.g;document.querySelectorAll('.tc').forEach(s=>{s.style.display=(g?s.dataset.g===g:(f==='all'||s.dataset.st===f))?'':'none'})});
</script></body></html>`;
fs.writeFileSync(path.join(testDir, 'index.html'), html);
console.log(JSON.stringify({ summary, total: rows.length, pass: count(r => r.st === 'ผ่าน'), fail: count(r => r.st === 'ล้ม'), block: count(r => r.st === 'บล็อก') }));
