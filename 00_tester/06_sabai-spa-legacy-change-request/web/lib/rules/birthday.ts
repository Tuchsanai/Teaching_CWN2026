// BR-13 ส่วนลดเดือนเกิด 20% 1 ครั้งต่อเดือนเกิด นับตามวันนัด ใช้กับเดี่ยว/คู่/กลุ่มเท่านั้น (A11)
import type { BookingType } from "./party.ts";

export const BIRTHDAY_PCT = 20;

export function isBirthdayMonth(birthDate: string | null, apptDate: string): boolean {
  return !!birthDate && birthDate.slice(5, 7) === apptDate.slice(5, 7);
}

export function birthdayEligible(opts: { birthDate: string | null; apptDate: string; alreadyUsed: boolean; type: BookingType }): boolean {
  if (!["single", "couple", "group"].includes(opts.type)) return false;
  return isBirthdayMonth(opts.birthDate, opts.apptDate) && !opts.alreadyUsed;
}
