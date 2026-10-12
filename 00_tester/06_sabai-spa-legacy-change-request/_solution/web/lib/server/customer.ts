// ข้อมูลลูกค้า ระดับ แต้ม เดือนเกิด คอร์ส (Wallet) และประวัติ
import { query, toSatang, type Db } from "../db.ts";
import { formatDate, pickName, t, type Lang } from "../i18n.ts";
import { formatBaht } from "../money.ts";
import { isBirthdayMonth } from "../rules/birthday.ts";
import { canCancel } from "../rules/cancel.ts";
import { courseDaysLeft, courseRemaining, isCourseExpired } from "../rules/course.ts";
import { maxRedeemBlocks } from "../rules/points.ts";
import { bangkokDate, bangkokTime, yearMonth } from "../rules/time.ts";
import { nextTier, TIER_PCT, tierOf } from "../rules/tier.ts";
import { therapistName } from "./catalog.ts";

export interface Customer {
  id: number;
  name: string;
  phone: string | null;
  email: string | null;
  birthDate: string | null;
  lang: Lang;
  lifetimeSpend: number;
  points: number;
  role: "customer" | "owner";
}

export async function loadCustomer(db: Db, id: number, lock = false): Promise<Customer | null> {
  const r = await query(`SELECT * FROM customer WHERE id = $1 ${lock ? "FOR UPDATE" : ""}`, [id], db);
  const c = r.rows[0];
  if (!c) return null;
  return {
    id: c.id,
    name: c.name,
    phone: c.phone,
    email: c.email,
    birthDate: c.birth_date,
    lang: c.lang,
    lifetimeSpend: toSatang(c.lifetime_spend),
    points: c.points_balance,
    role: c.role,
  };
}

export async function birthdayUsed(db: Db, customerId: number, ym: number): Promise<boolean> {
  const r = await query("SELECT 1 FROM birthday_use WHERE customer_id = $1 AND year_month = $2", [customerId, ym], db);
  return r.rowCount! > 0;
}

/** ระดับ + ข้อความ BR-12 */
export function tierInfo(spend: number, lang: Lang) {
  const tier = tierOf(spend);
  const nt = nextTier(spend);
  return {
    tier,
    tierLabel: t(lang, `tier.${tier}`),
    tierPct: TIER_PCT[tier],
    lifetimeSpend: spend / 100,
    nextTier: nt ? nt.next : null,
    remainingToNext: nt ? nt.remaining / 100 : 0,
    tierMessage: nt ? t(lang, "account.next", { x: formatBaht(nt.remaining), tier: t(lang, `tier.${nt.next}`) }) : t(lang, "account.top"),
  };
}

export async function accountSummary(db: Db, customerId: number, today: string, lang: Lang) {
  const c = await loadCustomer(db, customerId);
  if (!c) return null;
  const inBirthdayMonth = isBirthdayMonth(c.birthDate, today);
  const used = inBirthdayMonth ? await birthdayUsed(db, c.id, yearMonth(today)) : false;
  return {
    id: c.id,
    name: c.name,
    email: c.email,
    phone: c.phone,
    role: c.role,
    lang: c.lang,
    birthMonth: c.birthDate ? Number(c.birthDate.slice(5, 7)) : null,
    points: c.points,
    maxRedeemBlocks: maxRedeemBlocks(c.points),
    birthdayThisMonth: inBirthdayMonth ? (used ? "used" : "available") : "none",
    ...tierInfo(c.lifetimeSpend, lang),
  };
}

export async function myBookings(db: Db, customerId: number, now: Date, lang: Lang) {
  const r = await query(
    `SELECT b.*, s.code AS service_code, s.name_th, s.name_en, s.name_zh,
            COALESCE(json_agg(json_build_object('name', t.name, 'name_en', t.name_en, 'name_zh', t.name_zh) ORDER BY t.id)
              FILTER (WHERE t.id IS NOT NULL), '[]') AS therapists
       FROM booking b JOIN service s ON s.id = b.service_id
       LEFT JOIN booking_slot bs ON bs.booking_id = b.id
       LEFT JOIN therapist t ON t.id = bs.therapist_id
      WHERE b.customer_id = $1
      GROUP BY b.id, s.id
      ORDER BY b.start_at DESC, b.id DESC`,
    [customerId],
    db,
  );
  return r.rows.map((b) => {
    const start = new Date(b.start_at);
    const cancellable = b.status === "confirmed" && canCancel(now.getTime(), start.getTime());
    return {
      id: b.id,
      code: b.code,
      serviceCode: b.service_code,
      serviceName: pickName(b, lang),
      type: b.booking_type,
      people: b.party_size,
      date: bangkokDate(start),
      dateLabel: formatDate(bangkokDate(start), lang),
      time: bangkokTime(start),
      endTime: bangkokTime(new Date(b.end_at)),
      therapists: (b.therapists as { name: string; name_en: string; name_zh: string }[]).map((x) => therapistName(x, lang)),
      status: b.status,
      statusLabel: t(lang, `status.${b.status}`),
      total: toSatang(b.total_amount) / 100,
      totalLabel: formatBaht(toSatang(b.total_amount)),
      viaCourse: !!b.course_purchase_id,
      canCancel: cancellable,
      canReschedule: cancellable, // CR-01 เลื่อนเองได้ด้วยเงื่อนไขเดียวกับยกเลิก (ยืนยันอยู่ + เหลือ ≥ 24 ชม. จากนัดเดิม)
      cancelBlockedReason: b.status === "confirmed" && !cancellable ? t(lang, "account.cancelLate") : null,
    };
  });
}

export async function wallet(db: Db, customerId: number, today: string, lang: Lang) {
  const cr = await query("SELECT * FROM course_purchase WHERE customer_id = $1 ORDER BY purchased_on DESC, id DESC", [customerId], db);
  const courses = cr.rows.map((c) => {
    const remaining = courseRemaining({ total: c.total_sessions, used: c.used_sessions, reserved: c.reserved_sessions });
    const expired = isCourseExpired(today, c.expires_on);
    return {
      id: c.id,
      code: c.code,
      total: c.total_sessions,
      used: c.used_sessions,
      reserved: c.reserved_sessions,
      remaining,
      purchasedOn: c.purchased_on,
      expiresOn: c.expires_on,
      expiresLabel: formatDate(c.expires_on, lang),
      daysLeft: courseDaysLeft(today, c.expires_on),
      expired,
      usable: remaining >= 1 && !expired,
      remainingLabel: t(lang, "wallet.remaining", { r: remaining, t: c.total_sessions }),
    };
  });
  const ids = courses.map((c) => c.id);
  const wr = ids.length
    ? await query("SELECT * FROM waist_measurement WHERE course_purchase_id = ANY($1) ORDER BY measured_on, id", [ids], db)
    : { rows: [] as Record<string, unknown>[] };
  const waist = wr.rows.map((w) => ({ date: String(w.measured_on), cm: Number(w.waist_cm), courseId: Number(w.course_purchase_id) }));
  const pr = ids.length
    ? await query("SELECT id, course_purchase_id, phase FROM body_photo WHERE course_purchase_id = ANY($1) ORDER BY course_purchase_id, id", [ids], db)
    : { rows: [] as Record<string, unknown>[] };
  const photos = pr.rows.map((p) => ({ id: Number(p.id), courseId: Number(p.course_purchase_id), phase: String(p.phase), url: `/api/photos/${p.id}` }));
  const reduced = waist.length ? Math.round((waist[0].cm - waist[waist.length - 1].cm) * 10) / 10 : 0;
  return { courses, waist, waistReducedCm: reduced, photos };
}
