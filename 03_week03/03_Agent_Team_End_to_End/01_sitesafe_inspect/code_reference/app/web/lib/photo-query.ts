/** Load one photo, always filtered by the caller's site scope (supervisor → own site). */
import type { PoolClient } from 'pg';
import type { SessionUser } from './auth';
import { siteCondition } from './access';
import { pool } from './db';
import { isUuid } from './http';
import { PHOTO_COLUMNS, type PhotoRow } from './views';

export async function findPhotoInScope(
  user: SessionUser,
  id: string,
  opts: { client?: PoolClient; forUpdate?: boolean } = {},
): Promise<(PhotoRow & { storage_path: string }) | null> {
  if (!isUuid(id)) return null;
  const params: unknown[] = [id];
  const site = siteCondition(user, 'p.site_id', params);
  const sql = `SELECT ${PHOTO_COLUMNS}, p.storage_path
                 FROM photos p JOIN sites s ON s.id = p.site_id
                WHERE p.id = $1${site}${opts.forUpdate ? ' FOR UPDATE OF p' : ''}`;
  const r = await (opts.client ?? pool()).query<PhotoRow & { storage_path: string }>(sql, params);
  return r.rows[0] ?? null;
}
