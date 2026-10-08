import type { PoolClient } from "pg";
import { q, q1, tx } from "./db";
import { getNow } from "./clock";
import { AppError } from "./http";
import { birthdayStatus, tierOf, type UserRow } from "./auth";
import { mode } from "./env";
import {
  allSlotStarts, bkkDate, bkkInstant, bkkParts, canCancel, hhmmToMin, isBookableDate, isDateStr, minToHHMM, slotFits,
} from "../time";
import {
  COURSE_SERVICE, computeQuote, kindForPeople, transportQuote, type BookingKind, type Quote, type TransportQuote,
} from "../rules";

export type ServiceRow = {
  slug: string; sort: number; category: string; duration: number; price: number; herbs: string[]; image: string; is_package: boolean;
  name_th: string; name_en: string; name_zh: string; desc_th: string; desc_en: string; desc_zh: string;
};

export async function getService(slug: unknown, c?: PoolClient): Promise<ServiceRow | null> {
  if (typeof slug !== "string" || !slug) return null;
  const sql = "SELECT * FROM services WHERE slug = $1";
  return c ? (await c.query<ServiceRow>(sql, [slug])).rows[0] ?? null : q1<ServiceRow>(sql, [slug]);
}

export type BookingParams = {
  service?: string;
  date?: string;
  time?: string;
  people?: number;
  kind?: string;
  therapistId?: number | null;
  redeemSets?: number;
  useBirthday?: boolean;
  transport?: boolean;
  hotelId?: number | null;
  payWith?: "cash" | "course";
  giftCode?: string | null;
  guestName?: string;
  guestPhone?: string;
  source?: string;
};

export function normalizeParams(raw: Record<string, unknown>): BookingParams {
  const num = (v: unknown) => (v === null || v === undefined || v === "" ? undefined : Number(v));
  return {
    service: typeof raw.service === "string" ? raw.service : undefined,
    date: typeof raw.date === "string" ? raw.date : undefined,
    time: typeof raw.time === "string" ? raw.time : undefined,
    people: num(raw.people) ?? 1,
    kind: typeof raw.kind === "string" ? raw.kind : undefined,
    therapistId: num(raw.therapistId) || null,
    redeemSets: num(raw.redeemSets) ?? 0,
    useBirthday: raw.useBirthday === true || raw.useBirthday === "true",
    transport: raw.transport === true || raw.transport === "true",
    hotelId: num(raw.hotelId) || null,
    payWith: raw.payWith === "course" ? "course" : "cash",
    giftCode: typeof raw.giftCode === "string" && raw.giftCode.trim() ? raw.giftCode.trim().toUpperCase() : null,
    guestName: typeof raw.guestName === "string" ? raw.guestName.trim() : undefined,
    guestPhone: typeof raw.guestPhone === "string" ? raw.guestPhone.trim() : undefined,
    source: raw.source === "chatbot" ? "chatbot" : "web",
  };
}

/** BR-06 / BR-07 — people & kind */
export function checkPeople(p: BookingParams): BookingKind {
  const people = p.people ?? 1;
  const k = kindForPeople(people);
  if (k === "call") throw new AppError("GROUP_TOO_LARGE");
  if (k === null) throw new AppError("PEOPLE_INVALID");
  if (p.kind === "couple" && people !== 2) throw new AppError("COUPLE_NEEDS_TWO");
  if (p.kind === "group" && k !== "group") throw new AppError("GROUP_NEEDS_THREE");
  if (p.kind === "single" && people !== 1) throw new AppError("PEOPLE_INVALID");
  return k;
}

async function therapistIds(c?: PoolClient): Promise<number[]> {
  const sql = "SELECT id FROM therapists ORDER BY id";
  const rows = c ? (await c.query<{ id: number }>(sql)).rows : await q<{ id: number }>(sql);
  return rows.map((r) => r.id);
}

type Interval = { resource: string; start: number; end: number };

async function intervalsBetween(from: Date, to: Date, c?: PoolClient): Promise<Interval[]> {
  const sql = "SELECT resource, start_at, end_at FROM booking_resources WHERE start_at < $2 AND end_at > $1";
  const rows = c
    ? (await c.query<{ resource: string; start_at: Date; end_at: Date }>(sql, [from, to])).rows
    : await q<{ resource: string; start_at: Date; end_at: Date }>(sql, [from, to]);
  return rows.map((r) => ({ resource: r.resource, start: new Date(r.start_at).getTime(), end: new Date(r.end_at).getTime() }));
}

/** resources busy in [start, end) — touching end/start (e.g. 14:00–15:00 vs 15:00) is NOT an overlap (BR-04) */
function busyIn(intervals: Interval[], start: number, end: number): Set<string> {
  const s = new Set<string>();
  for (const i of intervals) if (i.start < end && i.end > start) s.add(i.resource);
  return s;
}

/** FR-02 / BR-04 / BR-06: pick therapists (+ Couple Suite). null = "เวลานี้ถูกจองแล้ว" */
function assign(busy: Set<string>, allTherapists: number[], people: number, kind: BookingKind, therapistId: number | null) {
  const taken = (id: number) => !mode() && busy.has(`T:${id}`);
  const chosen: number[] = [];
  if (therapistId) {
    if (taken(therapistId)) return null;
    chosen.push(therapistId);
  }
  for (const id of allTherapists) {
    if (chosen.length >= people) break;
    if (!chosen.includes(id) && !taken(id)) chosen.push(id);
  }
  if (chosen.length < people) return null;
  let room: string | null = null;
  if (kind === "couple") {
    if (busy.has("R:couple-suite")) return null;
    room = "couple-suite";
  }
  return { therapists: chosen, room };
}

export type Slot = { time: string; status: "free" | "booked" | "closed" };

/** FR-01: every 30-min start between 10:00 and 21:30 with its status */
export async function availability(p: BookingParams) {
  const svc = await getService(p.service);
  if (!svc) throw new AppError("SERVICE_REQUIRED");
  const kind = checkPeople(p);
  if (!p.date || !isDateStr(p.date)) throw new AppError("DATE_REQUIRED");
  const now = await getNow();
  if (!isBookableDate(p.date, now)) throw new AppError("DATE_OUT_OF_RANGE");
  const dayStart = bkkInstant(p.date, 0);
  const dayEnd = new Date(dayStart.getTime() + 24 * 3600_000);
  const intervals = await intervalsBetween(dayStart, dayEnd);
  const all = await therapistIds();
  const slots: Slot[] = allSlotStarts().map((m) => {
    if (!slotFits(m, svc.duration)) return { time: minToHHMM(m), status: "closed" };
    const start = bkkInstant(p.date!, m).getTime();
    const end = start + svc.duration * 60_000;
    const ok = assign(busyIn(intervals, start, end), all, p.people ?? 1, kind, p.therapistId ?? null);
    return { time: minToHHMM(m), status: ok ? "free" : "booked" };
  });
  return { service: svc.slug, duration: svc.duration, date: p.date, people: p.people ?? 1, kind, slots };
}

type GiftRow = { code: string; amount: number; balance: number; design: string; purchased_on: string; expires_on: string };
type CourseRow = { id: number; user_id: number; total_sessions: number; used_sessions: number; purchased_on: string; expires_on: string };

export async function findGift(code: string, c?: PoolClient): Promise<GiftRow | null> {
  const sql = "SELECT code, amount, balance, design, to_char(purchased_on,'YYYY-MM-DD') AS purchased_on, to_char(expires_on,'YYYY-MM-DD') AS expires_on FROM gift_cards WHERE code = $1";
  return c ? (await c.query<GiftRow>(sql + " FOR UPDATE", [code])).rows[0] ?? null : q1<GiftRow>(sql, [code]);
}

/** BR-18 → null when usable, else error code */
export function giftProblem(g: GiftRow | null, today: string): string | null {
  if (!g) return "GIFT_NOT_FOUND";
  if (today > g.expires_on) return "GIFT_EXPIRED";
  if (g.balance <= 0) return "GIFT_EMPTY";
  return null;
}

export async function userCourses(userId: number, c?: PoolClient): Promise<CourseRow[]> {
  const sql = `SELECT id, user_id, total_sessions, used_sessions, to_char(purchased_on,'YYYY-MM-DD') AS purchased_on, to_char(expires_on,'YYYY-MM-DD') AS expires_on
               FROM courses WHERE user_id = $1 ORDER BY expires_on DESC, id DESC`;
  return c ? (await c.query<CourseRow>(sql, [userId])).rows : q<CourseRow>(sql, [userId]);
}

/** BR-15 / BR-16 → usable course or an error code */
export function pickCourse(courses: CourseRow[], today: string): { course: CourseRow | null; problem: string | null } {
  if (!courses.length) return { course: null, problem: "COURSE_NONE" };
  const usable = courses.find((c) => today <= c.expires_on && c.total_sessions - c.used_sessions > 0);
  if (usable) return { course: usable, problem: null };
  const live = courses.find((c) => today <= c.expires_on);
  return { course: null, problem: live ? "COURSE_EMPTY" : "COURSE_EXPIRED" };
}

export type QuoteResult = {
  quote: Quote;
  issues: string[];
  service: ServiceRow;
  kind: BookingKind;
  transport: TransportQuote | null;
  hotel: { id: number; name: string; name_zh: string; distance_km: number } | null;
  courseId: number | null;
  birthday: "eligible" | "used" | "not-month" | null;
};

/** FR-06: price breakdown for the current visitor (member benefits when logged in) */
export async function buildQuote(p: BookingParams, user: UserRow | null, now: Date, c?: PoolClient): Promise<QuoteResult> {
  const svc = await getService(p.service, c);
  if (!svc) throw new AppError("SERVICE_REQUIRED");
  const kind = checkPeople(p);
  const people = p.people ?? 1;
  const today = bkkDate(now);
  const issues: string[] = [];

  let transport: TransportQuote | null = null;
  let hotel: QuoteResult["hotel"] = null;
  if (p.transport) {
    if (!p.hotelId) issues.push("HOTEL_REQUIRED");
    else {
      const sql = "SELECT id, name, name_zh, distance_km::float AS distance_km FROM hotels WHERE id = $1";
      hotel = c ? (await c.query(sql, [p.hotelId])).rows[0] ?? null : await q1(sql, [p.hotelId]);
      if (!hotel) issues.push("HOTEL_REQUIRED");
      else {
        transport = transportQuote(Number(hotel.distance_km), people);
        if (!transport.ok) issues.push(transport.code);
      }
    }
  }

  let courseId: number | null = null;
  const payWithCourse = p.payWith === "course";
  if (payWithCourse) {
    if (!user) issues.push("LOGIN_REQUIRED");
    else if (svc.slug !== COURSE_SERVICE || people !== 1) issues.push("COURSE_NOT_APPLICABLE");
    else {
      const { course, problem } = pickCourse(await userCourses(user.id, c), today);
      if (problem) issues.push(problem);
      else courseId = course!.id;
    }
  }

  let giftBalance = 0;
  if (p.giftCode) {
    const g = await findGift(p.giftCode, c);
    const prob = giftProblem(g, today);
    if (prob) issues.push(prob);
    else giftBalance = g!.balance;
  }

  const birthday = user ? birthdayStatus(user, now) : null;
  if (p.useBirthday && user && birthday !== "eligible") issues.push("BIRTHDAY_NOT_ELIGIBLE");
  if (p.useBirthday && !user) issues.push("LOGIN_REQUIRED");
  if ((p.redeemSets ?? 0) > 0) {
    if (!user) issues.push("LOGIN_REQUIRED");
    else if (user.points < 100) issues.push("POINTS_NOT_ENOUGH");
  }

  const quote = computeQuote({
    unitPrice: svc.price,
    people,
    member: user ? { tier: tierOf(user.total_spent), points: user.points, birthdayEligible: birthday === "eligible" } : null,
    useBirthday: !!p.useBirthday,
    redeemSets: p.redeemSets ?? 0,
    payWithCourse: payWithCourse && courseId !== null,
    transport,
    giftBalance,
  });
  return { quote, issues: [...new Set(issues)], service: svc, kind, transport, hotel, courseId, birthday };
}

export async function createBooking(p: BookingParams, sessionUser: UserRow | null) {
  if (!p.service) throw new AppError("SERVICE_REQUIRED");
  const svc = await getService(p.service);
  if (!svc) throw new AppError("SERVICE_REQUIRED");
  const kind = checkPeople(p);
  if (!p.date) throw new AppError("DATE_REQUIRED");
  if (!p.time) throw new AppError("TIME_REQUIRED");
  const startMin = hhmmToMin(p.time);
  if (startMin === null || !slotFits(startMin, svc.duration)) throw new AppError("TIME_INVALID");
  if (!sessionUser && (!p.guestName || !p.guestPhone || p.guestPhone.replace(/\D/g, "").length < 9)) throw new AppError("GUEST_INFO");
  if (p.therapistId) {
    const t = await q1("SELECT id FROM therapists WHERE id = $1", [p.therapistId]);
    if (!t) throw new AppError("THERAPIST_NOT_FOUND");
  }

  return tx(async (c) => {
    // NFR-06: serialise every booking write so two simultaneous requests can never both win
    await c.query("SELECT pg_advisory_xact_lock(727002)");
    const now = await getNow(c);
    if (!isBookableDate(p.date!, now)) throw new AppError("DATE_OUT_OF_RANGE");

    const user = sessionUser
      ? (await c.query<UserRow>("SELECT id, email, name, name_en, birth_month, birth_day, total_spent, points, birthday_used_year FROM users WHERE id = $1 FOR UPDATE", [sessionUser.id])).rows[0] ?? null
      : null;
    const r = await buildQuote(p, user, now, c);
    if (r.issues.length) throw new AppError(r.issues[0]);
    const qt = r.quote;

    const start = bkkInstant(p.date!, startMin);
    const end = new Date(start.getTime() + svc.duration * 60_000);
    const intervals = await intervalsBetween(start, end, c);
    const a = assign(busyIn(intervals, start.getTime(), end.getTime()), await therapistIds(c), qt.people, kind, p.therapistId ?? null);
    if (!a) throw new AppError("SLOT_TAKEN", 409);

    const birthdayUsed = qt.memberDiscountType === "birthday";
    const courseStep = r.courseId ? (mode() ? 0 : 1) : 0;
    const ins = await c.query<{ id: number }>(
      `INSERT INTO bookings (user_id, guest_name, guest_phone, service_slug, kind, people, start_at, end_at, therapist_ids, room_slug, hotel_id, cars,
         subtotal, group_discount, tier_discount, birthday_discount, points_used, points_discount, course_id, course_covered, course_step,
         transport_fee, total, gift_code, gift_used, due, points_earned, spent_added, birthday_used, source)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28,$29,$30) RETURNING id`,
      [user?.id ?? null, user ? null : p.guestName, user ? null : p.guestPhone, svc.slug, kind, qt.people, start, end, a.therapists, a.room,
        r.hotel?.id ?? null, qt.cars, qt.subtotal, qt.groupDiscount, qt.tierDiscount, qt.birthdayDiscount, qt.pointsUsed, qt.pointsDiscount,
        r.courseId, qt.courseCovered, courseStep, qt.transportFee, qt.total, qt.giftUsed > 0 ? p.giftCode : null, qt.giftUsed, qt.due,
        qt.pointsEarned, user ? qt.servicesNet : 0, birthdayUsed, p.source ?? "web"],
    );
    const id = ins.rows[0].id;
    const code = `SB${String(id).padStart(5, "0")}`;
    await c.query("UPDATE bookings SET code = $2 WHERE id = $1", [id, code]);
    for (const t of a.therapists) {
      await c.query("INSERT INTO booking_resources (booking_id, resource, start_at, end_at) VALUES ($1,$2,$3,$4)", [id, `T:${t}`, start, end]);
    }
    if (a.room) await c.query("INSERT INTO booking_resources (booking_id, resource, start_at, end_at) VALUES ($1,$2,$3,$4)", [id, `R:${a.room}`, start, end]);

    if (user) {
      // FR-10: points are deducted (and earned) as soon as the booking succeeds
      await c.query(
        `UPDATE users SET points = points - $2 + $3, total_spent = total_spent + $4, birthday_used_year = CASE WHEN $5 THEN $6 ELSE birthday_used_year END WHERE id = $1`,
        [user.id, qt.pointsUsed, qt.pointsEarned, qt.servicesNet, birthdayUsed, bkkParts(now).y],
      );
    }
    if (r.courseId) await c.query("UPDATE courses SET used_sessions = used_sessions + $2 WHERE id = $1", [r.courseId, courseStep]);
    if (qt.giftUsed > 0) await c.query("UPDATE gift_cards SET balance = balance - $2 WHERE code = $1", [p.giftCode, qt.giftUsed]);

    return {
      id, code, service: svc.slug, date: p.date!, time: minToHHMM(startMin), endTime: minToHHMM(startMin + svc.duration),
      people: qt.people, kind, therapists: a.therapists, room: a.room, quote: qt,
    };
  });
}

/** FR-07 / BR-09 */
export async function cancelBooking(id: number, user: UserRow) {
  return tx(async (c) => {
    await c.query("SELECT pg_advisory_xact_lock(727002)");
    const now = await getNow(c);
    const b = (await c.query("SELECT * FROM bookings WHERE id = $1 AND user_id = $2 FOR UPDATE", [id, user.id])).rows[0];
    if (!b) throw new AppError("NOT_FOUND", 404);
    if (b.status === "cancelled") throw new AppError("ALREADY_CANCELLED", 409);
    if (!canCancel(new Date(b.start_at), now)) throw new AppError("CANCEL_TOO_LATE", 409);
    await c.query("UPDATE bookings SET status = 'cancelled', cancelled_at = $2 WHERE id = $1", [id, now]);
    await c.query("DELETE FROM booking_resources WHERE booking_id = $1", [id]);
    await c.query(
      `UPDATE users SET points = GREATEST(0, points + $2 - $3), total_spent = GREATEST(0, total_spent - $4),
         birthday_used_year = CASE WHEN $5 THEN NULL ELSE birthday_used_year END WHERE id = $1`,
      [user.id, b.points_used, b.points_earned, b.spent_added, b.birthday_used],
    );
    if (b.course_id && b.course_step > 0) await c.query("UPDATE courses SET used_sessions = GREATEST(0, used_sessions - $2) WHERE id = $1", [b.course_id, b.course_step]);
    if (b.gift_code && b.gift_used > 0) await c.query("UPDATE gift_cards SET balance = balance + $2 WHERE code = $1", [b.gift_code, b.gift_used]);
    return { id, code: b.code as string, status: "cancelled" };
  });
}

export async function myBookings(user: UserRow) {
  const now = await getNow();
  const rows = await q(
    `SELECT b.id, b.code, b.service_slug, b.kind, b.people, b.start_at, b.end_at, b.status, b.therapist_ids, b.room_slug, b.total, b.due,
            b.points_earned, b.points_used, b.course_covered, s.name_th, s.name_en, s.name_zh, s.image
       FROM bookings b JOIN services s ON s.slug = b.service_slug
      WHERE b.user_id = $1 ORDER BY b.start_at DESC`,
    [user.id],
  );
  const ther = await q<{ id: number; name_th: string; name_en: string; name_zh: string }>("SELECT id, name_th, name_en, name_zh FROM therapists");
  const tmap = new Map(ther.map((t) => [t.id, t]));
  return rows.map((b) => {
    const start = new Date(b.start_at);
    const end = new Date(b.end_at);
    const sp = bkkParts(start);
    return {
      id: b.id as number,
      code: b.code as string,
      service: b.service_slug as string,
      serviceName: { th: b.name_th, en: b.name_en, zh: b.name_zh },
      image: b.image as string,
      kind: b.kind as string,
      people: b.people as number,
      date: bkkDate(start),
      time: minToHHMM(sp.h * 60 + sp.min),
      endTime: minToHHMM(bkkParts(end).h * 60 + bkkParts(end).min),
      startAt: start.toISOString(),
      status: b.status as string,
      past: start.getTime() <= now.getTime(),
      canCancel: b.status === "confirmed" && canCancel(start, now),
      therapists: (b.therapist_ids as number[]).map((id) => {
        const t = tmap.get(id);
        return { id, th: t?.name_th ?? "", en: t?.name_en ?? "", zh: t?.name_zh ?? "" };
      }),
      room: b.room_slug as string | null,
      total: b.total as number,
      due: b.due as number,
      pointsEarned: b.points_earned as number,
      paidByCourse: (b.course_covered as number) > 0,
    };
  });
}
