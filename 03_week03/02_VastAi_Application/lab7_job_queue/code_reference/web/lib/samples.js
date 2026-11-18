import "server-only";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

export const SAMPLES_DIR = process.env.SAMPLES_DIR || "/samples";
const OK = /^[\w.-]+\.(jpe?g|png|webp)$/i;

export async function listSamples() {
  const names = await readdir(SAMPLES_DIR).catch(() => []);
  return names.filter((n) => OK.test(n)).sort();
}

export async function readSample(name) {
  if (!OK.test(name)) return null;
  const all = await listSamples();
  if (!all.includes(name)) return null;
  return readFile(path.join(SAMPLES_DIR, name));
}

export function mimeOf(name) {
  const ext = name.split(".").pop().toLowerCase();
  return ext === "png" ? "image/png" : ext === "webp" ? "image/webp" : "image/jpeg";
}
