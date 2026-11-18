#!/usr/bin/env node
// make_report.mjs — สร้างผลประเมินที่คนอ่านได้จาก runs/<label>/results.json
//   node make_report.mjs [--on ai-rerank-on] [--off ai-rerank-off]
//   → eval/RESULTS.md · eval/results.html (ไฟล์เดียว ไม่ใช้ CDN · แม่แบบ results.template.html) · eval/SAMPLES.md (35 ข้อ)
// เกณฑ์ "ผ่าน/ไม่ผ่าน ต่อข้อ" ตาม METRICS.md:
//   rag  = correctness ≥ 0.5 และ faithfulness ≥ 0.5
//   qa   = correctness ≥ 0.5 และ exact_value = 1 (ถ้าข้อนั้นมีตัวเลข)
//   conv = ทุกรอบ correctness ≥ 0.5 (+ exact_value ≠ 0) และ context_retention ≥ 0.5 และ state_ok ≠ 0
//   ✅ = ผ่านและได้เต็มทุกตัว (= pass แบบเข้มของ score.mjs / dashboard) · ⚠️ = ผ่านตามเกณฑ์แต่ยังไม่เต็ม · ❌ = ไม่ผ่าน
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).reduce((a, x, i, arr) => (x.startsWith('--') ? [...a, [x.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]] : a), []),
);
const ON = String(args.on || 'ai-rerank-on');
const OFF = String(args.off || 'ai-rerank-off');
const load = (l) => {
  const f = path.join(HERE, 'runs', l, 'results.json');
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null;
};
const R_ON = load(ON);
const R_OFF = load(OFF);
if (!R_ON) throw new Error(`ไม่พบ runs/${ON}/results.json`);
const qaSrc = JSON.parse(fs.readFileSync(path.join(HERE, 'qa.json'), 'utf8'));
const qaById = Object.fromEntries((Array.isArray(qaSrc) ? qaSrc : qaSrc.items || []).map((q) => [q.id, q]));

// ---------------------------------------------------------------- metric info (ตาม METRICS.md)
const INFO = {
  hit_at_4: ['Hit@4', 'ใน 4 ย่อหน้าที่ค้นได้ มีหน้าที่มีคำตอบไหม', '≥ 0.90'],
  mrr: ['MRR', 'หน้าที่มีคำตอบอยู่อันดับเท่าไร (1 ÷ อันดับ)', '≥ 0.80'],
  citation_acc: ['อ้างอิงถูก (Citation)', 'ป้าย 📄 ไฟล์/หน้า ใต้คำตอบชี้ถูกหน้าไหม', '≥ 0.85'],
  faithfulness: ['ไม่แต่งเติม (Faithfulness)', 'ทุกประโยคในคำตอบมีที่มาจากย่อหน้าที่ค้นได้ไหม', '≥ 0.90'],
  correctness: ['ตอบถูก (Correctness)', 'สาระตรงกับคำตอบที่คาดไหม (ชุด B รวมปฏิเสธนอกเรื่อง/ถามกลับเมื่อกำกวม)', '≥ 0.85'],
  exact_value: ['ตัวเลขตรง (Exact value)', 'ราคา/สต็อก/ค่าส่ง/VAT ที่ต้องมี อยู่ครบและถูกเป๊ะไหม', '≥ 0.95'],
  sql_correct: ['ดึงสินค้าถูก (SQL correct)', 'ระบบดึงสินค้า (SKU) ที่ถูกตัวจาก DB มาตอบไหม', '≥ 0.95'],
  context_retention: ['จำบริบท (Context retention)', 'คำว่า "อันนั้น / ตามจำนวนนั้น" ถูกตีความเป็นสินค้า/จำนวนที่ถูกไหม', '≥ 0.90'],
  state_ok: ['ทำงานจริง (State OK)', 'สั่งใส่ตะกร้า/ขอใบเสนอราคาแล้ว เกิดขึ้นจริงในระบบไหม', '1.00'],
  stt_cer: ['CER (STT)', 'Whisper ถอดเสียงพลาดกี่ % (ยิ่งน้อยยิ่งดี)', '≤ 0.10'],
  key_fact_recall: ['key-fact recall', 'สัดส่วน key fact ที่พบในคำตอบ (โค้ดช่วยผู้ตัดสิน)', '–'],
  pass: ['ผ่าน (เกณฑ์ METRICS)', 'rag: ตอบถูก ≥ 0.5 และไม่แต่งเติม ≥ 0.5 · qa: ตอบถูก ≥ 0.5 และตัวเลขตรง · conv: ทุกรอบผ่าน + จำบริบท ≥ 0.5 + ทำงานจริง', '–'],
  strict: ['ผ่านเต็ม (ทุกคะแนน = 1)', 'ผ่านตามเกณฑ์ และได้เต็ม: rag ตอบถูก = 1 และไม่แต่งเติม = 1 · qa ตอบถูก = 1 · conv ทุกรอบตอบถูก = 1 และจำบริบท = 1', '–'],
};
const METRIC_ROWS = [
  ['1', 'hit_at_4', 'โค้ด'], ['2', 'mrr', 'โค้ด'], ['3', 'citation_acc', 'โค้ด'], ['4', 'faithfulness', 'AI'], ['5', 'correctness', 'AI'],
  ['6', 'exact_value', 'โค้ด'], ['7', 'sql_correct', 'โค้ด'], ['8', 'correctness', 'AI', 'ตอบถูก ชุด B', 'เหมือนข้อ 5 + ปฏิเสธนอกเรื่อง / ถามกลับเมื่อกำกวม'],
  ['9', 'context_retention', 'AI'], ['10', 'state_ok', 'โค้ด'], ['11', 'correctness', 'AI + โค้ด', 'ตอบถูก/ตัวเลขตรง ต่อรอบ', 'ข้อ 5–6 ในแต่ละรอบของบทสนทนา'], ['12', 'stt_cer', 'โค้ด'],
];

// ---------------------------------------------------------------- helpers
const pct = (v) => (v == null ? '–' : `${(v * 100).toFixed(1)}%`);
const num = (v, d = 3) => (v == null ? '–' : Number(v).toFixed(d));
const CNT = ['n', 'judged', 'turns', 'voice_turns'];
const fmt = (k, v) => (v == null ? '–' : k === 'stt_cer' || k === 'mrr' ? num(v, 3) : CNT.includes(k) ? String(v) : pct(v));
const delta = (k, a, b) => {
  if (a == null || b == null || CNT.includes(k)) return '–';
  if (k === 'stt_cer' || k === 'mrr') { const d = a - b; return `${d >= 0 ? '+' : ''}${d.toFixed(3)}`; }
  const d = (a - b) * 100;
  return `${d >= 0 ? '+' : ''}${d.toFixed(1)} pt`;
};
const trim = (s, n = 200) => {
  s = String(s ?? '').replace(/\s+/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
};
const md = (s) => String(s ?? '').replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
const short = (f) => String(f || '').replace(/^BM-(DS-)?/, '').replace(/\.pdf$/, '');
const pagesTxt = (arr) => (arr || []).map((r) => `${short(r.filename)} p${r.page}`).join(', ') || '–';
const avg = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);
const ge = (v, t) => v == null || v >= t;

function passM(it) {
  const m = it.metrics || {};
  if (it.set === 'rag') return ge(m.correctness, 0.5) && m.correctness != null && ge(m.faithfulness, 0.5);
  if (it.set === 'qa') return m.correctness != null && m.correctness >= 0.5 && m.exact_value !== 0;
  if (it.set === 'conv') {
    const ts = it.turns || [];
    if (!ts.length) return false;
    return ts.every((t, i) => {
      const x = t.metrics || {};
      return x.correctness != null && x.correctness >= 0.5 && x.exact_value !== 0 && x.state_ok !== 0 && (i === 0 || ge(x.context_retention, 0.5)) && !t.error;
    });
  }
  return !!it.pass;
}
function perfect(it) {
  if (!passM(it)) return false;
  const m = it.metrics || {};
  if (it.set === 'rag') return m.correctness === 1 && m.faithfulness === 1;
  if (it.set === 'qa') return m.correctness === 1;
  if (it.set === 'conv') return (it.turns || []).every((t, i) => t.metrics?.correctness === 1 && (i === 0 || t.metrics?.context_retention == null || t.metrics.context_retention === 1) && t.metrics?.state_ok !== 0);
  return true;
}
const verdict = (it) => (!passM(it) ? '❌' : perfect(it) ? '✅' : '⚠️');
const order = { '❌': 0, '⚠️': 1, '✅': 2 };
const rateM = (its) => (its.length ? its.filter(passM).length / its.length : null);
const rateS = (its) => (its.length ? its.filter(perfect).length / its.length : null);
const bySet = (R, s) => (R ? R.items.filter((i) => i.set === s) : []);

// ---------------------------------------------------------------- summary tables
const MET = {
  rag: ['hit_at_4', 'mrr', 'citation_acc', 'faithfulness', 'correctness', 'key_fact_recall'],
  qa: ['exact_value', 'sql_correct', 'correctness'],
  conv: ['correctness', 'context_retention', 'exact_value', 'state_ok', 'hit_at_4', 'stt_cer'],
};
function summaryTable() {
  const out = ['| set | ตัวชี้วัด | rerank on | rerank off | Δ (on − off) |', '|---|---|---:|---:|---:|'];
  for (const set of ['rag', 'qa', 'conv']) {
    const a = R_ON.summary?.[set] || {};
    const has = !!R_OFF?.summary?.[set];
    const b = R_OFF?.summary?.[set] || {};
    const itsA = bySet(R_ON, set), itsB = bySet(R_OFF, set);
    const row = (name, k, va, vb) => out.push(`| ${set} | ${name} | ${fmt(k, va)} | ${has ? fmt(k, vb) : '(ไม่ได้รัน)'} | ${has ? delta(k, va, vb) : '–'} |`);
    row(`**${INFO.pass[0]}**`, 'pass', rateM(itsA), rateM(itsB));
    row(INFO.strict[0], 'pass', rateS(itsA), rateS(itsB));
    for (const k of MET[set]) if (a[k] != null || b[k] != null) row(INFO[k]?.[0] || k, k, a[k], b[k]);
    row('จำนวนข้อ/บท', 'n', a.n, b.n);
    if (set === 'conv') row('จำนวนรอบ (เสียง)', 'turns', a.turns, b.turns);
  }
  return out.join('\n');
}
function groupTable(set, keyOf, keys, label) {
  const A = bySet(R_ON, set), B = bySet(R_OFF, set);
  const hasOff = B.length > 0;
  const groups = [...new Set(A.map(keyOf))].sort();
  const mean = (its, k) => avg(its.map((i) => i.metrics?.[k]).filter((v) => v != null));
  const cols = [...keys, 'pass'];
  const head = [label, 'n', ...cols.flatMap((k) => (hasOff ? [`${INFO[k][0]} on`, 'off'] : [INFO[k][0]]))];
  const out = [`| ${head.join(' | ')} |`, `|---|${head.slice(1).map(() => '---:').join('|')}|`];
  for (const g of groups) {
    const a = A.filter((i) => keyOf(i) === g), b = B.filter((i) => keyOf(i) === g);
    const v = (its, k) => (k === 'pass' ? pct(rateM(its)) : fmt(k, mean(its, k)));
    out.push(`| ${g} | ${a.length} | ${cols.flatMap((k) => (hasOff ? [v(a, k), b.length ? v(b, k) : '–'] : [v(a, k)])).join(' | ')} |`);
  }
  return out.join('\n');
}

// ---------------------------------------------------------------- items
function itemRow(it) {
  const src = it.set === 'rag' ? pagesTxt(it.expected?.sources || it.sources) : '–';
  const got = it.set === 'rag' ? pagesTxt((it.retrieved || []).slice(0, 4)) : (it.products || []).slice(0, 5).join(', ') || '–';
  const exp = it.set === 'qa' && it.expected?.values?.length ? `${trim(it.expected.answer, 150)} [ค่า: ${it.expected.values.map((v) => (Array.isArray(v) ? v.join('/') : v)).join(', ')}]` : trim(it.expected?.answer, 150);
  const sc = it.set === 'rag' ? ` (ถูก ${it.metrics?.correctness ?? '–'} · ไม่แต่ง ${it.metrics?.faithfulness ?? '–'})` : ` (ถูก ${it.metrics?.correctness ?? '–'})`;
  return `| ${it.id} | ${md(trim(it.question, 140))} | ${md(exp)} | ${md(trim(it.answer, 200))} | ${md(it.set === 'rag' ? `ค้นได้: ${got}<br>ที่ถูก: ${src}` : `สินค้าที่ดึง: ${got}`)} | ${verdict(it)}${sc} | ${md(trim(it.reason, 220)) || '–'} |`;
}
const ic = (v) => (v == null ? '–' : v === 1 ? '✅' : v === 0.5 ? '⚠️' : '❌');
function itemsSection(R) {
  const out = [];
  const H = '| id | คำถาม | คำตอบที่คาด | คำตอบจาก AI | หน้าที่ค้นได้ vs หน้าที่ถูก | ผล | เหตุผล |\n|---|---|---|---|---|:-:|---|';
  const sortF = (a, b) => order[verdict(a)] - order[verdict(b)] || a.id.localeCompare(b.id, 'en', { numeric: true });
  const rag = bySet(R, 'rag');
  out.push(`### set rag (${rag.length} ข้อ) — แยกตามเอกสาร`);
  for (const d of [...new Set(rag.map((i) => i.doc))].sort()) {
    const g = rag.filter((i) => i.doc === d).sort(sortF);
    out.push(`\n#### ${d} · ผ่าน ${g.filter(passM).length}/${g.length} (เต็ม ${g.filter((i) => verdict(i) === '✅').length})\n\n${H}\n${g.map(itemRow).join('\n')}`);
  }
  const qa = bySet(R, 'qa');
  if (qa.length) {
    out.push(`\n### set qa (${qa.length} ข้อ) — แยกตามหมวดคำถาม (ไม่ใช้ PDF · ตรวจจาก DB)`);
    for (const c of [...new Set(qa.map((i) => i.qtype))].sort()) {
      const g = qa.filter((i) => i.qtype === c).sort(sortF);
      out.push(`\n#### ${c} · ผ่าน ${g.filter(passM).length}/${g.length}\n\n${H}\n${g.map(itemRow).join('\n')}`);
    }
  }
  const conv = bySet(R, 'conv').sort(sortF);
  if (conv.length) {
    out.push(`\n### set conv (${conv.length} บท) — ทีละรอบ`);
    for (const c of conv) {
      out.push(`\n#### ${c.id} ${verdict(c)} ${md(c.title || '')} ${c.qtype === 'voice' ? '🎤' : ''}\n`);
      out.push(`ตอบถูก ${pct(c.metrics?.correctness)} · จำบริบท ${pct(c.metrics?.context_retention)}${c.metrics?.stt_cer != null ? ` · CER ${num(c.metrics.stt_cer)}` : ''}${c.reason ? ` · ${md(trim(c.reason, 300))}` : ''}\n`);
      out.push('| รอบ | คำถาม (เสียง → ถอดได้) | คำตอบที่คาด | คำตอบจาก AI | ค้นได้ / สถานะ | ตอบถูก | จำบริบท | เหตุผล |\n|:-:|---|---|---|---|:-:|:-:|---|');
      for (const t of c.turns || []) {
        const q = t.audio ? `🎤 ${t.audio}: “${trim(t.transcript ?? '(ถอดไม่ได้)', 110)}”` : trim(t.q, 130);
        const st = [t.retrieved?.length ? pagesTxt(t.retrieved.slice(0, 4)) : '', t.cartCount != null ? `ตะกร้า ${t.cartCount}` : '', t.quoteNo ? `ใบเสนอราคา ${t.quoteNo}` : '', t.metrics?.state_ok === 0 ? 'สถานะไม่ตรง ❌' : ''].filter(Boolean).join(' · ') || '–';
        out.push(`| ${t.n} | ${md(q)} | ${md(trim(t.expected, 140))} | ${md(trim(t.a, 200))} | ${md(st)} | ${ic(t.metrics?.correctness)} | ${t.n === 1 ? '–' : ic(t.metrics?.context_retention)} | ${md(trim(t.reason, 160)) || '–'} |`);
      }
    }
  }
  return out.join('\n');
}

// ---------------------------------------------------------------- ตัวอย่างจริงต่อตัวชี้วัด
const B = (s) => `**${s}**`;
const ranked = (it, n = 4) =>
  (it.retrieved || []).slice(0, n).map((r, i) => {
    const hit = (it.expected?.sources || it.sources || []).some((s) => s.filename === r.filename && s.page === r.page);
    return `${'①②③④⑤⑥'[i]} ${hit ? B(`${short(r.filename)}-${r.page}`) : `${short(r.filename)}-${r.page}`}`;
  }).join(' ');
const rankOf = (it) => {
  const i = (it.retrieved || []).slice(0, 4).findIndex((r) => (it.expected?.sources || it.sources || []).some((s) => s.filename === r.filename && s.page === r.page));
  return i < 0 ? 'ไม่เจอ' : String(i + 1);
};
const srcOf = (it) => (it.expected?.sources || it.sources || []).map((s) => `${short(s.filename)}-${s.page}`).join(', ') || '–';
const pickBy = (arr, preds) => {
  const used = new Set(), out = [];
  for (const p of preds) {
    const x = arr.find((i) => !used.has(i.id) && p(i));
    if (x) (used.add(x.id), out.push(x));
  }
  return out;
};
const idNum = (a, b) => a.id.localeCompare(b.id, 'en', { numeric: true });
function skusNeeded(id) {
  const q = qaById[id] || {};
  return [...new Set([...(q.needs_products || []), ...String(q.sql || '').match(/[A-Z]{3}-\d{3}/g) || []])];
}
function convTurns(R) {
  const out = [];
  for (const c of bySet(R, 'conv')) {
    const src = qaById[c.id]?.turns || [];
    (c.turns || []).forEach((t, i) => out.push({ conv: c.id, ...t, src: src[i] || {} }));
  }
  return out;
}
function examples() {
  const rag = bySet(R_ON, 'rag').filter((i) => i.qtype !== 'negative').sort(idNum);
  const ragAll = bySet(R_ON, 'rag').sort(idNum);
  const qa = bySet(R_ON, 'qa').sort(idNum);
  const turns = convTurns(R_ON);
  const turnsOff = R_OFF ? convTurns(R_OFF) : [];
  const E = [];
  // 1 Hit@4
  E.push({
    k: 'hit_at_4', n: '1',
    head: ['id', 'คำถาม', 'หน้าที่ถูก', '4 อันดับที่ค้นได้ (ตัวหนา = หน้าที่ถูก)', 'Hit@4'],
    rows: pickBy(rag, [(i) => i.metrics.mrr === 1, (i) => i.metrics.hit_at_4 === 1 && i.metrics.mrr <= 0.34, (i) => i.metrics.hit_at_4 === 0, (i) => i.metrics.hit_at_4 === 0]).map((i) => [i.id, trim(i.question, 90), srcOf(i), ranked(i), B(i.metrics.hit_at_4) + (i.metrics.hit_at_4 ? ` (อันดับ ${rankOf(i)})` : ' (ไม่อยู่ใน 4 อันดับ)')]),
  });
  // 2 MRR
  const mrrRows = pickBy(rag, [(i) => i.metrics.mrr === 1, (i) => i.metrics.mrr === 0.5, (i) => i.metrics.mrr > 0 && i.metrics.mrr < 0.5, (i) => i.metrics.mrr === 0]).map((i) => [i.id, trim(i.question, 90), ranked(i), rankOf(i), B(num(i.metrics.mrr, 2))]);
  let cmp = [];
  if (R_OFF) {
    const off = Object.fromEntries(bySet(R_OFF, 'rag').map((i) => [i.id, i]));
    cmp = rag.filter((i) => off[i.id] && i.metrics.mrr - (off[i.id].metrics.mrr ?? 0) > 0)
      .sort((a, b) => (b.metrics.mrr - off[b.id].metrics.mrr) - (a.metrics.mrr - off[a.id].metrics.mrr) || idNum(a, b))
      .slice(0, 2)
      .map((i) => [i.id, trim(i.question, 80), srcOf(i), `off: ${ranked(off[i.id])} → MRR ${num(off[i.id].metrics.mrr, 2)} · ตอบถูก ${off[i.id].metrics.correctness}`, `on: ${ranked(i)} → MRR ${B(num(i.metrics.mrr, 2))} · ตอบถูก ${i.metrics.correctness}`]);
  }
  E.push({ k: 'mrr', n: '2', head: ['id', 'คำถาม', '4 อันดับที่ค้นได้', 'อันดับหน้าที่ถูก', 'MRR'], rows: mrrRows, extra: cmp.length ? { title: 'reranker ช่วย: ข้อเดียวกัน rerank off → on', head: ['id', 'คำถาม', 'หน้าที่ถูก', 'rerank off', 'rerank on'], rows: cmp } : null });
  // 3 Citation
  E.push({
    k: 'citation_acc', n: '3',
    head: ['id', 'คำถาม', 'หน้าที่ถูก', 'ป้าย 📄 ที่บอทแสดง', 'citation'],
    rows: pickBy(rag, [(i) => i.metrics.citation_acc === 1 && i.cites.length === 1, (i) => i.metrics.citation_acc === 1 && i.cites.length > 1, (i) => i.metrics.citation_acc === 0 && i.cites.length > 0, (i) => i.metrics.citation_acc === 0 && !i.cites.length]).map((i) => [i.id, trim(i.question, 90), srcOf(i), i.cites.length ? i.cites.map((c) => `📄 ${short(c.filename)}-${c.page}`).join(' · ') : '(ไม่มีป้าย)', B(i.metrics.citation_acc)]),
  });
  // 4 Faithfulness
  E.push({
    k: 'faithfulness', n: '4',
    head: ['id', 'คำถาม', 'คำตอบจาก AI', 'หน้าที่ค้นได้', 'ไม่แต่งเติม', 'เหตุผลผู้ตัดสิน'],
    rows: pickBy(ragAll, [(i) => i.metrics.faithfulness === 1 && i.metrics.correctness === 1 && i.qtype === 'table_multiheader', (i) => i.metrics.faithfulness === 1 && i.metrics.correctness === 1 && i.qtype === 'negative', (i) => i.metrics.faithfulness === 0.5, (i) => i.metrics.faithfulness === 0]).map((i) => [i.id, trim(i.question, 80), trim(i.answer, 170), pagesTxt(i.retrieved.slice(0, 4)), B(i.metrics.faithfulness), trim(i.reason, 140) || '–']),
  });
  // 5 Correctness (rag)
  E.push({
    k: 'correctness', n: '5',
    head: ['id', 'คำถาม', 'คำตอบที่คาด', 'คำตอบจาก AI', 'ตอบถูก', 'เหตุผลผู้ตัดสิน'],
    rows: pickBy(ragAll, [(i) => i.metrics.correctness === 1 && i.qtype === 'cross_page', (i) => i.metrics.correctness === 0.5, (i) => i.metrics.correctness === 0 && i.metrics.hit_at_4 === 1, (i) => i.metrics.correctness === 0 && i.metrics.hit_at_4 === 0]).map((i) => [i.id, trim(i.question, 80), trim(i.expected?.answer, 130), trim(i.answer, 170), B(i.metrics.correctness), trim(i.reason, 140) || '–']),
  });
  // 6 Exact value
  const vals = (i) => (i.expected?.values || []).map((v) => (Array.isArray(v) ? v.join('/') : v)).join(', ');
  E.push({
    k: 'exact_value', n: '6',
    head: ['id', 'คำถาม', 'ค่าที่ต้องมี', 'คำตอบจาก AI', 'ตัวเลขตรง'],
    rows: pickBy(qa, [(i) => i.metrics.exact_value === 1 && i.qtype === 'tier_price', (i) => i.metrics.exact_value === 1 && i.qtype === 'cart_total', (i) => i.metrics.exact_value === 0, (i) => i.metrics.exact_value === 0, (i) => i.metrics.exact_value === 1 && i.qtype !== 'cart_total']).map((i) => [i.id, trim(i.question, 90), vals(i), trim(i.answer, 180), B(i.metrics.exact_value)]),
  });
  // 7 SQL correct
  const sqlRows = pickBy(qa, [(i) => i.metrics.sql_correct === 0, (i) => i.metrics.sql_correct === 1 && skusNeeded(i.id).length === 1, (i) => i.metrics.sql_correct === 1 && skusNeeded(i.id).length >= 2, (i) => i.metrics.sql_correct === 1 && i.qtype === 'stock_compare', (i) => i.metrics.sql_correct === 1 && i.qtype === 'coupon']).map((i) => [i.id, trim(i.question, 90), skusNeeded(i.id).join(', ') || '–', (i.products || []).join(', ') || '–', B(i.metrics.sql_correct)]);
  E.push({ k: 'sql_correct', n: '7', head: ['id', 'คำถาม', 'SKU ที่ต้องใช้', 'SKU ที่ระบบดึงมา', 'ดึงสินค้าถูก'], rows: sqlRows, note: bySet(R_ON, 'qa').every((i) => i.metrics.sql_correct !== 0) ? 'รอบนี้ไม่มีข้อที่ดึงสินค้าผิด (100%) — ตัวอย่างจึงเป็นข้อที่ได้ 1 ทั้งหมด' : '' });
  // 8 Correctness ชุด B
  E.push({
    k: 'correctness', n: '8', name: 'ตอบถูก ชุด B (qa)',
    head: ['id', 'ประเภท', 'คำถาม', 'คำตอบจาก AI', 'ตอบถูก', 'เหตุผลผู้ตัดสิน'],
    rows: pickBy(qa, [(i) => i.qtype === 'off_topic' && i.metrics.correctness === 1, (i) => i.qtype === 'ambiguous' && i.metrics.correctness === 1, (i) => i.metrics.correctness === 0.5, (i) => i.metrics.correctness === 0, (i) => i.qtype === 'shop_info' && i.metrics.correctness === 1]).map((i) => [i.id, i.qtype, trim(i.question, 80), trim(i.answer, 170), B(i.metrics.correctness), trim(i.reason, 140) || '–']),
  });
  // 9 Context retention
  const refT = (ts) => ts.filter((t) => t.n > 1 && t.refers_to);
  const ctxRows = [
    ...pickBy(refT(turns).map((t) => ({ ...t, id: `${t.conv}#${t.n}` })), [(t) => /200/.test(t.q || ''), (t) => /ตะกร้า/.test(t.q || ''), (t) => /DB16/.test(t.q || '')]).map((t) => ['on', `${t.conv} รอบ ${t.n}`, trim(t.q || t.ref_text, 70), trim(t.refers_to, 80), trim(t.a, 130), B(t.metrics?.context_retention)]),
    ...pickBy(refT(turnsOff).map((t) => ({ ...t, id: `${t.conv}#${t.n}` })), [(t) => t.metrics?.context_retention === 0.5]).map((t) => ['off', `${t.conv} รอบ ${t.n}`, trim(t.q || t.ref_text, 70), trim(t.refers_to, 80), trim(t.a, 130), B(t.metrics?.context_retention) + (t.reason ? ` — ${trim(t.reason, 90)}` : '')]),
  ];
  E.push({ k: 'context_retention', n: '9', head: ['run', 'บท/รอบ', 'ลูกค้าพูด', 'ต้องหมายถึง (refers_to)', 'คำตอบจาก AI', 'จำบริบท'], rows: ctxRows });
  // 10 State OK
  const stT = (ts) => ts.filter((t) => t.src.expect_state).map((t) => ({ ...t, id: `${t.conv}#${t.n}` }));
  const stRows = [
    ...pickBy(stT(turns), [(t) => t.metrics?.state_ok === 0, (t) => t.metrics?.state_ok === 1 && t.src.expect_state.cartCount != null, (t) => t.metrics?.state_ok === 1 && t.src.expect_state.quoteNo]).map((t) => ['on', t]),
    ...pickBy(stT(turnsOff), [(t) => t.conv === 'CV-01' && t.src.expect_state.quoteNo && t.metrics?.state_ok === 1]).map((t) => ['off', t]),
  ].map(([run, t]) => [run, `${t.conv} รอบ ${t.n}`, trim(t.q || t.ref_text, 60), JSON.stringify(t.src.expect_state).replace(/"/g, ''), `cartCount ${t.cartCount ?? '–'}${t.quoteNo ? ` · ${t.quoteNo}` : ' · ไม่มี quoteNo'}`, trim(t.a, 110), B(t.metrics?.state_ok)]);
  E.push({ k: 'state_ok', n: '10', head: ['run', 'บท/รอบ', 'คำสั่ง', 'คาด', 'ระบบส่งกลับ', 'คำตอบจาก AI', 'ทำงานจริง'], rows: stRows });
  // 11 per-turn correctness / exact
  E.push({
    k: 'correctness', n: '11', name: 'ตอบถูก/ตัวเลขตรง ต่อรอบ',
    head: ['บท/รอบ', 'ลูกค้าพูด', 'คำตอบที่คาด', 'คำตอบจาก AI', 'ตอบถูก', 'ตัวเลขตรง (โค้ด)', 'เหตุผล'],
    rows: pickBy(turns.map((t) => ({ ...t, id: `${t.conv}#${t.n}` })), [(t) => t.metrics?.correctness === 1 && t.metrics?.exact_value === 1 && t.n >= 4, (t) => t.metrics?.correctness === 0.5, (t) => t.metrics?.correctness === 0 && t.metrics?.exact_value === 0, (t) => t.metrics?.correctness === 0]).map((t) => [`${t.conv} รอบ ${t.n}`, trim(t.q || t.ref_text, 70), trim(t.expected, 120), trim(t.a, 150), B(t.metrics?.correctness), t.metrics?.exact_value ?? '–', trim(t.reason, 110) || '–']),
  });
  // 12 CER
  const voice = turns.filter((t) => t.audio && t.metrics?.stt_cer != null).sort((a, b) => a.metrics.stt_cer - b.metrics.stt_cer);
  const cerPick = [voice[0], voice[Math.floor(voice.length / 2)], voice[voice.length - 2], voice[voice.length - 1]].filter((v, i, a) => v && a.indexOf(v) === i);
  E.push({ k: 'stt_cer', n: '12', head: ['บท/รอบ · ไฟล์', 'ลูกค้าพูด (ข้อความอ้างอิง)', 'Whisper ถอดได้', 'CER', 'ผลต่อคำตอบ'], rows: cerPick.map((t) => [`${t.conv} รอบ ${t.n} · ${t.audio}`, trim(t.ref_text || t.src.text, 80), trim(t.transcript, 80), B(num(t.metrics.stt_cer, 3)), `ตอบถูก ${t.metrics?.correctness ?? '–'}${t.reason ? ` — ${trim(t.reason, 80)}` : ''}`]) });
  for (const e of E) {
    e.name = e.name || INFO[e.k][0];
    e.what = e.n === '8' ? 'เหมือนข้อ 5 + ปฏิเสธนอกเรื่อง / ถามกลับเมื่อกำกวม' : e.n === '11' ? 'ข้อ 5–6 ในแต่ละรอบของบทสนทนา' : INFO[e.k][1];
  }
  return E;
}
const EX = examples();
const tbl = (head, rows) => `| ${head.join(' | ')} |\n|${head.map(() => '---').join('|')}|\n${rows.map((r) => `| ${r.map((c) => md(c)).join(' | ')} |`).join('\n')}`;
const examplesMd = EX.map((e) => `### ${e.n}) ${e.name} — ${e.what}\n\n${e.note ? `> ${e.note}\n\n` : ''}${tbl(e.head, e.rows)}${e.extra ? `\n\n**${e.extra.title}**\n\n${tbl(e.extra.head, e.extra.rows)}` : ''}`).join('\n\n');

function metricsTable() {
  return ['| # | ตัวชี้วัด | วัดอะไร | ใครตรวจ | ค่าที่ดี |', '|---|---|---|---|---|', ...METRIC_ROWS.map(([n, k, who, name, what]) => `| ${n} | ${name || INFO[k][0]} | ${what || INFO[k][1]} | ${who} | ${INFO[k][2]} |`)].join('\n');
}
function failurePatterns(R) {
  const fails = R.items.filter((i) => !passM(i));
  const cnt = (f) => R.items.filter(f).length;
  return [
    `- ไม่ผ่านตามเกณฑ์ METRICS ${fails.length}/${R.items.length} ข้อ/บท · ไม่เต็ม (⚠️) ${R.items.filter((i) => verdict(i) === '⚠️').length}`,
    `- rag ค้นไม่เจอหน้าที่ถูก (hit@4 = 0): ${cnt((i) => i.set === 'rag' && i.metrics?.hit_at_4 === 0)} ข้อ`,
    `- rag ค้นเจอแต่ตอบผิด/ไม่ครบ (hit@4 = 1, ตอบถูก < 1): ${cnt((i) => i.set === 'rag' && i.metrics?.hit_at_4 === 1 && (i.metrics?.correctness ?? 1) < 1)} ข้อ`,
    `- rag ไม่แต่งเติม < 1: ${cnt((i) => i.set === 'rag' && (i.metrics?.faithfulness ?? 1) < 1)} ข้อ`,
    `- qa ตัวเลขไม่ตรง (exact_value = 0): ${cnt((i) => i.set === 'qa' && i.metrics?.exact_value === 0)} ข้อ`,
  ].join('\n');
}
function lat(R) {
  const L = R?.summary?.latency;
  if (!L) return '';
  return Object.entries(L).map(([k, v]) => `- ${k}: TTFT p50 ${v.ttft_p50} ms · p95 ${v.ttft_p95} ms · ทั้งคำตอบ p50 ${v.total_p50} ms · p95 ${v.total_p95} ms (n=${v.n})`).join('\n');
}
const cfg = (R) => Object.entries(R.config || {}).filter(([k]) => !/key|token|url|base|instance/i.test(k)).map(([k, v]) => `${k}=${typeof v === 'object' ? JSON.stringify(v) : v}`).join(' · ');

// ---------------------------------------------------------------- RESULTS.md
const resultsMd = `# ผลประเมิน RAG / คำถามร้าน / บทสนทนา — บ้านช่าง BuildMart (โหมด AI จริง)

> สร้างโดย \`eval/make_report.mjs\` จาก \`runs/${ON}/results.json\`${R_OFF ? ` และ \`runs/${OFF}/results.json\`` : ''} · ผู้ตัดสิน ไม่แต่งเติม/ตอบถูก/จำบริบท = Claude (rubric ใน \`eval/README.md\`) · ตารางค้น/กรองได้: [results.html](results.html) · คำอธิบายตัวชี้วัด: [METRICS.md](METRICS.md)

- **rerank on**: ${cfg(R_ON)}
${R_OFF ? `- **rerank off**: ${cfg(R_OFF)} (รันเฉพาะ set rag + conv)` : ''}

## ตัวชี้วัดคืออะไร (อ่านละเอียดใน [METRICS.md](METRICS.md))

${metricsTable()}

**ผ่าน/ไม่ผ่าน ต่อข้อ** (ตาม METRICS.md): rag = ตอบถูก ≥ 0.5 **และ** ไม่แต่งเติม ≥ 0.5 · qa = ตอบถูก ≥ 0.5 **และ** ตัวเลขตรง (ถ้าข้อนั้นมีตัวเลข) · conv = ทุกรอบผ่าน **และ** จำบริบท ≥ 0.5 **และ** ทำงานจริง · สัญลักษณ์: ✅ ผ่านและได้เต็ม · ⚠️ ผ่านแต่ยังไม่เต็ม (เช่น ตอบถูก 0.5) · ❌ ไม่ผ่าน · \`score.mjs\` และหน้า /admin/eval ใช้เกณฑ์เดียวกันนี้ (run \`ai-rerank-on-v2\` / \`ai-rerank-off-v2\`)

## สรุปต่อ set × ตัวชี้วัด

${summaryTable()}

> Δ = จุดเปอร์เซ็นต์ (on − off) · MRR/CER เป็นผลต่างตรง ๆ · CER ยิ่งต่ำยิ่งดี

## ตัวอย่างจริงต่อตัวชี้วัด (จากรอบนี้)

${examplesMd}

## แยกตามเอกสาร (set rag)

${groupTable('rag', (i) => i.doc, ['hit_at_4', 'mrr', 'faithfulness', 'correctness'], 'เอกสาร')}

## แยกตามประเภทคำถาม

### rag
${groupTable('rag', (i) => i.qtype, ['hit_at_4', 'correctness', 'faithfulness'], 'ประเภท')}

### qa
${groupTable('qa', (i) => i.qtype, ['exact_value', 'sql_correct', 'correctness'], 'หมวด')}

### conv
${groupTable('conv', (i) => i.qtype, ['correctness', 'context_retention', 'stt_cer'], 'ชนิด')}

## เวลา
**rerank on**
${lat(R_ON)}
${R_OFF ? `\n**rerank off**\n${lat(R_OFF)}` : ''}

## รูปแบบที่ไม่ผ่าน (rerank on)
${failurePatterns(R_ON)}

## ทุกข้อ (rerank on) — ข้อที่ไม่ผ่านขึ้นก่อนในแต่ละกลุ่ม

${itemsSection(R_ON)}
`;
fs.writeFileSync(path.join(HERE, 'RESULTS.md'), resultsMd);

// ---------------------------------------------------------------- SAMPLES.md (35)
function pickSamples(R) {
  const out = [];
  const used = new Set();
  const add = (it) => it && !used.has(it.id) && (used.add(it.id), out.push(it));
  const items = R.items.filter((i) => i.set !== 'conv').sort(idNum);
  const fails = items.filter((i) => verdict(i) !== '✅').sort((a, b) => order[verdict(a)] - order[verdict(b)] || idNum(a, b));
  const seenT = new Set();
  for (const f of fails) if (out.length < 8 && !seenT.has(f.qtype)) (seenT.add(f.qtype), add(f));
  for (const f of fails) if (out.length < 8) add(f);
  const types = (set) => [...new Set(items.filter((i) => i.set === set).map((i) => i.qtype))].sort();
  for (const t of types('rag')) items.filter((i) => i.set === 'rag' && i.qtype === t && verdict(i) === '✅').slice(0, 2).forEach(add);
  for (const t of types('qa')) if (out.length < 35) add(items.find((i) => i.set === 'qa' && i.qtype === t && verdict(i) === '✅'));
  for (const i of items) if (out.length < 35 && verdict(i) === '✅') add(i);
  return out.slice(0, 35);
}
const samples = pickSamples(R_ON);
const conv = bySet(R_ON, 'conv');
const sampleMd = `<!-- สร้างโดย eval/make_report.mjs จาก runs/${ON}/results.json · 35 ข้อ (ผสมทุกประเภท · ไม่เต็ม/ไม่ผ่าน ${samples.filter((s) => verdict(s) !== '✅').length} ข้อ) · ✅ ผ่านเต็ม ⚠️ ผ่านแต่ไม่เต็ม ❌ ไม่ผ่าน (เกณฑ์ใน METRICS.md) -->
| id | set · ประเภท | คำถาม | คำตอบที่คาด | คำตอบจาก AI (Qwen + RAG) | หน้าที่ค้นได้ / **ที่ถูก** | ผล | เหตุผล |
|---|---|---|---|---|---|:-:|---|
${samples
  .map((it) => {
    const pages = it.set === 'rag' ? `${pagesTxt((it.retrieved || []).slice(0, 4))} / **${pagesTxt(it.expected?.sources || it.sources)}**` : `DB: ${(it.products || []).slice(0, 3).join(', ') || '–'}`;
    return `| ${it.id} | ${it.set} · ${it.qtype} | ${md(trim(it.question, 110))} | ${md(trim(it.expected?.answer, 110))} | ${md(trim(it.answer, 170))} | ${md(pages)} | ${verdict(it)} | ${md(trim(it.reason, 120)) || '–'} |`;
  })
  .join('\n')}

บทสนทนาหลายรอบ: ผ่าน ${conv.filter(passM).length}/${conv.length} บท (เต็มทุกรอบ ${conv.filter((c) => verdict(c) === '✅').length}) · จำบริบท ${pct(R_ON.summary?.conv?.context_retention)} · ดูทีละรอบใน \`eval/RESULTS.md\`
`;
fs.writeFileSync(path.join(HERE, 'SAMPLES.md'), sampleMd);

// ---------------------------------------------------------------- results.html
const pageCache = new Map();
function pageText(label, filename, page) {
  const k = `${filename}#${page}`;
  if (pageCache.has(k)) return pageCache.get(k);
  let t = '';
  for (const l of [label, ON, OFF]) {
    const f = path.join(HERE, 'runs', l, 'pages', `${String(filename).replace(/\.pdf$/, '')}-p${page}.txt`);
    if (fs.existsSync(f)) { t = fs.readFileSync(f, 'utf8').replace(/\s+/g, ' ').trim(); break; }
  }
  pageCache.set(k, t);
  return t;
}
function snippet(text, q, n = 420) {
  if (!text) return '';
  const words = String(q || '').split(/[\s,?()]+/).filter((w) => w.length >= 2);
  let best = 0, bestScore = -1;
  for (let i = 0; i < text.length; i += 80) {
    const w = text.slice(i, i + n);
    const s = words.reduce((a, x) => a + (w.includes(x) ? x.length : 0), 0);
    if (s > bestScore) (bestScore = s), (best = i);
  }
  return (best > 0 ? '… ' : '') + text.slice(best, best + n) + (best + n < text.length ? ' …' : '');
}
function slim(R, label) {
  if (!R) return null;
  const S = {};
  for (const set of ['rag', 'qa', 'conv']) if (R.summary?.[set]) S[set] = { ...R.summary[set], pass_m: rateM(bySet(R, set)), pass_strict: rateS(bySet(R, set)) };
  return {
    label: R.label,
    config: Object.fromEntries(Object.entries(R.config || {}).filter(([k]) => !/key|token|url|base|instance/i.test(k))),
    summary: S,
    items: R.items.map((it) => {
      const snip = (rs, q) => (rs || []).slice(0, 4).map((r) => ({ f: r.filename, p: r.page, s: r.score, t: snippet(pageText(label, r.filename, r.page), q) }));
      const base = {
        id: it.id, set: it.set, doc: it.doc || null, qtype: it.qtype, title: it.title || null,
        q: it.question, exp: it.expected?.answer || '', vals: it.expected?.values || null, kf: it.expected?.key_facts || null,
        src: it.expected?.sources || it.sources || null, a: it.answer, cites: it.cites, products: it.products, m: it.metrics,
        pass: passM(it), v: verdict(it), reason: it.reason,
      };
      if (it.set === 'conv') {
        base.turns = (it.turns || []).map((t) => ({
          n: t.n, q: t.q, audio: t.audio || null, tr: t.transcript ?? null, ref: t.refers_to || null, exp: t.expected, a: t.a, m: t.metrics,
          reason: t.reason || '', cart: t.cartCount ?? null, quote: t.quoteNo || null, src: t.sources || null, ret: snip(t.retrieved, t.q + ' ' + t.a),
        }));
      } else base.ret = snip(it.retrieved, it.question + ' ' + (it.expected?.answer || ''));
      return base;
    }),
  };
}
const DATA = {
  on: slim(R_ON, ON), off: slim(R_OFF, OFF), generated: new Date().toISOString(),
  info: INFO, metrics: METRIC_ROWS.map(([n, k, who, name, what]) => ({ n, k, who, name: name || INFO[k][0], what: what || INFO[k][1], good: INFO[k][2] })),
  examples: EX,
};
const json = JSON.stringify(DATA).replace(/</g, '\\u003c');
const html = fs.readFileSync(path.join(HERE, 'results.template.html'), 'utf8').replace('/*__DATA__*/null', () => json);
fs.writeFileSync(path.join(HERE, 'results.html'), html);
console.log(`RESULTS.md · SAMPLES.md (${samples.length}) · results.html (${(html.length / 1024).toFixed(0)} KB) · ตัวอย่างต่อ metric: ${EX.map((e) => `${e.n}:${e.rows.length}`).join(' ')}`);
