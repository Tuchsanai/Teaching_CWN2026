/**
 * resetAndSeed(now?) — wipe the 7 tables and the photos volume, then insert the
 * seed of docs/TEST-DATA.md §1–§3 with fixed row ids (DESIGN §7.2):
 * 3 sites · 5 users · 1,233 photos · 1 override. Running it again gives the same data.
 *
 * Result values of seed photos are written exactly as listed in TEST-DATA §3
 * (not computed through lib/rules), so the report seed does not depend on the rules.
 * Used by POST /api/test/reset and by `npm run seed`.
 */
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { hashPassword } from '../lib/auth';
import { ownerPool } from '../lib/db';
import { RESET_LOCK_KEY } from '../lib/locks';
import { photosDir } from '../lib/photo-store';
import { applySchema } from './migrate';

type R = 'PASS' | 'WARN' | 'FAIL';
type St = 'QUEUED' | 'PROCESSING' | 'DONE' | 'FAILED';

export const SEED_SITES = [
  { id: 1, code: 'SITE-A', name: 'ไซต์ ก' },
  { id: 2, code: 'SITE-B', name: 'ไซต์ ข' },
  { id: 3, code: 'SITE-C', name: 'ไซต์ ค' },
] as const;

export const SEED_USERS = [
  { id: 1, email: 'manager@sitesafe.test', password: 'Test-Manager-01', full_name: 'ผู้จัดการความปลอดภัย', role: 'manager', site_id: null },
  { id: 2, email: 'sup.a@sitesafe.test', password: 'Test-SupA-01', full_name: 'หัวหน้างานไซต์ ก', role: 'supervisor', site_id: 1 },
  { id: 3, email: 'sup.b@sitesafe.test', password: 'Test-SupB-01', full_name: 'หัวหน้างานไซต์ ข', role: 'supervisor', site_id: 2 },
  { id: 4, email: 'sup.c@sitesafe.test', password: 'Test-SupC-01', full_name: 'หัวหน้างานไซต์ ค', role: 'supervisor', site_id: 3 },
  { id: 5, email: 'exec@sitesafe.test', password: 'Test-Exec-01', full_name: 'ผู้บริหาร', role: 'executive', site_id: null },
] as const;

const D1 = '2026-11-16';
const D2 = '2026-11-17';
const D3 = '2026-11-18';

/** One group of identical seed photos. */
type Part = { n: number; status: St; h?: number; v?: number; result?: R };

/** TEST-DATA §3, rows P-1 … P-9 (values copied as written, not computed). */
const GROUPS: { code: string; date: string; siteId: number; parts: Part[] }[] = [
  { code: 'P-1', date: D1, siteId: 1, parts: [
    { n: 269, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 11, status: 'DONE', h: 0, v: 1, result: 'WARN' },
    { n: 15, status: 'DONE', h: 1, v: 0, result: 'FAIL' },
    { n: 5, status: 'DONE', h: 0, v: 2, result: 'FAIL' },
  ] },
  { code: 'P-2', date: D1, siteId: 2, parts: [
    { n: 270, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 10, status: 'DONE', h: 0, v: 1, result: 'WARN' },
    { n: 10, status: 'DONE', h: 1, v: 0, result: 'FAIL' },
    { n: 5, status: 'DONE', h: 2, v: 0, result: 'FAIL' },
    { n: 5, status: 'DONE', h: 0, v: 2, result: 'FAIL' },
  ] },
  { code: 'P-3', date: D1, siteId: 3, parts: [
    { n: 271, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 9, status: 'DONE', h: 0, v: 1, result: 'WARN' },
    { n: 20, status: 'DONE', h: 1, v: 0, result: 'FAIL' },
  ] },
  // P-4: D2 · SITE-A has no photo
  { code: 'P-5', date: D2, siteId: 2, parts: [
    { n: 9, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 1, status: 'DONE', h: 0, v: 1, result: 'WARN' },
  ] },
  { code: 'P-6', date: D2, siteId: 3, parts: [
    { n: 9, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 1, status: 'FAILED' },
  ] },
  { code: 'P-7', date: D3, siteId: 1, parts: [
    { n: 269, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 11, status: 'DONE', h: 0, v: 1, result: 'WARN' },
    { n: 15, status: 'DONE', h: 1, v: 0, result: 'FAIL' },
    { n: 5, status: 'DONE', h: 0, v: 2, result: 'FAIL' },
  ] },
  { code: 'P-8', date: D3, siteId: 2, parts: [
    { n: 8, status: 'DONE', h: 0, v: 0, result: 'PASS' },
    { n: 1, status: 'DONE', h: 0, v: 1, result: 'WARN' },
    { n: 1, status: 'DONE', h: 1, v: 0, result: 'FAIL' },
    { n: 1, status: 'QUEUED' },
    { n: 1, status: 'PROCESSING' },
  ] },
  { code: 'P-9', date: D3, siteId: 3, parts: [
    { n: 1, status: 'DONE', h: 2, v: 1, result: 'FAIL' },
  ] },
];

/** P-7: U-1 changed one (0,2) photo of D3 · SITE-A from FAIL to PASS. */
const OVERRIDE = {
  id: 1,
  group: 'P-7',
  h: 0,
  v: 2,
  edited_by: 1,
  edited_at: `${D3}T10:00:00+07:00`,
  result_before: 'FAIL' as R,
  result_after: 'PASS' as R,
  reason: 'ตรวจซ้ำแล้ว คนในรูปสวมเสื้อสะท้อนแสงครบ',
};

/** Batches hold at most this many seed photos (fits upload_batches.declared_count). */
const SEED_BATCH_SIZE = 25;
const SAMPLE_STORAGE_PATH = 'seed/sample.jpg';
const SAMPLE_W = 64;
const SAMPLE_H = 48;
// 64×48 JPEG shared by every seed photo (TEST-DATA §3: one sample file)
const SAMPLE_JPEG_B64 =
  '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAwAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDuaKKKzGFFNYkdKTcfWvNr5nRoVHTknden+ZvChKceZD6KZuPrSqSTU0c0o1ZqEU7v0/zHLDyirsdRRRXqHOFFFFADX7U2nP2ptfHZn/vc/l+SPTofw0FKvWkpV61ngP8AeYepVb+Gx9FFFfanlBRRRQA1+1NqTFJgeleHi8snXrOopJX/AMjrp4hQio2GUq9adgelGBU4fKp0qsajktBzxClFqwtFFFe8cZ//2Q==';

const SITE_CODE: Record<number, string> = { 1: 'SITE-A', 2: 'SITE-B', 3: 'SITE-C' };
const SUPERVISOR_OF_SITE: Record<number, number> = { 1: 2, 2: 3, 3: 4 };

/** Fixed, valid v4-shaped UUIDs: 5eed0000-0000-4000-8000-{kind}{counter}. */
function seedUuid(kind: number, n: number): string {
  return `5eed0000-0000-4000-8000-${kind.toString(16).padStart(2, '0')}${n.toString(16).padStart(10, '0')}`;
}

export type SeedCounts = { sites: number; users: number; photos: number; overrides: number };

type PhotoSeed = {
  id: string; batch_id: string; site_id: number; uploaded_by: number; upload_date: string;
  original_filename: string; status: St; fail_reason: string | null; accepted_at: string;
  finished_at: string | null; model_h: number | null; model_v: number | null;
  model_result: R | null; current_result: R | null; is_overridden: boolean;
};

let passwordHashes: Promise<string[]> | null = null;
function seedPasswordHashes(): Promise<string[]> {
  return (passwordHashes ??= Promise.all(SEED_USERS.map((u) => hashPassword(u.password))));
}

async function clearPhotosDir(): Promise<void> {
  const root = photosDir();
  await fs.mkdir(root, { recursive: true });
  for (const entry of await fs.readdir(root)) {
    await fs.rm(path.join(root, entry), { recursive: true, force: true });
  }
  const sample = path.join(root, SAMPLE_STORAGE_PATH);
  await fs.mkdir(path.dirname(sample), { recursive: true });
  await fs.writeFile(sample, Buffer.from(SAMPLE_JPEG_B64, 'base64'));
}

function buildSeed() {
  const sample = Buffer.from(SAMPLE_JPEG_B64, 'base64');
  const batches: { id: string; site_id: number; uploaded_by: number; declared_count: number; created_at: string }[] = [];
  const photos: PhotoSeed[] = [];
  const detections: { photo_id: string; cls: string; i: number }[] = [];
  let overridePhotoId: string | null = null;
  let photoN = 0;
  let batchN = 0;

  for (const g of GROUPS) {
    const supervisor = SUPERVISOR_OF_SITE[g.siteId];
    const items: Part[] = g.parts.flatMap((p) => Array.from({ length: p.n }, () => ({ ...p, n: 1 })));
    for (let start = 0; start < items.length; start += SEED_BATCH_SIZE) {
      const chunk = items.slice(start, start + SEED_BATCH_SIZE);
      batchN += 1;
      const batchId = seedUuid(1, batchN);
      const minute = String(Math.floor(start / SEED_BATCH_SIZE)).padStart(2, '0');
      batches.push({
        id: batchId,
        site_id: g.siteId,
        uploaded_by: supervisor,
        declared_count: chunk.length,
        created_at: `${g.date}T09:${minute}:00+07:00`,
      });
      chunk.forEach((p, k) => {
        photoN += 1;
        const id = seedUuid(2, photoN);
        const sec = String(k).padStart(2, '0');
        const accepted = `${g.date}T09:${minute}:${sec}+07:00`;
        const done = p.status === 'DONE';
        const terminal = done || p.status === 'FAILED';
        photos.push({
          id,
          batch_id: batchId,
          site_id: g.siteId,
          uploaded_by: supervisor,
          upload_date: g.date,
          original_filename: done ? `h${p.h}_v${p.v}_${photoN}.jpg` : `seed_${photoN}.jpg`,
          status: p.status,
          fail_reason: p.status === 'FAILED' ? 'เปิดไฟล์รูปไม่ได้' : null,
          accepted_at: accepted,
          finished_at: terminal ? `${g.date}T09:${minute}:${sec}.900+07:00` : null,
          model_h: done ? p.h! : null,
          model_v: done ? p.v! : null,
          model_result: done ? p.result! : null,
          current_result: done ? p.result! : null,
          is_overridden: false,
        });
        if (done) {
          for (let i = 0; i < p.h!; i++) detections.push({ photo_id: id, cls: 'NO_HARDHAT', i });
          for (let i = 0; i < p.v!; i++) detections.push({ photo_id: id, cls: 'NO_VEST', i: p.h! + i });
        }
        if (
          g.code === OVERRIDE.group && overridePhotoId === null && done &&
          p.h === OVERRIDE.h && p.v === OVERRIDE.v && p.result === OVERRIDE.result_before
        ) {
          overridePhotoId = id;
          const last = photos[photos.length - 1];
          last.current_result = OVERRIDE.result_after;
          last.is_overridden = true;
        }
      });
    }
  }
  if (!overridePhotoId) throw new Error('seed: override photo not found');
  return { sample, batches, photos, detections, overridePhotoId: overridePhotoId as string };
}

/**
 * Reset the database and the photos volume to the TEST-DATA seed.
 * `now` is accepted for API symmetry (the system clock itself lives in lib/clock).
 */
export async function resetAndSeed(_now?: Date): Promise<SeedCounts> {
  const seed = buildSeed();
  const hashes = await seedPasswordHashes();
  const db = ownerPool();
  const c = await db.connect();
  try {
    await c.query('SELECT pg_advisory_lock($1)', [RESET_LOCK_KEY]); // pauses the dispatcher
    try {
      await applySchema(c);
      await clearPhotosDir();
      await c.query('BEGIN');
      await c.query(
        `TRUNCATE detections, result_overrides, photos, upload_batches, sessions, users, sites
         RESTART IDENTITY CASCADE`,
      );
      for (const s of SEED_SITES) {
        await c.query(`INSERT INTO sites (id, code, name) VALUES ($1, $2, $3)`, [s.id, s.code, s.name]);
      }
      for (const [i, u] of SEED_USERS.entries()) {
        await c.query(
          `INSERT INTO users (id, email, password_hash, full_name, role, site_id, is_active)
           VALUES ($1, $2, $3, $4, $5, $6, true)`,
          [u.id, u.email, hashes[i], u.full_name, u.role, u.site_id],
        );
      }
      const b = seed.batches;
      await c.query(
        `INSERT INTO upload_batches (id, site_id, uploaded_by, declared_count, created_at)
         SELECT * FROM unnest($1::uuid[], $2::int[], $3::int[], $4::int[], $5::timestamptz[])`,
        [b.map((x) => x.id), b.map((x) => x.site_id), b.map((x) => x.uploaded_by), b.map((x) => x.declared_count), b.map((x) => x.created_at)],
      );
      const p = seed.photos;
      await c.query(
        `INSERT INTO photos (id, batch_id, site_id, uploaded_by, upload_date, original_filename, mime,
                             size_bytes, sha256, storage_path, status, fail_reason, dispatch_state,
                             submit_attempts, accepted_at, submitted_at, finished_at,
                             model_h, model_v, model_result, current_result, is_overridden,
                             model_version, conf_threshold, image_w, image_h)
         SELECT t.id, t.batch_id, t.site_id, t.uploaded_by, t.upload_date, t.fname, 'image/jpeg',
                $16::bigint, $17, $18, t.status, t.fail_reason, 'CLOSED',
                1, t.accepted_at, t.accepted_at, t.finished_at,
                t.mh, t.mv, t.mr, t.cr, t.ov,
                CASE WHEN t.status = 'DONE' THEN 'seed' END,
                CASE WHEN t.status = 'DONE' THEN 0.5 END,
                CASE WHEN t.status = 'DONE' THEN $19::int END,
                CASE WHEN t.status = 'DONE' THEN $20::int END
           FROM unnest($1::uuid[], $2::uuid[], $3::int[], $4::int[], $5::date[], $6::text[], $7::text[],
                       $8::text[], $9::timestamptz[], $10::timestamptz[], $11::int[], $12::int[],
                       $13::text[], $14::text[], $15::boolean[])
             AS t(id, batch_id, site_id, uploaded_by, upload_date, fname, status, fail_reason,
                  accepted_at, finished_at, mh, mv, mr, cr, ov)`,
        [
          p.map((x) => x.id), p.map((x) => x.batch_id), p.map((x) => x.site_id), p.map((x) => x.uploaded_by),
          p.map((x) => x.upload_date), p.map((x) => x.original_filename), p.map((x) => x.status),
          p.map((x) => x.fail_reason), p.map((x) => x.accepted_at), p.map((x) => x.finished_at),
          p.map((x) => x.model_h), p.map((x) => x.model_v), p.map((x) => x.model_result),
          p.map((x) => x.current_result), p.map((x) => x.is_overridden),
          seed.sample.length,
          createHash('sha256').update(seed.sample).digest('hex'),
          SAMPLE_STORAGE_PATH, SAMPLE_W, SAMPLE_H,
        ],
      );
      const d = seed.detections;
      await c.query(
        `INSERT INTO detections (photo_id, cls, confidence, x1, y1, x2, y2)
         SELECT t.photo_id, t.cls, 0.9, 2 + t.i * 6, 4, 6 + t.i * 6, 44
           FROM unnest($1::uuid[], $2::text[], $3::int[]) AS t(photo_id, cls, i)`,
        [d.map((x) => x.photo_id), d.map((x) => x.cls), d.map((x) => x.i)],
      );
      await c.query(
        `INSERT INTO result_overrides (id, photo_id, edited_by, edited_at, result_before, result_after, reason)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [OVERRIDE.id, seed.overridePhotoId, OVERRIDE.edited_by, OVERRIDE.edited_at, OVERRIDE.result_before, OVERRIDE.result_after, OVERRIDE.reason],
      );
      for (const t of ['sites', 'users', 'result_overrides']) {
        await c.query(`SELECT setval(pg_get_serial_sequence($1, 'id'), (SELECT COALESCE(max(id), 0) + 1 FROM ${t}), false)`, [t]);
      }
      await c.query('COMMIT');
    } catch (e) {
      try {
        await c.query('ROLLBACK');
      } catch {
        /* ignore */
      }
      throw e;
    } finally {
      await c.query('SELECT pg_advisory_unlock($1)', [RESET_LOCK_KEY]).catch(() => undefined);
    }
  } finally {
    c.release();
  }
  return { sites: SEED_SITES.length, users: SEED_USERS.length, photos: seed.photos.length, overrides: 1 };
}

export const __seedForTests = { buildSeed, GROUPS, SITE_CODE };
