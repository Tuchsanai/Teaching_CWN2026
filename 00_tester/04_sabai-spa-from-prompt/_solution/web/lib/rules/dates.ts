// BR-03 วันที่จองได้ = พรุ่งนี้ (+1) ถึง +30 วันนับจากวันนี้
import { addDays, diffDays } from "./time.ts";

export const MIN_DAYS_AHEAD = 1;
export const MAX_DAYS_AHEAD = 30;

export function isBookableDate(today: string, date: string): boolean {
  const d = diffDays(today, date);
  return d >= MIN_DAYS_AHEAD && d <= MAX_DAYS_AHEAD;
}

export function bookableRange(today: string): { min: string; max: string } {
  return { min: addDays(today, MIN_DAYS_AHEAD), max: addDays(today, MAX_DAYS_AHEAD) };
}
