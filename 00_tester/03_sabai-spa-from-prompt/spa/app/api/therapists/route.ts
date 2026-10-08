import { q } from "@/lib/server/db";
import { handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

type Row = {
  id: number; image: string; name_th: string; name_en: string; name_zh: string; title_th: string; title_en: string; title_zh: string;
  review_count: number; rating: number | null;
};

/** FR-08 / BR-10: ?minRating=4.5 hides therapists below 4.5 and those with 0 reviews */
export async function GET(req: Request) {
  return handle(async () => {
    const min = Number(new URL(req.url).searchParams.get("minRating") ?? "0") || 0;
    const rows = await q<Row>(
      `SELECT t.*, COUNT(r.id)::int AS review_count, ROUND(AVG(r.rating)::numeric, 1)::float AS rating
         FROM therapists t LEFT JOIN reviews r ON r.therapist_id = t.id GROUP BY t.id ORDER BY t.id`,
    );
    const reviews = await q<{ therapist_id: number }>(
      "SELECT therapist_id, author, rating, to_char(reviewed_on,'YYYY-MM-DD') AS reviewed_on, text_th, text_en, text_zh FROM reviews ORDER BY reviewed_on DESC, id",
    );
    const list = rows
      .map((t) => ({ ...t, rating: t.review_count > 0 ? Number(t.rating) : null, reviews: reviews.filter((r) => r.therapist_id === t.id) }))
      .filter((t) => (min > 0 ? t.rating !== null && t.rating >= min : true));
    return json({ ok: true, minRating: min, therapists: list });
  });
}
