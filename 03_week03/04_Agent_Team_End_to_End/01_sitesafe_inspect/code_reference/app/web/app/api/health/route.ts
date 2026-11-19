// 1 · GET /api/health — no login; no user data, photos or keys (DESIGN §7.1)
import { promises as fs, constants as fsc } from 'node:fs';
import type { NextRequest } from 'next/server';
import { canAccess, deny } from '@/lib/access';
import { nowIso } from '@/lib/clock';
import { pool } from '@/lib/db';
import { readDispatcherState, type GatewayState } from '@/lib/heartbeat';
import { json } from '@/lib/http';
import { photosDir } from '@/lib/photo-store';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const VERSION = '0.1.0';

async function within<T>(ms: number, p: Promise<T>): Promise<T> {
  let t: NodeJS.Timeout | undefined;
  try {
    return await Promise.race([
      p,
      new Promise<T>((_, reject) => {
        t = setTimeout(() => reject(new Error('timeout')), ms);
      }),
    ]);
  } finally {
    if (t) clearTimeout(t);
  }
}

export async function GET(_req: NextRequest) {
  const d = canAccess(null, 'health.read');
  if (!d.ok) return deny(d.status);

  let db: 'ok' | 'down' = 'down';
  let dispatcher: 'ok' | 'down' = 'down';
  let gateway: GatewayState = 'down';
  try {
    await within(3000, pool().query('SELECT 1'));
    db = 'ok';
    const s = await within(3000, readDispatcherState(pool()));
    dispatcher = s.dispatcher;
    gateway = s.gateway;
  } catch {
    /* reported as down */
  }

  let storage: 'ok' | 'down' = 'down';
  try {
    const dir = photosDir();
    const st = await fs.stat(dir);
    await fs.access(dir, fsc.R_OK | fsc.W_OK);
    storage = st.isDirectory() ? 'ok' : 'down';
  } catch {
    storage = 'down';
  }

  const down = db !== 'ok' || storage !== 'ok';
  const degraded = !down && (dispatcher !== 'ok' || gateway !== 'ok');
  return json(
    {
      status: down ? 'down' : degraded ? 'degraded' : 'ok',
      db,
      storage,
      dispatcher,
      gateway,
      ai_mode: process.env.AI_MODE === 'mock' ? 'mock' : 'real',
      time: nowIso(),
      version: VERSION,
    },
    down ? 503 : 200,
  );
}
