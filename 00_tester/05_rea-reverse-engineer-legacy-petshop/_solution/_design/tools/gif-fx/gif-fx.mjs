#!/usr/bin/env node
// gif-fx.mjs · วิดีโอ Playwright (.webm) → GIF หลักฐาน test สไตล์บ้านของคอร์ส 00_tester (บท 02–04)
//
// ใช้:   node gif-fx.mjs <spec.json>            (ตัวอย่าง spec: bug01.json · gift-03-04.json ในโฟลเดอร์เดียวกัน)
//
// ได้อะไร (ตาม FINAL-REVIEW-V2 FR5V2-01..04 ของบท 05):
//   ① การ์ดไตเติลภาษาไทยต้นคลิป ("🎬 BUG-01 · …")
//   ② ป้ายชื่อ test ติดมุมซ้ายล่างทุกเฟรม (แบบ gif-TC-CART-02 / gif-bug-TC-PRICE-04)
//   ③ ตัดเฟรมขาวต้นวิดีโอ (กำหนด ss ของ clip แรกเอง)
//   ④ เฟรมค้าง (hold) ~2 วิ ที่ตัวเลขสำคัญ พร้อมวงแดงเลข ①②③ + แถบคำอธิบายด้านบน
//   ⑤ ภาพนิ่งปิดท้าย (still) เมื่อวิดีโอไม่มีเฟรมที่เห็นตัวเลขครบ
//   ⑥ ปิดข้อมูลส่วนตัว (masks: กล่องสีทึบ พิกัดวิดีโอต้นฉบับ ตั้งแต่วินาทีที่ from)
//   ⑦ คุมขนาด ≤ max_mb (ลดสี 96 → fps 6 → 64 สี → กว้าง 880 → 800 อัตโนมัติ) · clip ใส่ "speed": 1.5 เร่งช่วงเดินหน้าเว็บที่ไม่สำคัญได้
//
// ข้อความไทยทั้งหมดเรนเดอร์ด้วย Chromium headless (สระ/วรรณยุกต์ถูก) เป็น PNG แล้วให้ ffmpeg ซ้อนทับ
// ห้ามใช้ ffmpeg drawtext / PIL วาดภาษาไทย (วรรณยุกต์ลอย/ซ้อน)
//
// ต้องมี: ffmpeg/ffprobe ใน PATH · playwright 1.63 (หาจาก env PLAYWRIGHT_DIR → ข้างสคริปต์ → C:/t/work/a9)
//
// spec.json (พิกัดทุกตัวเป็นพิกัดวิดีโอต้นฉบับ เช่น 1280×800):
// {
//   "video": "C:/.../lab5-bug01.webm", "out": "C:/.../img/gif-bug-BUG-01.gif",
//   "src_w": 1280, "src_h": 800, "width": 960, "fps": 8, "colors": 128, "max_mb": 3,
//   "title": { "text": "🎬 BUG-01 · …", "sub": "…", "foot": "…", "dur": 2.2 },
//   "label": "🎬 BUG-01 · … · chromium",
//   "masks": [ { "x": 100, "y": 328, "w": 240, "h": 56, "color": "#ffffff", "from": 4.34 } ],
//   "segments": [
//     { "type": "clip",  "ss": 0.3, "to": 3.9 },
//     { "type": "hold",  "at": 3.9, "dur": 2.0, "caption": "…", "rings": [ { "x":870,"y":536,"w":340,"h":32,"n":"1" } ] },
//     { "type": "still", "image": "C:/.../site-order-bug01.png", "dur": 2.6, "caption": "…", "label": false }
//   ]
// }
// segment ทุกแบบรับ "caption" "caption_y" "caption_x" (ขอบบน/กึ่งกลางแถบ px ต้นฉบับ ค่าเริ่ม 88 / กลางจอ · ยาวเกิน 820 px ตัดบรรทัด) "rings" และ "label": false (ซ่อนป้าย)

import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const specPath = process.argv[2];
if (!specPath) { console.error('ใช้: node gif-fx.mjs <spec.json>'); process.exit(1); }
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const SW = spec.src_w ?? 1280, SH = spec.src_h ?? 800;
let width = spec.width ?? 960;
let fps = spec.fps ?? 8;
let colors = spec.colors ?? 128;
const dither = spec.dither ?? 'bayer:bayer_scale=4'; // 'none' = ไฟล์เล็กกว่ามากสำหรับหน้าเว็บสีเรียบ
const maxBytes = (spec.max_mb ?? 3) * 1024 * 1024;

function loadPlaywright() {
  for (const b of [process.env.PLAYWRIGHT_DIR, here, 'C:/t/work/a9'].filter(Boolean)) {
    try { return createRequire(path.join(path.resolve(b), 'noop.js'))('playwright'); } catch { /* ถัดไป */ }
  }
  console.error('หา playwright ไม่เจอ · npm i playwright@1.63.0 แล้วตั้ง PLAYWRIGHT_DIR'); process.exit(2);
}
function ff(argv) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...argv], { encoding: 'utf8' });
  if (r.status !== 0) { console.error(`ffmpeg ล้ม: ${argv.join(' ')}\n${r.stderr}`); process.exit(3); }
}
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const FONT = `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800&display=swap" rel="stylesheet">`;
const BASE_CSS = `*{margin:0;padding:0;box-sizing:border-box}html,body{width:${SW}px;height:${SH}px;background:transparent;overflow:hidden;
  font-family:'Noto Sans Thai','Leelawadee UI',Tahoma,'Segoe UI Emoji',sans-serif}`;

// ---------- HTML ของชั้นซ้อนทับ (ขนาดเท่าวิดีโอต้นฉบับ แล้วถ่ายที่ DSF = width/SW) ----------
function titleHtml(t) {
  return `<!doctype html><html><head><meta charset="utf-8">${FONT}<style>${BASE_CSS}
  body{background:linear-gradient(135deg,#111827 0%,#1f2937 60%,#3b2a20 100%);display:flex;flex-direction:column;justify-content:center;padding:0 90px;color:#fff}
  .kick{display:inline-block;align-self:flex-start;background:#e11d48;color:#fff;font-weight:700;font-size:28px;padding:6px 22px;border-radius:999px;margin-bottom:34px}
  h1{font-size:58px;line-height:1.45;font-weight:800;letter-spacing:.2px}
  .sub{margin-top:26px;font-size:34px;line-height:1.6;color:#e5e7eb;font-weight:600}
  .foot{position:absolute;left:90px;bottom:56px;font-size:26px;color:#9ca3af}
  .bar{position:absolute;left:0;top:0;width:14px;height:100%;background:#f97316}</style></head><body>
  <div class="bar"></div>${t.kick ? `<div class="kick">${esc(t.kick)}</div>` : ''}<h1>${esc(t.text).replace(/\n/g, '<br>')}</h1>
  ${t.sub ? `<div class="sub">${esc(t.sub).replace(/\n/g, '<br>')}</div>` : ''}${t.foot ? `<div class="foot">${esc(t.foot)}</div>` : ''}</body></html>`;
}
function overlayHtml({ label, caption, captionY = 88, captionX = SW / 2, rings = [] }) {
  const ringEls = rings.map((r) => `<div class="ring" style="left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px"></div>
    ${r.n ? `<div class="num" style="left:${r.x - 22}px;top:${r.y + r.h / 2 - 17}px">${esc(r.n)}</div>` : ''}`).join('');
  return `<!doctype html><html><head><meta charset="utf-8">${FONT}<style>${BASE_CSS}
  .label{position:absolute;left:8px;bottom:12px;background:rgba(17,24,39,.94);color:#fff;font-weight:700;font-size:23px;line-height:1.5;
    padding:6px 18px 7px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.35);max-width:${SW - 40}px}
  .cap{position:absolute;left:${captionX}px;transform:translateX(-50%);top:${captionY}px;max-width:820px;text-align:center;background:#be123c;color:#fff;font-weight:700;font-size:27px;
    line-height:1.5;padding:8px 26px 9px;border-radius:14px;box-shadow:0 4px 16px rgba(0,0,0,.35);width:max-content}
  .ring{position:absolute;border:4px solid #e11d48;border-radius:14px;box-shadow:0 0 0 2px rgba(255,255,255,.9)}
  .num{position:absolute;width:34px;height:34px;border-radius:50%;background:#e11d48;color:#fff;font-weight:800;font-size:20px;
    display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 2px #fff}</style></head><body>
  ${ringEls}${caption ? `<div class="cap">${esc(caption)}</div>` : ''}${label ? `<div class="label">${esc(label)}</div>` : ''}</body></html>`;
}

// ---------- เตรียมโฟลเดอร์ชั่วคราว ----------
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'gif-fx-'));
const pw = loadPlaywright();
const browser = await pw.chromium.launch({ headless: true });

async function shot(html, file, dsf) {
  const page = await browser.newPage({ viewport: { width: SW, height: SH }, deviceScaleFactor: dsf });
  await page.setContent(html, { waitUntil: 'networkidle' }).catch(() => {});
  const ok = await page.evaluate(async () => { await document.fonts.ready; return document.fonts.check('700 20px "Noto Sans Thai"'); });
  if (!ok) console.warn('⚠️ โหลด Noto Sans Thai ไม่ได้ (ออฟไลน์?) → ใช้ Leelawadee UI แทน');
  await page.screenshot({ path: file, omitBackground: true });
  await page.close();
}

function render(w) {
  const H = Math.round((SH * w) / SW / 2) * 2;
  const dsf = w / SW;
  return { H, dsf };
}

// วาด mask (พิกัดต้นฉบับ) สำหรับเวลาของ segment: ffmpeg drawbox ไม่มีข้อความ จึงใช้ได้ปลอดภัย
function maskFilter(tStart, tEnd) {
  const ms = (spec.masks ?? []).filter((m) => tEnd > (m.from ?? 0));
  return ms.map((m) => {
    const c = (m.color ?? '#ffffff').replace('#', '0x');
    const en = (m.from ?? 0) > tStart ? `:enable='gte(t+${tStart},${m.from})'` : '';
    return `drawbox=x=${m.x}:y=${m.y}:w=${m.w}:h=${m.h}:color=${c}@1:t=fill${en}`;
  });
}

async function buildFrames(w) {
  const { H, dsf } = render(w);
  const framesDir = path.join(tmp, `frames-${w}`);
  fs.rmSync(framesDir, { recursive: true, force: true });
  fs.mkdirSync(framesDir);
  let n = 0;
  const pushDir = (dir) => {
    for (const f of fs.readdirSync(dir).sort()) {
      n += 1;
      fs.renameSync(path.join(dir, f), path.join(framesDir, `${String(n).padStart(5, '0')}.png`));
    }
  };
  const log = [];
  // การ์ดไตเติล
  if (spec.title) {
    const card = path.join(tmp, `title-${w}.png`);
    await shot(titleHtml(spec.title), card, dsf);
    const d = path.join(tmp, `seg-title-${w}`); fs.mkdirSync(d, { recursive: true });
    ff(['-loop', '1', '-framerate', String(fps), '-t', String(spec.title.dur ?? 2), '-i', card,
      '-vf', `scale=${w}:${H}:flags=lanczos,format=rgb24`, path.join(d, '%05d.png')]);
    log.push(`title ${spec.title.dur ?? 2}s`); pushDir(d);
  }
  for (const [i, s] of spec.segments.entries()) {
    const ov = path.join(tmp, `ov-${i}-${w}.png`);
    await shot(overlayHtml({ label: s.label === false ? null : spec.label, caption: s.caption, captionY: s.caption_y, captionX: s.caption_x, rings: s.rings }), ov, dsf);
    const d = path.join(tmp, `seg-${i}-${w}`); fs.mkdirSync(d, { recursive: true });
    const out = path.join(d, '%05d.png');
    const post = `scale=${w}:${H}:flags=lanczos[b];[b][1:v]overlay=0:0,format=rgb24`;
    if (s.type === 'clip') {
      const pre = maskFilter(s.ss, s.to);
      ff(['-ss', String(s.ss), '-to', String(s.to), '-i', spec.video, '-i', ov, '-filter_complex',
        `[0:v]${[...pre, ...(s.speed ? [`setpts=PTS/${s.speed}`] : []), `fps=${fps}`].join(',')},${post}`, out]);
      log.push(`clip ${s.ss}→${s.to}s${s.speed ? ` ×${s.speed}` : ''}`);
    } else if (s.type === 'hold' || s.type === 'still') {
      const still = path.join(tmp, `still-${i}.png`);
      if (s.type === 'hold') {
        const pre = maskFilter(s.at, s.at + 0.01).map((f) => f.replace(/:enable='[^']*'/, ''));
        ff(['-ss', String(s.at), '-i', spec.video, '-frames:v', '1', ...(pre.length ? ['-vf', pre.join(',')] : []), still]);
      } else {
        ff(['-i', s.image, '-vf', `scale=${SW}:${SH}`, still]);
      }
      ff(['-loop', '1', '-framerate', String(fps), '-t', String(s.dur), '-i', still, '-i', ov, '-filter_complex',
        `[0:v]${post}`, out]);
      log.push(`${s.type} ${s.type === 'hold' ? `@${s.at}s` : path.basename(s.image)} ${s.dur}s`);
    } else { console.error(`ไม่รู้จัก segment type ${s.type}`); process.exit(1); }
    pushDir(d);
  }
  return { framesDir, H, n, log };
}

function encode(framesDir, out) {
  const palette = path.join(tmp, 'palette.png');
  const inp = ['-framerate', String(fps), '-i', path.join(framesDir, '%05d.png')];
  ff([...inp, '-vf', `palettegen=max_colors=${colors}:stats_mode=full`, palette]);
  ff([...inp, '-i', palette, '-lavfi', `[0:v][1:v]paletteuse=dither=${dither}:diff_mode=rectangle`, '-loop', '0', out]);
  return fs.statSync(out).size;
}

const steps = [() => { colors = 96; }, () => { fps = 6; }, () => { colors = 64; }, () => { width = 880; }, () => { width = 800; }];
let built = await buildFrames(width);
let size = encode(built.framesDir, spec.out);
for (const step of steps) {
  if (size <= maxBytes) break;
  const before = `${width}px ${fps}fps ${colors} สี`;
  const oldW = width, oldF = fps; step();
  console.warn(`${(size / 1048576).toFixed(2)} MB > ${maxBytes / 1048576} MB ที่ ${before} → ลอง ${width}px ${fps}fps ${colors} สี`);
  if (width !== oldW || fps !== oldF) built = await buildFrames(width);
  size = encode(built.framesDir, spec.out);
}
await browser.close();
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`segments: ${built.log.join(' | ')}`);
console.log(`${spec.out}\n${width}×${built.H} · ${built.n} เฟรม ${fps} fps ≈ ${(built.n / fps).toFixed(1)} วิ · ${colors} สี · ${(size / 1048576).toFixed(2)} MB${size > maxBytes ? ' ⚠️ เกินเพดาน' : ''}`);
