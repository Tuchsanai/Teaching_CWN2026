// สร้างรายงานหน้าเดียว e2e/index.html (เปิดด้วยดับเบิลคลิก ไม่ต้องมี server)
// อ่าน: plan-cases.json · test-report/summary.json · test-report/meta.json · triage.json
// ใช้: npm run report (สร้างใหม่หลังแก้ triage.json โดยไม่ต้องรัน test ซ้ำ)
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const BROWSERS = ['chromium', 'firefox', 'webkit'];
const read = (f, d) => (existsSync(join(ROOT, f)) ? JSON.parse(readFileSync(join(ROOT, f), 'utf8')) : d);
const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

export function build() {
  const cases = read('plan-cases.json', []);
  const summary = read('test-report/summary.json', { projects: {} });
  const meta = read('test-report/meta.json', {});
  const triage = read('triage.json', {});
  const P1 = cases.filter((c) => c.priority === 'P1').length;
  const need = Math.ceil(cases.length * 0.95 - 1e-9);

  // ผลของ TC ในเบราว์เซอร์ b — TC ที่ยิง API อย่างเดียวใช้ผลจาก project "api" นับให้ทุกเบราว์เซอร์ (แผน 6.2 ข้อ 3)
  const resultOf = (c, b) => summary.projects[c.apiOnly ? 'api' : b]?.results?.[c.id];
  const statusOf = (c, b) => {
    const r = resultOf(c, b);
    if (!r) return 'notrun';
    return r.status === 'passed' ? 'pass' : r.status === 'skipped' ? 'notrun' : 'fail';
  };

  const verdicts = BROWSERS.map((b) => {
    const st = cases.map((c) => ({ c, s: statusOf(c, b) }));
    const pass = st.filter((x) => x.s === 'pass').length;
    const fail = st.filter((x) => x.s === 'fail').length;
    const notrun = st.filter((x) => x.s === 'notrun').length;
    const p1pass = st.filter((x) => x.c.priority === 'P1' && x.s === 'pass').length;
    const ran = !!summary.projects[b];
    const ex1 = p1pass === P1; const ex2 = pass >= need;
    return { b, ran, pass, fail, notrun, p1pass, ex1, ex2, ok: ran && ex1 && ex2, at: summary.projects[b]?.at,
      failedP1: st.filter((x) => x.c.priority === 'P1' && x.s !== 'pass').map((x) => x.c.id) };
  });

  const bug = meta.bugMode === '1' ? { cls: 'mode-bug', t: 'โหมดบั๊ก (data-bug-mode="1")' }
    : meta.bugMode === '0' ? { cls: 'mode-ok', t: 'โหมดปกติ (data-bug-mode="0")' } : { cls: 'mode-unk', t: 'ไม่รู้โหมด' };

  const media = (id, apiOnly) => {
    const g = `test-report/gifs/${id}.gif`; const m = `test-report/videos/${id}.mp4`; const l = `test-report/logs/${id}.log`;
    const out = [];
    if (!apiOnly) {
      if (existsSync(join(ROOT, g))) out.push(`<a href="${g}" target="_blank">GIF</a>`);
      if (existsSync(join(ROOT, m))) out.push(`<a href="${m}" target="_blank">MP4</a>`);
    }
    if (existsSync(join(ROOT, l))) out.push(`<a href="${l}" target="_blank">log</a>`);
    return out.join(' · ') || '<span class="muted">—</span>';
  };
  const cell = (c, b) => {
    const s = statusOf(c, b); const r = resultOf(c, b);
    const label = { pass: '✅ ผ่าน', fail: '❌ ล้ม', notrun: '⏸ ไม่ได้รัน' }[s];
    const tip = r ? `${r.status} · ${(r.duration / 1000).toFixed(1)} วิ${c.apiOnly ? ' · ผลจาก API' : ''}` : '';
    return `<td class="st ${s}" title="${esc(tip)}">${label}</td>`;
  };

  const rows = cases.map((c) => {
    const anyFail = BROWSERS.some((b) => statusOf(c, b) === 'fail');
    const t = triage[c.id];
    const errs = BROWSERS.flatMap((b) => {
      const r = resultOf(c, b);
      if (!r || r.status === 'passed') return [];
      return [`<b>${c.apiOnly ? 'api' : b}</b>${r.failedSteps?.length ? ' · ขั้นที่ล้ม: ' + esc(r.failedSteps.join(' / ')) : ''}<pre>${esc((r.errors || []).join('\n---\n')).slice(0, 1500)}</pre>`];
    });
    const uniqErrs = [...new Set(errs)];
    const tri = anyFail
      ? (t ? `<span class="tri tri-${esc(t.verdict === 'เว็บผิด' ? 'web' : t.verdict === 'แผนผิด' ? 'plan' : 'test')}">${esc(t.verdict)}</span> ${esc(t.reason || '')}${t.evidence ? `<div class="muted small">หลักฐาน: ${esc(t.evidence)}</div>` : ''}`
        : '<span class="tri tri-none">ยังไม่จำแนก</span>')
      : '';
    return `<tr class="${anyFail ? 'row-fail' : ''}" data-pri="${c.priority}" data-mod="${c.moduleCode}">
      <td class="id">${c.id}${c.apiOnly ? '<div class="tag">API</div>' : ''}</td>
      <td><div>${esc(c.what)}</div><details><summary>ผลที่คาดหวัง</summary><div class="small">${esc(c.expected)}</div></details>
        ${uniqErrs.length ? `<details class="err"><summary>สิ่งที่ล้ม</summary>${uniqErrs.join('')}</details>` : ''}</td>
      <td class="pri ${c.priority}">${c.priority}</td>
      <td class="small">${esc(c.source)}</td>
      ${BROWSERS.map((b) => cell(c, b)).join('')}
      <td class="small">${media(c.id, c.apiOnly)}</td>
      <td class="small">${tri}</td></tr>`;
  }).join('\n');

  const boxes = verdicts.map((v) => `
    <div class="box ${v.ran ? (v.ok ? 'ok' : 'bad') : 'idle'}">
      <div class="bname">${v.b}</div>
      <div class="big">${v.ran ? (v.ok ? 'ผ่านเกณฑ์' : 'ไม่ผ่านเกณฑ์') : 'ยังไม่ได้รัน'}</div>
      <ul>
        <li class="${v.ex1 ? 'y' : 'n'}">EX-1 P1 ผ่าน <b>${v.p1pass} / ${P1}</b> ${v.ex1 ? '✔' : '✘'}</li>
        <li class="${v.ex2 ? 'y' : 'n'}">EX-2 ผ่านรวม <b>${v.pass} / ${cases.length}</b> (${cases.length ? ((v.pass / cases.length) * 100).toFixed(1) : 0}%) ต้อง ≥ ${need} ${v.ex2 ? '✔' : '✘'}</li>
        <li>ล้ม ${v.fail} · ไม่ได้รัน ${v.notrun}</li>
        ${v.failedP1.length ? `<li class="n small">P1 ที่ไม่ผ่าน: ${v.failedP1.join(', ')}</li>` : ''}
      </ul>
      <div class="muted small">${v.at ? 'รันล่าสุด ' + new Date(v.at).toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' }) : ''}</div>
    </div>`).join('');

  const mods = [...new Set(cases.map((c) => c.moduleCode))];
  const html = `<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ผลทดสอบ E2E สบายใจ สปา</title>
<style>
:root{--bg:#f7f5f0;--fg:#1f2421;--muted:#6b6f6a;--card:#fff;--line:#e3ded3;--ok:#1f7a4d;--okbg:#e5f4ec;--bad:#b42318;--badbg:#fdecea;--gold:#9a6b12}
@media (prefers-color-scheme:dark){:root{--bg:#141614;--fg:#e9ebe7;--muted:#9aa09a;--card:#1d201d;--line:#30352f;--okbg:#14301f;--badbg:#3a1714;--ok:#58c48b;--bad:#ff7b6e;--gold:#e0b45a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,"Noto Sans Thai","Leelawadee UI",sans-serif}
main{max-width:1280px;margin:0 auto;padding:20px 16px 60px}h1{margin:0 0 4px;font-size:24px}h2{font-size:18px;margin:28px 0 10px}
.muted{color:var(--muted)}.small{font-size:13px}.top{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.mode{padding:3px 10px;border-radius:99px;font-weight:600;font-size:13px}.mode-ok{background:var(--okbg);color:var(--ok)}.mode-bug{background:var(--badbg);color:var(--bad)}.mode-unk{background:var(--line)}
.boxes{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:14px}
.box{background:var(--card);border:2px solid var(--line);border-radius:12px;padding:14px 16px}.box.ok{border-color:var(--ok)}.box.bad{border-color:var(--bad)}
.box .bname{font-weight:700;text-transform:capitalize}.box .big{font-size:22px;font-weight:800;margin:2px 0 6px}.box.ok .big{color:var(--ok)}.box.bad .big{color:var(--bad)}
.box ul{margin:0;padding-left:18px}.y{color:var(--ok)}.n{color:var(--bad)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.filters select,.filters label{font:inherit;font-size:14px}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;min-width:1050px}th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--card);font-size:13px;color:var(--muted)}td.id{font-weight:700;white-space:nowrap}
td.st{white-space:nowrap;font-weight:600}td.pass{color:var(--ok)}td.fail{color:var(--bad);background:var(--badbg)}td.notrun{color:var(--muted)}
.pri{font-weight:700}.pri.P1{color:var(--bad)}.pri.P2{color:var(--gold)}.tag{display:inline-block;font-size:11px;border:1px solid var(--line);border-radius:6px;padding:0 5px;color:var(--muted)}
details summary{cursor:pointer;color:var(--muted);font-size:13px}details.err summary{color:var(--bad)}pre{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:6px;border-radius:6px;margin:4px 0}
.tri{display:inline-block;font-weight:700;border-radius:6px;padding:1px 7px;margin-bottom:2px}.tri-web{background:var(--badbg);color:var(--bad)}.tri-plan{background:#fff3d6;color:#8a5a00}.tri-test{background:#e6ecff;color:#2f4aa8}.tri-none{background:var(--line)}
a{color:inherit}
</style></head><body><main>
<div class="top"><h1>ผลทดสอบ E2E · สบายใจ สปา</h1><span class="mode ${bug.cls}">${bug.t}</span></div>
<div class="muted small">จาก TEST-PLAN.md หัวข้อ 5 (${cases.length} TC · P1 ${P1}) · เกณฑ์หัวข้อ 6.2 ตัดสินแยกทีละเบราว์เซอร์ · TODAY ${esc(meta.today || '')} · health ${esc(meta.health || '')} · สร้างรายงาน ${new Date().toLocaleString('th-TH', { timeZone: 'Asia/Bangkok' })}</div>
<div class="boxes">${boxes}</div>
<p class="muted small">กติกา: P1 ต้องผ่านครบ (EX-1) และผ่านรวม ≥ 95% = ≥ ${need}/${cases.length} (EX-2) · "ไม่ได้รัน" นับเป็นไม่ผ่าน · TC ที่ติดป้าย API ยิง API อย่างเดียว รัน 1 ครั้งแล้วใช้ผลเดียวกันทุกเบราว์เซอร์ · หลักฐาน GIF/MP4 อัดจาก chromium (npm run test:gif)</p>
<h2>ทุก TC</h2>
<div class="filters">
 <select id="fp"><option value="">ทุกระดับ</option><option>P1</option><option>P2</option><option>P3</option></select>
 <select id="fm"><option value="">ทุกโมดูล</option>${mods.map((m) => `<option>${m}</option>`).join('')}</select>
 <label><input type="checkbox" id="ff"> เฉพาะข้อที่ล้ม</label>
</div>
<div class="tablewrap"><table>
<thead><tr><th>รหัส</th><th>สิ่งที่ทดสอบ</th><th>ระดับ</th><th>ที่มา</th>${BROWSERS.map((b) => `<th>${b}</th>`).join('')}<th>หลักฐาน</th><th>การจำแนก (triage.json)</th></tr></thead>
<tbody>${rows}</tbody></table></div>
</main>
<script>
const f=()=>{const p=fp.value,m=fm.value,o=ff.checked;document.querySelectorAll('tbody tr').forEach(r=>{r.style.display=(!p||r.dataset.pri===p)&&(!m||r.dataset.mod===m)&&(!o||r.classList.contains('row-fail'))?'':'none'})};
[fp,fm,ff].forEach(e=>e.addEventListener('change',f));
</script></body></html>`;
  writeFileSync(join(ROOT, 'index.html'), html);
  return verdicts;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const v = build();
  for (const x of v) console.log(`${x.b.padEnd(9)} ผ่าน ${x.pass} ล้ม ${x.fail} ไม่ได้รัน ${x.notrun} · P1 ${x.p1pass} · ${x.ran ? (x.ok ? 'ผ่านเกณฑ์' : 'ไม่ผ่านเกณฑ์') : 'ยังไม่ได้รัน'}`);
  console.log('เขียน e2e/index.html แล้ว');
}
