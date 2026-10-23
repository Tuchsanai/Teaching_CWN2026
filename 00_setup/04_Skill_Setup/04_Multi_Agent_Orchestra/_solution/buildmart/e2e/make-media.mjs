// e2e/make-media.mjs — วิดีโอ webm ของทุกเคส → test-videos/<id>.mp4 (H.264 CRF 28 · กว้าง 1280 · faststart) + test-gifs/<id>.gif (fps 6 · กว้าง 800 · 96 สี ≲ 2.5 MB)
// env: BM_GIF_WIDTH BM_GIF_FPS BM_GIF_COLORS BM_GIF_DITHER · BM_MP4_CRF BM_MP4_WIDTH · BM_MEDIA_JOBS · BM_MEDIA_ONLY=M,V,D02 (เฉพาะกลุ่ม/เคส)
// เคส T/V/D02: ดาวน์โหลด WAV เสียงตอบจาก ${BM_URL}/api/tts/<audioId> (attachment 'audio') + เสียงคำถามจาก voice-fixtures/<file> (attachment 'mic')
//   แล้วรวมเข้า MP4 ด้วย adelay=offsetMs ให้ตรงจังหวะที่กดไมค์/เริ่มเล่น · เคสที่มีเสียงคำถาม ตรวจ silencedetect ว่ามีช่วงมีเสียง ≥ 2 ช่วงต่อรอบ
// ใช้ ffmpeg-static · ตรวจว่า MP4 มี audio stream (ffprobe ถ้ามีในเครื่อง ไม่งั้นอ่านจาก ffmpeg -i)
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import ffmpegPath from 'ffmpeg-static';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const RESULTS = path.join(DIR, process.argv[2] || 'results.json');
const VIDEOS = path.join(DIR, 'test-videos');
const GIFS = path.join(DIR, 'test-gifs');
const TMP = path.join(DIR, '.media-tmp');
const CONCURRENCY = Number(process.env.BM_MEDIA_JOBS || 4);
const VOICE_DIR = path.join(DIR, 'voice-fixtures');
const ONLY = (process.env.BM_MEDIA_ONLY || '').split(',').map((s) => s.trim().toUpperCase()).filter(Boolean);
const wanted = (id) => !ONLY.length || ONLY.some((o) => (/^[A-Z]$/.test(o) ? id.startsWith(o) : id === o));
for (const d of [VIDEOS, GIFS, TMP]) mkdirSync(d, { recursive: true });

if (!existsSync(RESULTS)) {
  console.error(`ไม่พบ ${RESULTS} — รัน npm run playlist ก่อน`);
  process.exit(1);
}
const report = JSON.parse(readFileSync(RESULTS, 'utf8'));
const BM_URL = (process.env.BM_URL || report.config?.metadata?.url || 'http://localhost:3400').replace(/\/$/, '');

/** ไล่ทุก test ใน JSON report → [{id, title, result}] (ใช้ result ล่าสุด) */
function collect(suites, out = []) {
  for (const s of suites || []) {
    for (const spec of s.specs || [])
      for (const t of spec.tests || []) {
        const result = t.results?.[t.results.length - 1];
        if (result) out.push({ id: spec.title.split(' ')[0], title: spec.title, result });
      }
    collect(s.suites, out);
  }
  return out;
}

const run = (args) =>
  new Promise((resolve, reject) => {
    const p = spawn(ffmpegPath, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    p.stderr.on('data', (d) => (err += d));
    p.on('close', (code) => (code === 0 ? resolve(err) : reject(new Error(`ffmpeg ${code}: ${err.slice(-800)}`))));
  });

/** ข้อมูล stream ของไฟล์: ใช้ ffprobe ถ้ามี ไม่งั้นอ่าน stderr ของ ffmpeg -i */
function probe(file) {
  const fp = process.env.FFPROBE || 'ffprobe';
  const r = spawnSync(fp, ['-v', 'error', '-show_entries', 'stream=codec_type,codec_name:format=duration', '-of', 'json', file], { encoding: 'utf8' });
  if (r.status === 0 && r.stdout) {
    const j = JSON.parse(r.stdout);
    const streams = j.streams || [];
    return {
      tool: 'ffprobe',
      durationSec: Number(j.format?.duration || 0),
      video: streams.find((s) => s.codec_type === 'video')?.codec_name || null,
      audio: streams.find((s) => s.codec_type === 'audio')?.codec_name || null,
    };
  }
  const e = spawnSync(ffmpegPath, ['-hide_banner', '-i', file], { encoding: 'utf8' }).stderr || '';
  const m = e.match(/Duration: (\d+):(\d+):([\d.]+)/);
  return {
    tool: 'ffmpeg',
    durationSec: m ? +m[1] * 3600 + +m[2] * 60 + +m[3] : 0,
    video: e.match(/Stream #\S+.*?Video: (\w+)/)?.[1] || null,
    audio: e.match(/Stream #\S+.*?Audio: (\w+)/)?.[1] || null,
  };
}

const attJson = (a) => {
  try {
    return JSON.parse(a.body ? Buffer.from(a.body, 'base64').toString('utf8') : readFileSync(a.path, 'utf8'));
  } catch {
    return null;
  }
};

async function downloadWav(audioId, file) {
  const r = await fetch(`${BM_URL}/api/tts/${encodeURIComponent(audioId)}`);
  if (!r.ok) throw new Error(`โหลด WAV ${audioId} ไม่ได้: HTTP ${r.status}`);
  writeFileSync(file, Buffer.from(await r.arrayBuffer()));
}

/** GIF: เฟรมละ fps คงที่ (ไม่ตัดเฟรมซ้ำ → ช่วงค้างภาพ 3–5 วิ ยังยาวเท่าเดิม) · palette 96 สี ไม่ dither (หน้าเว็บพื้นเรียบ — dither ทำให้ diff_mode บีบไม่ได้ ไฟล์โตขึ้น ~15%)
 *  ค่าเริ่มต้นตั้งให้แต่ละไฟล์ ≲ 2.5 MB (เคสยาว ~60–90 วิ) — ปรับได้ด้วย env */
const GIF_WIDTH = Number(process.env.BM_GIF_WIDTH || 800);
const GIF_FPS = Number(process.env.BM_GIF_FPS || 6);
const GIF_COLORS = Number(process.env.BM_GIF_COLORS || 96);
const GIF_DITHER = process.env.BM_GIF_DITHER || 'none';
/** MP4: H.264 กว้าง 1280 · CRF 28 (ข้อความยังคม ไฟล์เล็ก) */
const MP4_CRF = String(process.env.BM_MP4_CRF || 28);
const MP4_WIDTH = Number(process.env.BM_MP4_WIDTH || 1280);

/** ffmpeg silencedetect → ช่วงที่มีเสียง [[start,end],…] (วินาที) */
async function voicedSegments(file) {
  const log = await run(['-hide_banner', '-nostats', '-i', file, '-vn', '-af', 'silencedetect=noise=-38dB:d=0.35', '-f', 'null', '-']);
  const total = probe(file).durationSec;
  const sil = [];
  let cur = null;
  for (const line of log.split(/\r?\n/)) {
    const a = line.match(/silence_start: ([\d.]+)/);
    const b = line.match(/silence_end: ([\d.]+)/);
    if (a) cur = [Number(a[1]), total];
    if (b && cur) {
      cur[1] = Number(b[1]);
      sil.push(cur);
      cur = null;
    }
  }
  if (cur) sil.push(cur);
  const spans = [];
  let t = 0;
  for (const [s0, s1] of sil) {
    if (s0 - t > 0.15) spans.push([Math.round(t * 100) / 100, Math.round(s0 * 100) / 100]);
    t = s1;
  }
  if (total - t > 0.15) spans.push([Math.round(t * 100) / 100, Math.round(total * 100) / 100]);
  return { segments: spans.length, spans };
}

async function makeGif(src, gif) {
  await run([
    '-y', '-hide_banner', '-loglevel', 'error', '-i', src,
    // stats_mode=diff: palette เน้นส่วนที่ขยับ (หน้าเว็บพื้นเรียบ) · diff_mode=rectangle: เขียนเฉพาะกรอบที่เปลี่ยน → ช่วงค้างภาพแทบไม่กินที่
    '-vf',
    `fps=${GIF_FPS},scale=${GIF_WIDTH}:-2:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=${GIF_COLORS}:stats_mode=diff[p];` +
      `[s1][p]paletteuse=dither=${GIF_DITHER}:diff_mode=rectangle`,
    '-loop', '0', gif,
  ]);
}

async function processCase({ id, result }) {
  const video = (result.attachments || []).find((a) => a.name === 'video' && a.path && existsSync(a.path));
  const mp4 = path.join(VIDEOS, `${id}.mp4`);
  const gif = path.join(GIFS, `${id}.gif`);
  if (!video) {
    // webm ใน test-results/ หายไปแล้ว (Playwright ล้างโฟลเดอร์ทุกครั้งที่รัน เช่นรัน BM_ONLY=R ทีหลัง) → ทำ GIF ใหม่จาก MP4 เดิม
    if (!existsSync(mp4)) return { id, status: result.status, error: 'ไม่มีวิดีโอ' };
    await makeGif(mp4, gif);
    const info = probe(mp4);
    console.log(`✓ ${id} (GIF จาก MP4 เดิม)`);
    return {
      audios: [], ...(manifest[id] || {}), // เก็บข้อมูลเสียง (audioId/offset) ของรอบก่อนไว้
      id, status: result.status, mp4: `test-videos/${id}.mp4`, gif: `test-gifs/${id}.gif`,
      durationSec: Math.round(info.durationSec * 10) / 10, video: info.video, audio: info.audio, hasAudio: !!info.audio, probe: info.tool,
      gifFromMp4: true, mp4Bytes: statSync(mp4).size, gifBytes: statSync(gif).size,
    };
  }
  const audios = (result.attachments || []).filter((a) => a.name === 'audio').map(attJson).filter((a) => a?.audioId);
  const vEnc = [
    '-c:v', 'libx264', '-preset', 'medium', '-crf', MP4_CRF, '-pix_fmt', 'yuv420p', '-r', '25',
    '-vf', `scale='min(${MP4_WIDTH},iw)':-2:flags=lanczos,scale=trunc(iw/2)*2:trunc(ih/2)*2`, '-movflags', '+faststart',
  ];

  const mics = (result.attachments || []).filter((a) => a.name === 'mic').map(attJson).filter((a) => a?.file);
  const wavs = [];
  for (const m of mics) {
    const f = path.join(VOICE_DIR, path.basename(m.file));
    if (existsSync(f)) wavs.push({ kind: 'mic', micFile: m.file, offsetMs: m.offsetMs, durationMs: m.durationMs, file: f });
    else console.warn(`[${id}] ไม่พบไฟล์เสียงคำถาม ${f}`);
  }
  for (const [i, a] of audios.entries()) {
    const f = path.join(TMP, `${id}-${i}.wav`);
    try {
      await downloadWav(a.audioId, f);
      wavs.push({ kind: 'tts', ...a, file: f });
    } catch (e) {
      console.warn(`[${id}] ${e.message}`);
    }
  }

  if (wavs.length) {
    // [1:a]adelay=offset → (amix ถ้ามีหลายเสียง) → apad ให้ยาวเท่าวิดีโอ
    const inputs = wavs.flatMap((w) => ['-i', w.file]);
    const delays = wavs.map((w, i) => `[${i + 1}:a]aresample=48000,adelay=${Math.max(0, Math.round(w.offsetMs))}:all=1[d${i}]`);
    const mix = wavs.length > 1 ? `${wavs.map((_, i) => `[d${i}]`).join('')}amix=inputs=${wavs.length}:normalize=0[m];[m]apad[aout]` : `[d0]apad[aout]`;
    await run(['-y', '-hide_banner', '-loglevel', 'error', '-i', video.path, ...inputs, '-filter_complex', [...delays, mix].join(';'), '-map', '0:v', '-map', '[aout]', ...vEnc, '-c:a', 'aac', '-b:a', '160k', '-shortest', mp4]);
  } else {
    await run(['-y', '-hide_banner', '-loglevel', 'error', '-i', video.path, '-an', ...vEnc, mp4]);
  }
  await makeGif(video.path, gif);
  const info = probe(mp4);
  const out = {
    id,
    status: result.status,
    mp4: `test-videos/${id}.mp4`,
    gif: `test-gifs/${id}.gif`,
    durationSec: Math.round(info.durationSec * 10) / 10,
    video: info.video,
    audio: info.audio,
    hasAudio: !!info.audio,
    probe: info.tool,
    audios: wavs.filter((w) => w.kind === 'tts').map(({ audioId, offsetMs, durationMs, engine }) => ({ audioId, offsetMs, durationMs, engine })),
    mics: wavs.filter((w) => w.kind === 'mic').map(({ micFile, offsetMs, durationMs }) => ({ file: micFile, offsetMs, durationMs })),
    mp4Bytes: statSync(mp4).size,
    gifBytes: statSync(gif).size,
  };
  if (audios.length && !out.hasAudio) console.warn(`[${id}] ⚠ MP4 ไม่มี audio stream`);
  if (out.mics.length && out.hasAudio) {
    // BUILDMART ข้อ 7: เคสเสียง V ต้องได้ยินทั้งคำถามและคำตอบ → ช่วงมีเสียง ≥ 2 ช่วงต่อรอบ
    out.voiced = await voicedSegments(mp4);
    out.voicedTurns = out.mics.length;
    out.voicedOk = out.voiced.segments >= 2 * out.mics.length;
    // ทุกช่วงที่ส่งเสียงเข้าไป (คำถาม + คำตอบ) ต้องมีเสียงจริงอยู่ในช่วงนั้น
    const spans = wavs.map((w) => [w.offsetMs / 1000, (w.offsetMs + (w.durationMs || 1000)) / 1000, w.kind]);
    out.voicedCovered = spans.filter(([a, b]) => out.voiced.spans.some(([s0, s1]) => s0 < b && s1 > a)).length;
    out.voicedOk &&= out.voicedCovered === spans.length;
    if (!out.voicedOk) console.warn(`[${id}] ⚠ silencedetect: ช่วงมีเสียง ${out.voiced.segments} (ต้อง ≥ ${2 * out.mics.length}) · ครอบคลุม ${out.voicedCovered}/${spans.length}`);
  }
  console.log(`✓ ${id} ${out.durationSec}s ${out.hasAudio ? '🔊 ' + out.audio : ''}`);
  return out;
}

const cases = collect(report.suites).filter((c) => c.result.status !== 'skipped' && wanted(c.id));
const manifestFile = path.join(DIR, 'media.json');
const manifest = existsSync(manifestFile) ? JSON.parse(readFileSync(manifestFile, 'utf8')) : {};
const queue = [...cases];
await Promise.all(
  Array.from({ length: CONCURRENCY }, async () => {
    for (let c; (c = queue.shift()); ) {
      try {
        manifest[c.id] = { ...(await processCase(c)), mode: report.config?.metadata?.mode || 'mock', at: new Date().toISOString() };
      } catch (e) {
        console.error(`✗ ${c.id}: ${e.message}`);
        manifest[c.id] = { id: c.id, error: e.message };
      }
    }
  }),
);
writeFileSync(manifestFile, JSON.stringify(Object.fromEntries(Object.entries(manifest).sort()), null, 2));
const done = Object.values(manifest).filter((m) => m.mp4);
const avg = done.reduce((s, m) => s + (m.durationSec || 0), 0) / (done.length || 1);
console.log(`\nสร้างสื่อ ${cases.length} เคส · ความยาววิดีโอเฉลี่ย ${avg.toFixed(1)} วิ · มีเสียง: ${done.filter((m) => m.hasAudio).map((m) => m.id).join(', ') || '-'}`);
const vs = done.filter((m) => m.mics?.length);
if (vs.length) console.log(`เสียงถาม+ตอบ (silencedetect ≥ 2 ช่วง/รอบ): ${vs.map((m) => `${m.id} ${m.voicedOk ? '✓' : '✗'} ${m.voiced?.segments}/${2 * m.mics.length}`).join(' · ')}`);
