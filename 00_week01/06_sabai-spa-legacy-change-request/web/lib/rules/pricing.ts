// BR-06 ส่วนลดกลุ่ม · BR-19 แพ็กเกจ · BR-20 ลำดับคิดราคา (เงินทุกค่าเป็นสตางค์)
//   ① ราคาเต็ม → ② ส่วนลด % ที่มากที่สุด 1 อัน → ③ หักแลกแต้ม → ④ บวกค่ารถ → ⑤ Gift Card / ช่องทางอื่น
import { BIRTHDAY_PCT } from "./birthday.ts";
import type { BookingType } from "./party.ts";
import { earnBase, pointsFor, redeemPoints } from "./points.ts";
import { transportQuote } from "./transport.ts";
import { applyGiftCard } from "./giftcard.ts";

export const GROUP_DISCOUNT_MIN_PEOPLE = 4;
export const GROUP_PCT = 10;

export type DiscountKind = "none" | "group" | "tier" | "birthday";

export interface PriceInput {
  type: BookingType;
  unitPrice: number;
  people: number;
  tierPct: number;
  birthdayApplied: boolean;
  points: number;
  redeemBlocks: number;
  transport: { distanceKm: number } | null;
  giftCardBalance: number | null;
}

export interface PriceResult {
  gross: number;
  discountKind: DiscountKind;
  discountPct: number;
  discountAmount: number;
  pointsRedeemed: number;
  pointsDiscount: number;
  subtotal: number;
  distanceKm: number | null;
  vehicles: number;
  perVehicle: number;
  transportFee: number;
  total: number;
  giftcardPaid: number;
  otherPaid: number;
  pointsToEarn: number;
}

export type PriceOutcome = { ok: true; price: PriceResult } | { ok: false; code: "OUT_OF_AREA" | "BAD_DISTANCE" };

/** ส่วนลด % ที่มากที่สุดเพียง 1 อัน (เท่ากันเลือกตามลำดับ กลุ่ม → ระดับ → เดือนเกิด) */
export function bestPercent(input: Pick<PriceInput, "type" | "people" | "tierPct" | "birthdayApplied">): { kind: DiscountKind; pct: number } {
  if (input.type === "package" || input.type === "course") return { kind: "none", pct: 0 };
  const candidates: { kind: DiscountKind; pct: number }[] = [
    { kind: "group", pct: input.type === "group" && input.people >= GROUP_DISCOUNT_MIN_PEOPLE ? GROUP_PCT : 0 },
    { kind: "tier", pct: input.tierPct },
    { kind: "birthday", pct: input.birthdayApplied ? BIRTHDAY_PCT : 0 },
  ];
  let best: { kind: DiscountKind; pct: number } = { kind: "none", pct: 0 };
  for (const c of candidates) if (c.pct > best.pct) best = c;
  return best;
}

export function percentOf(amount: number, pct: number): number {
  return Math.round((amount * pct) / 100);
}

export function calcPrice(input: PriceInput): PriceOutcome {
  const gross = input.type === "course" ? 0 : input.unitPrice * input.people;
  const best = bestPercent(input);

  // ② ส่วนลด % → ③ หักแลกแต้ม
  const discountAmount = percentOf(gross, best.pct);
  const r = redeemPoints(input.type === "course" ? 0 : input.redeemBlocks, input.points, gross - discountAmount);
  const pointsRedeemed = r.blocks * 100;
  const pointsDiscount = r.discount;
  const subtotal = gross - discountAmount - pointsDiscount;

  let distanceKm: number | null = null;
  let vehicles = 0;
  let perVehicle = 0;
  let transportFee = 0;
  if (input.transport) {
    const tq = transportQuote(input.transport.distanceKm, input.people, input.type === "package");
    if (!tq.ok) return { ok: false, code: tq.code };
    distanceKm = tq.distanceKm;
    vehicles = tq.vehicles;
    perVehicle = tq.perVehicle;
    transportFee = tq.fee;
  }

  const total = subtotal + transportFee;
  const giftcardPaid = input.giftCardBalance ? applyGiftCard(input.giftCardBalance, total) : 0;
  const otherPaid = total - giftcardPaid;
  const pointsToEarn = pointsFor(earnBase({ gross, discountAmount, pointsDiscount, giftcardPaid }));

  return {
    ok: true,
    price: {
      gross,
      discountKind: best.pct > 0 ? best.kind : "none",
      discountPct: best.pct,
      discountAmount,
      pointsRedeemed,
      pointsDiscount,
      subtotal,
      distanceKm,
      vehicles,
      perVehicle,
      transportFee,
      total,
      giftcardPaid,
      otherPaid,
      pointsToEarn,
    },
  };
}
