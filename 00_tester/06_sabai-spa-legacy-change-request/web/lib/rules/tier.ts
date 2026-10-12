// BR-11 ระดับสมาชิก · BR-12 ข้อความ "อีก ฿X ถึงระดับถัดไป" (หน่วยเงินเป็นสตางค์)

export type Tier = "silver" | "gold" | "platinum";

export const GOLD_MIN = 10000_00;
export const PLATINUM_MIN = 30000_00;

export const TIER_PCT: Record<Tier, number> = { silver: 0, gold: 5, platinum: 10 };

export function tierOf(spend: number): Tier {
  if (spend >= PLATINUM_MIN) return "platinum";
  if (spend >= GOLD_MIN) return "gold";
  return "silver";
}

export function nextTier(spend: number): { next: Tier; remaining: number } | null {
  const t = tierOf(spend);
  if (t === "silver") return { next: "gold", remaining: GOLD_MIN - spend };
  if (t === "gold") return { next: "platinum", remaining: PLATINUM_MIN - spend };
  return null;
}
