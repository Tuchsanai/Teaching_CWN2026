// ย่อรูปที่ Codex สร้าง → webp
//   ใช้: node scripts/resize.mjs <โฟลเดอร์รูปต้นฉบับ .png>
//   กว้าง ≤ 1600px · panorama (pano-*) ≤ 4096px · รูปร่างกาย before/after (body-*) ไปที่ private/photos (ไม่อยู่ใน public/)
import { mkdirSync, readdirSync } from "node:fs";
import { basename, dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const here = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(here, "..");
const src = process.argv[2];
if (!src) {
  console.error("usage: node scripts/resize.mjs <source-dir>");
  process.exit(1);
}

const publicDir = join(webRoot, "public", "assets");
const privateDir = join(webRoot, "private", "photos");
mkdirSync(publicDir, { recursive: true });
mkdirSync(privateDir, { recursive: true });

const files = readdirSync(src).filter((f) => /\.(png|jpe?g|webp)$/i.test(f));
for (const f of files) {
  const name = basename(f, extname(f));
  if (name.endsWith("-photoreal")) continue;
  const isPano = name.startsWith("pano-");
  const isBody = name.startsWith("body-");
  const maxW = isPano ? 4096 : isBody ? 900 : 1600;
  const outName = isBody ? `c01-${name.replace("body-", "")}.webp` : `${name}.webp`;
  const out = join(isBody ? privateDir : publicDir, outName);
  const info = await sharp(join(src, f))
    .resize({ width: maxW, withoutEnlargement: true })
    .webp({ quality: isPano ? 82 : 78 })
    .toFile(out);
  console.log(`${f} → ${isBody ? "private/photos" : "public/assets"}/${outName} (${info.width}×${info.height}, ${Math.round(info.size / 1024)} KB)`);
}
