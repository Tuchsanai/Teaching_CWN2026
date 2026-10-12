// บริการจองที่หน้าเว็บและแชทใช้ร่วมกัน (FR-26): ใบเสนอราคา · จอง · ยกเลิก · ใช้บริการเสร็จ · รอบว่าง
// ราคาที่เก็บจริงคิดที่เซิร์ฟเวอร์เสมอ (NFR-17) · จองใน transaction + EXCLUDE (NFR-12)
import type pg from "pg";
import { clock } from "../clock.ts";
import { fromSatang, getPool, query, toSatang, withTx, type Db } from "../db.ts";
import { formatDate, pickName, t, type Lang } from "../i18n.ts";
import { formatBaht, toBaht } from "../money.ts";
import { birthdayEligible } from "../rules/birthday.ts";
import { canCancel } from "../rules/cancel.ts";
import { canUseCourse, courseRemaining } from "../rules/course.ts";
import { bookableRange, isBookableDate } from "../rules/dates.ts";
import { giftCardStatus } from "../rules/giftcard.ts";
import { freeTherapists, type BusySlot } from "../rules/overlap.ts";
import { BOOKING_TYPES, checkParty, type BookingType } from "../rules/party.ts";
import { earnBase, maxRedeemBlocks, pointsFor } from "../rules/points.ts";
import { calcPrice, type PriceResult } from "../rules/pricing.ts";
import { buildSlots, endTimeOf, isValidStartTime } from "../rules/slots.ts";
import { bangkokDate, isDateString, isTimeString, toInstant, yearMonth } from "../rules/time.ts";
import { TIER_PCT, tierOf } from "../rules/tier.ts";
import type { Session } from "../session.ts";
import { getHerbs, getHotel, getServiceByCode, therapistName, type ServiceRow } from "./catalog.ts";
import { birthdayUsed, loadCustomer, type Customer } from "./customer.ts";
import { ApiError } from "./http.ts";

export interface BookingInput {
  type: BookingType;
  serviceCode: string;
  people: number;
  date: string;
  time: string;
  therapists: string[];
  contactName: string;
  contactPhone: string;
  redeemBlocks: number;
  useBirthday: boolean;
  giftCardCode: string | null;
  hotelCode: string | null;
  distanceKm: number | null;
  coursePurchaseId: number | null;
  quotedTotal: number | null;
}

const str = (v: unknown) => (typeof v === "string" ? v.trim() : "");
const num = (v: unknown) => (typeof v === "number" ? v : typeof v === "string" && v.trim() !== "" ? Number(v) : NaN);

export function parseBookingInput(body: Record<string, unknown>): BookingInput {
  const type = str(body.type) as BookingType;
  if (!BOOKING_TYPES.includes(type)) throw new ApiError(422, "BAD_REQUEST", { field: "type" });
  const people = body.people === undefined ? (type === "couple" ? 2 : 1) : num(body.people);
  const serviceCode = str(body.serviceCode || body.service).toUpperCase() || (type === "package" ? "P01" : type === "course" ? "K01" : "");
  const date = str(body.date);
  const time = str(body.time);
  if (!isDateString(date)) throw new ApiError(422, "BAD_REQUEST", { field: "date" });
  if (!isTimeString(time)) throw new ApiError(422, "SLOT_INVALID", { field: "time" });
  const therapists = Array.isArray(body.therapists) ? body.therapists.map((x) => str(x).toUpperCase()).filter(Boolean) : [];
  const redeemBlocks = body.redeemBlocks === undefined || body.redeemBlocks === null ? 0 : num(body.redeemBlocks);
  if (!Number.isInteger(redeemBlocks) || redeemBlocks < 0) throw new ApiError(422, "BAD_REQUEST", { field: "redeemBlocks" });
  const distance = body.distanceKm === undefined || body.distanceKm === null || body.distanceKm === "" ? null : num(body.distanceKm);
  if (distance !== null && (!Number.isFinite(distance) || distance < 0)) throw new ApiError(422, "BAD_DISTANCE");
  const quoted = body.quotedTotal === undefined || body.quotedTotal === null ? null : num(body.quotedTotal);
  if (quoted !== null && !Number.isFinite(quoted)) throw new ApiError(422, "BAD_REQUEST", { field: "quotedTotal" });
  const cpid = body.coursePurchaseId === undefined || body.coursePurchaseId === null ? null : num(body.coursePurchaseId);
  return {
    type,
    serviceCode,
    people: Number.isFinite(people) ? people : NaN,
    date,
    time,
    therapists,
    contactName: str(body.contactName),
    contactPhone: str(body.contactPhone),
    redeemBlocks,
    useBirthday: body.useBirthday === true,
    giftCardCode: str(body.giftCardCode).toUpperCase() || null,
    hotelCode: str(body.hotelCode).toUpperCase() || null,
    distanceKm: distance,
    coursePurchaseId: cpid !== null && Number.isInteger(cpid) ? cpid : null,
    quotedTotal: quoted,
  };
}

function kindMatches(type: BookingType, kind: ServiceRow["kind"]): boolean {
  if (type === "package") return kind === "package";
  if (type === "course") return kind === "course";
  return kind === "single";
}

export interface Quote {
  service: ServiceRow;
  serviceName: string;
  herbs: string[];
  customer: Customer | null;
  input: BookingInput;
  startAt: Date;
  endAt: Date;
  price: PriceResult;
  birthdayAvailable: boolean;
  maxRedeemBlocks: number;
  course: { id: number; remainingBefore: number; expiresOn: string } | null;
  giftCard: { id: number; code: string; balance: number; status: string; expiresOn: string } | null;
  giftCardError: string | null;
}

/** ตรวจกฎทั้งหมดแล้วคิดราคา · lock=true ล็อกแถวลูกค้า/คอร์ส/บัตร (ใช้ตอนจองจริง) */
export async function buildQuote(db: Db, input: BookingInput, session: Session | null, today: string, lang: Lang, lock = false): Promise<Quote> {
  const service = await getServiceByCode(input.serviceCode, db);
  if (!service || !kindMatches(input.type, service.kind)) throw new ApiError(422, "SERVICE_INVALID");

  const partyErr = checkParty(input.type, input.people);
  if (partyErr) throw new ApiError(422, partyErr);

  if (!isBookableDate(today, input.date)) throw new ApiError(422, "DATE_OUT_OF_RANGE", bookableRange(today));
  if (!isValidStartTime(input.time, service.duration_min)) throw new ApiError(422, "SLOT_INVALID");

  const customer = session ? await loadCustomer(db, session.uid, lock) : null;

  let course: Quote["course"] = null;
  if (input.type === "course") {
    if (!customer) throw new ApiError(401, "LOGIN_REQUIRED");
    const cr = await query(
      `SELECT * FROM course_purchase WHERE customer_id = $1 ${input.coursePurchaseId ? "AND id = $2" : ""}
        ORDER BY expires_on, id ${lock ? "FOR UPDATE" : ""}`,
      input.coursePurchaseId ? [customer.id, input.coursePurchaseId] : [customer.id],
      db,
    );
    const usable = cr.rows.find((c) =>
      canUseCourse({
        remaining: courseRemaining({ total: c.total_sessions, used: c.used_sessions, reserved: c.reserved_sessions }),
        expiresOn: c.expires_on,
        apptDate: input.date,
      }),
    );
    if (!usable) throw new ApiError(422, "COURSE_UNAVAILABLE");
    course = {
      id: usable.id,
      remainingBefore: courseRemaining({ total: usable.total_sessions, used: usable.used_sessions, reserved: usable.reserved_sessions }),
      expiresOn: usable.expires_on,
    };
  }

  const tierPct = customer ? TIER_PCT[tierOf(customer.lifetimeSpend)] : 0;
  const bdAvailable = customer
    ? birthdayEligible({
        birthDate: customer.birthDate,
        apptDate: input.date,
        alreadyUsed: await birthdayUsed(db, customer.id, yearMonth(input.date)),
        type: input.type,
      })
    : false;
  if (input.useBirthday && !bdAvailable) throw new ApiError(422, "BIRTHDAY_UNAVAILABLE");

  const points = customer?.points ?? 0;
  if (input.redeemBlocks > 0) {
    if (!customer) throw new ApiError(401, "LOGIN_REQUIRED");
    if (input.type === "course" || input.redeemBlocks > maxRedeemBlocks(points)) throw new ApiError(422, "POINTS_NOT_ENOUGH");
  }

  let distanceKm = input.distanceKm;
  if (input.hotelCode) {
    const h = await getHotel(input.hotelCode, db);
    if (!h) throw new ApiError(422, "BAD_REQUEST", { field: "hotelCode" });
    distanceKm = h.distanceKm;
  }

  let giftCard: Quote["giftCard"] = null;
  let giftCardError: string | null = null;
  if (input.giftCardCode && input.type !== "course") {
    const g = await query(`SELECT * FROM gift_card WHERE code = $1 ${lock ? "FOR UPDATE" : ""}`, [input.giftCardCode], db);
    if (!g.rows[0]) throw new ApiError(422, "GC_NOT_FOUND");
    const row = g.rows[0];
    const balance = toSatang(row.balance);
    const status = giftCardStatus(today, row.expires_on, balance);
    giftCard = { id: row.id, code: row.code, balance, status, expiresOn: row.expires_on };
    if (status === "expired") giftCardError = "GC_EXPIRED";
    else if (status === "empty") giftCardError = "GC_EMPTY";
  }

  const outcome = calcPrice({
    type: input.type,
    unitPrice: toSatang(service.price),
    people: input.people,
    tierPct,
    birthdayApplied: input.useBirthday && bdAvailable,
    points,
    redeemBlocks: input.redeemBlocks,
    transport: distanceKm !== null ? { distanceKm } : null,
    giftCardBalance: giftCard && giftCard.status === "ok" ? giftCard.balance : null,
  });
  if (!outcome.ok) throw new ApiError(422, outcome.code);
  const price = { ...outcome.price, pointsToEarn: customer ? outcome.price.pointsToEarn : 0 };

  const startAt = toInstant(input.date, input.time);
  const endAt = toInstant(input.date, endTimeOf(input.time, service.duration_min));
  return {
    service,
    serviceName: pickName(service, lang),
    herbs: await getHerbs(service.id, lang, db),
    customer,
    input: { ...input, distanceKm },
    startAt,
    endAt,
    price,
    birthdayAvailable: bdAvailable,
    maxRedeemBlocks: customer && input.type !== "course" ? maxRedeemBlocks(points) : 0,
    course,
    giftCard,
    giftCardError,
  };
}

/** บรรทัดราคาสำหรับหน้าสรุป (FR-06, FR-23) */
export function priceLines(q: Quote, lang: Lang) {
  const p = q.price;
  const lines: { key: string; label: string; amount: number; display: string }[] = [];
  const add = (key: string, label: string, amount: number) => lines.push({ key, label, amount: toBaht(amount), display: formatBaht(amount) });
  if (q.input.type === "course") {
    add("course", t(lang, "line.course"), 0);
  } else {
    add("gross", `${t(lang, "line.gross")} (${formatBaht(toSatang(q.service.price))} × ${q.input.people})`, p.gross);
    if (p.discountAmount > 0) add("discount", t(lang, `line.discount.${p.discountKind}`, { p: p.discountPct }), -p.discountAmount);
    if (p.pointsDiscount > 0) add("points", t(lang, "line.points", { n: p.pointsRedeemed }), -p.pointsDiscount);
  }
  if (p.distanceKm !== null) {
    const label = t(lang, "line.transport", { v: p.vehicles, d: p.distanceKm.toFixed(1) }) + (q.input.type === "package" ? ` · ${t(lang, "line.transportIncluded")}` : "");
    add("transport", label, p.transportFee);
  }
  add("total", t(lang, "line.total"), p.total);
  if (p.giftcardPaid > 0) add("giftcard", t(lang, "line.giftcard"), -p.giftcardPaid);
  add("other", t(lang, "line.other"), p.otherPaid);
  return lines;
}

export function quoteJson(q: Quote, lang: Lang) {
  const p = q.price;
  return {
    service: { code: q.service.code, name: q.serviceName, durationMin: q.service.duration_min, herbs: q.herbs },
    type: q.input.type,
    people: q.input.people,
    date: q.input.date,
    time: q.input.time,
    endTime: endTimeOf(q.input.time, q.service.duration_min),
    whenLabel: `${formatDate(q.input.date, lang)} ${q.input.time}–${endTimeOf(q.input.time, q.service.duration_min)}`,
    gross: toBaht(p.gross),
    discountKind: p.discountKind,
    discountPct: p.discountPct,
    discountAmount: toBaht(p.discountAmount),
    pointsRedeemed: p.pointsRedeemed,
    pointsDiscount: toBaht(p.pointsDiscount),
    subtotal: toBaht(p.subtotal),
    distanceKm: p.distanceKm,
    vehicles: p.vehicles,
    transportFee: toBaht(p.transportFee),
    total: toBaht(p.total),
    totalLabel: formatBaht(p.total),
    giftcardPaid: toBaht(p.giftcardPaid),
    otherPaid: toBaht(p.otherPaid),
    pointsToEarn: p.pointsToEarn,
    lines: priceLines(q, lang),
    birthdayAvailable: q.birthdayAvailable,
    maxRedeemBlocks: q.maxRedeemBlocks,
    pointsBalance: q.customer?.points ?? 0,
    loggedIn: !!q.customer,
    course: q.course ? { id: q.course.id, remainingBefore: q.course.remainingBefore, remainingAfter: q.course.remainingBefore - 1, expiresOn: q.course.expiresOn } : null,
    giftCard: q.giftCard
      ? {
          code: q.giftCard.code,
          status: q.giftCard.status,
          balance: toBaht(q.giftCard.balance),
          balanceAfter: toBaht(q.giftCard.balance - p.giftcardPaid),
          expiresOn: q.giftCard.expiresOn,
        }
      : null,
    giftCardError: q.giftCardError ? { code: q.giftCardError, message: t(lang, `err.${q.giftCardError}`) } : null,
  };
}

async function busySlots(db: Db, from: Date, to: Date): Promise<BusySlot[]> {
  const r = await query(
    `SELECT therapist_id, lower(period) AS s, upper(period) AS e FROM booking_slot
      WHERE active AND period && tstzrange($1, $2, '[)')`,
    [from.toISOString(), to.toISOString()],
    db,
  );
  return r.rows.map((x) => ({ therapistId: x.therapist_id, start: new Date(x.s).getTime(), end: new Date(x.e).getTime() }));
}

async function roomBusy(db: Db, from: Date, to: Date): Promise<{ start: number; end: number }[]> {
  const r = await query(
    `SELECT lower(period) AS s, upper(period) AS e FROM booking
      WHERE room_id = 1 AND status <> 'cancelled' AND period && tstzrange($1, $2, '[)')`,
    [from.toISOString(), to.toISOString()],
    db,
  );
  return r.rows.map((x) => ({ start: new Date(x.s).getTime(), end: new Date(x.e).getTime() }));
}

async function capableTherapists(db: Db, serviceId: number) {
  const r = await query(
    `SELECT t.* FROM therapist t JOIN therapist_service ts ON ts.therapist_id = t.id
      WHERE ts.service_id = $1 AND t.active ORDER BY t.id`,
    [serviceId],
    db,
  );
  return r.rows as { id: number; code: string; name: string; name_en: string; name_zh: string }[];
}

/** รอบว่างของวัน (FR-01): รอบตาม BR-01 + นักบำบัดว่างพอ BR-02 + ห้องคู่ว่าง BR-04 */
export async function availableSlots(params: { serviceCode: string; date: string; type: BookingType; people: number }, lang: Lang) {
  const { today } = await clock();
  const db = getPool();
  const service = await getServiceByCode(params.serviceCode, db);
  if (!service || !kindMatches(params.type, service.kind)) throw new ApiError(422, "SERVICE_INVALID");
  const partyErr = checkParty(params.type, params.people);
  if (partyErr) throw new ApiError(422, partyErr);
  if (!isDateString(params.date)) throw new ApiError(422, "BAD_REQUEST", { field: "date" });
  if (!isBookableDate(today, params.date)) throw new ApiError(422, "DATE_OUT_OF_RANGE", bookableRange(today));

  const dayStart = toInstant(params.date, "00:00");
  const dayEnd = toInstant(params.date, "23:59");
  const capable = await capableTherapists(db, service.id);
  const busy = await busySlots(db, dayStart, dayEnd);
  const rooms = params.type === "couple" ? await roomBusy(db, dayStart, dayEnd) : [];
  const slots = buildSlots(service.duration_min).map((time) => {
    const s = toInstant(params.date, time).getTime();
    const e = toInstant(params.date, endTimeOf(time, service.duration_min)).getTime();
    const free = freeTherapists(capable.map((c) => c.id), busy, s, e);
    const roomFree = !rooms.some((r) => s < r.end && r.start < e);
    return {
      time,
      endTime: endTimeOf(time, service.duration_min),
      available: free.length >= params.people && roomFree,
      therapists: free.map((id) => {
        const c = capable.find((x) => x.id === id)!;
        return { code: c.code, name: therapistName(c, lang) };
      }),
    };
  });
  return { date: params.date, service: service.code, durationMin: service.duration_min, ...bookableRange(today), slots };
}

/** จองจริง (FR-03): transaction เดียว · ตรวจกฎซ้ำ · คิดราคาใหม่ · EXCLUDE กันซ้อน */
export async function createBooking(input: BookingInput, session: Session | null, lang: Lang) {
  const { today } = await clock();
  return withTx(async (c: pg.PoolClient) => {
    const q = await buildQuote(c, input, session, today, lang, true);
    const customer = q.customer;

    const contactName = input.contactName || customer?.name || "";
    const contactPhone = input.contactPhone || customer?.phone || "";
    if (!customer && (!contactName || !contactPhone)) throw new ApiError(422, "CONTACT_REQUIRED");

    if (input.quotedTotal === null) throw new ApiError(422, "QUOTE_REQUIRED");
    if (Math.round(input.quotedTotal * 100) !== q.price.total) {
      throw new ApiError(409, "PRICE_CHANGED", { total: toBaht(q.price.total), quote: quoteJson(q, lang) });
    }

    // นักบำบัด (BR-02) — เลือกเองหรือระบบจัดคนว่าง id น้อยสุด (D7)
    const capable = await capableTherapists(c, q.service.id);
    const busy = await busySlots(c, q.startAt, q.endAt);
    const free = freeTherapists(capable.map((x) => x.id), busy, q.startAt.getTime(), q.endAt.getTime());
    let chosen: number[];
    if (input.therapists.length) {
      const ids = [...new Set(input.therapists)].map((code) => capable.find((x) => x.code === code)?.id);
      if (ids.some((x) => x === undefined)) throw new ApiError(422, "THERAPIST_INVALID");
      if (ids.length !== input.people) throw new ApiError(422, "BAD_REQUEST", { field: "therapists" });
      chosen = ids as number[];
      if (chosen.some((id) => !free.includes(id))) throw new ApiError(409, "SLOT_TAKEN");
    } else {
      if (free.length < input.people) throw new ApiError(409, "SLOT_TAKEN");
      chosen = free.slice(0, input.people);
    }
    let roomId: number | null = null;
    if (input.type === "couple") {
      const rooms = await roomBusy(c, q.startAt, q.endAt);
      if (rooms.length) throw new ApiError(409, "SLOT_TAKEN");
      roomId = 1;
    }

    const p = q.price;
    const ins = await c.query(
      `INSERT INTO booking (customer_id, guest_name, guest_phone, contact_name, contact_phone, service_id, room_id, course_purchase_id,
         booking_type, party_size, start_at, end_at, status, gross_amount, discount_kind, discount_pct, discount_amount,
         points_redeemed, points_discount, distance_km, vehicles, transport_fee, total_amount, giftcard_paid, other_paid, points_earned)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'confirmed',$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,0)
       RETURNING id`,
      [
        customer?.id ?? null,
        customer ? null : contactName,
        customer ? null : contactPhone,
        contactName,
        contactPhone,
        q.service.id,
        roomId,
        q.course?.id ?? null,
        input.type,
        input.people,
        q.startAt.toISOString(),
        q.endAt.toISOString(),
        fromSatang(p.gross),
        p.discountKind,
        p.discountPct,
        fromSatang(p.discountAmount),
        p.pointsRedeemed,
        fromSatang(p.pointsDiscount),
        p.distanceKm,
        p.vehicles,
        fromSatang(p.transportFee),
        fromSatang(p.total),
        fromSatang(p.giftcardPaid),
        fromSatang(p.otherPaid),
      ],
    );
    const bookingId: number = ins.rows[0].id;
    const code = `B${String(bookingId).padStart(2, "0")}`;
    await c.query("UPDATE booking SET code = $1 WHERE id = $2", [code, bookingId]);
    for (const tid of chosen) {
      await c.query(`INSERT INTO booking_slot (booking_id, therapist_id, period) VALUES ($1, $2, tstzrange($3, $4, '[)'))`, [
        bookingId,
        tid,
        q.startAt.toISOString(),
        q.endAt.toISOString(),
      ]);
    }

    if (customer && p.pointsRedeemed > 0) {
      await c.query("UPDATE customer SET points_balance = points_balance - $1 WHERE id = $2", [p.pointsRedeemed, customer.id]);
      await c.query("INSERT INTO point_txn (customer_id, booking_id, points, reason) VALUES ($1, $2, $3, 'redeem')", [customer.id, bookingId, -p.pointsRedeemed]);
    }
    if (q.giftCard && p.giftcardPaid > 0) {
      await c.query("UPDATE gift_card SET balance = balance - $1 WHERE id = $2", [fromSatang(p.giftcardPaid), q.giftCard.id]);
      await c.query("INSERT INTO gift_card_txn (gift_card_id, booking_id, amount) VALUES ($1, $2, $3)", [q.giftCard.id, bookingId, fromSatang(-p.giftcardPaid)]);
    }
    if (customer && p.discountKind === "birthday") {
      await c.query("INSERT INTO birthday_use (customer_id, year_month, booking_id) VALUES ($1, $2, $3)", [customer.id, yearMonth(input.date), bookingId]);
    }
    if (q.course) {
      await c.query("UPDATE course_purchase SET reserved_sessions = reserved_sessions + 1 WHERE id = $1", [q.course.id]);
    }

    const names = chosen.map((id) => therapistName(capable.find((x) => x.id === id)!, lang));
    const quote = quoteJson(q, lang);
    return {
      bookingId,
      code,
      status: "confirmed",
      total: toBaht(p.total),
      totalLabel: formatBaht(p.total),
      therapists: chosen.map((id) => capable.find((x) => x.id === id)!.code),
      therapistNames: names,
      message: t(lang, "book.confirmed", { code }),
      detail: t(lang, "book.confirmedDetail", { service: q.serviceName, when: quote.whenLabel, total: formatBaht(p.total) }),
      quote,
    };
  });
}

/** ยกเลิกนัด (FR-07, BR-07) · คืนช่วงเวลา ครั้งคอร์ส ยอดบัตร แต้ม สิทธิ์เดือนเกิด */
export async function cancelBooking(bookingId: number, session: Session | null) {
  if (!session) throw new ApiError(401, "LOGIN_REQUIRED");
  const { now, today } = await clock();
  return withTx(async (c) => {
    const r = await c.query("SELECT * FROM booking WHERE id = $1 FOR UPDATE", [bookingId]);
    const b = r.rows[0];
    if (!b) throw new ApiError(404, "NOT_FOUND");
    if (b.customer_id !== session.uid && session.role !== "owner") throw new ApiError(403, "FORBIDDEN");
    if (b.status !== "confirmed") throw new ApiError(422, "CANCEL_NOT_ALLOWED");
    if (!canCancel(now.getTime(), new Date(b.start_at).getTime())) throw new ApiError(422, "CANCEL_TOO_LATE");

    await c.query("UPDATE booking SET status = 'cancelled', cancelled_at = $1 WHERE id = $2", [now.toISOString(), bookingId]);
    await c.query("UPDATE booking_slot SET active = FALSE WHERE booking_id = $1", [bookingId]);
    if (b.course_purchase_id) {
      await c.query("UPDATE course_purchase SET reserved_sessions = reserved_sessions - 1 WHERE id = $1 AND reserved_sessions > 0", [b.course_purchase_id]);
    }
    const g = await c.query("SELECT gift_card_id, SUM(amount) AS amt FROM gift_card_txn WHERE booking_id = $1 GROUP BY gift_card_id", [bookingId]);
    for (const row of g.rows) {
      const refund = -toSatang(row.amt);
      if (refund > 0) {
        await c.query("UPDATE gift_card SET balance = balance + $1 WHERE id = $2", [fromSatang(refund), row.gift_card_id]);
        await c.query("INSERT INTO gift_card_txn (gift_card_id, booking_id, amount) VALUES ($1, $2, $3)", [row.gift_card_id, bookingId, fromSatang(refund)]);
      }
    }
    if (b.customer_id && b.points_redeemed > 0) {
      await c.query("UPDATE customer SET points_balance = points_balance + $1 WHERE id = $2", [b.points_redeemed, b.customer_id]);
      await c.query("INSERT INTO point_txn (customer_id, booking_id, points, reason) VALUES ($1, $2, $3, 'refund')", [b.customer_id, bookingId, b.points_redeemed]);
    }
    const ym = yearMonth(bangkokDate(new Date(b.start_at)));
    if (yearMonth(today) <= ym) await c.query("DELETE FROM birthday_use WHERE booking_id = $1", [bookingId]);
    return { ok: true, bookingId, code: b.code, status: "cancelled" };
  });
}

/** เจ้าของร้านกด "ใช้บริการเสร็จ" (D3, D5, D11): ให้แต้ม BR-09 · ตัดครั้งคอร์ส · บันทึกรอบเอว · เพิ่มยอดสะสม */
export async function completeBooking(bookingId: number, waistCm: number | null, session: Session | null) {
  if (!session) throw new ApiError(401, "LOGIN_REQUIRED");
  if (session.role !== "owner") throw new ApiError(403, "FORBIDDEN");
  const { now } = await clock();
  return withTx(async (c) => {
    const r = await c.query("SELECT * FROM booking WHERE id = $1 FOR UPDATE", [bookingId]);
    const b = r.rows[0];
    if (!b) throw new ApiError(404, "NOT_FOUND");
    if (b.status !== "confirmed") throw new ApiError(422, "NOT_CONFIRMED");

    let earned = 0;
    if (b.customer_id && !b.course_purchase_id) {
      earned = pointsFor(
        earnBase({
          gross: toSatang(b.gross_amount),
          discountAmount: toSatang(b.discount_amount),
          pointsDiscount: toSatang(b.points_discount),
          giftcardPaid: toSatang(b.giftcard_paid),
        }),
      );
      const spend = toSatang(b.total_amount) - toSatang(b.transport_fee);
      await c.query("UPDATE customer SET points_balance = points_balance + $1, lifetime_spend = lifetime_spend + $2 WHERE id = $3", [
        earned,
        fromSatang(spend),
        b.customer_id,
      ]);
      if (earned > 0) {
        await c.query("INSERT INTO point_txn (customer_id, booking_id, points, reason) VALUES ($1, $2, $3, 'earn')", [b.customer_id, bookingId, earned]);
      }
    }
    if (b.course_purchase_id) {
      await c.query(
        "UPDATE course_purchase SET reserved_sessions = GREATEST(reserved_sessions - 1, 0), used_sessions = used_sessions + 1 WHERE id = $1",
        [b.course_purchase_id],
      );
      if (waistCm !== null) {
        await c.query("INSERT INTO waist_measurement (course_purchase_id, booking_id, measured_on, waist_cm) VALUES ($1, $2, $3, $4)", [
          b.course_purchase_id,
          bookingId,
          bangkokDate(new Date(b.start_at)),
          waistCm,
        ]);
      }
    }
    await c.query("UPDATE booking SET status = 'completed', completed_at = $1, points_earned = $2 WHERE id = $3", [now.toISOString(), earned, bookingId]);
    return { ok: true, bookingId, code: b.code, status: "completed", pointsEarned: earned };
  });
}
