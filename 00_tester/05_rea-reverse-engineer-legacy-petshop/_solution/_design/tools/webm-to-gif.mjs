#!/usr/bin/env node
// webm-to-gif.mjs · วิดีโอ Playwright (.webm/.mp4) → GIF สำหรับ README (≤ 3 MB) ด้วย ffmpeg แบบ 2 รอบ (palettegen → paletteuse)
//
// ใช้:   node webm-to-gif.mjs <in.webm> <out.gif> [--ss 1.5] [--to 9] [--t 6] [--width 960] [--fps 8]
//                                               [--colors 128] [--max-mb 3]
//   --ss  เริ่มที่วินาทีที่   --to  จบที่วินาทีที่   --t  ความยาว (วินาที) (ใช้ --to หรือ --t อย่างใดอย่างหนึ่ง)
//   ค่าเริ่มต้น: กว้าง 960 px · 8 fps · 128 สี · dither bayer · วนซ้ำไม่จบ
//   ถ้าไฟล์ > --max-mb จะลองใหม่อัตโนมัติ: 96 สี → 64 สี → 6 fps → กว้าง 800 px → 5 fps (แล้วพิมพ์บอกว่าใช้ค่าไหน)
//
// ต้องมี ffmpeg ใน PATH (ตรวจด้วย ffmpeg -version · Windows: winget install Gyan.FFmpeg)
// บท 04 ใช้ fps=5, กว้าง 800, 96 สี (e2e/tests/fixtures.ts) · บท 05–06 ใช้ 960 px 8 fps ตาม STYLE-GUIDE

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const args = process.argv.slice(2);
const takeOpt = (name, def) => {
  const i = args.indexOf(name);
  if (i < 0) return def;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const ss = takeOpt('--ss');
const to = takeOpt('--to');
const dur = takeOpt('--t');
let width = Number(takeOpt('--width', 960));
let fps = Number(takeOpt('--fps', 8));
let colors = Number(takeOpt('--colors', 128));
const maxBytes = Number(takeOpt('--max-mb', 3)) * 1024 * 1024;
const [input, output] = args;
if (!input || !output) {
  console.error('ใช้: node webm-to-gif.mjs <in.webm> <out.gif> [--ss 1.5] [--to 9 | --t 6] [--width 960] [--fps 8] [--colors 128] [--max-mb 3]');
  process.exit(1);
}
if (!fs.existsSync(input)) { console.error(`ไม่พบไฟล์ ${input}`); process.exit(1); }

const ver = spawnSync('ffmpeg', ['-version'], { encoding: 'utf8' });
if (ver.error || ver.status !== 0) {
  console.error('ไม่พบ ffmpeg ใน PATH · ติดตั้งด้วย winget install Gyan.FFmpeg แล้วเปิด terminal ใหม่');
  process.exit(2);
}
console.log(ver.stdout.split('\n')[0]);

const trim = [];
if (ss) trim.push('-ss', ss);
if (to) trim.push('-to', to);
else if (dur) trim.push('-t', dur);

const palette = path.join(os.tmpdir(), `gif-palette-${process.pid}.png`);
function ffmpeg(argv) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...argv], { encoding: 'utf8' });
  if (r.status !== 0) { console.error(`ffmpeg ล้ม:\n${r.stderr}`); process.exit(3); }
}
function build() {
  const base = `fps=${fps},scale=${width}:-2:flags=lanczos`;
  // รอบ 1: หาพาเลตจากทั้งคลิป (stats_mode=diff เน้นส่วนที่ขยับ เช่น วงแดงจุดคลิก)
  ffmpeg([...trim, '-i', input, '-vf', `${base},palettegen=max_colors=${colors}:stats_mode=diff`, palette]);
  // รอบ 2: ใช้พาเลต · diff_mode=rectangle อัปเดตเฉพาะส่วนที่เปลี่ยน → ไฟล์เล็กลง
  ffmpeg([...trim, '-i', input, '-i', palette, '-lavfi',
    `${base}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle`, '-loop', '0', output]);
  return fs.statSync(output).size;
}

const steps = [
  () => { colors = 96; }, () => { colors = 64; }, () => { fps = 6; }, () => { width = 800; }, () => { fps = 5; },
];
let size = build();
for (const step of steps) {
  if (size <= maxBytes) break;
  const before = `${width}px ${fps}fps ${colors} สี`;
  step();
  console.warn(`${(size / 1048576).toFixed(2)} MB > ${maxBytes / 1048576} MB ที่ ${before} → ลองใหม่ ${width}px ${fps}fps ${colors} สี`);
  size = build();
}
fs.rmSync(palette, { force: true });

const probe = spawnSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0',
  '-show_entries', 'stream=width,height,nb_read_frames', '-of', 'csv=p=0', output], { encoding: 'utf8' });
const [w, h, frames] = (probe.stdout || '').trim().split(',');
const mb = (size / 1048576).toFixed(2);
console.log(`${output} · ${w}×${h} · ${frames} เฟรม @ ${fps} fps (~${(frames / fps).toFixed(1)} วินาที) · ${colors} สี · ${mb} MB` +
  `${size > maxBytes ? ` ⚠️ ยังเกิน ${maxBytes / 1048576} MB · ตัดให้สั้นลงด้วย --ss/--to` : ''}`);
process.exit(size > maxBytes ? 4 : 0);
