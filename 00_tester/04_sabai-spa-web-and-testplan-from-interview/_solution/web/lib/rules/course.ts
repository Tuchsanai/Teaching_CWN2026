// BR-14 คอร์ส ฿15,000 ได้ 10+1 = 11 ครั้ง ใช้ได้ 180 วัน (วันหมดอายุยังใช้ได้ ตรวจจากวันนัด A12)
import { addDays, diffDays } from "./time.ts";

export const COURSE_PRICE = 15000_00;
export const COURSE_SESSIONS = 11;
export const COURSE_DAYS = 180;

export function courseExpiry(purchasedOn: string): string {
  return addDays(purchasedOn, COURSE_DAYS);
}

export function courseRemaining(c: { total: number; used: number; reserved: number }): number {
  return Math.max(0, c.total - c.used - c.reserved);
}

export function canUseCourse(opts: { remaining: number; expiresOn: string; apptDate: string }): boolean {
  return opts.remaining >= 1 && opts.apptDate <= opts.expiresOn;
}

export function isCourseExpired(today: string, expiresOn: string): boolean {
  return today > expiresOn;
}

export function courseDaysLeft(today: string, expiresOn: string): number {
  return Math.max(0, diffDays(today, expiresOn));
}
