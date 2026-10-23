#!/usr/bin/env node
// eval/score.mjs — รวม answers.json (metric โค้ด) + judgments (ผู้ตัดสิน = Claude) → results.json ตาม CONTRACT_V3 §6 แล้ว POST เข้า /api/admin/eval
//
//   node score.mjs --label <ชื่อ> [--post http://localhost:3400] [--token bm-eval] [--llm ..] [--rerank on|off] [--stt ..] [--tts ..] [--no-sql-alias]
//
// อ่าน:  eval/runs/<label>/answers.json
//        eval/runs/<label>/judge_batches/*.judgments.json  แล้วทับด้วย  eval/runs/<label>/judgments.json (ถ้ามี)
// เขียน: eval/runs/<label>/results.json  {label, config, summary, items}
//   summary.<set> = ค่าเฉลี่ยต่อ metric (0..1) + n + judged + pass_rate · summary.by_doc / by_type / by_difficulty / latency
//   summary.sql = สำเนาของ summary.qa (หน้า /admin/eval เดิมอ่านการ์ด B จาก key "sql") · ปิดด้วย --no-sql-alias
// ข้อที่ยังไม่ได้ตัดสิน: correctness/faithfulness/context_retention = null (ไม่นับในค่าเฉลี่ย) · pass คิดจาก metric โค้ดแทน และ reason บอกไว้
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = parseArgs(process.argv.slice(2));
if (!args.label) {
  console.error('ต้องระบุ --label <ชื่อ run> (โฟลเดอร์ eval/runs/<label>)');
  process.exit(1);
}
const DIR = path.join(HERE, 'runs', String(args.label));
const ansFile = path.join(DIR, 'answers.json');
if (!existsSync(ansFile)) {
  console.error(`ไม่พบ ${ansFile} — รัน node run_eval.mjs --label ${args.label} ก่อน`);
  process.exit(1);
}
const answers = JSON.parse(readFileSync(ansFile, 'utf8'));
let judgments, jfiles, problems, items, summary, results;

async function main() {
  ({ judgments, files: jfiles, problems } = loadJudgments());

  items = answers.items.map((it) => (it.set === 'conv' ? scoreConv(it) : scoreSingle(it)));
  summary = summarize(items);

  const config = { ...(answers.meta?.config || {}) };
  for (const k of ['llm', 'rerank', 'stt', 'tts', 'mode']) if (args[k] != null && args[k] !== true) config[k] = String(args[k]);
  if (/^(off|false|0|no)$/i.test(config.rerank || '')) config.rerank = 'off';

  results = {
    label: answers.meta?.label || String(args.label),
    config,
    summary,
    items,
    meta: {
      base: answers.meta?.base,
      started: answers.meta?.started,
      finished: answers.meta?.finished,
      scored: new Date().toISOString(),
      judgments: jfiles.map((f) => path.relative(DIR, f).replace(/\\/g, '/')),
      api: answers.meta?.api,
      warnings: [...(answers.meta?.warnings || []), ...problems],
    },
  };
  const outFile = path.join(DIR, 'results.json');
  writeFileSync(outFile, JSON.stringify(results, null, 2) + '\n');
  printSummary();
  console.log(`\n→ ${path.relative(process.cwd(), outFile) || outFile}`);
  for (const p of problems) console.log(`⚠ ${p}`);

  if (args.post) {
    const base = String(args.post === true ? answers.meta?.base || 'http://localhost:3400' : args.post).replace(/\/+$/, '');
    const token = String(args.token || process.env.EVAL_TOKEN || 'bm-eval');
    try {
      const res = await fetch(`${base}/api/admin/eval`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-eval-token': token },
        body: JSON.stringify(results),
        signal: AbortSignal.timeout(30_000),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) {
        console.error(`POST ${base}/api/admin/eval → ${res.status} ${JSON.stringify(j)}`);
        process.exit(3);
      }
      console.log(`POST ${base}/api/admin/eval → ${res.status} id=${j.id} · ดูที่ ${base}/admin/eval`);
    } catch (e) {
      console.error(`POST ไม่สำเร็จ: ${e.message}`);
      process.exit(3);
    }
  }
}

// ---------------------------------------------------------------- judgments
function loadJudgments() {
  const files = [];
  const bdir = path.join(DIR, 'judge_batches');
  if (existsSync(bdir)) for (const f of readdirSync(bdir).filter((x) => x.endsWith('.judgments.json')).sort()) files.push(path.join(bdir, f));
  if (existsSync(path.join(DIR, 'judgments.json'))) files.push(path.join(DIR, 'judgments.json')); // ไฟล์รวมชนะ
  const out = {};
  const problems = [];
  for (const f of files) {
    let j;
    try {
      j = JSON.parse(readFileSync(f, 'utf8'));
    } catch (e) {
      problems.push(`อ่าน ${path.basename(f)} ไม่ได้: ${e.message}`);
      continue;
    }
    const entries = Array.isArray(j) ? j.map((x) => [x.id, x]) : Object.entries(j);
    for (const [id, v] of entries) if (id && v && typeof v === 'object') out[id] = { ...(out[id] || {}), ...v };
  }
  const ids = new Set(answers.items.map((i) => i.id));
  const unknown = Object.keys(out).filter((id) => !ids.has(id));
  if (unknown.length) problems.push(`judgment ของ id ที่ไม่อยู่ใน answers: ${unknown.slice(0, 10).join(', ')}${unknown.length > 10 ? ' …' : ''}`);
  const missing = [...ids].filter((id) => !out[id] || !hasScore(out[id]));
  if (missing.length) problems.push(`ยังไม่ได้ตัดสิน ${missing.length}/${ids.size} ข้อ (${missing.slice(0, 8).join(', ')}${missing.length > 8 ? ' …' : ''}) → pass ใช้ metric โค้ดแทน`);
  return { judgments: out, files, problems };
}
const hasScore = (j) => j.correctness != null || (Array.isArray(j.turns) && j.turns.some((t) => t?.correctness != null));

/** คะแนนผู้ตัดสิน: 0 | 0.5 | 1 (ค่าอื่นในช่วง 0..1 ปัดเข้าใกล้สุด) · null = ไม่มี */
function sc(v) {
  if (v == null || v === '') return null;
  const n = Number(v);
  if (!Number.isFinite(n)) return null;
  return Math.max(0, Math.min(1, Math.round(n * 2) / 2));
}

// ---------------------------------------------------------------- ต่อข้อ
function scoreSingle(it) {
  const j = judgments[it.id] || {};
  const m = { ...(it.metrics || {}) };
  const judged = j.correctness != null;
  m.correctness = sc(j.correctness);
  if (it.set === 'rag') m.faithfulness = sc(j.faithfulness ?? (it.type === 'negative' && judged ? 1 : null));
  if (it.set !== 'rag') delete m.faithfulness;
  for (const k of Object.keys(m)) if (m[k] == null) delete m[k];

  const negative = it.type === 'negative' || it.category === 'off_topic';
  let pass;
  if (it.error) pass = false;
  else if (it.set === 'rag') {
    const retrievalOk = negative || m.hit_at_4 == null || m.hit_at_4 === 1;
    pass = judged ? m.correctness === 1 && retrievalOk : retrievalOk && (m.key_fact_recall ?? 0) === 1;
  } else {
    const exactOk = m.exact_value == null || m.exact_value === 1;
    pass = judged ? m.correctness === 1 && exactOk : exactOk && (m.exact_value != null || (m.key_fact_recall ?? 0) === 1);
  }

  const why = [];
  if (it.error) why.push(`error: ${it.error}`);
  if (j.reason && (m.correctness ?? 1) < 1) why.push(j.reason);
  else if (j.reason && (m.faithfulness ?? 1) < 1) why.push(j.reason);
  if (it.set === 'rag' && m.hit_at_4 === 0) why.push(`ไม่พบ ${pagesOf(it.sources)} ใน top 4`);
  if (it.set === 'rag' && m.citation_acc === 0) why.push(it.cites?.length ? `อ้างอิง ${srcText(it.cites)} ไม่ตรง` : 'ไม่มีป้ายอ้างอิง');
  if (m.exact_value === 0) why.push(`ไม่พบค่า ${(it.missing_values || []).join(', ')} ในคำตอบ`);
  if (m.sql_correct === 0) why.push(`products ไม่มี ${skusOf(it).filter((s) => !(it.products || []).includes(s)).join(', ') || 'ตัวเลขกติกาที่ถูก'}`);
  if (!judged) why.unshift('(ยังไม่ได้ตัดสิน · pass จาก metric โค้ด)');

  const expected =
    it.set === 'rag'
      ? { answer: it.expected, sources: it.sources || [], key_facts: it.key_facts || [] }
      : { answer: it.expected, values: it.expected_values || [], ...(it.sql ? { sql: it.sql } : {}) };
  return {
    id: it.id,
    set: it.set,
    ...(it.set === 'rag' ? { doc: it.sources?.[0]?.filename || '(ไม่มีแหล่ง)' } : {}),
    qtype: it.type || it.category || undefined,
    ...(it.difficulty ? { difficulty: it.difficulty } : {}),
    question: it.question,
    expected,
    ...(it.sources ? { sources: it.sources } : {}),
    answer: it.answer || '',
    retrieved: it.retrieved || [],
    cites: (it.cites || []).map(({ filename, page }) => ({ filename, page })),
    products: it.products || [],
    metrics: round(m),
    pass: !!pass,
    judged,
    reason: pass && judged ? '' : why.join(' · '),
    timing: it.timing,
  };
}

function scoreConv(it) {
  const j = judgments[it.id] || {};
  const jt = Array.isArray(j.turns) ? j.turns : [];
  const turns = (it.turns || []).map((t, i) => {
    const tj = jt[i] || {};
    const tm = { ...(t.metrics || {}) };
    const c = sc(tj.correctness);
    const r = i === 0 ? null : sc(tj.context_retention);
    if (c != null) tm.correctness = c;
    if (r != null) tm.context_retention = r;
    return {
      n: t.n ?? i + 1,
      q: t.q || t.ref_text,
      a: t.answer || '',
      ...(t.audio ? { audio: t.audio, ref_text: t.ref_text, transcript: t.stt?.text ?? null } : {}),
      ...(t.refers_to ? { refers_to: t.refers_to } : {}),
      expected: t.expected,
      ...(t.expected_values ? { values: t.expected_values } : {}),
      ...(t.key_facts ? { key_facts: t.key_facts } : {}),
      ...(t.sources ? { sources: t.sources } : {}),
      retrieved: t.retrieved || [],
      cites: (t.cites || []).map(({ filename, page }) => ({ filename, page })),
      products: t.products || [],
      ...(t.cartCount != null ? { cartCount: t.cartCount } : {}),
      ...(t.quoteNo ? { quoteNo: t.quoteNo } : {}),
      metrics: round(tm),
      ...(tj.reason ? { reason: tj.reason } : {}),
      ...(t.error ? { error: t.error } : {}),
      _missing: t.missing_values,
      _state: t.expect_state,
    };
  });

  const m = { ...(it.metrics || {}) };
  const perTurnC = turns.map((t) => t.metrics.correctness).filter((v) => v != null);
  const perTurnR = turns.slice(1).map((t) => t.metrics.context_retention).filter((v) => v != null);
  m.correctness = perTurnC.length ? mean(perTurnC) : sc(j.correctness);
  m.context_retention = perTurnR.length ? mean(perTurnR) : sc(j.context_retention);
  for (const k of Object.keys(m)) if (m[k] == null) delete m[k];
  const judged = m.correctness != null;

  let pass;
  const anyErr = turns.some((t) => t.error) || !turns.length;
  if (anyErr) pass = false;
  else if (perTurnC.length === turns.length) pass = perTurnC.every((v) => v === 1);
  else if (judged) pass = m.correctness === 1;
  else pass = turns.every((t) => (t.metrics.exact_value ?? t.metrics.key_fact_recall ?? 0) === 1 && (t.metrics.state_ok ?? 1) === 1);

  const why = [];
  if (!judged) why.push('(ยังไม่ได้ตัดสิน · pass จาก metric โค้ด)');
  if (j.reason && !pass) why.push(j.reason);
  for (const t of turns) {
    const bits = [];
    if (t.error) bits.push(`error: ${t.error}`);
    if ((t.metrics.correctness ?? 1) < 1 || (t.metrics.context_retention ?? 1) < 1) bits.push(t.reason || `correctness ${t.metrics.correctness ?? '–'} / retention ${t.metrics.context_retention ?? '–'}`);
    if (t.metrics.exact_value === 0) bits.push(`ไม่พบค่า ${(t._missing || []).join(', ')}`);
    if (t.metrics.state_ok === 0) bits.push(`สถานะไม่ตรง (คาด ${JSON.stringify(t._state)} ได้ cartCount ${t.cartCount ?? '–'}${t.quoteNo ? ` quote ${t.quoteNo}` : ''})`);
    if (bits.length) why.push(`รอบ ${t.n}: ${bits.join(' / ')}`);
  }
  for (const t of turns) {
    delete t._missing;
    delete t._state;
  }

  const seen = new Set();
  const retrieved = [];
  for (const t of turns)
    for (const r of t.retrieved) {
      const k = `${r.filename}#${r.page}`;
      if (seen.has(k)) continue;
      seen.add(k);
      retrieved.push(r);
    }
  const cites = [];
  const cs = new Set();
  for (const t of turns)
    for (const c of t.cites) {
      const k = `${c.filename}#${c.page}`;
      if (cs.has(k)) continue;
      cs.add(k);
      cites.push(c);
    }
  return {
    id: it.id,
    set: 'conv',
    qtype: it.voice ? 'voice' : 'multi-turn',
    title: it.title,
    question: it.question || turns.map((t) => t.q).join(' → '),
    turns,
    expected: { answer: (it.turns || []).map((t, i) => `${i + 1}) ${t.expected}`).join('\n') },
    answer: turns.map((t) => `${t.n}) ${t.a}`).join('\n'),
    retrieved: retrieved.slice(0, 8),
    cites,
    metrics: round(m),
    pass: !!pass,
    judged,
    reason: pass && judged ? '' : why.join(' · '),
  };
}

// ---------------------------------------------------------------- summary
function summarize(items) {
  const S = {};
  const bySet = (s) => items.filter((i) => i.set === s);
  const avg = (its, k) => mean(its.map((i) => i.metrics?.[k]));
  const base = (its) => ({ n: its.length, judged: its.filter((i) => i.judged).length, pass_rate: its.length ? its.filter((i) => i.pass).length / its.length : null });

  const rag = bySet('rag');
  if (rag.length)
    S.rag = clean({ hit_at_4: avg(rag, 'hit_at_4'), mrr: avg(rag, 'mrr'), citation_acc: avg(rag, 'citation_acc'), faithfulness: avg(rag, 'faithfulness'), correctness: avg(rag, 'correctness'), key_fact_recall: avg(rag, 'key_fact_recall'), ...base(rag) });
  const qa = bySet('qa');
  if (qa.length) S.qa = clean({ exact_value: avg(qa, 'exact_value'), sql_correct: avg(qa, 'sql_correct'), correctness: avg(qa, 'correctness'), ...base(qa) });
  const conv = bySet('conv');
  if (conv.length) {
    const turns = conv.flatMap((c) => c.turns);
    S.conv = clean({
      context_retention: mean(turns.slice().filter((t) => t.n > 1).map((t) => t.metrics.context_retention)) ?? avg(conv, 'context_retention'),
      correctness: mean(turns.map((t) => t.metrics.correctness)) ?? avg(conv, 'correctness'),
      stt_cer: mean(turns.map((t) => t.metrics.stt_cer)),
      exact_value: mean(turns.map((t) => t.metrics.exact_value)),
      hit_at_4: mean(turns.map((t) => t.metrics.hit_at_4)),
      state_ok: mean(turns.map((t) => t.metrics.state_ok)),
      ...base(conv),
      turns: turns.length,
      voice_turns: turns.filter((t) => t.audio).length,
    });
  }
  if (S.qa && !args['no-sql-alias']) S.sql = { ...S.qa, alias_of: 'qa' };

  // แยกตามเอกสาร (rag · นับทุกไฟล์ใน sources ของข้อ)
  const byDoc = {};
  for (const it of rag) {
    const files = [...new Set((it.sources || []).map((s) => s.filename))];
    for (const f of files.length ? files : ['(ไม่มีแหล่ง · negative)']) (byDoc[f] ||= []).push(it);
  }
  S.by_doc = mapVals(byDoc, (its) => clean({ hit_at_4: avg(its, 'hit_at_4'), mrr: avg(its, 'mrr'), citation_acc: avg(its, 'citation_acc'), faithfulness: avg(its, 'faithfulness'), correctness: avg(its, 'correctness'), ...base(its) }));

  // แยกตามประเภท: rag.type · qa.category · conv (เสียง/ข้อความ)
  S.by_type = {};
  for (const set of ['rag', 'qa', 'conv']) {
    const g = groupBy(bySet(set), (i) => i.qtype || '(ไม่ระบุ)');
    if (!Object.keys(g).length) continue;
    S.by_type[set] = mapVals(g, (its) =>
      clean(
        set === 'rag'
          ? { correctness: avg(its, 'correctness'), faithfulness: avg(its, 'faithfulness'), hit_at_4: avg(its, 'hit_at_4'), mrr: avg(its, 'mrr'), ...base(its) }
          : set === 'qa'
            ? { correctness: avg(its, 'correctness'), exact_value: avg(its, 'exact_value'), sql_correct: avg(its, 'sql_correct'), ...base(its) }
            : { correctness: avg(its, 'correctness'), context_retention: avg(its, 'context_retention'), stt_cer: avg(its, 'stt_cer'), ...base(its) },
      ),
    );
  }
  // แยกตามความยาก (rag)
  const byDiff = groupBy(rag.filter((i) => i.difficulty), (i) => i.difficulty);
  if (Object.keys(byDiff).length) S.by_difficulty = { rag: mapVals(byDiff, (its) => clean({ correctness: avg(its, 'correctness'), hit_at_4: avg(its, 'hit_at_4'), mrr: avg(its, 'mrr'), ...base(its) })) };

  // เวลา (ms) ต่อ set จาก answers
  S.latency = {};
  for (const set of ['rag', 'qa', 'conv']) {
    const src = answers.items.filter((i) => i.set === set).flatMap((i) => (set === 'conv' ? i.turns || [] : [i]));
    const ttft = src.map((x) => x.timing?.ttft_ms).filter(Number.isFinite);
    const tot = src.map((x) => x.timing?.total_ms).filter(Number.isFinite);
    if (tot.length) S.latency[set] = { ttft_p50: pct(ttft, 50), ttft_p95: pct(ttft, 95), total_p50: pct(tot, 50), total_p95: pct(tot, 95), n: tot.length };
  }
  return S;
}

function printSummary() {
  const show = (o) =>
    Object.entries(o)
      .filter(([, v]) => typeof v === 'number')
      .map(([k, v]) => `${k}=${['n', 'judged', 'turns', 'voice_turns'].includes(k) ? v : (v * 100).toFixed(1) + '%'}`)
      .join(' ');
  console.log(`score ${results.label} · ${items.length} ข้อ · ผ่าน ${items.filter((i) => i.pass).length} · ตัดสินแล้ว ${items.filter((i) => i.judged).length}`);
  for (const s of ['rag', 'qa', 'conv']) if (summary[s]) console.log(`  ${s.padEnd(4)} ${show(summary[s])}`);
  for (const [f, v] of Object.entries(summary.by_doc || {})) console.log(`    ${f.padEnd(22)} ${show(v)}`);
}

// ---------------------------------------------------------------- utils
function mean(vs) {
  const a = vs.filter((v) => typeof v === 'number' && Number.isFinite(v));
  return a.length ? a.reduce((s, v) => s + v, 0) / a.length : null;
}
function clean(o) {
  const out = {};
  for (const [k, v] of Object.entries(o)) if (v != null) out[k] = typeof v === 'number' && !Number.isInteger(v) ? Math.round(v * 1000) / 1000 : v;
  return out;
}
const round = (m) => clean(m);
function groupBy(a, f) {
  const o = {};
  for (const x of a) (o[f(x)] ||= []).push(x);
  return o;
}
const mapVals = (o, f) => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, f(v)]));
function pct(a, p) {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  return s[Math.min(s.length - 1, Math.floor((p / 100) * s.length))];
}
const srcText = (l) => (l || []).map((s) => `${s.filename} หน้า ${s.page}`).join(', ');
function pagesOf(sources) {
  const g = groupBy(sources || [], (s) => s.filename.replace(/\.pdf$/i, ''));
  return Object.entries(g).map(([f, ss]) => `หน้า ${ss.map((s) => s.page).join('/')} ของ ${f}`).join(' หรือ ') || 'หน้าที่ถูก';
}
const skusOf = (it) => [...new Set([...(it.needs_products || []), ...((it.sql || '').match(/[A-Z]{3}-\d{3}/g) || [])])];
function parseArgs(a) {
  const o = {};
  for (let i = 0; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const [k, inline] = a[i].slice(2).split('=', 2);
    if (inline !== undefined) o[k] = inline;
    else o[k] = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
  }
  return o;
}

await main();
