// BR-07 ยกเลิกเองได้เมื่อเหลือเวลาก่อนนัด ≥ 24 ชม. (24 ชม. พอดียกเลิกได้ A6)

export const CANCEL_MIN_MS = 24 * 3600 * 1000;

export function canCancel(nowMs: number, startMs: number): boolean {
  return startMs - nowMs >= CANCEL_MIN_MS;
}
