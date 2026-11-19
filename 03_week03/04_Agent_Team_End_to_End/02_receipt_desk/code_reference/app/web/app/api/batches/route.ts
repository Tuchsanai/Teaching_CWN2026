/**
 * W7 · POST /api/batches — อัปโหลดชุด · พนักงาน · หัวหน้า · ลูกค้า (ร้านตัวเอง) · เจ้าของ → 403
 * W8 · GET  /api/batches — รายการชุด · พนักงาน · หัวหน้า · เจ้าของ · ลูกค้า → 403
 *
 * POST multipart/form-data:
 *   files (หลายไฟล์ · ชื่อช่อง `files` หรือ `file`) · clientId (สำนักงานต้องส่ง · ลูกค้าถูกบังคับเป็นร้านตัวเอง)
 *   urgent=true (เฉพาะหัวหน้าทีม คนอื่น → 403 forbidden)
 *
 * ลำดับการตัดสิน (ทุกข้อเรียก rules.ts):
 *   1. BR-01 · BR-02 · BR-03  rules.validateUpload()      → 422 batch_size / file_too_large / file_type / pdf_pages
 *   2. BR-08 (ถ้า urgent)      rules.checkUrgentSize()     → 422 urgent_too_large
 *   3. เขียนไฟล์ลง volume (fsync) ก่อนเปิดธุรกรรม
 *   4. ธุรกรรมเดียว: LOCK TABLE batches, receipts (SHARE ROW EXCLUSIVE) → นับใหม่ภายใต้ล็อก
 *      BR-09 (ถ้า urgent)      rules.checkUrgentQuota()    → 409 urgent_quota
 *      BR-11 · BR-12           rules.checkQueueCapacity()  → 429 queue_full + retryAfterMinutes + Retry-After
 *      ผ่าน → INSERT batches + receipts (queued · pending) + receipt_events → COMMIT → 201
 *   ไม่ผ่านข้อใด → ROLLBACK + ลบไฟล์ที่เขียนไว้ ไม่มีแถวใดถูกสร้าง (FR-23)
 */
import { randomUUID } from 'node:crypto';
import { mkdir, open, rm } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import rules, { LIMITS, bangkokDayRange, resolveFileKind } from '../../../lib/rules';
import type { FileKind, UploadFileInput } from '../../../lib/rules';
import { OFFICE, clientExists, requireUser } from '../_lib/auth';
import { isUuid, query, transaction } from '../_lib/db';
import { ApiError, badRequest, boolParam, forbidden, handle, json, notFound, ruleError } from '../_lib/http';
import { STATUSES } from '../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MIME: Record<FileKind, string> = { jpg: 'image/jpeg', png: 'image/png', pdf: 'application/pdf' };
const EXT: Record<FileKind, string> = { jpg: '.jpg', png: '.png', pdf: '.pdf' };

function uploadDir(): string {
  return resolve(/*turbopackIgnore: true*/ process.env.UPLOAD_DIR || '/app/uploads');
}

/** เขียนไฟล์แล้ว fsync — ไฟล์ต้องถาวรก่อนตอบ "รับแล้ว" (NFR-06) */
async function writeDurable(path: string, bytes: Uint8Array): Promise<void> {
  const fh = await open(path, 'wx', 0o640);
  try {
    await fh.writeFile(bytes);
    await fh.sync();
  } finally {
    await fh.close();
  }
}

async function syncDir(path: string): Promise<void> {
  try {
    const fh = await open(path, 'r');
    try {
      await fh.sync();
    } finally {
      await fh.close();
    }
  } catch {
    // บางระบบไฟล์ไม่รองรับ fsync ของโฟลเดอร์
  }
}

function isFileEntry(v: FormDataEntryValue): v is File {
  return typeof v === 'object' && v !== null && 'arrayBuffer' in v;
}

export const POST = handle(async (request: Request) => {
  const user = await requireUser(request, ['staff', 'lead', 'client']);

  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    throw badRequest('ต้องส่งแบบ multipart/form-data');
  }

  const urgent = boolParam(form.get('urgent') as string | null) === true;
  // FR-19: ตั้งด่วนได้เฉพาะหัวหน้าทีม
  if (urgent && user.role !== 'lead') throw forbidden();

  // ร้านของชุด: ลูกค้าถูกบังคับเป็นร้านของ session (FR-26) · สำนักงานต้องเลือก (A-16)
  let clientId: string;
  if (user.role === 'client') {
    clientId = user.clientId as string;
  } else {
    const raw = form.get('clientId') ?? form.get('client_id');
    if (typeof raw !== 'string' || !raw) throw badRequest('กรุณาเลือกลูกค้า (clientId)');
    if (!isUuid(raw) || !(await clientExists(raw))) throw notFound();
    clientId = raw;
  }

  // ไฟล์ — ช่องว่างจากเบราว์เซอร์ (ไม่มีชื่อ ขนาด 0) ไม่นับ
  const entries = [...form.getAll('files'), ...form.getAll('file')].filter(isFileEntry);
  const files = entries.filter((f) => !(f.size === 0 && !f.name));
  const inputs: Array<UploadFileInput & { bytes: Uint8Array }> = [];
  for (const f of files) {
    inputs.push({ name: f.name || 'unnamed', size: f.size, bytes: new Uint8Array(await f.arrayBuffer()), mimeType: f.type || null });
  }

  // BR-01 · BR-02 · BR-03
  const upload = rules.validateUpload(inputs);
  if (!upload.ok) throw ruleError(upload, { accepted: 0 });

  // BR-08 (ตั้งด่วนตอนอัปโหลด)
  if (urgent) {
    const size = rules.checkUrgentSize(inputs.length);
    if (!size.ok) throw ruleError(size, { accepted: 0 });
  }

  // เขียนไฟล์ก่อนเปิดธุรกรรม เพื่อไม่ถือล็อกตารางระหว่างเขียนดิสก์
  const batchId = randomUUID();
  const dir = join(uploadDir(), batchId);
  const planned = inputs.map((f) => {
    const kind = resolveFileKind(f) as FileKind;
    const id = randomUUID();
    return { id, name: f.name, kind, size: f.size, bytes: f.bytes, relPath: `${batchId}/${id}${EXT[kind]}` };
  });

  let committed = false;
  try {
    await mkdir(dir, { recursive: true, mode: 0o750 });
    for (const p of planned) await writeDurable(join(uploadDir(), p.relPath), p.bytes);
    await syncDir(dir);
    for (const p of planned) p.bytes = new Uint8Array(0);

    const result = await transaction(async (client) => {
      await client.query(`SET LOCAL lock_timeout = '30s'`);
      // DESIGN 6.2: นับ BR-11 ในธุรกรรมเดียวกับการสร้างชุด (ล็อกระดับตาราง) — ลำดับ batches → receipts เสมอ
      await client.query('LOCK TABLE batches IN SHARE ROW EXCLUSIVE MODE');
      await client.query('LOCK TABLE receipts IN SHARE ROW EXCLUSIVE MODE');
      const { rows: [clock] } = await client.query<{ now: Date }>('SELECT clock_timestamp() AS now');
      const now = new Date(clock.now);

      let urgentUsedToday: number | undefined;
      if (urgent) {
        const { start, end } = bangkokDayRange(now);
        const { rows: [u] } = await client.query<{ n: number }>(
          `SELECT count(*)::int AS n FROM batches
            WHERE priority = 'urgent' AND urgent_set_at >= $1 AND urgent_set_at < $2`,
          [start, end],
        );
        urgentUsedToday = u.n;
        const quota = rules.checkUrgentQuota(u.n);
        if (!quota.ok) throw ruleError(quota, { accepted: 0, usedToday: u.n });
      }

      const { rows: [pending] } = await client.query<{ n: number }>(
        `SELECT count(*)::int AS n FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'normal' AND r.status IN ('queued', 'processing')`,
      );
      const { rows: [ws] } = await client.query<{ value: string; updated_at: Date }>(
        `SELECT value, updated_at FROM system_state WHERE key = 'workers_alive'`,
      );
      const workersAlive = ws && Number.isFinite(Number(ws.value)) ? Number(ws.value) : null;
      const capacity = rules.checkQueueCapacity({
        pendingNormal: pending.n,
        newCount: planned.length,
        urgent,
        workersAlive,
        workersUpdatedAt: ws ? ws.updated_at : null,
        now,
      });
      if (!capacity.ok) throw ruleError(capacity, { accepted: 0 });

      await client.query(
        `INSERT INTO batches (id, client_id, uploaded_by, priority, urgent_set_by, urgent_set_at, receipt_count, accepted_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
        [batchId, clientId, user.id, urgent ? 'urgent' : 'normal', urgent ? user.id : null, urgent ? now : null, planned.length, now],
      );
      await client.query(
        `INSERT INTO receipts (id, batch_id, client_id, file_name, file_path, mime_type, size_bytes,
                               status, dispatch_state, accepted_at)
         SELECT f.id, $1, $2, f.name, f.path, f.mime, f.size, 'queued', 'pending', $3
           FROM unnest($4::uuid[], $5::text[], $6::text[], $7::text[], $8::int[]) AS f(id, name, path, mime, size)`,
        [
          batchId,
          clientId,
          now,
          planned.map((p) => p.id),
          planned.map((p) => p.name),
          planned.map((p) => p.relPath),
          planned.map((p) => MIME[p.kind]),
          planned.map((p) => p.size),
        ],
      );
      await client.query(
        `INSERT INTO receipt_events (receipt_id, from_status, to_status, actor_id, created_at)
         SELECT id, NULL, 'queued', $2, $3 FROM unnest($1::uuid[]) AS id`,
        [planned.map((p) => p.id), user.id, now],
      );
      return {
        now,
        pendingNormalAfter: urgent ? pending.n : pending.n + planned.length,
        urgentUsedToday: urgentUsedToday === undefined ? undefined : urgentUsedToday + 1,
      };
    });
    committed = true;

    return json(
      {
        batchId,
        accepted: planned.length,
        priority: urgent ? 'urgent' : 'normal',
        clientId,
        acceptedAt: result.now.toISOString(),
        receipts: planned.map((p) => ({ id: p.id, fileName: p.name, status: 'queued' })),
        queue: { pendingNormal: result.pendingNormalAfter, limit: LIMITS.NORMAL_QUEUE_CAP },
        ...(result.urgentUsedToday !== undefined ? { urgentUsedToday: result.urgentUsedToday } : {}),
        message: `รับแล้ว ${planned.length} ใบ`,
      },
      201,
    );
  } catch (error) {
    const code = (error as { code?: string }).code;
    if (code === '55P03') {
      throw new ApiError(503, 'busy', 'ระบบกำลังรับชุดอื่นอยู่ กรุณาลองใหม่อีกครั้ง', { accepted: 0 }, { 'Retry-After': '5' });
    }
    throw error;
  } finally {
    if (!committed) await rm(dir, { recursive: true, force: true }).catch(() => {});
  }
});

interface BatchRow {
  id: string;
  client_id: string;
  client_code: string;
  client_name: string;
  uploaded_by_name: string;
  priority: 'normal' | 'urgent';
  urgent_set_at: Date | null;
  receipt_count: number;
  accepted_at: Date;
  counts: Record<string, number> | null;
  flagged: number;
}

export const GET = handle(async (request: Request) => {
  await requireUser(request, OFFICE);
  const url = new URL(request.url);
  const params: unknown[] = [];
  const where: string[] = [];
  const clientId = url.searchParams.get('clientId');
  if (clientId) {
    if (!isUuid(clientId)) throw badRequest('clientId ไม่ถูกต้อง');
    params.push(clientId);
    where.push(`b.client_id = $${params.length}`);
  }
  const priority = url.searchParams.get('priority');
  if (priority) {
    if (priority !== 'normal' && priority !== 'urgent') throw badRequest('priority ต้องเป็น normal หรือ urgent');
    params.push(priority);
    where.push(`b.priority = $${params.length}`);
  }
  const limit = Math.min(500, Math.max(1, Number(url.searchParams.get('limit')) || 100));
  const offset = Math.max(0, Number(url.searchParams.get('offset')) || 0);
  params.push(limit, offset);

  const rows = await query<BatchRow>(
    `SELECT b.id, b.client_id, c.code AS client_code, c.name AS client_name, u.display_name AS uploaded_by_name,
            b.priority, b.urgent_set_at, b.receipt_count, b.accepted_at,
            (SELECT jsonb_object_agg(s.status, s.n) FROM (
               SELECT r.status, count(*)::int AS n FROM receipts r WHERE r.batch_id = b.id GROUP BY r.status) s) AS counts,
            (SELECT count(*)::int FROM receipts r WHERE r.batch_id = b.id
               AND r.status IN ('review', 'unreadable') AND (r.flag_low_confidence OR r.flag_mismatch)) AS flagged
       FROM batches b
       JOIN clients c ON c.id = b.client_id
       JOIN users u ON u.id = b.uploaded_by
      ${where.length ? `WHERE ${where.join(' AND ')}` : ''}
      ORDER BY b.accepted_at DESC, b.id
      LIMIT $${params.length - 1} OFFSET $${params.length}`,
    params,
  );

  return json({
    batches: rows.map((b) => {
      const counts = Object.fromEntries(STATUSES.map((s) => [s, b.counts?.[s] ?? 0]));
      const sum = STATUSES.reduce((n, s) => n + counts[s], 0);
      return {
        id: b.id,
        clientId: b.client_id,
        clientCode: b.client_code,
        clientName: b.client_name,
        uploadedBy: b.uploaded_by_name,
        priority: b.priority,
        urgentSetAt: b.urgent_set_at ? new Date(b.urgent_set_at).toISOString() : null,
        acceptedAt: new Date(b.accepted_at).toISOString(),
        accepted: b.receipt_count,
        counts,
        sum,
        diff: b.receipt_count - sum,
        flagged: b.flagged,
      };
    }),
    limit,
    offset,
  });
});
