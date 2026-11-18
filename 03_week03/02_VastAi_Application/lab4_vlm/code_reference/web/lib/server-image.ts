import sharp from "sharp";
import { readFile } from "fs/promises";
import path from "path";
import { SAMPLES } from "./samples";

export const MAX_SIDE = 1280;

/** Uploaded file or sample id -> JPEG whose long side is at most 1280 px. */
export async function loadImage(form: FormData): Promise<{ jpeg: Buffer; title: string }> {
  const sampleId = form.get("sample");
  let raw: Buffer, title: string;
  if (typeof sampleId === "string" && sampleId) {
    const s = SAMPLES.find((x) => x.id === sampleId);
    if (!s) throw new Error("ไม่พบใบเสร็จตัวอย่าง " + sampleId);
    raw = await readFile(path.join(process.cwd(), "public", s.image));
    title = s.id;
  } else {
    const f = form.get("file");
    if (!(f instanceof File)) throw new Error("กรุณาเลือกรูปใบเสร็จ");
    raw = Buffer.from(await f.arrayBuffer());
    title = f.name.replace(/\.[^.]+$/, "") || "ใบเสร็จ";
  }
  const jpeg = await sharp(raw).rotate()
    .resize({ width: MAX_SIDE, height: MAX_SIDE, fit: "inside", withoutEnlargement: true })
    .jpeg({ quality: 92 }).toBuffer();
  return { jpeg, title };
}
