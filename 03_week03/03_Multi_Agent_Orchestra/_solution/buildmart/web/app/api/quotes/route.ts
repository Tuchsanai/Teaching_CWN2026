// POST /api/quotes {name, company?, taxId?} (B2) → {quoteNo} — สร้างใบเสนอราคาจากตะกร้า (ไม่ล้างตะกร้า) อายุ 7 วัน
import { tx } from '@/lib/db';
import { getSessionId } from '@/lib/session';
import { errorJson, readJson } from '../cart/_lib';
import { createQuote } from './_quote';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const sid = getSessionId();
  const b = await readJson(req);
  try {
    const out = await tx((c) =>
      createQuote(c, sid, {
        name: String(b.name ?? '').trim(),
        company: String(b.company ?? '').trim(),
        taxId: String(b.taxId ?? '').trim(),
      }),
    );
    return Response.json(out);
  } catch (e) {
    return errorJson(e);
  }
}
