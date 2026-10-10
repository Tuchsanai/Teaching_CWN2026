// BR-15 มูลค่า ฿500–฿10,000 จำนวนเต็ม · BR-16 ใช้ได้ 365 วัน (วันที่ 365 ยังใช้ได้) ใช้ได้หลายครั้งจนหมด
import { addDays } from "./time.ts";

export const GC_MIN = 500;
export const GC_MAX = 10000;
export const GC_DAYS = 365;
export const GC_DESIGNS = ["orchid", "lotus", "gold"] as const;
export const GC_CHANNELS = ["line", "email"] as const;

export function isValidFaceValue(baht: unknown): boolean {
  return typeof baht === "number" && Number.isInteger(baht) && baht >= GC_MIN && baht <= GC_MAX;
}

export function giftCardExpiry(purchasedOn: string): string {
  return addDays(purchasedOn, GC_DAYS);
}

export type GiftCardStatus = "ok" | "expired" | "empty";

/** ตรวจอายุจากวันที่จ่าย (วันนี้ตามนาฬิการะบบ T14) */
export function giftCardStatus(today: string, expiresOn: string, balance: number): GiftCardStatus {
  if (today > expiresOn) return "expired";
  if (balance <= 0) return "empty";
  return "ok";
}

export function applyGiftCard(balance: number, due: number): number {
  return Math.max(0, Math.min(balance, due));
}
