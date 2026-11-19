/**
 * W6 · GET /api/clients — พนักงาน · หัวหน้า · เจ้าของ (ลูกค้า → 403)
 */
import { OFFICE, requireUser } from '../_lib/auth';
import { query } from '../_lib/db';
import { handle, json } from '../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request) => {
  await requireUser(request, OFFICE);
  const rows = await query<{ id: string; code: string; name: string; business_type: string }>(
    'SELECT id, code, name, business_type FROM clients ORDER BY code',
  );
  return json({
    clients: rows.map((c) => ({ id: c.id, code: c.code, name: c.name, businessType: c.business_type })),
  });
});
