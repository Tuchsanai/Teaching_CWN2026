/**
 * Business Rules BR-01 … BR-07 of SiteSafe Inspect.
 *
 * This file is the ONLY place in the system that holds BR thresholds and the
 * ONLY place that reads the BUG_MODE environment variable (DESIGN §8, §9).
 * API routes, the dispatcher and the pages must import the constants and
 * functions below instead of writing any threshold themselves.
 *
 * Pure module: no database, no I/O. Safe to import from server code and tests.
 */

export type Result = 'PASS' | 'WARN' | 'FAIL';
export type PhotoStatus = 'QUEUED' | 'PROCESSING' | 'DONE' | 'FAILED';

export const RESULTS: readonly Result[] = ['PASS', 'WARN', 'FAIL'];
export const PHOTO_STATUSES: readonly PhotoStatus[] = ['QUEUED', 'PROCESSING', 'DONE', 'FAILED'];

export const RESULT_LABELS: Readonly<Record<Result, string>> = {
  PASS: 'ผ่าน',
  WARN: 'เตือน',
  FAIL: 'ไม่ผ่าน',
};

export const STATUS_LABELS: Readonly<Record<PhotoStatus, string>> = {
  QUEUED: 'รอคิว',
  PROCESSING: 'กำลังตรวจ',
  DONE: 'เสร็จแล้ว',
  FAILED: 'ตรวจไม่สำเร็จ',
};

// ---------------------------------------------------------------------------
// Service mode — read exactly once, when this module is first loaded.
// ---------------------------------------------------------------------------

function readMode(raw: string | undefined): 0 | 1 {
  return raw !== undefined && raw.trim() === '1' ? 1 : 0;
}

const MODE: 0 | 1 = readMode(process.env.BUG_MODE);

// ---------------------------------------------------------------------------
// BR-01 … BR-03 · judging one photo from H and V (DESIGN §9.1)
// ---------------------------------------------------------------------------

/** BR-01: H ≥ 1 → FAIL */
export const HELMET_FAIL_MIN = 1;
/** BR-02: H = 0 and V ≥ 2 → FAIL (AS-03) */
export const VEST_FAIL_MIN = 2;
/** BR-03: H = 0 and V ≥ 1 (and below VEST_FAIL_MIN) → WARN */
export const VEST_WARN_MIN = 1;

const vestFailCut = VEST_FAIL_MIN + MODE;

function assertCount(name: string, n: number): void {
  if (!Number.isSafeInteger(n) || n < 0) {
    throw new RangeError(`${name} must be a non-negative integer`);
  }
}

/**
 * Result of a photo from the model counts.
 * Order: BR-01, then BR-02, then BR-03, otherwise PASS.
 */
export function judge(h: number, v: number): Result {
  assertCount('h', h);
  assertCount('v', v);
  if (h >= HELMET_FAIL_MIN) return 'FAIL';
  if (v >= vestFailCut) return 'FAIL';
  if (v >= VEST_WARN_MIN) return 'WARN';
  return 'PASS';
}

// ---------------------------------------------------------------------------
// BR-04 · pass rate and red flag of the daily report (DESIGN §9.2)
// ---------------------------------------------------------------------------

/** Sites whose pass rate is below this percentage are shown red. */
export const PASS_RATE_RED_BELOW_PERCENT = 90;

function assertRateInput(passCount: number, resultCount: number): void {
  assertCount('passCount', passCount);
  assertCount('resultCount', resultCount);
  if (passCount > resultCount) throw new RangeError('passCount must not exceed resultCount');
}

/**
 * Pass rate in percent, NOT rounded (e.g. 269/300 → 89.666…).
 * Returns null when no photo has a result yet (nothing to divide by).
 */
export function passRate(passCount: number, resultCount: number): number | null {
  assertRateInput(passCount, resultCount);
  if (resultCount === 0) return null;
  return (passCount * 100) / resultCount;
}

/** Pass rate for display with 2 decimals ("89.67"), or null when there is no result. */
export function formatPassRate(passCount: number, resultCount: number): string | null {
  assertRateInput(passCount, resultCount);
  if (resultCount === 0) return null;
  const hundredths = Math.round((passCount * 10_000) / resultCount);
  return (hundredths / 100).toFixed(2);
}

/**
 * Red flag, compared with integers only (pass × 100 < 90 × results), never with
 * a rounded value. A day/site without any result is never red.
 */
export function isRed(passCount: number, resultCount: number): boolean {
  assertRateInput(passCount, resultCount);
  if (resultCount === 0) return false;
  return passCount * 100 < PASS_RATE_RED_BELOW_PERCENT * resultCount + MODE;
}

// ---------------------------------------------------------------------------
// BR-05 · file size per photo (DESIGN §9.3)
// ---------------------------------------------------------------------------

export const BYTES_PER_MB = 1_048_576;
export const MAX_FILE_MB = 15;
/** 15 × 1,048,576 = 15,728,640 bytes. */
export const MAX_FILE_BYTES = MAX_FILE_MB * BYTES_PER_MB;

/** size ≤ 15,728,640 bytes → accepted. Count the bytes actually received. */
export function isSizeAllowed(sizeBytes: number): boolean {
  assertCount('sizeBytes', sizeBytes);
  return sizeBytes <= MAX_FILE_BYTES;
}

export const FILE_TOO_LARGE_MESSAGE = `ขนาดสูงสุด ${MAX_FILE_MB} MB`;

// ---------------------------------------------------------------------------
// BR-06 · number of photos per upload (DESIGN §9.3)
// ---------------------------------------------------------------------------

export const MIN_PHOTOS_PER_UPLOAD = 1;
export const MAX_PHOTOS_PER_UPLOAD = 50;

const photoCountCeiling = MAX_PHOTOS_PER_UPLOAD + MODE;

export type CountCheck = 'OK' | 'TOO_FEW' | 'TOO_MANY';

/** Count check done by POST /api/uploads before any file is received. */
export function checkPhotoCount(count: number): CountCheck {
  if (!Number.isSafeInteger(count)) throw new RangeError('count must be an integer');
  if (count < MIN_PHOTOS_PER_UPLOAD) return 'TOO_FEW';
  if (count > photoCountCeiling) return 'TOO_MANY';
  return 'OK';
}

export function isCountAllowed(count: number): boolean {
  return Number.isSafeInteger(count) && checkPhotoCount(count) === 'OK';
}

export const TOO_FEW_PHOTOS_MESSAGE = `ต้องเลือกอย่างน้อย ${MIN_PHOTOS_PER_UPLOAD} รูป`;
export const TOO_MANY_PHOTOS_MESSAGE = `ส่งได้ครั้งละไม่เกิน ${MAX_PHOTOS_PER_UPLOAD} รูป กรุณาแบ่งส่ง`;

/**
 * Limits the upload page must use for its own pre-check, so the page and the
 * API always agree (the page gets these through the API, never hard-codes them).
 */
export function uploadLimits(): {
  min_photos: number;
  max_photos: number;
  max_file_bytes: number;
  max_file_mb: number;
  accepted_types: string[];
} {
  return {
    min_photos: MIN_PHOTOS_PER_UPLOAD,
    max_photos: photoCountCeiling,
    max_file_bytes: MAX_FILE_BYTES,
    max_file_mb: MAX_FILE_MB,
    accepted_types: ['image/jpeg', 'image/png'],
  };
}

// ---------------------------------------------------------------------------
// BR-07 · daily report must be available from 18:00 Thai time (DESIGN §9.2)
// ---------------------------------------------------------------------------

export const TIME_ZONE = 'Asia/Bangkok';
/** Thailand has no daylight saving time: always UTC+07:00. */
export const BANGKOK_UTC_OFFSET_MINUTES = 7 * 60;
export const REPORT_READY_HOUR = 18;
export const REPORT_READY_MINUTE = 0;

export const REPORT_READY_LABEL = 'รายงานประจำวันพร้อมแล้ว';
export const REPORT_INTRADAY_LABEL = 'ข้อมูลระหว่างวัน';

const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

/** True for a real calendar date written as YYYY-MM-DD. */
export function isValidDateString(date: string): boolean {
  const m = DATE_RE.exec(date);
  if (!m) return false;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const t = new Date(Date.UTC(y, mo - 1, d));
  return t.getUTCFullYear() === y && t.getUTCMonth() === mo - 1 && t.getUTCDate() === d;
}

/** The instant (UTC ms) of 18:00 Thai time on the given Thai calendar date. */
export function reportReadyAt(date: string): number {
  if (!isValidDateString(date)) throw new RangeError('date must be YYYY-MM-DD');
  const [y, mo, d] = date.split('-').map(Number);
  return (
    Date.UTC(y, mo - 1, d, REPORT_READY_HOUR, REPORT_READY_MINUTE) -
    BANGKOK_UTC_OFFSET_MINUTES * 60_000
  );
}

/** now ≥ 18:00 (Thai time) of `date` → the daily report is "ready". */
export function isReportReady(now: Date, date: string): boolean {
  return now.getTime() >= reportReadyAt(date);
}

/** Thai calendar date (YYYY-MM-DD) of an instant — used for photos.upload_date. */
export function bangkokDate(instant: Date): string {
  const shifted = new Date(instant.getTime() + BANGKOK_UTC_OFFSET_MINUTES * 60_000);
  return shifted.toISOString().slice(0, 10);
}

/** ISO 8601 with +07:00 offset, e.g. 2026-11-18T18:00:00+07:00. */
export function bangkokIso(instant: Date): string {
  const shifted = new Date(instant.getTime() + BANGKOK_UTC_OFFSET_MINUTES * 60_000);
  return `${shifted.toISOString().slice(0, 19)}+07:00`;
}

/** Add whole days to a YYYY-MM-DD date. */
export function addDays(date: string, days: number): string {
  if (!isValidDateString(date)) throw new RangeError('date must be YYYY-MM-DD');
  const [y, mo, d] = date.split('-').map(Number);
  return new Date(Date.UTC(y, mo - 1, d + days)).toISOString().slice(0, 10);
}
