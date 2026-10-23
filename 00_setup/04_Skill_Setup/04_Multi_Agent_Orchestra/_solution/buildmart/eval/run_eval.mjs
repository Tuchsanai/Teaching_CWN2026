#!/usr/bin/env node
// eval/run_eval.mjs — ถามชุดประเมินผ่าน web API จริง แล้วคิด metric ที่คำนวณด้วยโค้ดได้ (BUILDMART ข้อ 8 · CONTRACT_V3 §7)
//
//   node run_eval.mjs --label mock-smoke [--base http://localhost:3400] [--set rag,qa,conv] [--limit n] [--concurrency 2]
//                     [--ids CV-01,Q-03] [--qa qa.json] [--mode mock|ai] [--rerank on|off] [--llm <ชื่อ>] [--stt <ชื่อ>] [--tts <ชื่อ>]
//                     [--no-voice] [--timeout 240000] [--batch-size 20] [--context-chars 1400] [--docs <LAB/documents>] [--pdf-engine auto|pymupdf|pdfjs]
//
// - ทุกข้อ (rag/qa) และทุกบท (conv) ใช้ session ใหม่: ไม่ส่ง cookie ตอนเริ่ม · รับ bm_sid จาก Set-Cookie แล้วใช้ต่อเฉพาะรอบถัดไปของบทเดียวกัน
// - รอบที่เป็นเสียง: POST /api/voice (multipart `audio` = ไฟล์ใน e2e/voice-fixtures) → เอา text ที่ถอดได้ไปถาม /api/chat
// - ไม่เรียก LLM ใด ๆ ที่นี่ — metric ที่ต้องใช้ผู้ตัดสินเขียนเป็น judge_batches/*.md ให้ Claude ตัดสิน (ดู README.md)
//
// ผลลัพธ์ → eval/runs/<label>/
//   answers.json            คำตอบ + cites + retrieved + products + เวลา + metric โค้ด (hit_at_4 mrr citation_acc exact_value sql_correct stt_cer key_fact_recall state_ok)
//   pages/<file>-p<N>.txt   ข้อความเต็มของหน้า PDF ที่ถูกค้นเจอ (หลักฐานให้ผู้ตัดสิน)
//   judge_batches/batch-NN.md + batch-NN.template.json   ชุดละ 20 ข้อ (conv: รวมไม่เกิน 20 รอบ)
import { readFileSync, readdirSync, writeFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { digitsForThaiNumbers } from '../shared/thainum.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const LAB = path.resolve(ROOT, '../..');

const args = parseArgs(process.argv.slice(2));
const BASE = String(args.base || process.env.EVAL_BASE || 'http://localhost:3400').replace(/\/+$/, '');
const LABEL = String(args.label || `run-${new Date().toISOString().slice(0, 16).replace(/[:T]/g, '')}`).replace(/[^\w.\-]+/g, '_');
const SETS = String(args.set || args.sets || 'rag,qa,conv').split(',').map((s) => s.trim()).filter(Boolean);
const LIMIT = args.limit ? Number(args.limit) : Infinity;
const CONC = Math.max(1, Number(args.concurrency || 2));
const IDS = args.ids ? new Set(String(args.ids).split(',').map((s) => s.trim())) : null;
const TIMEOUT = Number(args.timeout || 240_000);
const BATCH = Math.max(1, Number(args['batch-size'] || 20));
const CTX_CHARS = Number(args['context-chars'] || 1400);
const DOCS_DIR = path.resolve(String(args.docs || path.join(LAB, 'documents')));
const FIXTURES = path.resolve(String(args.fixtures || path.join(ROOT, 'e2e/voice-fixtures')));
const NO_VOICE = !!args['no-voice'];
const PDF_ENGINE = String(args['pdf-engine'] || 'auto'); // auto = PyMuPDF ก่อน แล้ว pdfjs
const OUT = path.join(HERE, 'runs', LABEL);

const config = buildConfig();
const warnings = [];

// ---------------------------------------------------------------- main
async function main() {
  const all = loadItems();
  const picked = pick(all);
  if (!picked.length) {
    console.error(`ไม่มีข้อให้ถาม (set=${SETS.join(',')}${IDS ? ` ids=${[...IDS].join(',')}` : ''})`);
    process.exit(1);
  }
  await preflight();

  mkdirSync(OUT, { recursive: true });
  console.log(`run_eval → ${BASE} · label ${LABEL} · ${picked.length} ข้อ/บท (${countBy(picked, (i) => i.set)}) · concurrency ${CONC}`);
  const started = new Date();
  let done = 0;
  const results = await pool(picked, CONC, async (item) => {
    const r = item.set === 'conv' ? await runConv(item) : await runSingle(item);
    done++;
    const flag = r.error || r.turns?.some((t) => t.error) ? '✗' : '✓';
    console.log(`  [${String(done).padStart(3)}/${picked.length}] ${flag} ${item.id.padEnd(12)} ${fmtMetrics(r.metrics)}`);
    return r;
  });

  const api = apiFieldReport(results);
  if (!api.retrieved) warnings.push('API ไม่ส่งฟิลด์ `retrieved` ใน SSE done (หรือว่างทุกข้อ) → hit_at_4/mrr = null (ข้าม)');
  if (!api.products) warnings.push('API ไม่ส่งฟิลด์ `products` ใน SSE done → sql_correct (ข้อที่อ้าง SKU) = null');

  const answers = {
    meta: {
      label: LABEL,
      base: BASE,
      started: started.toISOString(),
      finished: new Date().toISOString(),
      config,
      sets: SETS,
      counts: Object.fromEntries(SETS.map((s) => [s, results.filter((r) => r.set === s).length])),
      api,
      warnings,
      args: { limit: Number.isFinite(LIMIT) ? LIMIT : null, ids: IDS ? [...IDS] : null, concurrency: CONC, voice: !NO_VOICE },
    },
    items: results,
  };
  writeFileSync(path.join(OUT, 'answers.json'), JSON.stringify(answers, null, 2) + '\n');
  const pages = await writePages(results);
  const batches = writeJudgeBatches(results);

  console.log(`\n→ ${rel(path.join(OUT, 'answers.json'))}`);
  console.log(`→ ${rel(path.join(OUT, 'pages'))} (${pages} หน้า)  · judge_batches: ${batches} ชุด`);
  printSummary(results);
  for (const w of warnings) console.log(`⚠ ${w}`);
  console.log(`\nขั้นต่อไป: ให้ Claude ตัดสินตาม ${rel(path.join(OUT, 'judge_batches'))}/batch-*.md → แล้ว node score.mjs --label ${LABEL} [--post ${BASE}]`);
}

// ---------------------------------------------------------------- โหลดชุดคำถาม
function loadItems() {
  const file = path.resolve(HERE, String(args.qa || 'qa.json'));
  if (existsSync(file)) return JSON.parse(readFileSync(file, 'utf8'));
  // ยังไม่ได้ merge → รวม parts/*.json ในหน่วยความจำ (ไม่เขียน qa.json)
  const dir = path.join(HERE, 'parts');
  if (!existsSync(dir)) throw new Error(`ไม่พบ ${file} และ ${dir}`);
  warnings.push(`ไม่พบ ${rel(file)} → ใช้ parts/*.json โดยตรง (รัน node merge.mjs เพื่อตรวจ id ซ้ำ)`);
  const out = [];
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.json')).sort()) {
    try {
      const d = JSON.parse(readFileSync(path.join(dir, f), 'utf8'));
      out.push(...(Array.isArray(d) ? d : d.items || []));
    } catch (e) {
      warnings.push(`อ่าน parts/${f} ไม่ได้: ${e.message}`);
    }
  }
  return out;
}

function pick(items) {
  const per = {};
  return items.filter((it) => {
    const set = it.set || (Array.isArray(it.turns) ? 'conv' : undefined);
    if (!SETS.includes(set)) return false;
    if (IDS && !IDS.has(it.id)) return false;
    per[set] = (per[set] || 0) + 1;
    return per[set] <= LIMIT;
  });
}

async function preflight() {
  try {
    const r = await fetch(`${BASE}/api/health`, { signal: AbortSignal.timeout(10_000) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) warnings.push(`/api/health ตอบ ${r.status}`);
    config.instance = j.instanceId;
  } catch (e) {
    console.error(`เชื่อมต่อ ${BASE} ไม่ได้ (${e.message}) — stack รันอยู่หรือเปล่า?`);
    process.exit(2);
  }
  if (SETS.includes('conv') && !NO_VOICE) {
    try {
      const v = await (await fetch(`${BASE}/api/voice/status`, { signal: AbortSignal.timeout(10_000) })).json();
      if (!v?.enabled) warnings.push('/api/voice/status enabled=false (ไม่มี stt-worker) → รอบเสียงใช้ข้อความอ้างอิงแทน');
      config.voice = !!v?.enabled;
    } catch {
      warnings.push('/api/voice/status ใช้ไม่ได้ → รอบเสียงใช้ข้อความอ้างอิงแทน');
      config.voice = false;
    }
  }
}

function buildConfig() {
  const mode = String(args.mode || process.env.MODE || 'unknown');
  const rerankOn = !/^(off|false|0|no)$/i.test(String(args.rerank ?? process.env.RERANK ?? 'on'));
  const ai = mode === 'ai';
  return {
    mode,
    llm: String(args.llm || (ai ? process.env.LLM_MODEL || 'Qwen3.8-27B-nvfp4' : mode === 'mock' ? 'mock-llm' : 'unknown')),
    rerank: rerankOn ? String(args['rerank-model'] || (ai ? 'bge-reranker-v2-m3' : mode === 'mock' ? 'mock (ลำดับเดิม)' : 'on')) : 'off',
    stt: String(args.stt || (ai ? 'whisper-large-v3' : mode === 'mock' ? 'mock (sha256/fingerprint)' : 'unknown')),
    tts: String(args.tts || (ai ? 'voxcpm2' : mode === 'mock' ? 'mock (tts-cache)' : 'unknown')),
    top_k: 4,
    candidates: 20,
  };
}

// ---------------------------------------------------------------- เรียก API
/** POST /api/chat → อ่าน SSE จนจบ · jar = {cookie} ของ session (null = session ใหม่) */
async function chat(text, jar) {
  const t0 = Date.now();
  const out = { text: '', cites: [], retrieved: null, products: null, cartCount: null, quoteNo: null, error: null, ttft_ms: null, total_ms: null, fields: [] };
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT);
  try {
    const res = await fetch(`${BASE}/api/chat`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', accept: 'text/event-stream', ...(jar.cookie ? { cookie: jar.cookie } : {}) },
      body: JSON.stringify({ text }),
      signal: ctrl.signal,
    });
    takeCookie(res, jar);
    if (!res.ok || !res.body) {
      out.error = `HTTP ${res.status} ${(await res.text().catch(() => '')).slice(0, 200)}`;
      return out;
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    let finished = false;
    while (!finished) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const raw = buf.slice(0, i);
        buf = buf.slice(i + 2);
        const ev = parseEvent(raw);
        if (!ev) continue;
        if (ev.event === 'delta') {
          if (out.ttft_ms == null) out.ttft_ms = Date.now() - t0;
          out.text = ev.data?.text ?? out.text;
        } else if (ev.event === 'done') {
          const d = ev.data || {};
          out.fields = Object.keys(d);
          out.text = d.text ?? out.text;
          out.cites = Array.isArray(d.cites) ? d.cites.map((c) => ({ filename: c.filename, page: Number(c.page), ...(c.snippet ? { snippet: c.snippet } : {}) })) : [];
          out.retrieved = Array.isArray(d.retrieved) ? d.retrieved.map((r) => ({ filename: r.filename, page: Number(r.page), score: r.score })) : null;
          out.products = Array.isArray(d.products) ? d.products : null;
          out.cartCount = typeof d.cartCount === 'number' ? d.cartCount : null;
          out.quoteNo = d.quoteNo || null;
          if (out.ttft_ms == null) out.ttft_ms = Date.now() - t0;
          finished = true;
        } else if (ev.event === 'error') {
          out.error = ev.data?.message || ev.data?.error || 'error';
          finished = true;
        }
      }
    }
    try {
      await reader.cancel();
    } catch {
      /* ปิดแล้ว */
    }
    if (!finished && !out.error) out.error = 'stream จบโดยไม่มี done';
  } catch (e) {
    out.error = e.name === 'AbortError' ? `timeout ${TIMEOUT} ms` : String(e.message || e);
  } finally {
    clearTimeout(timer);
    out.total_ms = Date.now() - t0;
  }
  return out;
}

function parseEvent(raw) {
  let event = 'message';
  const data = [];
  for (const line of raw.split('\n')) {
    if (line.startsWith(':')) continue;
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''));
  }
  if (!data.length) return null;
  try {
    return { event, data: JSON.parse(data.join('\n')) };
  } catch {
    return { event, data: { text: data.join('\n') } };
  }
}

function takeCookie(res, jar) {
  const list = typeof res.headers.getSetCookie === 'function' ? res.headers.getSetCookie() : [res.headers.get('set-cookie') || ''];
  for (const c of list) {
    const m = /(?:^|,\s*)bm_sid=([^;,\s]+)/.exec(c || '');
    if (m) jar.cookie = `bm_sid=${m[1]}`;
  }
}

/** POST /api/voice ด้วยไฟล์ fixture → {text, language, durationMs, ms, error} */
async function voice(file, lang, jar) {
  const t0 = Date.now();
  try {
    const buf = readFileSync(file);
    const fd = new FormData();
    fd.append('audio', new Blob([buf], { type: mimeOf(file) }), path.basename(file));
    if (lang) fd.append('lang', lang);
    const res = await fetch(`${BASE}/api/voice`, {
      method: 'POST',
      body: fd,
      headers: jar.cookie ? { cookie: jar.cookie } : {},
      signal: AbortSignal.timeout(90_000),
    });
    takeCookie(res, jar);
    const j = await res.json().catch(() => ({}));
    if (!res.ok) return { text: String(j.text || ''), error: `HTTP ${res.status} ${j.error || ''}`.trim(), ms: Date.now() - t0 };
    return { text: String(j.text || '').trim(), language: j.language ?? null, durationMs: j.durationMs ?? null, engine: j.engine, ms: Date.now() - t0 };
  } catch (e) {
    return { text: '', error: String(e.message || e), ms: Date.now() - t0 };
  }
}

const mimeOf = (f) => ({ '.wav': 'audio/wav', '.webm': 'audio/webm', '.ogg': 'audio/ogg', '.mp3': 'audio/mpeg' })[path.extname(f).toLowerCase()] || 'application/octet-stream';

function fixturePath(audio) {
  for (const p of [path.resolve(FIXTURES, audio), path.resolve(ROOT, audio), path.resolve(HERE, audio)]) if (existsSync(p)) return p;
  return null;
}

// ---------------------------------------------------------------- ถามทีละข้อ / ทีละบท
async function runSingle(it) {
  const jar = { cookie: null }; // session ใหม่ต่อข้อ
  const r = await chat(it.question, jar);
  const out = {
    id: it.id,
    set: it.set,
    ...(it.type ? { type: it.type } : {}),
    ...(it.category ? { category: it.category } : {}),
    ...(it.difficulty ? { difficulty: it.difficulty } : {}),
    question: it.question,
    expected: it.expected,
    ...(it.key_facts ? { key_facts: it.key_facts } : {}),
    ...(it.expected_values ? { expected_values: it.expected_values } : {}),
    ...(it.sources ? { sources: it.sources } : {}),
    ...(it.sql ? { sql: it.sql } : {}),
    ...(it.needs_products ? { needs_products: it.needs_products } : {}),
    ...(it.volatile ? { volatile: true } : {}),
    answer: r.text,
    cites: r.cites,
    retrieved: r.retrieved,
    products: r.products,
    cartCount: r.cartCount,
    quoteNo: r.quoteNo,
    done_fields: r.fields,
    timing: { ttft_ms: r.ttft_ms, total_ms: r.total_ms },
    error: r.error,
  };
  out.metrics = codeMetrics(out, it.set);
  return out;
}

async function runConv(it) {
  const jar = { cookie: null }; // session ใหม่ต่อบท · ใช้ cookie เดิมทุกรอบในบท
  const turns = [];
  for (const [i, t] of (it.turns || []).entries()) {
    const turn = {
      n: i + 1,
      ...(t.audio ? { audio: t.audio } : {}),
      ref_text: t.text || null,
      ...(t.refers_to ? { refers_to: t.refers_to } : {}),
      expected: t.expected,
      ...(t.key_facts ? { key_facts: t.key_facts } : {}),
      ...(t.expected_values ? { expected_values: t.expected_values } : {}),
      ...(t.sources ? { sources: t.sources } : {}),
      ...(t.needs_products ? { needs_products: t.needs_products } : {}),
      ...(t.expect_state ? { expect_state: t.expect_state } : {}),
      ...(t.volatile ? { volatile: true } : {}),
    };
    let q = t.text || '';
    if (t.audio) {
      const file = NO_VOICE || config.voice === false ? null : fixturePath(t.audio);
      if (!file) {
        turn.stt = { skipped: NO_VOICE || config.voice === false ? 'voice ปิด' : `ไม่พบไฟล์ ${t.audio}` };
      } else {
        const v = await voice(file, t.lang, jar);
        turn.stt = v;
        if (v.text) q = v.text;
        else turn.stt.fallback = 'ถอดเสียงไม่ได้ → ใช้ข้อความอ้างอิงถามแทน';
        turn.stt_cer = cerMin(v.text || '', [t.text, ...(t.accept || [])]);
      }
    }
    if (!q) {
      turn.error = 'ไม่มีข้อความถาม';
      turns.push(turn);
      continue;
    }
    const r = await chat(q, jar);
    Object.assign(turn, {
      q,
      answer: r.text,
      cites: r.cites,
      retrieved: r.retrieved,
      products: r.products,
      cartCount: r.cartCount,
      quoteNo: r.quoteNo,
      done_fields: r.fields,
      timing: { stt_ms: turn.stt?.ms ?? null, ttft_ms: r.ttft_ms, total_ms: r.total_ms },
      error: r.error,
    });
    turn.metrics = codeMetrics(turn, 'conv');
    if (turn.stt_cer != null) turn.metrics.stt_cer = turn.stt_cer;
    turns.push(turn);
  }
  const out = {
    id: it.id,
    set: 'conv',
    title: it.title,
    voice: !!(it.voice || it.turns?.some((t) => t.audio)),
    question: turns.map((t) => t.q || t.ref_text).join(' → '),
    turns,
  };
  // รวมต่อบท = เฉลี่ยของรอบที่มีค่า
  const keys = ['hit_at_4', 'mrr', 'citation_acc', 'exact_value', 'sql_correct', 'key_fact_recall', 'state_ok', 'stt_cer'];
  out.metrics = {};
  for (const k of keys) {
    const v = mean(turns.map((t) => t.metrics?.[k]));
    if (v != null) out.metrics[k] = round3(v);
  }
  return out;
}

// ---------------------------------------------------------------- metric ที่คิดด้วยโค้ด
function codeMetrics(x, set) {
  const m = {};
  const answer = x.answer || '';
  const hasSrc = Array.isArray(x.sources) && x.sources.length > 0;
  const negative = x.type === 'negative';
  if (hasSrc && !negative) {
    if (x.retrieved) {
      const top = x.retrieved.slice(0, 4);
      const rank = top.findIndex((r) => srcMatch(r, x.sources)) + 1;
      m.hit_at_4 = rank > 0 ? 1 : 0;
      m.mrr = rank > 0 ? round3(1 / rank) : 0;
    }
    const cites = x.cites || [];
    const files = new Set(x.sources.map((s) => normFile(s.filename)));
    m.citation_acc = cites.length && cites.some((c) => srcMatch(c, x.sources)) && cites.every((c) => files.has(normFile(c.filename))) ? 1 : 0;
  }
  if (Array.isArray(x.expected_values) && x.expected_values.length) {
    const miss = x.expected_values.filter((v) => !valueMatch(answer, v));
    m.exact_value = miss.length ? 0 : 1;
    if (miss.length) x.missing_values = miss.map((v) => (Array.isArray(v) ? v[0] : v));
  }
  if (Array.isArray(x.key_facts) && x.key_facts.length) {
    const hit = x.key_facts.filter((f) => valueMatch(answer, f));
    m.key_fact_recall = round3(hit.length / x.key_facts.length);
    const miss = x.key_facts.filter((f) => !valueMatch(answer, f));
    if (miss.length) x.missing_facts = miss.map((v) => (Array.isArray(v) ? v[0] : v));
  }
  // sql_correct: products ⊇ SKU ที่ข้อนั้นอ้าง (needs_products ∪ SKU ใน sql) · ข้อคูปอง/ค่าส่ง/ยอดรวม = ตัวเลขตรง
  const skus = [...new Set([...(x.needs_products || []), ...((x.sql || '').match(/[A-Z]{3}-\d{3}/g) || [])])];
  if (set === 'qa' || (set === 'conv' && x.needs_products?.length)) {
    if (skus.length) {
      if (Array.isArray(x.products)) m.sql_correct = skus.every((s) => x.products.includes(s)) ? 1 : 0;
    } else if (set === 'qa' && (x.sql || /coupon|shipping|cart_total/.test(x.category || '')) && m.exact_value != null) {
      m.sql_correct = m.exact_value;
    }
  }
  if (x.expect_state) {
    const s = x.expect_state;
    const ok = (s.cartCount == null || x.cartCount === s.cartCount) && (!s.quoteNo || !!x.quoteNo);
    m.state_ok = ok ? 1 : 0;
  }
  return m;
}

const normFile = (f) => path.basename(String(f || '')).toLowerCase().replace(/\.pdf$/, '');
const srcMatch = (r, sources) => sources.some((s) => normFile(s.filename) === normFile(r.filename) && Number(s.page) === Number(r.page));

const THAI_DIGITS = '๐๑๒๓๔๕๖๗๘๙';
function thaiDigits(s) {
  return String(s).replace(/[๐-๙]/g, (d) => String(THAI_DIGITS.indexOf(d)));
}
/** normalize สำหรับ match ข้อความ: NFC · เลขไทย→อารบิก · ตัด , ในตัวเลข · ตัวพิมพ์เล็ก · ตัดช่องว่าง · ขีดทุกแบบ → - · × → x */
function norm(s) {
  return thaiDigits(String(s ?? '').normalize('NFC'))
    .replace(/(\d),(?=\d)/g, '$1')
    .toLowerCase()
    .replace(/[–—−‑]/g, '-')
    .replace(/[×✕]/g, 'x')
    .replace(/\s+/g, '');
}
function numbersIn(s) {
  const t = thaiDigits(String(s ?? '')).replace(/(\d),(?=\d{3}\b)/g, '$1').replace(/(\d),(?=\d)/g, '$1');
  return (t.match(/\d+(?:\.\d+)?/g) || []).map(Number);
}
const NUMERIC = /^\s*[\d,]+(?:\.\d+)?\s*$/;
/** ค่า 1 ตัว (หรือ array ของรูปเขียนที่ยอมรับ) อยู่ในคำตอบไหม · ตัวเลขล้วนเทียบเชิงตัวเลข (137.75 = 137.750 · "13,775" = 13775) */
function valueMatch(answer, v) {
  if (Array.isArray(v)) return v.some((x) => valueMatch(answer, x));
  if (typeof v === 'number' || NUMERIC.test(String(v))) {
    const want = Number(String(v).replace(/,/g, ''));
    return numbersIn(answer).some((n) => Math.abs(n - want) < 1e-6);
  }
  const nv = norm(v);
  return nv.length > 0 && norm(answer).includes(nv);
}

/** CER = (S+D+I)/N ระดับตัวอักษร · normalize: ตัดช่องว่าง/เครื่องหมาย · ตัวพิมพ์เล็ก · เลขไทย→อารบิก · ค่าต่ำสุดเทียบข้อความหลัก + accept */
function cerMin(hyp, refs) {
  const vals = refs.filter(Boolean).map((r) => cer(hyp, r));
  return vals.length ? round3(Math.min(...vals)) : null;
}
function cerNorm(s) {
  // คำตัวเลขไทย → ตัวเลข ทั้งสองฝั่ง ("สองจุดห้า"→2.5 · "ร้อยถุง"→100 ถุง · "หกสิบคูณหกสิบ"→60x60 · "ดีบี 12"→DB12)
  return thaiDigits(digitsForThaiNumbers(String(s || '').normalize('NFC')))
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}]+/gu, '');
}
function cer(hyp, ref) {
  const a = Array.from(cerNorm(ref));
  const b = Array.from(cerNorm(hyp));
  if (!a.length) return b.length ? 1 : 0;
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    prev = cur;
  }
  return prev[b.length] / a.length;
}

// ---------------------------------------------------------------- หน้า PDF (หลักฐานให้ผู้ตัดสิน)
let pdfjs; // undefined = ยังไม่โหลด · null = ใช้ไม่ได้
const pageCache = new Map(); // filename → string[] (index 0 = หน้า 1)

async function loadPdfjs() {
  if (pdfjs !== undefined) return pdfjs;
  const tries = [
    'pdfjs-dist/legacy/build/pdf.mjs',
    pathToFileURL(path.join(ROOT, 'workers/node_modules/pdfjs-dist/legacy/build/pdf.mjs')).href,
    pathToFileURL(path.join(ROOT, 'web/node_modules/pdfjs-dist/legacy/build/pdf.mjs')).href,
  ];
  for (const t of tries) {
    try {
      pdfjs = await import(t);
      return pdfjs;
    } catch {
      /* ลองตัวถัดไป */
    }
  }
  pdfjs = null;
  warnings.push('โหลด pdfjs-dist ไม่ได้ (npm i ใน eval/ หรือ workers/) → judge batch ใช้เฉพาะ snippet ของ cites');
  return null;
}

async function pdfPages(filename) {
  const key = path.basename(filename);
  if (pageCache.has(key)) return pageCache.get(key);
  const file = path.join(DOCS_DIR, key.endsWith('.pdf') ? key : `${key}.pdf`);
  let pages = null;
  if (existsSync(file)) {
    if (PDF_ENGINE !== 'pdfjs') pages = pymupdfPages(file);
    if (!pages && PDF_ENGINE !== 'pymupdf') pages = await pdfjsPages(file, key);
  }
  pageCache.set(key, pages);
  return pages;
}

/** PyMuPDF (ข้อความไทยสะอาดกว่า pdfjs) · ใช้ python ในเครื่องถ้ามี fitz · ไม่มี → null */
const PY_EXTRACT = [
  'import sys,json',
  'sys.stdout.reconfigure(encoding="utf-8")',
  'import fitz',
  'd=fitz.open(sys.argv[1])',
  'print(json.dumps([p.get_text() for p in d],ensure_ascii=False))',
].join('\n');
let pyBroken = false;
function pymupdfPages(file) {
  if (pyBroken) return null;
  for (const py of [process.env.PYTHON, 'python', 'python3', 'py'].filter(Boolean)) {
    const r = spawnSync(py, ['-I', '-c', PY_EXTRACT, file], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, windowsHide: true });
    if (r.status === 0 && r.stdout) {
      try {
        return JSON.parse(r.stdout);
      } catch {
        /* ลองตัวถัดไป */
      }
    }
  }
  pyBroken = true;
  warnings.push('ไม่มี python + PyMuPDF (fitz) → ใช้ pdfjs-dist ดึงข้อความหน้า PDF (สระ/วรรณยุกต์ไทยบางตัวอาจเพี้ยน)');
  return null;
}

async function pdfjsPages(file, key) {
  const lib = await loadPdfjs();
  if (!lib) return null;
  try {
    const doc = await lib.getDocument({ data: new Uint8Array(readFileSync(file)), isEvalSupported: false, useSystemFonts: false, disableFontFace: true, verbosity: 0 }).promise;
    const pages = [];
    for (let i = 1; i <= doc.numPages; i++) {
      const tc = await (await doc.getPage(i)).getTextContent();
      const t = tc.items.map((x) => (x.str ?? '') + (x.hasEOL ? '\n' : '')).join('');
      // pdfjs แยกสระอำเป็น นิคหิต + อา → รวมกลับ
      pages.push(t.normalize('NFC').replace(/ํา/g, 'ำ').replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n'));
    }
    await doc.destroy();
    return pages;
  } catch (e) {
    warnings.push(`pdfjs อ่าน ${key} ไม่ได้: ${e.message}`);
    return null;
  }
}

async function pageText(filename, page) {
  const pages = await pdfPages(filename);
  return pages?.[Number(page) - 1] ?? null;
}

async function writePages(results) {
  const want = new Map();
  const addSrc = (list) => (list || []).forEach((r) => r?.filename && want.set(`${path.basename(r.filename)}#${r.page}`, r));
  for (const r of results) {
    for (const x of r.set === 'conv' ? r.turns : [r]) {
      addSrc(x.retrieved?.slice(0, 4));
      addSrc(x.cites);
    }
  }
  if (!want.size) return 0;
  const dir = path.join(OUT, 'pages');
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  let n = 0;
  for (const r of want.values()) {
    const t = await pageText(r.filename, r.page);
    if (t == null) continue;
    writeFileSync(path.join(dir, pageFile(r.filename, r.page)), t);
    n++;
  }
  return n;
}
const pageFile = (f, p) => `${path.basename(f).replace(/\.pdf$/i, '')}-p${p}.txt`;

/** ย่อหน้าที่เกี่ยวที่สุดในหน้า (เทียบ trigram กับ คำถาม+คำตอบ) ยาวไม่เกิน CTX_CHARS */
function excerpt(text, query) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  if (t.length <= CTX_CHARS) return t;
  const grams = (s) => {
    const z = norm(s);
    const g = new Set();
    for (let i = 0; i + 3 <= z.length; i++) g.add(z.slice(i, i + 3));
    return g;
  };
  const q = grams(query);
  const W = Math.max(300, Math.floor(CTX_CHARS / 2));
  const wins = [];
  for (let s = 0; s < t.length; s += Math.floor(W / 2)) {
    const w = t.slice(s, s + W);
    let score = 0;
    for (const g of grams(w)) if (q.has(g)) score++;
    wins.push({ s, w, score });
  }
  wins.sort((a, b) => b.score - a.score);
  const chosen = [];
  for (const w of wins) {
    if (chosen.length >= 2) break;
    if (chosen.every((c) => Math.abs(c.s - w.s) >= W)) chosen.push(w);
  }
  chosen.sort((a, b) => a.s - b.s);
  return chosen.map((c) => (c.s > 0 ? '… ' : '') + c.w.trim() + ' …').join('\n');
}

// ---------------------------------------------------------------- judge batches (ให้ Claude ตัดสิน)
function writeJudgeBatches(results) {
  const dir = path.join(OUT, 'judge_batches');
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  const groups = [];
  for (const set of ['rag', 'qa']) {
    const its = results.filter((r) => r.set === set);
    for (let i = 0; i < its.length; i += BATCH) groups.push(its.slice(i, i + BATCH));
  }
  // conv: รวมบทจนจำนวนรอบไม่เกิน BATCH
  let cur = [];
  let turns = 0;
  for (const c of results.filter((r) => r.set === 'conv')) {
    if (cur.length && turns + c.turns.length > BATCH) {
      groups.push(cur);
      cur = [];
      turns = 0;
    }
    cur.push(c);
    turns += c.turns.length;
  }
  if (cur.length) groups.push(cur);

  groups.forEach((g, gi) => {
    const no = String(gi + 1).padStart(2, '0');
    const md = [batchHeader(no, g), ...g.map((r, i) => (r.set === 'conv' ? convBlock(r, i + 1) : singleBlock(r, i + 1)))].join('\n');
    writeFileSync(path.join(dir, `batch-${no}.md`), md);
    const tpl = {};
    for (const r of g) tpl[r.id] = template(r);
    writeFileSync(path.join(dir, `batch-${no}.template.json`), JSON.stringify(tpl, null, 2) + '\n');
  });
  return groups.length;
}

function template(r) {
  if (r.set === 'rag') return { faithfulness: null, correctness: null, reason: '' };
  if (r.set === 'qa') return { correctness: null, reason: '' };
  return {
    turns: r.turns.map((t) => (t.n === 1 ? { correctness: null, reason: '' } : { correctness: null, context_retention: null, reason: '' })),
    reason: '',
  };
}

function batchHeader(no, g) {
  const sets = [...new Set(g.map((r) => r.set))].join(', ');
  return `# Judge batch ${no} · run \`${LABEL}\` · ${g.length} ${sets === 'conv' ? 'บท' : 'ข้อ'} (set: ${sets})

> **คุณ (Claude) คือผู้ตัดสิน** — อ่านทุกข้อด้านล่างแล้วให้คะแนนตาม rubric (ฉบับเต็มใน \`eval/README.md\` หัวข้อ "Rubric ผู้ตัดสิน")
> เขียนผลเป็น JSON ลงไฟล์ \`batch-${no}.judgments.json\` ในโฟลเดอร์นี้ (คัดลอกโครงจาก \`batch-${no}.template.json\` แล้วเติมค่า) — \`score.mjs\` จะรวมทุกไฟล์ \`*.judgments.json\` + \`../judgments.json\` ให้เอง
> คะแนนใช้ได้แค่ **0 · 0.5 · 1** · \`reason\` = ภาษาไทยสั้น ๆ (บังคับเมื่อคะแนน < 1 เช่น "ตอบ 64 แทน 48", "แต่งระยะเวลาที่ไม่มีในเอกสาร")

**Rubric ย่อ**
- \`correctness\` (ทุก set): 1 = ข้อเท็จจริงหลัก/ตัวเลขตาม "คำตอบที่คาด" ครบและถูก (ถ้อยคำต่างได้ หน่วยเทียบเท่าได้) · 0.5 = ถูกบางส่วน/ขาดบางค่า/มีค่าเกินที่ผิดเล็กน้อย · 0 = ผิด ไม่ตอบ ตอบคนละเรื่อง หรือ error · ข้อ \`negative\`/นอกเรื่อง: 1 เมื่อบอกว่าไม่มีข้อมูล/ปฏิเสธสุภาพโดยไม่แต่ง · ข้อ \`ambiguous\`: 1 เมื่อถามกลับหรือให้ตัวเลือกที่ถูก
- \`faithfulness\` (rag): แยกคำตอบเป็นข้อกล่าวอ้าง → สัดส่วนที่มีหลักฐานใน "ย่อหน้าที่ค้นได้" ปัดเป็น 1 (ทุกข้อมีหลักฐาน) · 0.5 (มีบางข้อไม่มีหลักฐาน) · 0 (ส่วนใหญ่/ประเด็นหลักไม่มีหลักฐาน) · คำตอบปฏิเสธว่าไม่มีข้อมูล = 1 · ตัวเลขราคา/สต็อกจาก DB ไม่ต้องมีหลักฐานใน PDF
- \`context_retention\` (conv · ตั้งแต่รอบ 2): 1 = ตีความสิ่งที่อ้างถึง ("อันนั้น" "ตัวเมื่อกี้" "แล้วถ้า…ล่ะ" "ใส่ตะกร้า") ตรงกับ \`refers_to\` · 0.5 = ถูกครึ่งเดียว (เช่น ถูกสินค้าแต่ผิดจำนวน) · 0 = ตีความผิด/ลืมบริบท/ถามซ้ำทั้งที่บริบทชัด · ให้คะแนนการตีความ ไม่ใช่ความถูกของตัวเลข
- metric โค้ด (hit/mrr/exact/key_fact) แสดงไว้ช่วยดูเท่านั้น — ตัดสินจากเนื้อหาจริง · ถ้าหลักฐานใน excerpt ไม่พอ เปิดหน้าเต็มที่ \`../pages/<ไฟล์>-p<หน้า>.txt\`
- ข้อที่ \`volatile\` (สต็อก) ตัวเลขอาจเปลี่ยนเพราะมีการตัดสต็อกระหว่างทดสอบ: ถ้าคำตอบสอดคล้องกับ "สินค้าที่ดึงจาก DB" ให้ถือว่าถูก

`;
}

function srcList(list) {
  return (list || []).map((s) => `${s.filename} หน้า ${s.page}`).join(' · ') || '–';
}
function ctxBlock(x, query) {
  const lines = [];
  const top = (x.retrieved || []).slice(0, 4);
  top.forEach((r, i) => {
    const t = pageCache.get(path.basename(r.filename))?.[Number(r.page) - 1];
    const hit = x.sources && srcMatch(r, x.sources) ? ' ✓ตรง sources' : '';
    lines.push(`  ${i + 1}. **${r.filename} หน้า ${r.page}** (score ${r.score ?? '–'})${hit}`);
    if (t) lines.push('     > ' + excerpt(t, query).replace(/\n/g, '\n     > '));
  });
  if (!top.length) lines.push(x.retrieved ? '  (ไม่มีย่อหน้าที่ค้นได้ — คำถาม DB/ทั่วไป)' : '  (API ไม่ส่ง `retrieved`)');
  const snips = (x.cites || []).filter((c) => c.snippet);
  if (snips.length) lines.push('  - snippet ของ cites: ' + snips.map((c) => `「${c.snippet.slice(0, 300)}」(${c.filename} หน้า ${c.page})`).join(' · '));
  return lines.join('\n');
}
function expectLines(x) {
  const out = [`- **คำตอบที่คาด:** ${typeof x.expected === 'string' ? x.expected : JSON.stringify(x.expected)}`];
  if (x.key_facts) out.push(`- **key_facts:** ${x.key_facts.map((f) => (Array.isArray(f) ? f.join(' / ') : f)).join(' · ')}`);
  if (x.expected_values) out.push(`- **expected_values:** ${x.expected_values.map((f) => (Array.isArray(f) ? f.join(' / ') : f)).join(' · ')}`);
  if (x.sources) out.push(`- **sources:** ${srcList(x.sources)}`);
  if (x.sql) out.push(`- **sql:** \`${x.sql}\``);
  return out.join('\n');
}
function actualLines(x) {
  const out = [];
  out.push(`- **คำตอบจริง:**${x.error ? ` ⚠ error: ${x.error}` : ''}\n\n${quote(x.answer)}\n`);
  out.push(`- **cites:** ${srcList(x.cites)} · **สินค้าที่ดึงจาก DB (products):** ${x.products ? x.products.join(', ') || '–' : '(API ไม่ส่ง)'}${x.cartCount != null ? ` · cartCount ${x.cartCount}` : ''}${x.quoteNo ? ` · quoteNo ${x.quoteNo}` : ''}`);
  out.push(`- **metric โค้ด:** ${fmtMetrics(x.metrics) || '–'}${x.missing_values ? ` · ค่าที่ไม่พบ: ${x.missing_values.join(', ')}` : ''}${x.missing_facts ? ` · key_fact ที่ไม่พบ: ${x.missing_facts.join(', ')}` : ''}`);
  return out.join('\n');
}
const quote = (s) => (String(s || '(ว่าง)').trim() || '(ว่าง)').split('\n').map((l) => `> ${l}`).join('\n');

function singleBlock(r, i) {
  const kind = [r.set, r.type || r.category, r.difficulty, r.volatile ? 'volatile' : ''].filter(Boolean).join(' · ');
  return `---
## ${i}. \`${r.id}\` (${kind})
- **คำถาม:** ${r.question}
${expectLines(r)}
${actualLines(r)}
- **ย่อหน้าที่ค้นได้ (top 4):**
${ctxBlock(r, `${r.question} ${r.answer || ''}`)}
`;
}

function convBlock(r, i) {
  const head = `---
## ${i}. \`${r.id}\` (conv${r.voice ? ' · 🎙 เสียง' : ''}) — ${r.title || ''}
`;
  const body = r.turns
    .map((t) => {
      const stt = t.audio
        ? `- **เสียง:** \`${t.audio}\` · ข้อความจริง: "${t.ref_text}" · ถอดได้: "${t.stt?.text ?? ''}"${t.stt_cer != null ? ` · CER ${t.stt_cer}` : ''}${t.stt?.skipped ? ` · (${t.stt.skipped} → ใช้ข้อความจริงถาม)` : ''}${t.stt?.fallback ? ` · (${t.stt.fallback})` : ''}\n`
        : '';
      return `### รอบ ${t.n}${t.volatile ? ' (volatile)' : ''}
- **ผู้ใช้ถาม:** ${t.q || t.ref_text}
${stt}${t.refers_to ? `- **สิ่งที่อ้างถึง (refers_to):** ${t.refers_to}\n` : ''}${t.expect_state ? `- **สถานะที่ควรเกิด:** ${JSON.stringify(t.expect_state)}\n` : ''}${expectLines(t)}
${actualLines(t)}
${t.retrieved?.length || t.sources ? `- **ย่อหน้าที่ค้นได้ (top 4):**\n${ctxBlock(t, `${t.q || ''} ${t.answer || ''}`)}\n` : ''}`;
    })
    .join('\n');
  return head + body;
}

// ---------------------------------------------------------------- สรุป
function apiFieldReport(results) {
  const dones = [];
  for (const r of results) for (const x of r.set === 'conv' ? r.turns : [r]) if (x.done_fields?.length) dones.push(x);
  const has = (k) => dones.some((d) => d.done_fields.includes(k));
  const ragish = dones.filter((d) => d.sources?.length);
  const retrievedNonEmpty = dones.some((d) => d.retrieved?.length);
  return {
    done_events: dones.length,
    retrieved: has('retrieved') && (retrievedNonEmpty || !ragish.length),
    products: has('products'),
    cites: has('cites'),
  };
}

function printSummary(results) {
  console.log('\nmetric โค้ด (เฉลี่ย · ยังไม่รวมผู้ตัดสิน):');
  for (const set of ['rag', 'qa', 'conv']) {
    const its = results.filter((r) => r.set === set);
    if (!its.length) continue;
    const keys = [...new Set(its.flatMap((r) => Object.keys(r.metrics || {})))];
    const parts = keys.map((k) => `${k}=${fmtNum(mean(its.map((r) => r.metrics?.[k])))}`);
    const errs = its.filter((r) => r.error || r.turns?.some((t) => t.error)).length;
    const ms = its.flatMap((r) => (r.set === 'conv' ? r.turns : [r]).map((x) => x.timing?.total_ms)).filter((v) => v != null);
    console.log(`  ${set.padEnd(4)} n=${its.length} ${parts.join(' ')}${errs ? ` · error ${errs}` : ''} · เวลา/คำตอบ p50 ${pct(ms, 50)} ms`);
  }
}

function fmtMetrics(m) {
  return Object.entries(m || {})
    .map(([k, v]) => `${k}=${fmtNum(v)}`)
    .join(' ');
}
const fmtNum = (v) => (v == null ? '–' : Number.isInteger(v) ? String(v) : v.toFixed(3));
const round3 = (v) => Math.round(v * 1000) / 1000;
function mean(vs) {
  const a = vs.filter((v) => typeof v === 'number' && Number.isFinite(v));
  return a.length ? a.reduce((s, v) => s + v, 0) / a.length : null;
}
function pct(a, p) {
  if (!a.length) return '–';
  const s = [...a].sort((x, y) => x - y);
  return s[Math.min(s.length - 1, Math.floor((p / 100) * s.length))];
}
function countBy(a, f) {
  const o = {};
  for (const x of a) o[f(x)] = (o[f(x)] || 0) + 1;
  return Object.entries(o).map(([k, v]) => `${k} ${v}`).join(' · ');
}
const rel = (p) => path.relative(process.cwd(), p) || p;

async function pool(items, n, fn) {
  const out = new Array(items.length);
  let next = 0;
  await Promise.all(
    Array.from({ length: Math.min(n, items.length) }, async () => {
      while (next < items.length) {
        const i = next++;
        try {
          out[i] = await fn(items[i]);
        } catch (e) {
          out[i] = { id: items[i].id, set: items[i].set, error: String(e?.stack || e), metrics: {}, ...(items[i].set === 'conv' ? { turns: [] } : {}) };
        }
      }
    }),
  );
  return out;
}

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

if (args['rescore-cer']) rescoreCer();
else await main();

/** --rescore-cer: คิด stt_cer ใหม่จาก transcript ที่บันทึกไว้ใน runs/<label>/answers.json (ไม่ถาม API ใหม่) */
function rescoreCer() {
  const f = path.join(OUT, 'answers.json');
  const ans = JSON.parse(readFileSync(f, 'utf8'));
  const src = Object.fromEntries(loadItems().map((i) => [i.id, i]));
  let n = 0;
  for (const it of ans.items) {
    if (it.set !== 'conv') continue;
    const ts = src[it.id]?.turns || [];
    it.turns.forEach((t, i) => {
      if (!t.audio || !t.stt || t.stt.skipped) return;
      const ref = ts[i] || {};
      const before = t.stt_cer;
      t.stt_cer = cerMin(t.stt.text || '', [ref.text, ...(ref.accept || [])]);
      t.metrics = t.metrics || {};
      if (t.stt_cer != null) t.metrics.stt_cer = t.stt_cer;
      if (before !== t.stt_cer) console.log(`  ${it.id} รอบ ${i + 1} ${t.audio}: CER ${before} → ${t.stt_cer}`);
      n++;
    });
    const v = mean(it.turns.map((t) => t.metrics?.stt_cer));
    if (v != null) it.metrics.stt_cer = round3(v);
  }
  writeFileSync(f, JSON.stringify(ans, null, 2));
  console.log(`rescore-cer ${LABEL}: ${n} รอบเสียง → ${path.relative(HERE, f)}`);
}
