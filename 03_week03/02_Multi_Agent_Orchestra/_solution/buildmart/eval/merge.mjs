#!/usr/bin/env node
// eval/merge.mjs — รวม eval/parts/*.json → eval/qa.json (BUILDMART ข้อ 8.1 · CONTRACT_V3 §7)
//   node merge.mjs [--parts parts] [--out qa.json] [--strict]
// ตรวจ: JSON valid · id ซ้ำ · set ∈ rag|qa|conv · ฟิลด์ที่ต้องมีต่อ set · จำนวนต่อ set (rag 150–170 · qa 70–80 · conv 10–12 บท × 4–6 รอบ)
// --strict → exit 1 เมื่อมี error (id ซ้ำ/ฟิลด์ขาด) หรือจำนวนไม่อยู่ในช่วง
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = parseArgs(process.argv.slice(2));
const partsDir = path.resolve(HERE, args.parts || 'parts');
const outFile = path.resolve(HERE, args.out || 'qa.json');

const SET_ORDER = ['rag', 'qa', 'conv'];
const RANGE = { rag: [150, 170], qa: [70, 80], conv: [10, 12] };

const errors = [];
const warns = [];
const items = [];
const seen = new Map(); // id → ไฟล์แรกที่เจอ

if (!existsSync(partsDir)) {
  console.error(`ไม่พบโฟลเดอร์ ${partsDir}`);
  process.exit(1);
}
const files = readdirSync(partsDir).filter((f) => f.endsWith('.json')).sort();
for (const f of files) {
  let data;
  try {
    data = JSON.parse(readFileSync(path.join(partsDir, f), 'utf8'));
  } catch (e) {
    errors.push(`${f}: JSON ไม่ถูกต้อง (${e.message})`);
    continue;
  }
  const arr = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : null;
  if (!arr) {
    errors.push(`${f}: ต้องเป็น array ของ item (หรือ {items:[...]})`);
    continue;
  }
  let n = 0;
  for (const it of arr) {
    if (!it || typeof it !== 'object') {
      errors.push(`${f}: มี item ที่ไม่ใช่ object`);
      continue;
    }
    const set = it.set || guessSet(it);
    if (!SET_ORDER.includes(set)) {
      errors.push(`${f}: ${it.id ?? '(ไม่มี id)'} set "${it.set}" ไม่รู้จัก (ต้องเป็น rag|qa|conv)`);
      continue;
    }
    if (!it.id) {
      errors.push(`${f}: item ไม่มี id (${(it.question || '').slice(0, 40)})`);
      continue;
    }
    if (seen.has(it.id)) {
      errors.push(`id ซ้ำ: ${it.id} (${seen.get(it.id)} และ ${f})`);
      continue;
    }
    seen.set(it.id, f);
    for (const msg of validate({ ...it, set })) errors.push(`${f}: ${it.id} ${msg}`);
    items.push({ ...it, set, _part: f });
    n++;
  }
  console.log(`  ${f.padEnd(28)} ${String(n).padStart(4)} ข้อ`);
}

items.sort((a, b) => SET_ORDER.indexOf(a.set) - SET_ORDER.indexOf(b.set) || a.id.localeCompare(b.id, 'en', { numeric: true }));

// ---------- นับ ----------
const count = {};
const byKind = {};
for (const it of items) {
  count[it.set] = (count[it.set] || 0) + 1;
  const kind = it.set === 'rag' ? it.type : it.set === 'qa' ? it.category || it.type : it.voice ? 'voice' : 'text';
  const k = `${it.set}:${kind || '(ไม่ระบุ)'}`;
  byKind[k] = (byKind[k] || 0) + 1;
}
for (const s of SET_ORDER) {
  const n = count[s] || 0;
  const [lo, hi] = RANGE[s];
  if (n < lo || n > hi) warns.push(`set ${s} มี ${n} ข้อ (ควร ${lo}–${hi})`);
}
const conv = items.filter((i) => i.set === 'conv');
const turns = conv.reduce((a, c) => a + (c.turns?.length || 0), 0);
const voiceConv = conv.filter((c) => c.voice || c.turns?.some((t) => t.audio)).length;
if (conv.length && voiceConv < 3) warns.push(`conv ที่ใช้เสียงมี ${voiceConv} บท (ต้อง ≥ 3)`);
const docs = {};
for (const it of items.filter((i) => i.set === 'rag')) for (const s of it.sources || []) docs[s.filename] = (docs[s.filename] || 0) + 1;

const out = items.map(({ _part, ...it }) => it);
writeFileSync(outFile, JSON.stringify(out, null, 2) + '\n');

console.log(`\n→ ${path.relative(process.cwd(), outFile) || outFile}: ${out.length} item`);
for (const s of SET_ORDER) console.log(`  ${s.padEnd(5)} ${String(count[s] || 0).padStart(4)}${s === 'conv' ? `  (${turns} รอบ · เสียง ${voiceConv} บท)` : ''}`);
console.log('  ต่อประเภท: ' + Object.entries(byKind).map(([k, v]) => `${k}=${v}`).join(' · '));
if (Object.keys(docs).length) console.log('  rag ต่อเอกสาร (นับ source): ' + Object.entries(docs).map(([k, v]) => `${k}=${v}`).join(' · '));
for (const w of warns) console.log(`  ⚠ ${w}`);
for (const e of errors) console.log(`  ✗ ${e}`);
if (args.strict && (errors.length || warns.length)) process.exit(1);
if (errors.some((e) => e.startsWith('id ซ้ำ'))) process.exitCode = 1;

// ---------- helpers ----------
function guessSet(it) {
  if (Array.isArray(it.turns)) return 'conv';
  if (Array.isArray(it.sources) || it.key_facts) return 'rag';
  if (it.expected_values || it.sql || it.category) return 'qa';
  return undefined;
}

function validate(it) {
  const m = [];
  if (it.set === 'conv') {
    if (!Array.isArray(it.turns) || !it.turns.length) return ['ไม่มี turns'];
    if (it.turns.length < 4 || it.turns.length > 6) m.push(`มี ${it.turns.length} รอบ (ต้อง 4–6)`);
    it.turns.forEach((t, i) => {
      if (!t.text && !t.audio) m.push(`รอบ ${i + 1} ไม่มี text/audio`);
      if (!t.expected) m.push(`รอบ ${i + 1} ไม่มี expected`);
      if (!t.key_facts && !t.expected_values) m.push(`รอบ ${i + 1} ไม่มี key_facts/expected_values`);
      checkSources(t.sources, `รอบ ${i + 1} `, m);
    });
    return m;
  }
  if (!it.question) m.push('ไม่มี question');
  if (!it.expected) m.push('ไม่มี expected');
  if (it.set === 'rag') {
    const neg = it.type === 'negative';
    if (!neg && !(it.sources || []).length) m.push('ไม่มี sources');
    if (!Array.isArray(it.key_facts)) m.push('ไม่มี key_facts');
    checkSources(it.sources, '', m);
  }
  if (it.set === 'qa' && it.expected_values != null && !Array.isArray(it.expected_values)) m.push('expected_values ต้องเป็น array');
  return m;
}

function checkSources(src, pre, m) {
  if (src == null) return;
  if (!Array.isArray(src)) return m.push(`${pre}sources ต้องเป็น array`);
  for (const s of src) if (!s?.filename || !(Number(s.page) >= 1)) m.push(`${pre}source ไม่ถูกต้อง ${JSON.stringify(s)}`);
}

function parseArgs(a) {
  const o = {};
  for (let i = 0; i < a.length; i++) {
    if (!a[i].startsWith('--')) continue;
    const k = a[i].slice(2);
    const v = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
    o[k] = v;
  }
  return o;
}
