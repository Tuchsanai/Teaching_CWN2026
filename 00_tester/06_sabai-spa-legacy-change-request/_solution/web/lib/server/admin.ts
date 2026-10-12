// หลังร้าน (D3): ตารางคิวรายวัน
import { fromSatang, query, toSatang } from "../db.ts";
import { pickName, t, type Lang } from "../i18n.ts";
import { formatBaht, toBaht } from "../money.ts";
import { addDays, bangkokDate, bangkokTime, diffDays, isDateString, toInstant } from "../rules/time.ts";
import { therapistName } from "./catalog.ts";
import { ApiError } from "./http.ts";

export async function queueForDate(date: string, lang: Lang) {
  const r = await query(
    `SELECT b.*, s.code AS service_code, s.name_th, s.name_en, s.name_zh, c.name AS customer_name,
            COALESCE(json_agg(json_build_object('code', t.code, 'name', t.name, 'name_en', t.name_en, 'name_zh', t.name_zh) ORDER BY t.id)
              FILTER (WHERE t.id IS NOT NULL), '[]') AS therapists
       FROM booking b JOIN service s ON s.id = b.service_id
       LEFT JOIN customer c ON c.id = b.customer_id
       LEFT JOIN booking_slot bs ON bs.booking_id = b.id
       LEFT JOIN therapist t ON t.id = bs.therapist_id
      WHERE b.start_at >= $1 AND b.start_at < $2
      GROUP BY b.id, s.id, c.id
      ORDER BY b.start_at, b.id`,
    [toInstant(date, "00:00").toISOString(), new Date(toInstant(date, "00:00").getTime() + 86400000).toISOString()],
  );
  return r.rows.map((b) => ({
    id: b.id,
    code: b.code,
    time: `${bangkokTime(new Date(b.start_at))}–${bangkokTime(new Date(b.end_at))}`,
    customer: b.customer_name ?? `${b.guest_name} (${b.guest_phone})`,
    member: !!b.customer_id,
    service: pickName(b, lang),
    serviceCode: b.service_code,
    type: b.booking_type,
    people: b.party_size,
    therapists: (b.therapists as { code: string; name: string; name_en: string; name_zh: string }[]).map((x) => `${x.code} ${therapistName(x, lang)}`),
    status: b.status,
    statusLabel: t(lang, `status.${b.status}`),
    total: toSatang(b.total_amount) / 100,
    totalLabel: formatBaht(toSatang(b.total_amount)),
    viaCourse: !!b.course_purchase_id,
    pointsEarned: b.points_earned,
  }));
}

// ── CR-05 รายงานยอดสำหรับเจ้าของร้าน ─────────────────────────────────────
// นับตาม "วันนัด" เวลาไทย รวมวันแรกและวันสุดท้าย [D:CR-05 ①] → ช่วง [from 00:00 ไทย, (to+1) 00:00 ไทย)
// เงิน: NUMERIC → toSatang() (integer) แล้วรวม → JSON เป็นบาท · CSV เป็นสตริง 2 ทศนิยม (fromSatang)
export const REPORT_MAX_DAYS = 92;

/** ตรวจช่วงวัน: รูปแบบผิด → BAD_REQUEST · from > to หรือเกิน 92 วัน (รวมหัวท้าย) → REPORT_RANGE */
export function checkReportRange(from: unknown, to: unknown): { from: string; to: string } {
  if (!isDateString(from)) throw new ApiError(422, "BAD_REQUEST", { field: "from" });
  if (!isDateString(to)) throw new ApiError(422, "BAD_REQUEST", { field: "to" });
  if (from > to || diffDays(from, to) + 1 > REPORT_MAX_DAYS) throw new ApiError(422, "REPORT_RANGE", { maxDays: REPORT_MAX_DAYS });
  return { from, to };
}

function reportBounds(from: string, to: string): [string, string] {
  return [toInstant(from, "00:00").toISOString(), toInstant(addDays(to, 1), "00:00").toISOString()];
}

export async function salesReport(from: string, to: string) {
  const [a, b] = reportBounds(from, to);
  const r = await query(
    `SELECT id, status, total_amount, giftcard_paid, other_paid, transport_fee, discount_kind, discount_amount, points_earned, course_purchase_id
       FROM booking WHERE start_at >= $1 AND start_at < $2`,
    [a, b],
  );
  const counts = { confirmed: 0, completed: 0, cancelled: 0 };
  const sum = { revenue: 0, giftcardPaid: 0, otherPaid: 0, transportFee: 0, pending: 0 };
  const disc = { group: 0, tier: 0, birthday: 0 };
  let pointsEarned = 0;
  let courseSessions = 0;
  for (const x of r.rows) {
    if (x.status in counts) counts[x.status as keyof typeof counts]++;
    if (x.status === "confirmed") sum.pending += toSatang(x.total_amount);
    if (x.status !== "completed") continue;
    sum.revenue += toSatang(x.total_amount);
    sum.giftcardPaid += toSatang(x.giftcard_paid);
    sum.otherPaid += toSatang(x.other_paid);
    sum.transportFee += toSatang(x.transport_fee);
    if (x.discount_kind in disc) disc[x.discount_kind as keyof typeof disc] += toSatang(x.discount_amount);
    pointsEarned += Number(x.points_earned);
    if (x.course_purchase_id) courseSessions++;
  }
  const tq = await query(
    `SELECT t.code, COUNT(DISTINCT b.id)::int AS completed
       FROM therapist t
       LEFT JOIN booking_slot bs ON bs.therapist_id = t.id
       LEFT JOIN booking b ON b.id = bs.booking_id AND b.status = 'completed' AND b.start_at >= $1 AND b.start_at < $2
      GROUP BY t.code ORDER BY t.code`,
    [a, b],
  );
  return {
    from,
    to,
    counts,
    revenue: toBaht(sum.revenue),
    giftcardPaid: toBaht(sum.giftcardPaid),
    otherPaid: toBaht(sum.otherPaid),
    transportFee: toBaht(sum.transportFee),
    discounts: { group: toBaht(disc.group), tier: toBaht(disc.tier), birthday: toBaht(disc.birthday) },
    pointsEarned,
    courseSessions,
    pendingValue: toBaht(sum.pending),
    byTherapist: tq.rows.map((x) => ({ code: x.code as string, completed: Number(x.completed) })),
  };
}

export const REPORT_CSV_HEADER = [
  "date", "code", "status", "type", "people", "service", "total", "giftcard_paid", "other_paid", "discount_kind", "discount_amount", "points_earned",
];

function csvCell(v: string | number): string {
  const s = String(v);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** CSV 1 แถวต่อ 1 นัด เรียงตามเวลา [D:CR-05 ①②] · ขึ้นต้นด้วย BOM ให้ Excel อ่านไทยออก · ชื่อบริการภาษาไทย */
export async function salesReportCsv(from: string, to: string): Promise<string> {
  const [a, b] = reportBounds(from, to);
  const r = await query(
    `SELECT b.start_at, b.code, b.status, b.booking_type, b.party_size, s.name_th, b.total_amount, b.giftcard_paid, b.other_paid,
            b.discount_kind, b.discount_amount, b.points_earned
       FROM booking b JOIN service s ON s.id = b.service_id
      WHERE b.start_at >= $1 AND b.start_at < $2
      ORDER BY b.start_at, b.id`,
    [a, b],
  );
  const lines = [REPORT_CSV_HEADER.join(",")];
  for (const x of r.rows) {
    lines.push(
      [
        bangkokDate(new Date(x.start_at)),
        x.code,
        x.status,
        x.booking_type,
        x.party_size,
        x.name_th,
        fromSatang(toSatang(x.total_amount)),
        fromSatang(toSatang(x.giftcard_paid)),
        fromSatang(toSatang(x.other_paid)),
        x.discount_kind,
        fromSatang(toSatang(x.discount_amount)),
        x.points_earned,
      ]
        .map(csvCell)
        .join(","),
    );
  }
  return "\uFEFF" + lines.join("\r\n") + "\r\n";
}
