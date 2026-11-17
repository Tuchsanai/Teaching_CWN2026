import { pool, type Service } from "./db";

export type BookingTag = {
  customer_name: string;
  phone: string;
  service: string;
  booking_time: string;
};

export type BookingResult = {
  id: number;
  customer_name: string;
  phone: string;
  service_name: string;
  duration_min: number;
  price_thb: number;
  booking_time: string;
  status: string;
};

const TAG_RE = /\[BOOKING\]\s*(\{[\s\S]*?\})/;

/** ข้อความสำหรับแสดงผล: ตัดแท็ก [BOOKING]{...} (รวมถึงที่ยังมาไม่ครบ) ออก */
export function displayText(text: string): string {
  let s = text.replace(/\[BOOKING\][\s\S]*$/, "");
  const tail = s.match(/\[[A-Z]*$/);
  if (tail && "[BOOKING]".startsWith(tail[0])) s = s.slice(0, tail.index);
  return s.trimEnd();
}

export function parseBookingTag(text: string): BookingTag | null {
  const m = text.match(TAG_RE);
  if (!m) return null;
  try {
    const j = JSON.parse(m[1]);
    if (!j.customer_name || !j.phone || !j.service || !j.booking_time) return null;
    return {
      customer_name: String(j.customer_name).trim(),
      phone: String(j.phone).trim(),
      service: String(j.service).trim(),
      booking_time: String(j.booking_time).trim(),
    };
  } catch {
    return null;
  }
}

function matchService(name: string, services: Service[]): Service | undefined {
  const n = name.replace(/\s+/g, "");
  const norm = (s: Service) => s.name_th.replace(/\s+/g, "");
  return (
    services.find((s) => norm(s) === n) ??
    services.find((s) => norm(s).includes(n)) ??
    services.find((s) => n.includes(norm(s)))
  );
}

/** บันทึกการจองลง Postgres — คืนค่า error เป็นข้อความภาษาไทยถ้าไม่สำเร็จ */
export async function createBooking(
  tag: BookingTag,
  services: Service[]
): Promise<{ ok: true; booking: BookingResult } | { ok: false; error: string }> {
  const svc = matchService(tag.service, services);
  if (!svc) return { ok: false, error: `ไม่พบบริการ "${tag.service}" ในระบบ` };

  const t = tag.booking_time.replace("T", " ").match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})/);
  if (!t) return { ok: false, error: `รูปแบบวันเวลาไม่ถูกต้อง: ${tag.booking_time}` };
  const when = `${t[1]}-${t[2]}-${t[3]} ${t[4].padStart(2, "0")}:${t[5]}`;

  const r = await pool.query<{ id: number; status: string; booking_time: string }>(
    `INSERT INTO bookings (customer_name, phone, service_id, booking_time, status)
     VALUES ($1, $2, $3, $4::timestamp, 'confirmed')
     RETURNING id, status, to_char(booking_time, 'YYYY-MM-DD HH24:MI') AS booking_time`,
    [tag.customer_name, tag.phone, svc.id, when]
  );
  const row = r.rows[0];
  return {
    ok: true,
    booking: {
      id: row.id,
      customer_name: tag.customer_name,
      phone: tag.phone,
      service_name: svc.name_th,
      duration_min: svc.duration_min,
      price_thb: svc.price_thb,
      booking_time: row.booking_time,
      status: row.status,
    },
  };
}
