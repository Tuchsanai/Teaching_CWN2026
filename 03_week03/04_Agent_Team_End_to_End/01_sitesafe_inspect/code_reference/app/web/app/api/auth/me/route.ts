// 4 · GET /api/auth/me — every role: name, role, site, permissions and upload limits
import type { NextRequest } from 'next/server';
import { canAccess, requireAccess } from '@/lib/access';
import { json, serverError } from '@/lib/http';
import { uploadLimits } from '@/lib/rules';
import { publicUser } from '@/lib/views';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const a = await requireAccess(req, 'auth.me');
    if (a.res) return a.res;
    const u = a.user;
    return json({
      user: publicUser(u),
      permissions: {
        upload: canAccess(u, 'upload.create').ok,
        view_photos: canAccess(u, 'photo.view').ok,
        override: canAccess(u, 'photo.override').ok,
        override_history: canAccess(u, 'override.history').ok,
        reports: canAccess(u, 'report.view').ok,
        all_sites: u.role !== 'supervisor',
      },
      limits: uploadLimits(),
    });
  } catch (e) {
    return serverError('auth/me', e);
  }
}
