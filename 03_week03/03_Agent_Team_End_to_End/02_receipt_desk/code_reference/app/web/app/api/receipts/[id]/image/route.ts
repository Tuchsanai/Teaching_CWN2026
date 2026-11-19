/**
 * W13 · GET /api/receipts/{id}/image — รูปใบเสร็จ · ทุกบทบาท (ลูกค้า: ร้านตัวเองเท่านั้น · ร้านอื่น → 404)
 * รูปเปิดผ่าน API ที่ตรวจสิทธิ์เท่านั้น ไม่มีลิงก์ตรงไปที่ไฟล์ (DESIGN 8)
 */
import { readFile } from 'node:fs/promises';
import { relative, resolve, sep } from 'node:path';
import { requireUser } from '../../../_lib/auth';
import { ApiError, handle, paramId } from '../../../_lib/http';
import type { IdContext } from '../../../_lib/http';
import { loadReceipt } from '../../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request);
  const id = await paramId(ctx);
  const row = await loadReceipt(user, id);

  const root = resolve(/*turbopackIgnore: true*/ process.env.UPLOAD_DIR || '/app/uploads');
  const file = resolve(root, row.file_path);
  const rel = relative(root, file);
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`)) {
    throw new ApiError(404, 'not_found', 'ไม่พบไฟล์รูปของใบนี้');
  }
  let bytes: Buffer;
  try {
    bytes = await readFile(file);
  } catch {
    throw new ApiError(404, 'image_missing', 'ไม่พบไฟล์รูปของใบนี้');
  }
  const safeName = encodeURIComponent(row.file_name);
  return new Response(new Uint8Array(bytes), {
    status: 200,
    headers: {
      'Content-Type': row.mime_type,
      'Content-Length': String(bytes.length),
      'Content-Disposition': `inline; filename*=UTF-8''${safeName}`,
      'Cache-Control': 'private, no-store',
      'X-Content-Type-Options': 'nosniff',
    },
  });
});
