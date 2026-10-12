// หลังร้าน (D3): ตารางคิวรายวัน
import { query, toSatang } from "../db.ts";
import { pickName, t, type Lang } from "../i18n.ts";
import { formatBaht } from "../money.ts";
import { bangkokTime, toInstant } from "../rules/time.ts";
import { therapistName } from "./catalog.ts";

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
