import { readFile } from 'node:fs/promises';
import { request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import { extname, relative, resolve, sep } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import { Pool } from 'pg';
import type { PoolClient } from 'pg';
import { computeFlags } from '../lib/rules';

const POLL_MS = 5_000;
const MAX_ATTEMPTS = 3;
const RETRY_KEY_PREFIX = 'dispatcher:retry:';

type ActiveStatus = 'queued' | 'processing';
type ReceiptStatus = ActiveStatus | 'review' | 'unreadable';
type Priority = 'normal' | 'urgent';

interface Receipt {
  id: string;
  batch_id: string;
  file_name: string;
  file_path: string;
  mime_type: string;
  accepted_at: Date;
  priority: Priority;
  status: ActiveStatus;
  attempts: number;
}

interface ReaderResult {
  merchant: string | null;
  date: string | null;
  items: Array<{ name: string | null; price: string | null }>;
  total: string | null;
  total_confidence: number | null;
}

type JobResult =
  | { status: ActiveStatus; attempts: number }
  | { status: 'done'; attempts: number; result: ReaderResult }
  | { status: 'dead'; attempts: number; error?: string };

interface GatewayJob {
  priority: Priority;
  receipts: Array<JobResult & { receipt_ref: string }>;
}

interface MockFixture {
  prices?: string[];
  total?: string;
  confidence?: number;
  failures?: number;
}

const mockFixtures = new Map<string, MockFixture>([
  ['conf-089', { confidence: 0.89 }],
  ['conf-090', { confidence: 0.90 }],
  ['conf-091', { confidence: 0.91 }],
  ['conf-08999', { confidence: 0.8999 }],
  ['both-flags', { confidence: 0.50, prices: ['45.00', '30.00', '20.00'] }],
  ['diff-099', { prices: ['45.00', '30.00', '24.01'] }],
  ['diff-100', { prices: ['45.00', '30.00', '24.00'] }],
  ['diff-101', { prices: ['45.00', '30.00', '23.99'] }],
  ['diff-over-101', { prices: ['60.00', '41.01'] }],
  ['diff-149', { prices: ['50.00', '48.51'] }],
  ['total-000', { total: '0.00', prices: [], confidence: 0.95 }],
  ['total-001', { total: '0.01', prices: ['0.01'] }],
  ['total-002', { total: '0.02', prices: ['0.02'] }],
  ['fail1-then-ok', { failures: 1 }],
  ['fail2-then-ok', { failures: 2 }],
  ['fail3', { failures: 3 }],
]);

export function mockRead(fileName: string, attempts = 1): JobResult {
  const stem = fileName.slice(0, fileName.length - extname(fileName).length);
  const fixture = mockFixtures.get(stem.split('__', 1)[0]) ?? {};
  if (attempts <= (fixture.failures ?? 0)) {
    return attempts >= MAX_ATTEMPTS
      ? { status: 'dead', attempts, error: 'unreadable_image' }
      : { status: 'queued', attempts };
  }

  const names = ['ข้าวสาร', 'น้ำมันพืช', 'น้ำตาลทราย'];
  const prices = fixture.prices ?? ['45.00', '30.00', '25.00'];
  return {
    status: 'done', attempts,
    result: {
      merchant: 'ร้านตัวอย่าง',
      date: '2026-11-18',
      items: prices.map((price, index) => ({ name: names[index], price })),
      total: fixture.total ?? '100.00',
      total_confidence: fixture.confidence ?? 0.99,
    },
  };
}

interface GatewayResponse {
  status: number;
  retryAfter: string | undefined;
  body: string;
}

async function connectGateway() {
  const { GATEWAY_URL, GATEWAY_API_KEY, GATEWAY_CA_CERT } = process.env;
  if (!GATEWAY_URL || !GATEWAY_API_KEY) {
    throw new Error('GATEWAY_URL and GATEWAY_API_KEY are required in gateway mode');
  }
  const base = new URL(GATEWAY_URL);
  if (base.protocol !== 'https:' && base.protocol !== 'http:') {
    throw new Error('GATEWAY_URL must use HTTP or HTTPS');
  }
  const ca = GATEWAY_CA_CERT ? await readFile(GATEWAY_CA_CERT) : undefined;
  const request = base.protocol === 'https:' ? httpsRequest : httpRequest;

  return async (method: string, path: string, form?: FormData): Promise<GatewayResponse> => {
    const url = new URL(path, base);
    const headers: Record<string, string> = { 'X-API-Key': GATEWAY_API_KEY };
    let body: Buffer | undefined;
    if (form) {
      const multipart = new Request(url, { method, body: form });
      body = Buffer.from(await multipart.arrayBuffer());
      headers['Content-Type'] = multipart.headers.get('content-type')!;
      headers['Content-Length'] = String(body.length);
    }
    return new Promise((resolve, reject) => {
      const req = request(url, { method, headers, ca, signal: AbortSignal.timeout(10_000) }, (res) => {
        let content = '';
        res.setEncoding('utf8');
        res.on('data', (chunk: string) => { content += chunk; });
        res.on('error', reject);
        res.on('end', () => resolve({
          status: res.statusCode ?? 0,
          retryAfter: res.headers['retry-after'],
          body: content,
        }));
      });
      req.on('error', reject);
      req.end(body);
    });
  };
}

type Gateway = Awaited<ReturnType<typeof connectGateway>>;

export function retryDeadline(retryAfter: string | undefined, fallbackMs: number, now = Date.now()): number {
  const value = retryAfter?.trim();
  if (value) {
    const deadline = /^\d+$/.test(value) ? now + Number(value) * 1_000 : Date.parse(value);
    if (Number.isFinite(deadline) && deadline <= 8.64e15) return Math.max(deadline, now);
  }
  return now + fallbackMs;
}

function report(action: string, error: unknown) {
  console.error(`[dispatcher] ${action}`, error instanceof Error ? error.message : error);
}

async function transaction<T>(pool: Pool, work: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await work(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

const receiptColumns = `r.id, r.batch_id, r.file_name, r.file_path, r.mime_type,
                        r.accepted_at, r.status, r.attempts, b.priority`;
const queueOrder = `b.priority DESC, b.urgent_set_at ASC NULLS LAST, r.accepted_at, r.id`;

async function submit(gateway: Gateway, uploads: string, receipt: Receipt) {
  const file = resolve(uploads, receipt.file_path);
  const localPath = relative(uploads, file);
  if (!localPath || localPath === '..' || localPath.startsWith(`..${sep}`)) {
    throw new Error('Invalid receipt upload path');
  }
  const bytes = await readFile(file);
  const extension = { 'image/jpeg': '.jpg', 'image/png': '.png', 'application/pdf': '.pdf' }[receipt.mime_type] ?? '';
  const form = new FormData();
  form.set('file', new Blob([new Uint8Array(bytes)], { type: receipt.mime_type }), `${receipt.id}${extension}`);
  form.set('receipt_ref', receipt.id);
  form.set('job_ref', receipt.batch_id);
  form.set('priority', receipt.priority);
  form.set('accepted_at', receipt.accepted_at.toISOString());
  return gateway('POST', '/v1/receipts', form);
}

async function deferReceipt(client: PoolClient, key: string, deadline: number) {
  // Even Retry-After: 0 waits for the next dispatch tick.
  const nextTick = new Date(Math.max(deadline, Date.now() + POLL_MS));
  await client.query(`
    INSERT INTO system_state (key, value) VALUES ($1, $2)
    ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
  `, [key, nextTick.toISOString()]);
}

async function dispatchOne(pool: Pool, gateway: Gateway | undefined, uploads: string): Promise<boolean> {
  return transaction(pool, async (client) => {
    const { rows: [receipt] } = await client.query<Receipt>(`
      SELECT ${receiptColumns}
      FROM receipts r JOIN batches b ON b.id = r.batch_id
      LEFT JOIN system_state retry ON retry.key = $1 || r.id::text
      WHERE r.dispatch_state = 'pending' AND r.status = 'queued'
        AND (retry.value IS NULL OR retry.value::timestamptz <= now())
      ORDER BY ${queueOrder}
      LIMIT 1 FOR UPDATE OF r SKIP LOCKED
    `, [RETRY_KEY_PREFIX]);
    if (!receipt) return false;

    const retryKey = RETRY_KEY_PREFIX + receipt.id;
    if (gateway) {
      // A different dispatcher can commit a retry deadline while this query is choosing a row.
      const retry = await client.query(`
        SELECT 1 FROM system_state WHERE key = $1 AND value::timestamptz > clock_timestamp()
      `, [retryKey]);
      if (retry.rowCount) return false;

      let response: GatewayResponse;
      try {
        response = await submit(gateway, uploads, receipt);
      } catch (error) {
        report(`submit ${receipt.id}`, error);
        await deferReceipt(client, retryKey, Date.now() + POLL_MS);
        return false;
      }
      if (response.status !== 202 && response.status !== 200) {
        if (response.status !== 429) report(`submit ${receipt.id}`, `HTTP ${response.status}`);
        const fallback = response.status === 429 ? 60_000 : 10_000;
        await deferReceipt(client, retryKey, retryDeadline(response.retryAfter, fallback));
        return false;
      }
    }

    await client.query("UPDATE receipts SET dispatch_state = 'sent' WHERE id = $1", [receipt.id]);
    await client.query('DELETE FROM system_state WHERE key = $1', [retryKey]);
    return true;
  });
}

async function transition(
  client: PoolClient, id: string, from: ReceiptStatus, to: ReceiptStatus, attempts: number,
) {
  await client.query('UPDATE receipts SET status = $2, attempts = $3 WHERE id = $1', [id, to, attempts]);
  if (from !== to) {
    await client.query(`
      INSERT INTO receipt_events (receipt_id, from_status, to_status, created_at)
      VALUES ($1, $2, $3, clock_timestamp())
    `, [id, from, to]);
  }
}

async function writeResult(client: PoolClient, receipt: Receipt, job: JobResult): Promise<boolean> {
  const { id, status } = receipt;
  if (job.status === 'queued' || job.status === 'processing') {
    if (status !== job.status || receipt.attempts !== job.attempts) {
      await transition(client, id, status, job.status, job.attempts);
    }
    return false;
  }

  // A worker can start and finish between two polls.
  if (status === 'queued') await transition(client, id, status, 'processing', job.attempts);
  if (job.status === 'dead') {
    await transition(client, id, 'processing', 'unreadable', job.attempts);
    await client.query(`
      UPDATE receipts SET result_at = now(), unreadable_reason = $2 WHERE id = $1
    `, [id, job.error ?? 'unreadable_image']);
    return true;
  }
  if (job.status !== 'done') throw new Error('Unexpected gateway receipt status');

  const result = job.result;
  const flags = computeFlags({
    totalConfidence: result.total_confidence,
    itemPrices: result.items.map((item) => item.price),
    total: result.total,
  });
  await transition(client, id, 'processing', 'review', job.attempts);
  await client.query(`
    UPDATE receipts SET ai_merchant = $2, ai_receipt_date = $3, ai_total = $4,
        merchant = $2, receipt_date = $3, total = $4, total_confidence = $5,
        flag_low_confidence = $6, flag_mismatch = $7, result_at = now()
    WHERE id = $1
  `, [id, result.merchant, result.date, result.total, result.total_confidence, flags.lowConfidence, flags.mismatch]);
  await client.query(`
    INSERT INTO receipt_items (receipt_id, line_no, ai_name, ai_price, name, price)
    SELECT $1, line_no, name, price, name, price
    FROM unnest($2::text[], $3::numeric[]) WITH ORDINALITY AS lines(name, price, line_no)
  `, [id, result.items.map((item) => item.name), result.items.map((item) => item.price)]);
  return true;
}

async function lockSent(client: PoolClient, id: string): Promise<Receipt | undefined> {
  const { rows: [receipt] } = await client.query<Receipt>(`
    SELECT ${receiptColumns}
    FROM receipts r JOIN batches b ON b.id = r.batch_id
    WHERE r.id = $1 AND r.dispatch_state = 'sent' AND r.status IN ('queued', 'processing')
    FOR UPDATE OF r SKIP LOCKED
  `, [id]);
  return receipt;
}

async function requeue(pool: Pool, id: string) {
  await transaction(pool, async (client) => {
    const receipt = await lockSent(client, id);
    if (!receipt) return;
    await transition(client, id, receipt.status, 'queued', 0);
    await client.query("UPDATE receipts SET dispatch_state = 'pending' WHERE id = $1", [id]);
  });
}

async function pollJob(
  pool: Pool, gateway: Gateway, receipts: Receipt[], promotionBackoff: Map<string, number>,
) {
  const { batch_id: jobId, priority } = receipts[0];
  const path = `/v1/jobs/${jobId}`;
  const response = await gateway('GET', path);
  if (response.status === 404) {
    for (const { id } of receipts) await requeue(pool, id);
    return;
  }
  if (response.status !== 200) throw new Error(`HTTP ${response.status}`);

  const job = JSON.parse(response.body) as GatewayJob;
  const byId = new Map(job.receipts.map((result) => [result.receipt_ref, result]));
  if (priority === 'urgent' && job.priority === 'normal' && job.receipts.some((r) => r.status === 'queued')
      && (promotionBackoff.get(jobId) ?? 0) <= Date.now()) {
    try {
      const promotion = await gateway('POST', `${path}/urgent`);
      if (promotion.status === 429 || promotion.status === 503) {
        promotionBackoff.set(jobId, retryDeadline(promotion.retryAfter, 60_000));
      } else if (promotion.status !== 200 && promotion.status !== 404) {
        report(`promote job ${jobId}`, `HTTP ${promotion.status}`);
      }
    } catch (error) {
      report(`promote job ${jobId}`, error);
    }
  }

  const finishedIds: string[] = [];
  for (const { id } of receipts) {
    try {
      const result = byId.get(id);
      if (!result) {
        await requeue(pool, id);
        continue;
      }
      const finished = await transaction(pool, async (client) => {
        const current = await lockSent(client, id);
        return current ? writeResult(client, current, result) : false;
      });
      if (finished) finishedIds.push(id);
    } catch (error) {
      report(`sync receipt ${id}`, error);
    }
  }
  await Promise.all(finishedIds.map(async (id) => {
    try {
      const cleanup = await gateway('DELETE', `/v1/receipts/${id}`);
      if (cleanup.status !== 204 && cleanup.status !== 404) throw new Error(`HTTP ${cleanup.status}`);
    } catch (error) {
      report(`clean up gateway receipt ${id}`, error);
    }
  }));
}

async function pollMock(pool: Pool, id: string) {
  await transaction(pool, async (client) => {
    const receipt = await lockSent(client, id);
    if (!receipt) return;
    const attempts = Math.min(receipt.attempts + 1, MAX_ATTEMPTS);
    await transition(client, id, receipt.status, 'processing', attempts);
    await writeResult(client, { ...receipt, status: 'processing', attempts }, mockRead(receipt.file_name, attempts));
  });
}

async function pollResults(pool: Pool, gateway: Gateway | undefined, promotionBackoff: Map<string, number>) {
  const { rows } = await pool.query<Receipt>(`
    SELECT ${receiptColumns}
    FROM receipts r JOIN batches b ON b.id = r.batch_id
    WHERE r.dispatch_state = 'sent' AND r.status IN ('queued', 'processing')
    ORDER BY ${queueOrder}
  `);

  if (!gateway) {
    for (const { id } of rows) {
      try { await pollMock(pool, id); } catch (error) { report(`mock receipt ${id}`, error); }
    }
    return;
  }

  const jobs = new Map<string, Receipt[]>();
  for (const receipt of rows) {
    const job = jobs.get(receipt.batch_id);
    if (job) job.push(receipt);
    else jobs.set(receipt.batch_id, [receipt]);
  }
  for (const [id, deadline] of promotionBackoff) {
    if (!jobs.has(id) || deadline <= Date.now()) promotionBackoff.delete(id);
  }
  const batches = [...jobs.values()];
  for (let i = 0; i < batches.length; i += 12) {
    await Promise.all(batches.slice(i, i + 12).map(async (receipts) => {
      try {
        await pollJob(pool, gateway, receipts, promotionBackoff);
      } catch (error) {
        report(`poll job ${receipts[0].batch_id}`, error);
      }
    }));
  }
}

async function pollWorkers(pool: Pool, gateway: Gateway) {
  const response = await gateway('GET', '/v1/queue');
  if (response.status !== 200) throw new Error(`HTTP ${response.status}`);
  const { workers_alive: count } = JSON.parse(response.body);
  if (!Number.isInteger(count) || count < 0) throw new Error('Invalid workers_alive');
  await pool.query(`
    INSERT INTO system_state (key, value) VALUES ('workers_alive', $1)
    ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
  `, [String(count)]);
}

async function everyTick(label: string, task: () => Promise<void>, signal: AbortSignal) {
  while (!signal.aborted) {
    const started = Date.now();
    try { await task(); } catch (error) { report(label, error); }
    await sleep(Math.max(0, POLL_MS - (Date.now() - started)), undefined, { signal }).catch(() => {});
  }
}

async function main() {
  const mode = process.env.AI_MODE || 'gateway';
  if (mode !== 'mock' && mode !== 'gateway') throw new Error('AI_MODE must be mock or gateway');
  const gateway = mode === 'gateway' ? await connectGateway() : undefined;
  const uploads = resolve(process.env.UPLOAD_DIR || '/app/uploads');
  const pool = new Pool({ connectionString: process.env.DATABASE_URL, connectionTimeoutMillis: 5_000 });
  pool.on('error', (error) => report('database connection', error));
  const stop = new AbortController();
  process.once('SIGINT', () => stop.abort());
  process.once('SIGTERM', () => stop.abort());

  const promotionBackoff = new Map<string, number>();
  try {
    const dispatch = everyTick('dispatch', async () => {
      for (let i = 0; i < 100 && !stop.signal.aborted; i++) {
        if (!(await dispatchOne(pool, gateway, uploads))) break;
      }
    }, stop.signal);
    const results = everyTick('poll receipts', () => pollResults(pool, gateway, promotionBackoff), stop.signal);
    const workers = gateway && everyTick('poll workers', () => pollWorkers(pool, gateway), stop.signal);
    await Promise.all([dispatch, results, workers]);
  } finally {
    await pool.end();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    report('startup', error);
    process.exitCode = 1;
  });
}
