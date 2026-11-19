// 10 · GET /api/photos/{id}/image — the original file, only through this route (FR-22, NFR-05)
import { createReadStream, promises as fs } from 'node:fs';
import { Readable } from 'node:stream';
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess } from '@/lib/access';
import { serverError } from '@/lib/http';
import { absolutePhotoPath } from '@/lib/photo-store';
import { findPhotoInScope } from '@/lib/photo-query';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  try {
    const a = await requireAccess(req, 'photo.view');
    if (a.res) return a.res;
    const user = a.user;
    const { id } = await ctx.params;

    const photo = await findPhotoInScope(user, id);
    if (!photo) return deny(404);
    const d = canAccess(user, 'photo.view', photo.site_id);
    if (!d.ok) return deny(d.status);

    const abs = absolutePhotoPath(photo.storage_path);
    let size: number;
    try {
      const st = await fs.stat(abs);
      if (!st.isFile()) return deny(404);
      size = st.size;
    } catch {
      console.error(`[api] photos/{id}/image: file missing for photo ${photo.id}`);
      return deny(404);
    }
    const stream = Readable.toWeb(createReadStream(abs)) as unknown as ReadableStream<Uint8Array>;
    return new Response(stream, {
      status: 200,
      headers: {
        'Content-Type': photo.mime,
        'Content-Length': String(size),
        'Cache-Control': 'private, no-store',
        'X-Content-Type-Options': 'nosniff',
        'Content-Disposition': 'inline',
      },
    });
  } catch (e) {
    return serverError('photos/{id}/image GET', e);
  }
}
