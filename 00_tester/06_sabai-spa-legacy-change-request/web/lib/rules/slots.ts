// BR-01 ร้านเปิด 10:00–22:00 รอบเริ่มทุก 30 นาที บริการต้องจบไม่เกิน 22:00
import { minutesOf, timeOf } from "./time.ts";

export const OPEN_MIN = 10 * 60;
export const CLOSE_MIN = 22 * 60;
export const SLOT_STEP_MIN = 30;

function fitsDay(startMin: number, durationMin: number): boolean {
  return startMin + durationMin <= CLOSE_MIN;
}

/** รอบเวลาเริ่มทั้งหมดของบริการที่ยาว durationMin นาที */
export function buildSlots(durationMin: number): string[] {
  const out: string[] = [];
  for (let t = OPEN_MIN; t < CLOSE_MIN; t += SLOT_STEP_MIN) {
    if (fitsDay(t, durationMin)) out.push(timeOf(t));
  }
  return out;
}

export function isValidStartTime(time: string, durationMin: number): boolean {
  return buildSlots(durationMin).includes(time);
}

export function endTimeOf(time: string, durationMin: number): string {
  return timeOf(minutesOf(time) + durationMin);
}
