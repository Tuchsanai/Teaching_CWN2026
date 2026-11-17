// ทำ GIF ของแต่ละเคส:  out/frames/case<N>-<slug>/  ->  out/gifs/case<N>-<slug>.gif
// ใช้:  node make-media.mjs
// ต้นทางคือภาพหน้าจอที่เทสต์เก็บไว้ทุกครั้งที่จอเปลี่ยน (frames.txt บอกเวลาของแต่ละภาพ)
// GIF กว้าง 800 px, 8 fps, ใช้ palette — ถ้าไฟล์ใหญ่เกิน 1.5 MB จะลด fps/จำนวนสีลงเอง
// (วิดีโอเต็มของแต่ละเคสอยู่ที่ out/videos/*.webm — ไม่ใช้ทำ GIF เพราะ noise ของวิดีโอทำให้ GIF ใหญ่ขึ้นหลายเท่า)
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(here, "out", "frames");
const outDir = path.join(here, "out", "gifs");
const GIF_WIDTH = 800;
const MAX_GIF_MB = 1.5;
const TRIES = [
  { fps: 8, colors: 128 },
  { fps: 6, colors: 96 },
  { fps: 5, colors: 64 },
  { fps: 4, colors: 48 },
];

if (spawnSync("ffmpeg", ["-version"], { stdio: "ignore" }).status !== 0) {
  console.error("ไม่พบ ffmpeg — ติดตั้งก่อน:  apt-get install -y ffmpeg");
  process.exit(1);
}

/** frames.txt ("<เวลา> <ไฟล์>" ต่อบรรทัด, บรรทัดสุดท้าย "<เวลาจบ> END") -> ไฟล์รายการภาพพร้อมระยะเวลาสำหรับ ffmpeg */
function writeConcatList(dir) {
  const rows = fs.readFileSync(path.join(dir, "frames.txt"), "utf8").trim().split("\n").map((l) => l.split(" "));
  const frames = rows.filter((r) => r[1] !== "END");
  if (!frames.length) return null;
  const endTime = Number(rows[rows.length - 1][0]);
  const lines = ["ffconcat version 1.0"];
  frames.forEach(([time, file], i) => {
    const next = i + 1 < frames.length ? Number(frames[i + 1][0]) : endTime;
    lines.push(`file ${file}`, `duration ${Math.max(next - Number(time), 0.01).toFixed(3)}`);
  });
  lines.push(`file ${frames[frames.length - 1][1]}`); // ffmpeg ต้องการภาพสุดท้ายซ้ำอีกครั้ง
  const list = path.join(dir, "list.txt");
  fs.writeFileSync(list, lines.join("\n") + "\n");
  return list;
}

function makeGif(list, output, { fps, colors }) {
  const filter =
    `fps=${fps},scale=${GIF_WIDTH}:-1:flags=lanczos,split[a][b];` +
    `[a]palettegen=max_colors=${colors}:stats_mode=full[p];` +
    `[b][p]paletteuse=dither=none:diff_mode=rectangle`;
  const r = spawnSync(
    "ffmpeg",
    ["-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", list,
     "-filter_complex", filter, "-loop", "0", output],
    { stdio: "inherit" }
  );
  if (r.status !== 0) throw new Error("ffmpeg ทำงานไม่สำเร็จ: " + list);
  return fs.statSync(output).size / 1024 / 1024;
}

const caseNo = (name) => Number((name.match(/^case(\d+)/) || [])[1] || 0);
const names = fs.existsSync(srcDir)
  ? fs.readdirSync(srcDir).filter((d) => fs.existsSync(path.join(srcDir, d, "frames.txt"))).sort((a, b) => caseNo(a) - caseNo(b))
  : [];
if (!names.length) {
  console.error(`ไม่มีภาพหน้าจอใน ${srcDir} — รันเทสต์ก่อน (bash run-all.sh)`);
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });

let made = 0;
for (const name of names) {
  const list = writeConcatList(path.join(srcDir, name));
  if (!list) continue;
  const gif = path.join(outDir, `${name}.gif`);
  let size = 0;
  for (const t of TRIES) {
    size = makeGif(list, gif, t);
    if (size <= MAX_GIF_MB) break;
  }
  made++;
  console.log(`${name}.gif  ${size.toFixed(2)} MB${size > MAX_GIF_MB ? "  (ยังใหญ่เกิน 1.5 MB)" : ""}`);
}
console.log(`\nได้ GIF ${made} ไฟล์ที่ ${outDir}`);
