// BR-08 คะแนนเฉลี่ยทศนิยม 1 ตำแหน่ง (ปัดครึ่งขึ้น A7) · ตัวกรอง "4.5 ดาวขึ้นไป" ใช้ค่าที่ปัดแล้ว

export const FILTER_MIN_TENTHS = 45;

/** ค่าเฉลี่ยเป็นหน่วย 0.1 ดาว คิดแบบจำนวนเต็มล้วน · ไม่มีรีวิว = null */
export function ratingTenths(sumStars: number, count: number): number | null {
  if (count <= 0) return null;
  return Math.floor((20 * sumStars + count) / (2 * count));
}

/** ปัดค่าเฉลี่ยที่ให้มาเป็นหน่วย 0.1 ดาว (ปัดครึ่งขึ้น) */
export function roundAverage(avg: number): number {
  return Math.floor(avg * 10 + 0.5 + 1e-9);
}

export function formatRating(tenths: number | null): string | null {
  return tenths === null ? null : (tenths / 10).toFixed(1);
}

export function passesRatingFilter(tenths: number | null): boolean {
  return tenths !== null && tenths >= FILTER_MIN_TENTHS;
}
