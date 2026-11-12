// e2e/make-tts-cache.mjs — อัดเสียง VoxCPM2 จาก ai-box จริง ไว้ให้โหมด mock (ฟรี) เล่นซ้ำ (CONTRACT_V3 §3)
//
// mock-llm /v1/audio/speech หาไฟล์ voice-fixtures/tts-cache/<sha256(input)>.wav · ไม่เจอ → generic.wav
// input = speechText(ข้อความ) (shared/speech.js · ตัวเดียวกับที่ tts-worker ใช้) → sha256 ตรงกันแน่นอน
//
// ใช้:
//   TTS_URL=http://localhost:8090 AIBOX_API_KEY=... node make-tts-cache.mjs [--file texts.txt|texts.json] ["ข้อความ" ...]
//   (หรือ --key-file C:/t/bm3/aibox.key แทน AIBOX_API_KEY) · --force = อัดทับไฟล์เดิม
//   ไม่ให้ข้อความ → ใช้ชุดเริ่มต้น (คำตอบ mock ของเคส T01–T03 + ประโยคทั่วไป) · generic.wav = ประโยคทักทายของน้องช่าง
// หลังอัดเสร็จ: docker compose -p buildmart --profile mock up -d --build mock-llm (ไฟล์ถูก copy เข้า image)
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { speechText, speechLang, sha256Hex, wavDurationMs } from '../shared/speech.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(here, 'voice-fixtures', 'tts-cache');
const args = process.argv.slice(2);
const opt = (k) => {
  const i = args.indexOf(k);
  if (i < 0) return null;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const force = args.includes('--force') ? (args.splice(args.indexOf('--force'), 1), true) : false;
const file = opt('--file');
const keyFile = opt('--key-file');
const url = (process.env.TTS_URL || process.env.AIBOX_URL || 'http://localhost:8090').replace(/\/+$/, '');
const key = (process.env.AIBOX_API_KEY || (keyFile ? readFileSync(keyFile, 'utf8') : '')).trim();

const GENERIC = 'สวัสดีครับ ผมน้องช่าง ผู้ช่วยของร้านบ้านช่าง บิลด์มาร์ท มีอะไรให้ช่วยไหมครับ';
const DEFAULT_TEXTS = [
  'ร้านเปิดวันจันทร์–เสาร์ 07:00–18:00 น. และวันอาทิตย์ 08:00–12:00 น. ครับ',
  'Portland cement Type 1 (50 kg) (CEM-001) costs 145 baht per bag (excluding 7% VAT).\nPortland cement Type 1 (50 kg) (CEM-001) is in stock at 3 branch(es): LKB 800 · BNA 500 · RST 300.',
  'มีโค้ดส่วนลดดังนี้ครับ (ใช้ได้ทีละ 1 ใบ ลดจากยอดหลังราคาส่ง)\n- BUILD5 ลด 5% เมื่อยอดก่อน VAT ตั้งแต่ 5,000 บาท\n- CONTRACTOR10 ลด 10% เมื่อยอดก่อน VAT ตั้งแต่ 30,000 บาท\nใส่โค้ดได้ที่หน้าตะกร้าครับ',
];

let texts = args.filter((a) => !a.startsWith('--'));
if (file) {
  const raw = readFileSync(file, 'utf8');
  texts.push(...(file.endsWith('.json') ? JSON.parse(raw) : raw.split(/\r?\n/).filter((l) => l.trim())));
}
if (!texts.length) texts = DEFAULT_TEXTS;

mkdirSync(OUT, { recursive: true });

async function speak(input) {
  const r = await fetch(`${url}/v1/audio/speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
    body: JSON.stringify({ input, voice: 'nongchang', response_format: 'wav', language: speechLang(input) }),
  });
  const buf = Buffer.from(await r.arrayBuffer());
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${buf.toString('utf8').slice(0, 200)}`);
  if (!wavDurationMs(buf)) throw new Error('not a WAV response');
  return buf;
}

// เหมือน web/app/api/tts/ttsText.ts speakable() — /api/tts ทำข้อความแบบนี้ก่อนส่งเข้าคิว แล้ว tts-worker ทำ speechText() ซ้ำ
const speakable = (raw) =>
  String(raw)
    .replace(/\[(CALC|ADD_TO_CART|QUOTE)\][^\n]*/g, '')
    .replace(/\[\d+\]/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '')
    .replace(/[*_`#>|]/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()
    .slice(0, 1500);

const jobs = [...texts.map((t) => ({ input: speechText(speakable(t)) })), { input: GENERIC, name: 'generic.wav' }];
let ok = 0;
let fail = 0;
for (const j of jobs) {
  if (!j.input) continue;
  const name = j.name || `${sha256Hex(j.input)}.wav`;
  const out = path.join(OUT, name);
  if (existsSync(out) && !force) {
    console.log(`skip  ${name} (มีแล้ว)`);
    continue;
  }
  const t0 = Date.now();
  try {
    const wav = await speak(j.input);
    writeFileSync(out, wav);
    ok++;
    console.log(`ok    ${name} ${wavDurationMs(wav)}ms audio · ${Date.now() - t0}ms · ${JSON.stringify(j.input.slice(0, 50))}`);
  } catch (e) {
    fail++;
    console.error(`FAIL  ${JSON.stringify(j.input.slice(0, 50))}: ${e.message}`);
  }
}
console.log(`\n${ok} recorded, ${fail} failed → ${OUT}`);
process.exit(fail ? 1 : 0);
