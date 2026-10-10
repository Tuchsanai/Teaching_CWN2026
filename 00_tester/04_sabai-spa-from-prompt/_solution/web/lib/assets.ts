// ไฟล์รูปทั้งหมดอยู่ที่ public/assets (ดู ASSETS.md) · ชื่อ → path
// รูปที่ Codex สร้างไม่สำเร็จจะเป็น .svg แทน (กำหนดใน SVG_ASSETS)
const SVG_ASSETS = new Set<string>([]);

export function asset(name: string): string {
  return `/assets/${name}.${SVG_ASSETS.has(name) ? "svg" : "webp"}`;
}

export function serviceImage(code: string): string {
  return asset(`svc-${code.toLowerCase()}`);
}

export function therapistImage(code: string): string {
  return asset(`thr-${code.toLowerCase()}`);
}
