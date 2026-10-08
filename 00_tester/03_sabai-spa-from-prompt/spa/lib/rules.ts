// Shared, pure business rules (BR-06 … BR-21). No I/O here.

export type Tier = "silver" | "gold" | "platinum";
export const TIER_PCT: Record<Tier, number> = { silver: 0, gold: 5, platinum: 10 }; // BR-13
export const GOLD_MIN = 10_000;
export const PLATINUM_MIN = 30_000;

export const POINT_BAHT = 100; // BR-11: every ฿100 = 1 point
export const REDEEM_POINTS = 100; // BR-12: 100 points …
export const REDEEM_BAHT = 50; // … = ฿50 off
export const BIRTHDAY_PCT = 20; // BR-14
export const GROUP_MIN = 3; // BR-07
export const GROUP_MAX = 6; // BR-07
export const GROUP_DISCOUNT_MIN = 4; // BR-08
export const GROUP_DISCOUNT_PCT = 10; // BR-08
export const COURSE_PRICE = 15_000; // BR-15
export const COURSE_SESSIONS = 11; // BR-15 (10 + 1 free)
export const COURSE_DAYS = 180; // BR-15
export const COURSE_SERVICE = "body-contouring";
export const GIFT_MIN = 500; // BR-17
export const GIFT_MAX = 10_000; // BR-17
export const GIFT_DAYS = 365; // BR-18
export const GIFT_DESIGNS = ["orchid", "lotus", "gold"] as const; // BR-17
export const GIFT_CHANNELS = ["line", "email"] as const; // BR-17
export const TRANSPORT_FREE_KM = 5; // BR-20
export const TRANSPORT_MAX_KM = 15; // BR-20
export const TRANSPORT_FEE = 300; // BR-20 (per car)
export const CAR_SEATS = 4; // BR-21
export const PACKAGE_SLUG = "bangkok-relax"; // BR-19

export type BookingKind = "single" | "couple" | "group";

/** BR-06 / BR-07: people → kind. null = must call the shop (7+) or invalid */
export function kindForPeople(people: number): BookingKind | "call" | null {
  if (!Number.isInteger(people) || people < 1) return null;
  if (people === 1) return "single";
  if (people === 2) return "couple";
  if (people <= GROUP_MAX) return "group";
  return "call";
}

/** BR-11: ฿100 = 1 point, remainder dropped */
export function pointsFor(amount: number): number {
  return Math.max(0, Math.floor(amount / POINT_BAHT));
}

/** BR-12: how many ฿50 sets can be redeemed */
export function maxRedeemSets(points: number, payable: number): number {
  return Math.max(0, Math.min(Math.floor(points / REDEEM_POINTS), Math.floor(payable / REDEEM_BAHT)));
}

export function nextTier(tier: Tier, spent: number): { tier: Tier; need: number } | null {
  if (tier === "silver") return { tier: "gold", need: Math.max(0, GOLD_MIN - spent) };
  if (tier === "gold") return { tier: "platinum", need: Math.max(0, PLATINUM_MIN - spent) };
  return null;
}

export type TransportQuote =
  | { ok: true; distanceKm: number; cars: number; feePerCar: number; fee: number }
  | { ok: false; distanceKm: number; cars: number; code: "TRANSPORT_TOO_FAR" };

/** BR-20 / BR-21 */
export function transportQuote(distanceKm: number, people: number): TransportQuote {
  const cars = Math.max(1, Math.ceil(Math.max(1, people) / CAR_SEATS));
  if (distanceKm > TRANSPORT_MAX_KM) return { ok: false, distanceKm, cars, code: "TRANSPORT_TOO_FAR" };
  const feePerCar = distanceKm <= TRANSPORT_FREE_KM ? 0 : TRANSPORT_FEE;
  return { ok: true, distanceKm, cars, feePerCar, fee: feePerCar * cars };
}

export type QuoteInput = {
  unitPrice: number;
  people: number;
  member: null | {
    tier: Tier;
    points: number;
    birthdayEligible: boolean;
  };
  useBirthday: boolean;
  redeemSets: number;
  payWithCourse: boolean;
  transport: TransportQuote | null;
  giftBalance: number; // 0 when no usable gift card
};

export type Quote = {
  unitPrice: number;
  people: number;
  subtotal: number;
  groupDiscount: number;
  memberDiscountType: "tier" | "birthday" | null;
  tier: Tier | null;
  tierPct: number;
  tierDiscount: number;
  birthdayDiscount: number;
  courseCovered: number;
  maxRedeemSets: number;
  redeemSets: number;
  pointsUsed: number;
  pointsDiscount: number;
  servicesNet: number;
  transportRequested: boolean;
  transportOk: boolean;
  distanceKm: number | null;
  cars: number;
  transportFee: number;
  total: number;
  giftUsed: number;
  due: number;
  pointsEarned: number;
};

/**
 * FR-06 price calculation. Order:
 * subtotal → group 10% (4+ people) → max(tier %, birthday 20%) → points (฿50 / 100 pts)
 * → + transport → total → gift card → amount due. Points earned on services net (BR-11).
 */
export function computeQuote(inp: QuoteInput): Quote {
  const people = Math.max(1, inp.people);
  const subtotal = inp.unitPrice * people;
  const t = inp.transport;
  const transportFee = t && t.ok ? t.fee : 0;
  const base: Quote = {
    unitPrice: inp.unitPrice,
    people,
    subtotal,
    groupDiscount: 0,
    memberDiscountType: null,
    tier: inp.member ? inp.member.tier : null,
    tierPct: inp.member ? TIER_PCT[inp.member.tier] : 0,
    tierDiscount: 0,
    birthdayDiscount: 0,
    courseCovered: 0,
    maxRedeemSets: 0,
    redeemSets: 0,
    pointsUsed: 0,
    pointsDiscount: 0,
    servicesNet: subtotal,
    transportRequested: !!t,
    transportOk: t ? t.ok : true,
    distanceKm: t ? t.distanceKm : null,
    cars: t ? t.cars : 0,
    transportFee,
    total: 0,
    giftUsed: 0,
    due: 0,
    pointsEarned: 0,
  };

  if (inp.payWithCourse) {
    base.courseCovered = subtotal;
    base.servicesNet = 0;
    base.total = transportFee;
    base.giftUsed = Math.min(inp.giftBalance, base.total);
    base.due = base.total - base.giftUsed;
    return base;
  }

  const groupDiscount = people >= GROUP_DISCOUNT_MIN ? Math.round((subtotal * GROUP_DISCOUNT_PCT) / 100) : 0;
  const afterGroup = subtotal - groupDiscount;

  let tierDiscount = 0;
  let birthdayDiscount = 0;
  let memberDiscountType: Quote["memberDiscountType"] = null;
  if (inp.member) {
    const tierPct = TIER_PCT[inp.member.tier];
    const canBirthday = inp.useBirthday && inp.member.birthdayEligible;
    if (canBirthday && BIRTHDAY_PCT > tierPct) {
      birthdayDiscount = Math.round((afterGroup * BIRTHDAY_PCT) / 100);
      memberDiscountType = "birthday";
    } else if (tierPct > 0) {
      tierDiscount = Math.round((afterGroup * tierPct) / 100);
      memberDiscountType = "tier";
    }
  }
  const afterMember = afterGroup - tierDiscount - birthdayDiscount;

  const maxSets = inp.member ? maxRedeemSets(inp.member.points, afterMember) : 0;
  const sets = Math.max(0, Math.min(Math.floor(inp.redeemSets || 0), maxSets));
  const pointsDiscount = sets * REDEEM_BAHT;
  const servicesNet = afterMember - pointsDiscount;
  const total = servicesNet + transportFee;
  const giftUsed = Math.min(Math.max(0, inp.giftBalance), total);

  return {
    ...base,
    groupDiscount,
    memberDiscountType,
    tierDiscount,
    birthdayDiscount,
    maxRedeemSets: maxSets,
    redeemSets: sets,
    pointsUsed: sets * REDEEM_POINTS,
    pointsDiscount,
    servicesNet,
    total,
    giftUsed,
    due: total - giftUsed,
    pointsEarned: inp.member ? pointsFor(servicesNet) : 0,
  };
}
