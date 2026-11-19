/**
 * Dispatcher heartbeat shared through PostgreSQL (no extra table · DESIGN §7.1).
 *
 * The dispatcher keeps one dedicated DB connection and, on every loop, runs
 *   SELECT set_config('application_name', dispatcherApplicationName(gatewayState), false)
 * (helper: beatDispatcher). /api/health reads pg_stat_activity: the dispatcher is
 * "ok" when that connection ran a statement within the last 10 seconds, and the
 * gateway state is the value carried in application_name.
 * Both services must use the same DB role (same DATABASE_URL) so the timestamps are visible.
 */
import type { Pool, PoolClient } from 'pg';

export const DISPATCHER_APP_PREFIX = 'sitesafe-dispatcher';
export const DISPATCHER_FRESH_SECONDS = 10;

export type GatewayState = 'ok' | 'down' | 'unauthorized';

export function dispatcherApplicationName(gateway: GatewayState): string {
  return `${DISPATCHER_APP_PREFIX};gw=${gateway}`;
}

/** Called by the dispatcher once per loop on its dedicated client. */
export async function beatDispatcher(client: Pick<PoolClient, 'query'>, gateway: GatewayState): Promise<void> {
  await client.query(`SELECT set_config('application_name', $1, false)`, [dispatcherApplicationName(gateway)]);
}

export async function readDispatcherState(
  p: Pool,
): Promise<{ dispatcher: 'ok' | 'down'; gateway: GatewayState }> {
  const r = await p.query<{ application_name: string; fresh: boolean }>(
    `SELECT application_name,
            COALESCE(GREATEST(query_start, state_change) > now() - make_interval(secs => $2), false) AS fresh
       FROM pg_stat_activity
      WHERE application_name LIKE $1
      ORDER BY GREATEST(query_start, state_change) DESC NULLS LAST
      LIMIT 1`,
    [`${DISPATCHER_APP_PREFIX};%`, DISPATCHER_FRESH_SECONDS],
  );
  const row = r.rows[0];
  if (!row || !row.fresh) return { dispatcher: 'down', gateway: 'down' };
  const m = /;gw=(ok|down|unauthorized)$/.exec(row.application_name);
  return { dispatcher: 'ok', gateway: (m?.[1] as GatewayState | undefined) ?? 'down' };
}
