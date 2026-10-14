// แปลงวิดีโอจากการเทสต์ (videos/*.webm) -> .gif + .mp4 ไว้ใช้ในเอกสาร
// ใช้:  node make-media.mjs  [โฟลเดอร์ปลายทาง]
// ค่าเริ่มต้นปลายทาง: ../../../image/ex2  (01_VastAi_Skill/image/ex2)
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const here = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(here, "videos");
const outDir = path.resolve(process.argv[2] || path.join(here, "..", "..", "..", "image", "ex2"));
const GIF_WIDTH = 800;
const MAX_GIF_MB = 6;

// 1) หา ffmpeg: ใช้ตัวในเครื่องก่อน ถ้าไม่มีใช้ ffmpeg-static (npm)
function findFfmpeg() {
  const r = spawnSync("ffmpeg", ["-version"], { stdio: "ignore", shell: false });
  if (r.status === 0) return "ffmpeg";
  try {
    const p = createRequire(import.meta.url)("ffmpeg-static");
    if (p && fs.existsSync(p)) return p;
  } catch {}
  console.error(
    "ไม่พบ ffmpeg — ติดตั้งก่อน เช่น  winget install Gyan.FFmpeg  (แล้วเปิด Git Bash ใหม่)\n" +
      "หรือ  npm install-scripts approve ffmpeg-static && npm rebuild ffmpeg-static"
  );
  process.exit(1);
}
const FFMPEG = findFfmpeg();

function run(args) {
  const r = spawnSync(FFMPEG, ["-hide_banner", "-loglevel", "error", "-y", ...args], { stdio: "inherit" });
  if (r.status !== 0) throw new Error("ffmpeg failed: " + args.join(" "));
}

function makeGif(input, output, fps) {
  const filter =
    `fps=${fps},scale=${GIF_WIDTH}:-1:flags=lanczos,split[a][b];` +
    `[a]palettegen=max_colors=128:stats_mode=diff[p];` +
    `[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`;
  const tmp = output.replace(/\.gif$/, ".tmp.gif"); // เขียนไฟล์ชั่วคราวก่อน แล้วค่อยแทนที่
  run(["-i", input, "-filter_complex", filter, "-loop", "0", tmp]);
  fs.rmSync(output, { force: true });
  fs.renameSync(tmp, output);
}

if (!fs.existsSync(srcDir)) {
  console.error(`ไม่พบโฟลเดอร์ ${srcDir} — รัน  npx playwright test  ก่อนนะ`);
  process.exit(1);
}
const videos = fs.readdirSync(srcDir).filter((f) => f.endsWith(".webm")).sort();
if (!videos.length) {
  console.error("ไม่มีไฟล์ .webm ใน videos/ — รัน  npx playwright test  ก่อนนะ");
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });
console.log(`ffmpeg: ${FFMPEG}\nปลายทาง: ${outDir}\n`);

for (const f of videos) {
  const slug = path.basename(f, ".webm"); // เช่น case1-hours
  const input = path.join(srcDir, f);
  const gif = path.join(outDir, `ex2-${slug}.gif`);
  const mp4 = path.join(outDir, `ex2-${slug}.mp4`);

  // MP4 (H.264) — เปิดได้ทุกเครื่อง/ทุกเบราว์เซอร์
  run(["-i", input, "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p",
       "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-movflags", "+faststart", "-an", mp4]);

  // GIF — ลอง 10 fps ก่อน ถ้าใหญ่เกินค่อยลด fps
  let size = 0;
  for (const fps of [10, 8, 6, 5]) {
    makeGif(input, gif, fps);
    size = fs.statSync(gif).size / 1024 / 1024;
    if (size <= MAX_GIF_MB) break;
  }
  const mp4Size = fs.statSync(mp4).size / 1024 / 1024;
  console.log(`✔ ${slug}: gif ${size.toFixed(2)} MB, mp4 ${mp4Size.toFixed(2)} MB`);
}
console.log("\nเสร็จแล้ว 🎉");
