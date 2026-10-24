// อ่านข้อมูลร้าน: บริการ+สมุนไพร นักบำบัด+คะแนน โรงแรม
import { query, toSatang, type Db } from "../db.ts";
import { pickName, type Lang } from "../i18n.ts";
import { formatRating, passesRatingFilter, ratingTenths } from "../rules/rating.ts";

export interface ServiceRow {
  id: number;
  code: string;
  name_th: string;
  name_en: string;
  name_zh: string;
  kind: "single" | "package" | "course";
  duration_min: number;
  price: string;
  includes_transport: boolean;
}

export interface ServiceView {
  id: number;
  code: string;
  name: string;
  kind: ServiceRow["kind"];
  durationMin: number;
  price: number;
  priceSatang: number;
  includesTransport: boolean;
  herbs: string[];
  image: string;
}

export async function getServiceByCode(code: string, db?: Db): Promise<ServiceRow | null> {
  const r = await query<ServiceRow>("SELECT * FROM service WHERE code = $1", [code], db);
  return r.rows[0] ?? null;
}

export async function getHerbs(serviceId: number, lang: Lang, db?: Db): Promise<string[]> {
  const r = await query(
    `SELECT h.* FROM service_herb sh JOIN herb h ON h.id = sh.herb_id WHERE sh.service_id = $1 ORDER BY sh.sort_order`,
    [serviceId],
    db,
  );
  return r.rows.map((h) => pickName(h, lang));
}

export async function listServices(lang: Lang): Promise<ServiceView[]> {
  const s = await query<ServiceRow>("SELECT * FROM service ORDER BY id");
  const h = await query(
    `SELECT sh.service_id, h.* FROM service_herb sh JOIN herb h ON h.id = sh.herb_id ORDER BY sh.service_id, sh.sort_order`,
  );
  return s.rows.map((row) => ({
    id: row.id,
    code: row.code,
    name: pickName(row, lang),
    kind: row.kind,
    durationMin: row.duration_min,
    price: toSatang(row.price) / 100,
    priceSatang: toSatang(row.price),
    includesTransport: row.includes_transport,
    herbs: h.rows.filter((x) => x.service_id === row.id).map((x) => pickName(x, lang)),
    image: `/assets/svc-${row.code.toLowerCase()}.webp`,
  }));
}

export interface TherapistView {
  id: number;
  code: string;
  name: string;
  rating: string | null;
  ratingTenths: number | null;
  reviewCount: number;
  passes45: boolean;
  services: string[];
  image: string;
}

export async function listTherapists(lang: Lang): Promise<TherapistView[]> {
  const r = await query(
    `SELECT t.*, COALESCE(SUM(rv.stars), 0)::int AS sum_stars, COUNT(rv.id)::int AS review_count,
            (SELECT array_agg(s.code ORDER BY s.id) FROM therapist_service ts JOIN service s ON s.id = ts.service_id WHERE ts.therapist_id = t.id) AS services
       FROM therapist t LEFT JOIN review rv ON rv.therapist_id = t.id
      WHERE t.active GROUP BY t.id ORDER BY t.id`,
  );
  return r.rows.map((row) => {
    const tenths = ratingTenths(row.sum_stars, row.review_count);
    return {
      id: row.id,
      code: row.code,
      name: lang === "th" ? row.name : lang === "en" ? row.name_en : row.name_zh,
      rating: formatRating(tenths),
      ratingTenths: tenths,
      reviewCount: row.review_count,
      passes45: passesRatingFilter(tenths),
      services: row.services ?? [],
      image: `/assets/thr-${String(row.code).toLowerCase()}.webp`,
    };
  });
}

export async function listHotels(lang: Lang) {
  const r = await query("SELECT * FROM hotel ORDER BY id");
  return r.rows.map((h) => ({ code: h.code, name: pickName(h, lang), distanceKm: Number(h.distance_km) }));
}

export async function getHotel(code: string, db?: Db) {
  const r = await query("SELECT * FROM hotel WHERE code = $1", [code], db);
  return r.rows[0] ? { code: r.rows[0].code as string, distanceKm: Number(r.rows[0].distance_km) } : null;
}

export function therapistName(row: { name: string; name_en: string; name_zh: string }, lang: Lang): string {
  return lang === "th" ? row.name : lang === "en" ? row.name_en : row.name_zh;
}
