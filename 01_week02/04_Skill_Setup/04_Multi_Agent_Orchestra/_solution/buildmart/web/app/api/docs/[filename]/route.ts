// GET /api/docs/[filename] → ไฟล์ PDF จาก docs.bytes (application/pdf · เปิดในเบราว์เซอร์)
// ใช้กับป้ายอ้างอิงในแชท เช่น /api/docs/BM-DS-CEM.pdf#page=1 (#page ไม่ถูกส่งมาที่ server — viewer ของเบราว์เซอร์จัดการเอง)
import { query } from '@/lib/db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(_req: Request, { params }: { params: { filename: string } }) {
  const filename = decodeURIComponent(params.filename);
  const r = await query<{ bytes: Buffer; updated_at: Date }>('SELECT bytes, updated_at FROM docs WHERE filename = $1', [
    filename,
  ]);
  if (!r.rowCount) {
    return new Response('ไม่พบเอกสาร', { status: 404, headers: { 'content-type': 'text/plain; charset=utf-8' } });
  }
  const { bytes, updated_at } = r.rows[0];
  return new Response(new Uint8Array(bytes), {
    headers: {
      'content-type': 'application/pdf',
      'content-length': String(bytes.length),
      'content-disposition': `inline; filename*=UTF-8''${encodeURIComponent(filename)}`,
      'cache-control': 'no-cache',
      'last-modified': new Date(updated_at).toUTCString(),
    },
  });
}
