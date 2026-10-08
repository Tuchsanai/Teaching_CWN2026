import { cookies } from "next/headers";
import { q, q1 } from "./db";
import { newToken } from "./password";
import { getNow } from "./clock";
import { bkkParts } from "../time";
import { nextTier, TIER_PCT, type Tier, GOLD_MIN, PLATINUM_MIN } from "../rules";
import { mode } from "./env";

export const SESSION_COOKIE = "sabai_session";

export type UserRow = {
  id: number;
  email: string;
  name: string;
  name_en: string | null;
  birth_month: number;
  birth_day: number | null;
  total_spent: number;
  points: number;
  birthday_used_year: number | null;
};

const USER_COLS = "id, email, name, name_en, birth_month, birth_day, total_spent, points, birthday_used_year";

export async function currentUser(): Promise<UserRow | null> {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!token || !/^[a-f0-9]{64}$/.test(token)) return null;
  return q1<UserRow>(`SELECT ${USER_COLS.split(", ").map((c) => "u." + c).join(", ")} FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token = $1`, [token]);
}

export async function startSession(userId: number): Promise<void> {
  const token = newToken();
  await q("INSERT INTO sessions (token, user_id) VALUES ($1, $2)", [token, userId]);
  (await cookies()).set(SESSION_COOKIE, token, { httpOnly: true, sameSite: "lax", path: "/", maxAge: 60 * 60 * 24 * 30 });
}

export async function endSession(): Promise<void> {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  if (token) await q("DELETE FROM sessions WHERE token = $1", [token]);
  jar.delete(SESSION_COOKIE);
}

/** BR-13 */
export function tierOf(spent: number): Tier {
  if (spent >= PLATINUM_MIN) return "platinum";
  if (mode() ? spent > GOLD_MIN : spent >= GOLD_MIN) return "gold";
  return "silver";
}

/** BR-14: birthday month of the (locked) current date, once per year */
export function birthdayStatus(u: UserRow, now: Date): "eligible" | "used" | "not-month" {
  const p = bkkParts(now);
  if (u.birth_month !== p.m) return "not-month";
  if (u.birthday_used_year === p.y) return "used";
  return "eligible";
}

export async function memberSummary(u: UserRow) {
  const now = await getNow();
  const tier = tierOf(u.total_spent);
  const nt = nextTier(tier, u.total_spent);
  return {
    id: u.id,
    email: u.email,
    name: u.name,
    nameEn: u.name_en ?? u.name,
    birthMonth: u.birth_month,
    totalSpent: u.total_spent,
    points: u.points,
    tier,
    tierPct: TIER_PCT[tier],
    nextTier: nt ? nt.tier : null,
    nextTierNeed: nt ? nt.need : 0,
    birthday: birthdayStatus(u, now),
  };
}
