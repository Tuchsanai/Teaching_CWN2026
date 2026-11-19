/**
 * ReceiptDesk · โมดูลกฎ (Business Rule) ของฝั่งเว็บ — DESIGN หลักข้อ 4
 *
 * รวมกฎที่เกี่ยวกับการตัดสินใจของคนทั้งหมดไว้ที่นี่ที่เดียว:
 *   BR-01 BR-02 BR-03  ตรวจชุดและไฟล์ตอนอัปโหลด
 *   BR-04 BR-05        ติดธง "ระบบไม่แน่ใจ"
 *   BR-06              ยอดรวมที่ยืนยันได้
 *   BR-08 BR-09        งานด่วน (ขนาดชุด · โควตาต่อวันตามเวลาไทย)
 *   BR-11 BR-12        เพดานคิวงานปกติ · นาทีที่ให้ลองใหม่
 *   BR-13              งานปกติค้างเกินกำหนด
 *   BR-14              นับเดือนตามวันที่บนใบเสร็จ (เวลาไทย)
 * BR-07 และ BR-10 ทำงานจริงที่ฝั่ง AI (gateway/Worker) — ที่นี่มีเฉพาะแบบจำลองอ้างอิงแบบฟังก์ชันบริสุทธิ์
 * (`readAttemptOutcome` · `nextQueue` · `planReadOrder`) ไว้ให้ชุดทดสอบตรวจกติกาครบ 62 แถว
 * และให้ฝั่งเว็บอธิบายผลได้ตรงกับฝั่ง AI
 *
 * ไม่มี I/O: ไม่อ่านไฟล์ ไม่ต่อฐานข้อมูล ไม่เรียกเครือข่าย ทุกฟังก์ชันรับค่าแล้วคืนค่า
 * เวลาปัจจุบันส่งเข้ามาเป็นพารามิเตอร์ `now` เสมอ เพื่อให้ทดสอบได้
 *
 * จำนวนเงินเทียบเป็นสตางค์ (จำนวนเต็ม) ไม่ใช้ float — ค่าจาก PostgreSQL `numeric(12,2)`
 * มาเป็น string เช่น "100.00" ส่งเข้ามาตรง ๆ ได้
 *
 * โหมดฝึกทดสอบ: อ่าน `BUG_MODE` ครั้งเดียวตอนโหลดโมดูล (DESIGN 9.6)
 * ชุดทดสอบใช้ `createRules({ bugMode })` เพื่อสร้างชุดกฎของโหมดที่ต้องการได้
 *
 * เขียนให้รันได้ทั้ง TypeScript ปกติ และ `node --experimental-strip-types`
 * (ไม่ใช้ enum · namespace · parameter property)
 */

// ---------------------------------------------------------------------------
// ค่าคงที่ของกฎ
// ---------------------------------------------------------------------------

export const LIMITS = Object.freeze({
  /** BR-01 */
  BATCH_MIN_FILES: 1,
  BATCH_MAX_FILES: 100,
  /** BR-02 · 10.00 MB = 10 × 1,048,576 ไบต์ */
  MAX_FILE_BYTES: 10 * 1024 * 1024,
  /** BR-03 */
  PDF_PAGES: 1,
  /** BR-04 */
  MIN_TOTAL_CONFIDENCE: 0.9,
  /** BR-05 · 1.00 บาท */
  MAX_ITEMS_DIFF_SATANG: 100,
  /** BR-06 · 0.01 บาท */
  MIN_CONFIRM_TOTAL_SATANG: 1,
  /** BR-07 · อ่านได้ไม่เกิน 3 ครั้งต่อใบ (คิดที่ฝั่ง AI) */
  MAX_READ_ATTEMPTS: 3,
  /** BR-08 */
  URGENT_MAX_RECEIPTS: 10,
  /** BR-09 */
  URGENT_MAX_PER_DAY: 5,
  /** BR-10 · อ่านใบด่วนติดกันได้ไม่เกิน 4 ใบเมื่อมีใบปกติรอ (คิดที่ฝั่ง AI) */
  MAX_URGENT_STREAK: 4,
  /** BR-11 */
  NORMAL_QUEUE_CAP: 400,
  /** BR-12 · ใบ/นาที ต่อ Worker 1 ตัว */
  READS_PER_MINUTE_PER_WORKER: 4,
  /** BR-12 · ค่า workers_alive เก่ากว่านี้ถือว่าไม่ทราบ (DESIGN 6.2) */
  WORKERS_STALE_MS: 30_000,
  /** BR-13 */
  OVERDUE_MINUTES: 120,
});

/** เวลาไทย Asia/Bangkok = UTC+7 ไม่มีเวลาออมแสง */
export const BANGKOK_OFFSET_MS = 7 * 60 * 60 * 1000;

const DAY_MS = 24 * 60 * 60 * 1000;

export const ACCEPTED_EXTENSIONS = Object.freeze(['jpg', 'jpeg', 'png', 'pdf']);
export const ACCEPTED_MIME_TYPES = Object.freeze(['image/jpeg', 'image/png', 'application/pdf']);

// ---------------------------------------------------------------------------
// ชนิดข้อมูล
// ---------------------------------------------------------------------------

export type RuleId =
  | 'BR-01'
  | 'BR-02'
  | 'BR-03'
  | 'BR-04'
  | 'BR-05'
  | 'BR-06'
  | 'BR-08'
  | 'BR-09'
  | 'BR-11'
  | 'BR-12'
  | 'BR-13'
  | 'BR-14';

export type RuleErrorCode =
  | 'batch_size'
  | 'file_too_large'
  | 'file_type'
  | 'pdf_pages'
  | 'queue_full'
  | 'total_invalid'
  | 'urgent_too_large'
  | 'urgent_quota';

/** รายละเอียดของไฟล์ที่ไม่ผ่าน (FR-05: บอกชื่อไฟล์และเหตุผล) */
export interface FileViolation {
  /** ลำดับของไฟล์ในชุด เริ่มที่ 0 (ใช้กับ data-testid `upload-file-error-{ลำดับ}`) */
  index: number;
  name: string;
  error: 'file_too_large' | 'file_type' | 'pdf_pages';
  rule: 'BR-02' | 'BR-03';
  message: string;
}

/**
 * ผลเมื่อผิดกฎ — `status` คือรหัส HTTP ที่ route ควรตอบ
 * ส่วนที่เหลือคือเนื้อหาคำตอบ `{"error","rule","message",...}` (DESIGN 9.2)
 */
export interface RuleViolation {
  ok: false;
  status: 409 | 422 | 429;
  error: RuleErrorCode;
  rule: RuleId;
  message: string;
  /** ชื่อไฟล์ (กรณีผิดที่ไฟล์เดียว) */
  file?: string;
  /** ทุกไฟล์ที่ไม่ผ่านในชุด (BR-02/BR-03) */
  files?: FileViolation[];
  limit?: number;
  /** BR-12 */
  retryAfterMinutes?: number;
  pending?: number;
}

export interface RulePass {
  ok: true;
}

export type RuleResult = RulePass | RuleViolation;

/** ค่าเงินที่รับได้: number (บาท) · string แบบ numeric ของ PostgreSQL · bigint (สตางค์ ไม่รองรับ) */
export type MoneyInput = number | string;

export type FileKind = 'jpg' | 'png' | 'pdf';

export interface UploadFileInput {
  name: string;
  /** ขนาดไฟล์เป็นไบต์ */
  size: number;
  /** ชนิดจริงของไฟล์ ถ้าไม่ส่งจะดูจาก `bytes` แล้วจึงดูจาก `mimeType` / นามสกุล */
  kind?: FileKind | null;
  /** เนื้อไฟล์ (ทั้งไฟล์ หรืออย่างน้อยส่วนหัว) ใช้ตรวจ magic bytes และนับหน้า PDF */
  bytes?: Uint8Array | null;
  mimeType?: string | null;
  /** จำนวนหน้า PDF ที่นับมาแล้ว (ถ้าไม่ส่ง จะนับจาก `bytes`) */
  pdfPages?: number | null;
}

export interface FlagInput {
  totalConfidence: number | string | null | undefined;
  itemPrices: ReadonlyArray<MoneyInput | null | undefined>;
  total: MoneyInput | null | undefined;
}

export interface FlagResult {
  /** BR-04 · ธง "ไม่แน่ใจยอดรวม" */
  lowConfidence: boolean;
  /** BR-05 · ธง "ยอดไม่ตรงรายการ" */
  mismatch: boolean;
  /** ใบติดธง (ธงใดธงหนึ่ง) — ใบเดียวนับเป็น 1 ใบแม้ติด 2 ธง */
  flagged: boolean;
  /** ผลต่างสัมบูรณ์ระหว่างผลรวมรายการกับยอดรวม (สตางค์) */
  diffSatang: number;
  reasons: string[];
}

export type ReceiptStatus = 'queued' | 'processing' | 'review' | 'confirmed' | 'unreadable';
export type BatchPriority = 'normal' | 'urgent';

export interface OverdueInput {
  priority: BatchPriority | string;
  status: ReceiptStatus | string;
  acceptedAt: Date | string | number;
}

export interface QueueCapacityInput {
  /** ใบงานปกติที่ queued + processing ทั้งระบบตอนนี้ */
  pendingNormal: number;
  /** จำนวนใบในชุดใหม่ */
  newCount: number;
  /** ชุดใหม่ตั้งด่วนตอนอัปโหลด (งานด่วนไม่นับในเพดาน) */
  urgent?: boolean;
  /** `system_state.workers_alive` */
  workersAlive?: number | null;
  /** เวลาที่อัปเดต workers_alive ล่าสุด (ถ้าส่งพร้อม `now` จะตรวจความเก่า 30 วินาที) */
  workersUpdatedAt?: Date | string | number | null;
  now?: Date | string | number;
}

export interface MonthBounds {
  month: string;
  /** วันแรกที่นับ (รวมวันนี้) 'YYYY-MM-DD' */
  startDate: string;
  /** วันสุดท้ายที่นับ (รวมวันนี้) 'YYYY-MM-DD' */
  endDate: string;
}

export interface MonthlyReceiptInput {
  status: ReceiptStatus | string;
  /** วันที่บนใบเสร็จ (ค่าที่ยืนยันแล้ว) */
  receiptDate: Date | string | null | undefined;
  total: MoneyInput | null | undefined;
  categoryId?: string | number | null;
}

export interface MonthlySummary {
  month: string;
  count: number;
  totalSatang: number;
  /** ยอดรวมเป็นบาท 2 ตำแหน่ง ไม่มีจุลภาค เช่น "1340.00" */
  total: string;
  byCategory: Record<string, { count: number; totalSatang: number; total: string }>;
}

export interface CreateRulesOptions {
  /** true = โหมดฝึกทดสอบ (DESIGN 9.6) */
  bugMode?: boolean;
}

// ---------------------------------------------------------------------------
// ตัวช่วยที่ไม่ขึ้นกับโหมด
// ---------------------------------------------------------------------------

/**
 * แปลงจำนวนเงินเป็นสตางค์ (จำนวนเต็ม) — คืน null ถ้าอ่านไม่ได้
 * string แยกส่วนจำนวนเต็ม/ทศนิยมเองเพื่อไม่ผ่าน float · รับจุลภาคคั่นหลักพัน
 * ทศนิยมเกิน 2 ตำแหน่งปัดแบบครึ่งขึ้น (ห่างจากศูนย์)
 */
export function toSatang(value: MoneyInput | null | undefined): number | null {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) return null;
    const s = Math.round(Math.abs(value) * 100 + 1e-7);
    return value < 0 ? -s : s;
  }
  const str = String(value).trim().replace(/,/g, '');
  const m = /^([+-]?)(\d*)(?:\.(\d*))?$/.exec(str);
  if (!m || (m[2] === '' && (m[3] === undefined || m[3] === ''))) return null;
  const sign = m[1] === '-' ? -1 : 1;
  const whole = m[2] === '' ? 0 : Number(m[2]);
  const frac = (m[3] ?? '').padEnd(3, '0');
  let cents = Number(frac.slice(0, 2));
  if (Number(frac[2]) >= 5) cents += 1;
  const s = whole * 100 + cents;
  if (!Number.isSafeInteger(s)) return null;
  return s === 0 ? 0 : sign * s;
}

/** สตางค์ → "1340.00" (ไม่มีจุลภาค เหมาะกับ CSV และ API) */
export function satangToBaht(satang: number): string {
  const neg = satang < 0;
  const abs = Math.abs(Math.trunc(satang));
  const whole = Math.floor(abs / 100);
  const cents = abs % 100;
  return `${neg ? '-' : ''}${whole}.${String(cents).padStart(2, '0')}`;
}

/** สตางค์ → "1,340.00" (สำหรับแสดงบนหน้าเว็บ) */
export function formatBaht(satang: number): string {
  const plain = satangToBaht(satang);
  const neg = plain.startsWith('-');
  const [whole, cents] = (neg ? plain.slice(1) : plain).split('.');
  return `${neg ? '-' : ''}${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}.${cents}`;
}

/**
 * ข้อความวันที่/เวลาแบบ ISO 8601 หรือรูปแบบข้อความของ PostgreSQL
 *   '2026-11-01' · '2026-10-31T17:00:00Z' · '2026-10-31 17:00:00+00' · '2026-11-01T00:00:00+07:00'
 * คืน y m d (ตามตัวอักษร) และ ms (ช่วงเวลาจริง) — ข้อความที่ไม่มีเขตเวลาถือเป็นเวลาไทย
 * ไม่พึ่ง `new Date(string)` เพราะผลขึ้นกับ TZ ของเครื่อง
 */
const ISO_RE =
  /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:[.,](\d{1,9}))?)?)?\s*(Z|[+-]\d{2}(?::?\d{2})?)?$/i;

function parseIso(
  value: string,
): { y: number; m: number; d: number; hasTime: boolean; hasZone: boolean; ms: number } | null {
  const r = ISO_RE.exec(value.trim());
  if (!r) return null;
  const y = +r[1];
  const m = +r[2];
  const d = +r[3];
  if (!isValidYmd(y, m, d)) return null;
  const hh = r[4] === undefined ? 0 : +r[4];
  const mi = r[5] === undefined ? 0 : +r[5];
  const ss = r[6] === undefined ? 0 : +r[6];
  const frac = r[7] === undefined ? 0 : Math.floor(Number(`0.${r[7]}`) * 1000);
  if (hh > 24 || mi > 59 || ss > 60 || (hh === 24 && (mi > 0 || ss > 0 || frac > 0))) return null;
  let offsetMs = BANGKOK_OFFSET_MS;
  const zone = r[8];
  if (zone !== undefined) {
    if (zone.toUpperCase() === 'Z') offsetMs = 0;
    else {
      const sign = zone[0] === '-' ? -1 : 1;
      const digits = zone.slice(1).replace(':', '');
      const oh = +digits.slice(0, 2);
      const om = digits.length > 2 ? +digits.slice(2, 4) : 0;
      if (oh > 23 || om > 59) return null;
      offsetMs = sign * (oh * 60 + om) * 60_000;
    }
  }
  const ms = Date.UTC(y, m - 1, d, hh, mi, ss, frac) - offsetMs;
  return { y, m, d, hasTime: r[4] !== undefined, hasZone: zone !== undefined, ms };
}

/** แปลงเป็น Date — ข้อความไม่มีเขตเวลาถือเป็นเวลาไทย (ไม่ขึ้นกับ TZ ของเครื่อง) */
function toDate(value: Date | string | number): Date {
  if (value instanceof Date) return value;
  if (typeof value === 'string') {
    const p = parseIso(value);
    return p ? new Date(p.ms) : new Date(value);
  }
  return new Date(value);
}

/** ส่วนวันที่และเวลาตามเวลาไทยของช่วงเวลาหนึ่ง */
function bangkokParts(at: Date | string | number): { y: number; m: number; d: number } {
  const shifted = new Date(toDate(at).getTime() + BANGKOK_OFFSET_MS);
  return { y: shifted.getUTCFullYear(), m: shifted.getUTCMonth() + 1, d: shifted.getUTCDate() };
}

function pad2(n: number): string {
  return String(n).padStart(2, '0');
}

/** วันปฏิทินไทยของเวลาที่ให้ เช่น '2026-11-19' */
export function bangkokDateKey(at: Date | string | number): string {
  const p = bangkokParts(at);
  return `${p.y}-${pad2(p.m)}-${pad2(p.d)}`;
}

/**
 * ช่วงของวันปฏิทินไทยที่มี `now` อยู่: [start, end) เป็น Date (UTC instant)
 * ใช้กับ SQL เช่น `urgent_set_at >= $start AND urgent_set_at < $end` (BR-09)
 */
export function bangkokDayRange(now: Date | string | number): { start: Date; end: Date } {
  const t = toDate(now).getTime();
  const localMidnight = Math.floor((t + BANGKOK_OFFSET_MS) / DAY_MS) * DAY_MS;
  const start = new Date(localMidnight - BANGKOK_OFFSET_MS);
  return { start, end: new Date(start.getTime() + DAY_MS) };
}

/**
 * วันที่บนใบเสร็จ → 'YYYY-MM-DD' ตามปฏิทินไทย
 * - 'YYYY-MM-DD' ล้วน หรือวันเวลาที่ไม่มีเขตเวลา (ถือเป็นเวลาไทยอยู่แล้ว) → ใช้วันที่ตามตัวอักษร
 * - วันเวลาที่มีเขตเวลา เช่น '2026-10-31T17:00:00Z' → แปลงเป็นเวลาไทยก่อน (= 2026-11-01)
 *   จึงได้ผลเดียวกับ Date ของช่วงเวลาเดียวกัน
 * - Date (เช่นคอลัมน์ `date` ที่ node-postgres แปลงเป็นเที่ยงคืนเวลาเครื่อง) ดูตามปฏิทินไทย
 */
export function toDateKey(value: Date | string | null | undefined): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string') {
    const p = parseIso(value);
    if (p) return p.hasZone ? bangkokDateKey(p.ms) : `${p.y}-${pad2(p.m)}-${pad2(p.d)}`;
    if (!/[a-z]/i.test(value) || /^\s*\d{4}-\d{2}-\d{2}/.test(value)) return null;
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? null : bangkokDateKey(d);
  }
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : bangkokDateKey(value);
  return null;
}

function daysInMonth(y: number, m: number): number {
  return new Date(Date.UTC(y, m, 0)).getUTCDate();
}

function isValidYmd(y: number, m: number, d: number): boolean {
  return m >= 1 && m <= 12 && d >= 1 && d <= daysInMonth(y, m);
}

/** 'YYYY-MM' ถูกรูปแบบหรือไม่ */
export function isValidMonth(month: string): boolean {
  const m = /^(\d{4})-(\d{2})$/.exec(month ?? '');
  return !!m && +m[2] >= 1 && +m[2] <= 12;
}

function isNonNegativeInt(n: unknown): n is number {
  return typeof n === 'number' && Number.isInteger(n) && n >= 0;
}

function extensionOf(name: string): string {
  const i = name.lastIndexOf('.');
  return i < 0 ? '' : name.slice(i + 1).toLowerCase();
}

/** ดูชนิดไฟล์จาก magic bytes — JPG (FF D8 FF) · PNG (89 50 4E 47 0D 0A 1A 0A) · PDF (%PDF-) */
export function detectFileKind(bytes: Uint8Array | null | undefined): FileKind | null {
  if (!bytes || bytes.length < 4) return null;
  if (bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return 'jpg';
  const png = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  if (bytes.length >= 8 && png.every((b, i) => bytes[i] === b)) return 'png';
  // %PDF- อาจมีขยะนำหน้าได้ไม่เกิน 1024 ไบต์ตามที่ตัวอ่าน PDF ทั่วไปยอม
  const head = latin1(bytes.subarray(0, Math.min(bytes.length, 1024 + 5)));
  if (head.includes('%PDF-')) return 'pdf';
  return null;
}

function latin1(bytes: Uint8Array): string {
  let s = '';
  const CHUNK = 0x8000;
  for (let i = 0; i < bytes.length; i += CHUNK) {
    s += String.fromCharCode.apply(null, Array.from(bytes.subarray(i, i + CHUNK)));
  }
  return s;
}

// ---------------------------------------------------------------------------
// BR-03 · อ่านโครงสร้าง PDF เพื่อนับหน้า (ไม่ใช้ไลบรารี ไม่มี I/O)
// ---------------------------------------------------------------------------

/** inflate (RFC 1950/1951) ขนาดเล็ก สำหรับคลาย Object Stream แบบ FlateDecode */
const INFLATE_LEN_BASE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258];
const INFLATE_LEN_EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0];
const INFLATE_DIST_BASE = [
  1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145,
  8193, 12289, 16385, 24577,
];
const INFLATE_DIST_EXTRA = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13];
const INFLATE_CL_ORDER = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];
/** กันไฟล์ระเบิด: ผลคลายของสตรีมหนึ่งไม่เกิน 64 MB */
const INFLATE_MAX_OUTPUT = 64 * 1024 * 1024;

interface Huffman {
  counts: Int32Array;
  symbols: Int32Array;
}

function buildHuffman(lengths: ArrayLike<number>, start: number, n: number): Huffman {
  const counts = new Int32Array(16);
  for (let i = 0; i < n; i++) counts[lengths[start + i]]++;
  counts[0] = 0;
  const offs = new Int32Array(16);
  for (let len = 1; len < 16; len++) offs[len] = offs[len - 1] + counts[len - 1];
  const symbols = new Int32Array(n);
  for (let i = 0; i < n; i++) {
    const len = lengths[start + i];
    if (len !== 0) symbols[offs[len]++] = i;
  }
  return { counts, symbols };
}

export function inflate(input: Uint8Array): Uint8Array | null {
  let pos = 0;
  let bitBuf = 0;
  let bitCnt = 0;
  let out = new Uint8Array(Math.max(1024, input.length * 4));
  let outLen = 0;

  const fail = (): never => {
    throw new Error('inflate');
  };
  const bits = (need: number): number => {
    let val = bitBuf;
    while (bitCnt < need) {
      if (pos >= input.length) fail();
      val |= input[pos++] << bitCnt;
      bitCnt += 8;
    }
    bitBuf = val >>> need;
    bitCnt -= need;
    return val & ((1 << need) - 1);
  };
  const ensure = (extra: number) => {
    if (outLen + extra <= out.length) return;
    if (outLen + extra > INFLATE_MAX_OUTPUT) fail();
    let size = out.length * 2;
    while (size < outLen + extra) size *= 2;
    const next = new Uint8Array(Math.min(size, INFLATE_MAX_OUTPUT));
    next.set(out.subarray(0, outLen));
    out = next;
  };
  const decode = (h: Huffman): number => {
    let code = 0;
    let first = 0;
    let index = 0;
    for (let len = 1; len < 16; len++) {
      code |= bits(1);
      const count = h.counts[len];
      if (code - count < first) return h.symbols[index + (code - first)];
      index += count;
      first += count;
      first <<= 1;
      code <<= 1;
    }
    return fail();
  };
  const codes = (lit: Huffman, dist: Huffman) => {
    for (;;) {
      const sym = decode(lit);
      if (sym < 256) {
        ensure(1);
        out[outLen++] = sym;
      } else if (sym === 256) {
        return;
      } else {
        const li = sym - 257;
        if (li >= 29) fail();
        const len = INFLATE_LEN_BASE[li] + bits(INFLATE_LEN_EXTRA[li]);
        const di = decode(dist);
        if (di >= 30) fail();
        const d = INFLATE_DIST_BASE[di] + bits(INFLATE_DIST_EXTRA[di]);
        if (d > outLen) fail();
        ensure(len);
        for (let i = 0; i < len; i++, outLen++) out[outLen] = out[outLen - d];
      }
    }
  };

  let fixedLit: Huffman | null = null;
  let fixedDist: Huffman | null = null;

  try {
    // ห่อ zlib: CM = 8 และ (CMF·256 + FLG) หาร 31 ลงตัว → ข้าม 2 ไบต์ ไม่เช่นนั้นถือเป็น deflate ดิบ
    if (input.length >= 2 && (input[0] & 0x0f) === 8 && ((input[0] << 8) | input[1]) % 31 === 0) pos = 2;
    let last = 0;
    while (!last) {
      last = bits(1);
      const type = bits(2);
      if (type === 0) {
        bitBuf = 0;
        bitCnt = 0;
        if (pos + 4 > input.length) fail();
        const len = input[pos] | (input[pos + 1] << 8);
        const nlen = input[pos + 2] | (input[pos + 3] << 8);
        pos += 4;
        if (len !== (~nlen & 0xffff) || pos + len > input.length) fail();
        ensure(len);
        out.set(input.subarray(pos, pos + len), outLen);
        outLen += len;
        pos += len;
      } else if (type === 1) {
        if (!fixedLit || !fixedDist) {
          const l = new Array<number>(288);
          for (let i = 0; i < 288; i++) l[i] = i < 144 ? 8 : i < 256 ? 9 : i < 280 ? 7 : 8;
          fixedLit = buildHuffman(l, 0, 288);
          fixedDist = buildHuffman(new Array<number>(30).fill(5), 0, 30);
        }
        codes(fixedLit, fixedDist);
      } else if (type === 2) {
        const nlen = bits(5) + 257;
        const ndist = bits(5) + 1;
        const ncode = bits(4) + 4;
        if (nlen > 286 || ndist > 30) fail();
        const cl = new Array<number>(19).fill(0);
        for (let i = 0; i < ncode; i++) cl[INFLATE_CL_ORDER[i]] = bits(3);
        const clh = buildHuffman(cl, 0, 19);
        const lengths = new Array<number>(nlen + ndist).fill(0);
        for (let i = 0; i < nlen + ndist; ) {
          const sym = decode(clh);
          if (sym < 16) {
            lengths[i++] = sym;
          } else {
            let rep = 0;
            let val = 0;
            if (sym === 16) {
              if (i === 0) fail();
              val = lengths[i - 1];
              rep = 3 + bits(2);
            } else if (sym === 17) rep = 3 + bits(3);
            else rep = 11 + bits(7);
            if (i + rep > nlen + ndist) fail();
            while (rep--) lengths[i++] = val;
          }
        }
        if (lengths[256] === 0) fail();
        codes(buildHuffman(lengths, 0, nlen), buildHuffman(lengths, nlen, ndist));
      } else {
        fail();
      }
    }
    return out.slice(0, outLen);
  } catch {
    return null;
  }
}

interface PdfObject {
  /** ส่วนพจนานุกรม/ค่าของวัตถุ (ไม่รวมเนื้อสตรีม) — ตัดคอมเมนต์ `%...` ออกแล้ว */
  body: string;
  /** เนื้อสตรีมดิบ (ถ้ามี) */
  stream?: Uint8Array;
}

/**
 * แทนคอมเมนต์ PDF (`%` ถึงท้ายบรรทัด) ด้วยช่องว่าง 1 ตัว ตาม ISO 32000 7.2.3 คอมเมนต์ถือเป็นช่องว่าง
 * เช่น `/Type % c\n/Page` = `/Type /Page` · ไม่แตะ `%` ที่อยู่ในสตริง `( )` หรือ hex `< >`
 */
export function stripPdfComments(body: string): string {
  if (!body.includes('%')) return body;
  let out = '';
  let paren = 0;
  let hex = false;
  for (let i = 0; i < body.length; i++) {
    const c = body[i];
    if (paren > 0) {
      out += c;
      if (c === '\\') {
        if (i + 1 < body.length) out += body[++i];
      } else if (c === '(') paren++;
      else if (c === ')') paren--;
    } else if (hex) {
      out += c;
      if (c === '>') hex = false;
    } else if (c === '(') {
      paren = 1;
      out += c;
    } else if (c === '<') {
      if (body[i + 1] === '<') {
        out += '<<';
        i++;
      } else {
        hex = true;
        out += c;
      }
    } else if (c === '%') {
      while (i + 1 < body.length && body[i + 1] !== '\n' && body[i + 1] !== '\r') i++;
      out += ' ';
    } else {
      out += c;
    }
  }
  return out;
}

const PDF_DELIMS = '()<>[]{}/%';

/** ตำแหน่ง i อยู่ต้นโทเคน (ตัวก่อนหน้าเป็นช่องว่าง/ตัวคั่น หรือต้นข้อความ) */
function atTokenStart(text: string, i: number): boolean {
  if (i === 0) return true;
  const c = text[i - 1];
  return /\s/.test(c) || c === '\0' || PDF_DELIMS.includes(c);
}

/** ตำแหน่ง i อยู่ท้ายโทเคน (ตัวถัดไปเป็นช่องว่าง/ตัวคั่น หรือท้ายข้อความ) */
function atTokenEnd(text: string, i: number): boolean {
  if (i >= text.length) return true;
  const c = text[i];
  return /\s/.test(c) || c === '\0' || PDF_DELIMS.includes(c);
}

/**
 * หาคีย์เวิร์ด `stream` หรือ `endobj` ตัวแรกหลัง start ที่เป็นโทเคนจริง
 * โดยข้ามคอมเมนต์ `%...` สตริง `( )` และ hex `< >` (เช่น `/Type % endobj\n/Page` ไม่ใช่จุดจบวัตถุ)
 * คืน null ถ้าไม่พบ
 */
function findObjectEnd(
  text: string,
  start: number,
): { kind: 'stream'; at: number; dataStart: number } | { kind: 'endobj'; at: number } | null {
  for (let i = start; i < text.length; i++) {
    const c = text[i];
    if (c === '%') {
      while (i + 1 < text.length && text[i + 1] !== '\n' && text[i + 1] !== '\r') i++;
    } else if (c === '(') {
      let depth = 1;
      while (depth > 0 && ++i < text.length) {
        const d = text[i];
        if (d === '\\') i++;
        else if (d === '(') depth++;
        else if (d === ')') depth--;
      }
    } else if (c === '<') {
      if (text[i + 1] === '<') i++;
      else {
        const close = text.indexOf('>', i + 1);
        if (close < 0) return null;
        i = close;
      }
    } else if (c === 'e' && text.startsWith('endobj', i) && atTokenStart(text, i) && atTokenEnd(text, i + 6)) {
      return { kind: 'endobj', at: i };
    } else if (c === 's' && text.startsWith('stream', i) && atTokenStart(text, i)) {
      const eol = /^stream(\r\n|\n|\r)/.exec(text.slice(i, i + 8));
      if (eol) return { kind: 'stream', at: i, dataStart: i + eol[0].length };
    }
  }
  return null;
}

/** หัววัตถุ `n g obj` ที่พบอยู่หลัง `%` บนบรรทัดเดียวกัน (อยู่ในคอมเมนต์ ไม่ใช่วัตถุจริง) */
function inLineComment(text: string, at: number): boolean {
  const lineStart = Math.max(text.lastIndexOf('\n', at - 1), text.lastIndexOf('\r', at - 1)) + 1;
  return text.slice(lineStart, at).includes('%');
}

/** อ่านวัตถุ `n g obj ... endobj` ทั้งหมด (ตัวหลังทับตัวก่อนตามการแก้ไขแบบต่อท้าย) */
function scanPdfObjects(bytes: Uint8Array, text: string): Map<number, PdfObject> {
  const objects = new Map<number, PdfObject>();
  const objRe = /(\d+)\s+(\d+)\s+obj\b/g;
  let m: RegExpExecArray | null;
  while ((m = objRe.exec(text))) {
    if (!atTokenStart(text, m.index) || inLineComment(text, m.index)) continue;
    const num = Number(m[1]);
    const start = m.index + m[0].length;
    const end = findObjectEnd(text, start);
    if (!end) break;
    if (end.kind === 'stream') {
      const body = stripPdfComments(text.slice(start, end.at));
      const dataStart = end.dataStart;
      // ใช้ /Length ตรง ๆ ถ้าชี้ไปหน้า endstream พอดี ไม่เช่นนั้นหา endstream ถัดไป
      let dataEnd = -1;
      const len = /\/Length\s+(\d+)(?!\s+\d+\s+R)/.exec(body);
      if (len) {
        const e = dataStart + Number(len[1]);
        if (/^\s*endstream/.test(text.slice(e, e + 32))) dataEnd = e;
      }
      if (dataEnd < 0) {
        dataEnd = text.indexOf('endstream', dataStart);
        if (dataEnd < 0) break;
      }
      objects.set(num, { body, stream: bytes.subarray(dataStart, dataEnd) });
      const after = findObjectEnd(text, dataEnd + 'endstream'.length);
      objRe.lastIndex = after && after.kind === 'endobj' ? after.at + 6 : dataEnd + 'endstream'.length;
    } else {
      objects.set(num, { body: stripPdfComments(text.slice(start, end.at)) });
      objRe.lastIndex = end.at + 6;
    }
  }
  return objects;
}

/** เนื้อสตรีมหลังถอด filter (รองรับไม่มี filter และ FlateDecode ที่ไม่มี predictor) */
function decodePdfStream(obj: PdfObject): Uint8Array | null {
  if (!obj.stream) return null;
  const f = /\/Filter\s*(\[[^\]]*\]|\/[A-Za-z0-9]+)/.exec(obj.body);
  const filters = f ? f[1].match(/\/[A-Za-z0-9]+/g) ?? [] : [];
  if (/\/Predictor\s+(\d+)/.test(obj.body) && !/\/Predictor\s+1\b/.test(obj.body)) return null;
  let data: Uint8Array | null = obj.stream;
  for (const name of filters) {
    if (name !== '/FlateDecode' && name !== '/Fl') return null;
    data = inflate(data);
    if (!data) return null;
  }
  return data;
}

/** แตกวัตถุใน Object Stream (PDF 1.5+) เพิ่มเข้าตาราง ถ้าเลขนั้นยังไม่มี */
function expandObjectStreams(objects: Map<number, PdfObject>): void {
  for (const obj of Array.from(objects.values())) {
    if (!/\/Type\s*\/ObjStm\b/.test(obj.body)) continue;
    const n = /\/N\s+(\d+)/.exec(obj.body);
    const first = /\/First\s+(\d+)/.exec(obj.body);
    const data = decodePdfStream(obj);
    if (!n || !first || !data) continue;
    const text = latin1(data);
    const header = text.slice(0, Number(first[1])).trim().split(/\s+/).map(Number);
    const count = Math.min(Number(n[1]), Math.floor(header.length / 2));
    for (let i = 0; i < count; i++) {
      const num = header[2 * i];
      const off = Number(first[1]) + header[2 * i + 1];
      const next = i + 1 < count ? Number(first[1]) + header[2 * i + 3] : text.length;
      if (!Number.isInteger(num) || !(off >= 0) || next < off) continue;
      if (!objects.has(num)) objects.set(num, { body: stripPdfComments(text.slice(off, next)) });
    }
  }
}

const PDF_REF = /(\d+)\s+(\d+)\s+R\b/;

function refOf(body: string, key: string): number | null {
  const r = new RegExp(`/${key}\\s+(\\d+)\\s+\\d+\\s+R\\b`).exec(body);
  return r ? Number(r[1]) : null;
}

/** ค่าของคีย์ /Type ระดับบนสุดของพจนานุกรม (ข้ามพจนานุกรมซ้อน) */
function topLevelType(body: string): string | null {
  let depth = 0;
  for (let i = 0; i < body.length; i++) {
    if (body.startsWith('<<', i)) {
      depth++;
      i++;
    } else if (body.startsWith('>>', i)) {
      depth--;
      i++;
    } else if (depth === 1 && body.startsWith('/Type', i)) {
      const t = /^\/Type\s*\/([A-Za-z]+)/.exec(body.slice(i, i + 40));
      if (t) return t[1];
    }
  }
  return null;
}

/**
 * พจนานุกรม `<< ... >>` ตัวแรกหลังตำแหน่ง from (นับ `<<`/`>>` ซ้อน ข้ามคอมเมนต์ สตริง `( )` และ hex `< >`)
 * คืน null ถ้าไม่พบหรือไม่ปิด
 */
function dictAfter(text: string, from: number): string | null {
  let i = from;
  for (; i < text.length; i++) {
    const c = text[i];
    if (c === '%') {
      while (i + 1 < text.length && text[i + 1] !== '\n' && text[i + 1] !== '\r') i++;
    } else if (c === '<' && text[i + 1] === '<') break;
    else if (!/\s/.test(c) && c !== '\0') return null;
  }
  if (i >= text.length) return null;
  const start = i;
  let depth = 0;
  for (; i < text.length; i++) {
    const c = text[i];
    if (c === '%') {
      while (i + 1 < text.length && text[i + 1] !== '\n' && text[i + 1] !== '\r') i++;
    } else if (c === '(') {
      let p = 1;
      while (p > 0 && ++i < text.length) {
        const d = text[i];
        if (d === '\\') i++;
        else if (d === '(') p++;
        else if (d === ')') p--;
      }
    } else if (c === '<' && text[i + 1] === '<') {
      depth++;
      i++;
    } else if (c === '>' && text[i + 1] === '>') {
      depth--;
      i++;
      if (depth === 0) return text.slice(start, i + 1);
    } else if (c === '<') {
      const close = text.indexOf('>', i + 1);
      if (close < 0) return null;
      i = close;
    }
  }
  return null;
}

/** ลบเนื้อสตริง `( )` และ hex `< >` ออก (คงตัวคั่นไว้) เพื่อไม่ให้ข้อความในสตริงถูกอ่านเป็นคีย์ */
function blankPdfStrings(body: string): string {
  let out = '';
  for (let i = 0; i < body.length; i++) {
    const c = body[i];
    if (c === '(') {
      let p = 1;
      while (p > 0 && ++i < body.length) {
        const d = body[i];
        if (d === '\\') i++;
        else if (d === '(') p++;
        else if (d === ')') p--;
      }
      out += '()';
    } else if (c === '<' && body[i + 1] === '<') {
      out += '<<';
      i++;
    } else if (c === '<') {
      const close = body.indexOf('>', i + 1);
      i = close < 0 ? body.length : close;
      out += '<>';
    } else out += c;
  }
  return out;
}

/** พจนานุกรมระบุว่าไฟล์เข้ารหัส: มีคีย์ /Encrypt (อ้างวัตถุหรือพจนานุกรมตรง) นอกคอมเมนต์และสตริง */
function dictHasEncrypt(dict: string): boolean {
  return /\/Encrypt(?![A-Za-z0-9])\s*(\d+\s+\d+\s+R\b|<<)/.test(blankPdfStrings(stripPdfComments(dict)));
}

/**
 * ไฟล์ PDF เข้ารหัสหรือไม่ — ดูเฉพาะคีย์ /Encrypt ใน trailer จริง (คำ `trailer` ที่ไม่อยู่ในคอมเมนต์)
 * และใน XRef stream (`/Type /XRef`) · คำว่า /Encrypt ในคอมเมนต์ (เช่น `/Type % /Encrypt 9 0 R\n/Page`)
 * ในสตริง หรือในวัตถุอื่นไม่นับ
 */
function isEncryptedPdf(text: string, objects: Map<number, PdfObject>): boolean {
  const re = /trailer/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    if (!atTokenStart(text, m.index) || !atTokenEnd(text, m.index + 7) || inLineComment(text, m.index)) continue;
    const dict = dictAfter(text, m.index + 7);
    if (dict && dictHasEncrypt(dict)) return true;
  }
  for (const o of objects.values()) {
    if (topLevelType(o.body) !== 'XRef') continue;
    const dict = dictAfter(o.body, 0);
    if (dict && dictHasEncrypt(dict)) return true;
  }
  return false;
}

export interface PdfInspection {
  /** โครงสร้างครบพอให้โปรแกรมอ่าน PDF เปิดได้ */
  openable: boolean;
  /** จำนวนหน้าจริงจากต้นไม้หน้า (0 ถ้าเปิดไม่ได้) */
  pages: number;
  reason?: string;
}

/**
 * ตรวจ PDF โดยเดินต้นไม้หน้าจริง: /Root (Catalog) → /Pages → /Kids → ใบ /Page
 * เปิดไม่ได้ (pages = 0) เมื่อ: ไม่ใช่ PDF · ไม่มี %%EOF · ไม่มีวัตถุ · หา Catalog ไม่พบ
 * · /Pages หรือ /Kids อ้างวัตถุที่ไม่มี · ต้นไม้วนซ้ำ · ไม่มีหน้าเลย
 * · โหนดใน /Kids ที่ไม่ใช่ /Type /Pages หรือ /Type /Page (เช่นวัตถุว่าง `<< >>`)
 * ไฟล์ที่มีแค่หัว PDF กับ `/Count 1` และ `%%EOF` จึงไม่ผ่าน
 * รองรับ Object Stream แบบ FlateDecode (PDF 1.5+) · ไฟล์เข้ารหัสหรือ filter อื่นถือว่าเปิดไม่ได้
 */
export function inspectPdf(bytes: Uint8Array | null | undefined): PdfInspection {
  const broken = (reason: string): PdfInspection => ({ openable: false, pages: 0, reason });
  if (!bytes || detectFileKind(bytes) !== 'pdf') return broken('not_pdf');
  const text = latin1(bytes);
  if (!text.includes('%%EOF')) return broken('no_eof');

  const objects = scanPdfObjects(bytes, text);
  if (objects.size === 0) return broken('no_objects');
  if (isEncryptedPdf(text, objects)) return broken('encrypted');
  expandObjectStreams(objects);

  // Catalog: จาก /Root ของ trailer หรือ XRef stream (ตัวท้ายสุด) ไม่เช่นนั้นวัตถุ /Type /Catalog
  let catalog: PdfObject | undefined;
  const roots = Array.from(text.matchAll(/\/Root\s+(\d+)\s+\d+\s+R\b/g));
  for (let i = roots.length - 1; i >= 0 && !catalog; i--) {
    const o = objects.get(Number(roots[i][1]));
    if (o && topLevelType(o.body) === 'Catalog') catalog = o;
  }
  if (!catalog) {
    for (const o of objects.values()) if (topLevelType(o.body) === 'Catalog') catalog = o;
  }
  if (!catalog) return broken('no_catalog');

  const rootPages = refOf(catalog.body, 'Pages');
  if (rootPages === null) return broken('no_page_tree');

  let pages = 0;
  const seen = new Set<number>();
  const walk = (num: number, depth: number): string | null => {
    if (seen.has(num) || depth > 64) return 'page_tree_cycle';
    seen.add(num);
    const node = objects.get(num);
    if (!node) return 'missing_object';
    if (!node.body.includes('<<')) return 'bad_page_node';
    const type = topLevelType(node.body);
    if (type === 'Pages') {
      let kidsText: string | null = null;
      const arr = /\/Kids\s*\[([^\]]*)\]/.exec(node.body);
      if (arr) kidsText = arr[1];
      else {
        const ref = refOf(node.body, 'Kids');
        const kidsObj = ref === null ? undefined : objects.get(ref);
        const inner = kidsObj ? /\[([^\]]*)\]/.exec(kidsObj.body) : null;
        if (inner) kidsText = inner[1];
      }
      if (kidsText === null) return 'missing_kids';
      const re = new RegExp(PDF_REF.source, 'g');
      let k: RegExpExecArray | null;
      while ((k = re.exec(kidsText))) {
        const err = walk(Number(k[1]), depth + 1);
        if (err) return err;
      }
      return null;
    }
    // ใบของต้นไม้ต้องเป็นพจนานุกรม /Type /Page จริง (ISO 32000 7.7.3.3) — วัตถุว่าง `<< >>`
    // หรือพจนานุกรมที่ไม่ระบุชนิด ไม่นับเป็นหน้า และทำให้ไฟล์ถือว่าเปิดไม่ได้
    if (type === 'Page') {
      pages++;
      return null;
    }
    return type === null ? 'empty_page_object' : 'bad_page_node';
  };
  const err = walk(rootPages, 0);
  if (err) return broken(err);
  if (pages === 0) return broken('no_pages');
  return { openable: true, pages };
}

/**
 * นับหน้า PDF จากเนื้อไฟล์แบบไม่ต้องใช้ไลบรารี — ไฟล์เสีย/เปิดไม่ได้ → 0
 * route ที่มีไลบรารี PDF จริงจะนับเองแล้วส่ง `pdfPages` มาก็ได้
 */
export function countPdfPages(bytes: Uint8Array | null | undefined): number {
  return inspectPdf(bytes).pages;
}

/** ชนิดไฟล์ที่ใช้ตัดสิน BR-03: kind ที่ส่งมา → magic bytes → MIME → นามสกุล */
export function resolveFileKind(file: UploadFileInput): FileKind | null {
  if (file.kind) return file.kind;
  if (file.bytes && file.bytes.length > 0) return detectFileKind(file.bytes);
  const mime = (file.mimeType ?? '').toLowerCase();
  if (mime === 'image/jpeg' || mime === 'image/jpg') return 'jpg';
  if (mime === 'image/png') return 'png';
  if (mime === 'application/pdf') return 'pdf';
  if (mime) return null;
  const ext = extensionOf(file.name);
  if (ext === 'jpg' || ext === 'jpeg') return 'jpg';
  if (ext === 'png') return 'png';
  if (ext === 'pdf') return 'pdf';
  return null;
}

// ---------------------------------------------------------------------------
// แบบจำลองอ้างอิงของกฎฝั่ง AI (BR-07 · BR-10) — ไม่ขึ้นกับ BUG_MODE
// ---------------------------------------------------------------------------

export interface ReadAttemptOutcome {
  /** จำนวนครั้งที่อ่านจริง (1–3) */
  attempts: number;
  /** review = ได้ผล รอตรวจ · unreadable = อ่านไม่ได้ ไป Dead-letter Queue */
  status: 'review' | 'unreadable';
}

/**
 * BR-07 · ใบหนึ่งอ่านได้ไม่เกิน 3 ครั้ง
 * `failuresBeforeSuccess` = จำนวนครั้งที่ล้มเหลวก่อนสำเร็จ (Infinity หรือ ≥ 3 = ล้มเหลวทุกครั้ง)
 * ล้มเหลว 2 ครั้ง (ต่ำกว่าเส้น) ได้อ่านครั้งที่ 3 · ล้มเหลวครบ 3 → อ่านไม่ได้ ไม่มีครั้งที่ 4
 */
export function readAttemptOutcome(failuresBeforeSuccess: number): ReadAttemptOutcome {
  const f = Number.isNaN(failuresBeforeSuccess) ? Infinity : Math.max(0, Math.floor(failuresBeforeSuccess));
  if (f >= LIMITS.MAX_READ_ATTEMPTS) return { attempts: LIMITS.MAX_READ_ATTEMPTS, status: 'unreadable' };
  return { attempts: f + 1, status: 'review' };
}

/** BR-07 · ล้มเหลวมาแล้ว `attemptsSoFar` ครั้ง ยังอ่านได้อีกหรือไม่ */
export function canRetryRead(attemptsSoFar: number): boolean {
  return Math.max(0, Math.floor(attemptsSoFar)) < LIMITS.MAX_READ_ATTEMPTS;
}

/**
 * BR-10 · เลือกคิวของใบถัดไป: ด่วนก่อน แต่ถ้าอ่านด่วนติดกันครบ 4 ใบแล้วและมีใบปกติรอ ต้องอ่านปกติ 1 ใบ
 * `urgentStreak` = จำนวนใบด่วนที่อ่านติดกันล่าสุด (รีเซ็ตเป็น 0 เมื่ออ่านใบปกติ)
 */
export function nextQueue(
  urgentWaiting: number,
  normalWaiting: number,
  urgentStreak: number,
): 'urgent' | 'normal' | 'none' {
  const u = Math.max(0, Math.floor(urgentWaiting));
  const n = Math.max(0, Math.floor(normalWaiting));
  if (u === 0) return n > 0 ? 'normal' : 'none';
  if (n > 0 && urgentStreak >= LIMITS.MAX_URGENT_STREAK) return 'normal';
  return 'urgent';
}

/**
 * BR-10 · ลำดับการอ่านของ Worker 1 ตัวเมื่อใส่งานครบก่อนเริ่ม (TEST-DATA หัวข้อ 6 BR-10)
 * คืนรายการเช่น ['U1','U2','U3','U4','N1','U5','N2']
 */
export function planReadOrder(urgentCount: number, normalCount: number): string[] {
  let u = Math.max(0, Math.floor(urgentCount));
  let n = Math.max(0, Math.floor(normalCount));
  let streak = 0;
  let ui = 0;
  let ni = 0;
  const order: string[] = [];
  for (;;) {
    const q = nextQueue(u, n, streak);
    if (q === 'none') return order;
    if (q === 'urgent') {
      order.push(`U${++ui}`);
      u--;
      streak++;
    } else {
      order.push(`N${++ni}`);
      n--;
      streak = 0;
    }
  }
}

// ---------------------------------------------------------------------------
// โรงงานชุดกฎ
// ---------------------------------------------------------------------------

export function createRules(options: CreateRulesOptions = {}) {
  const bug = options.bugMode === true;

  const pass: RulePass = Object.freeze({ ok: true }) as RulePass;

  // ----- BR-01 · ชุดละ 1–100 ไฟล์ -------------------------------------------
  function checkBatchSize(fileCount: number): RuleResult {
    if (isNonNegativeInt(fileCount) && fileCount >= LIMITS.BATCH_MIN_FILES && fileCount <= LIMITS.BATCH_MAX_FILES) {
      return pass;
    }
    return {
      ok: false,
      status: 422,
      error: 'batch_size',
      rule: 'BR-01',
      message:
        fileCount === 0
          ? 'กรุณาเลือกไฟล์อย่างน้อย 1 ไฟล์'
          : `อัปโหลดได้ชุดละ ${LIMITS.BATCH_MIN_FILES}–${LIMITS.BATCH_MAX_FILES} ไฟล์ (ชุดนี้มี ${fileCount} ไฟล์) กรุณาแบ่งเป็นหลายชุด`,
      limit: LIMITS.BATCH_MAX_FILES,
    };
  }

  // ----- BR-02 · ไฟล์ไม่เกิน 10.00 MB ---------------------------------------
  function isFileSizeOk(bytes: number): boolean {
    return isNonNegativeInt(bytes) && bytes <= LIMITS.MAX_FILE_BYTES;
  }

  function checkFileSize(name: string, bytes: number): RuleResult {
    if (isFileSizeOk(bytes)) return pass;
    return {
      ok: false,
      status: 422,
      error: 'file_too_large',
      rule: 'BR-02',
      message: `ไฟล์ ${name} มีขนาดเกิน 10.00 MB`,
      file: name,
      limit: LIMITS.MAX_FILE_BYTES,
    };
  }

  // ----- BR-03 · JPG · PNG · PDF 1 หน้า -------------------------------------
  function isPdfPageCountOk(pages: number | null | undefined): boolean {
    return pages === LIMITS.PDF_PAGES;
  }

  function checkFileType(file: UploadFileInput): RuleResult {
    const kind = resolveFileKind(file);
    if (kind === null) {
      return {
        ok: false,
        status: 422,
        error: 'file_type',
        rule: 'BR-03',
        message: `ไฟล์ ${file.name} ไม่ใช่ชนิดที่รับ (รับเฉพาะ JPG · PNG · PDF 1 หน้า)`,
        file: file.name,
      };
    }
    if (kind === 'pdf') {
      const pages =
        typeof file.pdfPages === 'number' ? file.pdfPages : file.bytes ? countPdfPages(file.bytes) : null;
      if (!isPdfPageCountOk(pages)) {
        return {
          ok: false,
          status: 422,
          error: 'pdf_pages',
          rule: 'BR-03',
          message:
            !pages
              ? `ไฟล์ ${file.name} เปิดไม่ได้หรือไม่มีหน้า (PDF ต้องมี 1 หน้าพอดี)`
              : `ไฟล์ ${file.name} มี ${pages} หน้า (PDF ต้องมี 1 หน้าพอดี)`,
          file: file.name,
          limit: LIMITS.PDF_PAGES,
        };
      }
    }
    return pass;
  }

  /** ตรวจไฟล์เดียวตาม BR-02 แล้ว BR-03 */
  function checkFile(file: UploadFileInput): RuleResult {
    const size = checkFileSize(file.name, file.size);
    if (!size.ok) return size;
    return checkFileType(file);
  }

  /**
   * ตรวจชุดอัปโหลดตาม BR-01 · BR-02 · BR-03 (ยังไม่รวม BR-11 ซึ่งต้องนับคิวในธุรกรรม)
   * ไฟล์ใดไม่ผ่าน ทั้งชุดไม่ถูกรับ และคืนรายชื่อไฟล์ที่ไม่ผ่านทุกไฟล์ใน `files`
   * ค่า `error`/`rule` ระดับบนเป็นของไฟล์แรกที่ไม่ผ่าน
   */
  function validateUpload(files: ReadonlyArray<UploadFileInput>): RuleResult {
    const size = checkBatchSize(files.length);
    if (!size.ok) return size;
    const violations: FileViolation[] = [];
    files.forEach((f, index) => {
      const r = checkFile(f);
      if (!r.ok) {
        violations.push({
          index,
          name: f.name,
          error: r.error as FileViolation['error'],
          rule: r.rule as FileViolation['rule'],
          message: r.message,
        });
      }
    });
    if (violations.length === 0) return pass;
    const first = violations[0];
    return {
      ok: false,
      status: 422,
      error: first.error,
      rule: first.rule,
      message:
        violations.length === 1
          ? `${first.message} · ชุดนี้ยังไม่ถูกรับ กรุณาเอาไฟล์นี้ออกแล้วส่งใหม่`
          : `มี ${violations.length} ไฟล์ที่ไม่ผ่าน · ชุดนี้ยังไม่ถูกรับ กรุณาเอาไฟล์เหล่านั้นออกแล้วส่งใหม่`,
      file: first.name,
      files: violations,
    };
  }

  // ----- BR-04 · ความมั่นใจของยอดรวมต่ำกว่า 0.90 → ติดธง ---------------------
  /** ไม่ปัดก่อนเทียบ (0.8999 ติดธง) · ไม่มีค่า/อ่านไม่ได้ ถือว่าไม่แน่ใจ */
  function isLowConfidence(totalConfidence: number | string | null | undefined): boolean {
    if (totalConfidence === null || totalConfidence === undefined || totalConfidence === '') return true;
    const c = typeof totalConfidence === 'number' ? totalConfidence : Number(totalConfidence);
    if (!Number.isFinite(c)) return true;
    return c < LIMITS.MIN_TOTAL_CONFIDENCE;
  }

  // ----- BR-05 · ผลรวมรายการต่างจากยอดรวมเกิน 1.00 บาท → ติดธง ----------------
  /** ผลต่างสัมบูรณ์ (สตางค์) ระหว่างผลรวมราคารายการกับยอดรวม · ค่าที่อ่านไม่ได้นับเป็น 0 */
  function itemsDiffSatang(
    itemPrices: ReadonlyArray<MoneyInput | null | undefined>,
    total: MoneyInput | null | undefined,
  ): number {
    let sum = 0;
    for (const p of itemPrices ?? []) sum += toSatang(p) ?? 0;
    return Math.abs(sum - (toSatang(total) ?? 0));
  }

  function isMismatch(
    itemPrices: ReadonlyArray<MoneyInput | null | undefined>,
    total: MoneyInput | null | undefined,
  ): boolean {
    let diff = itemsDiffSatang(itemPrices, total);
    if (bug) diff -= diff % 100;
    return diff > LIMITS.MAX_ITEMS_DIFF_SATANG;
  }

  /** ธงของใบหนึ่งใบ (BR-04 + BR-05) */
  function computeFlags(input: FlagInput): FlagResult {
    const lowConfidence = isLowConfidence(input.totalConfidence);
    const mismatch = isMismatch(input.itemPrices, input.total);
    const diffSatang = itemsDiffSatang(input.itemPrices, input.total);
    const reasons: string[] = [];
    if (lowConfidence) reasons.push('ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90');
    if (mismatch) {
      reasons.push(`ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม ${formatBaht(diffSatang)} บาท (เกิน 1.00 บาท)`);
    }
    return { lowConfidence, mismatch, flagged: lowConfidence || mismatch, diffSatang, reasons };
  }

  // ----- BR-06 · ยืนยันได้เมื่อยอดรวมตั้งแต่ 0.01 บาท -----------------------
  function isConfirmableTotal(total: MoneyInput | null | undefined): boolean {
    const s = toSatang(total);
    return s !== null && s >= LIMITS.MIN_CONFIRM_TOTAL_SATANG;
  }

  function checkConfirmTotal(total: MoneyInput | null | undefined): RuleResult {
    if (isConfirmableTotal(total)) return pass;
    return {
      ok: false,
      status: 422,
      error: 'total_invalid',
      rule: 'BR-06',
      message: 'ยืนยันไม่ได้: ยอดรวมต้องตั้งแต่ 0.01 บาทขึ้นไป',
    };
  }

  // ----- BR-08 · งานด่วนไม่เกิน 10 ใบ ---------------------------------------
  function checkUrgentSize(receiptCount: number): RuleResult {
    if (isNonNegativeInt(receiptCount) && receiptCount <= LIMITS.URGENT_MAX_RECEIPTS) return pass;
    return {
      ok: false,
      status: 422,
      error: 'urgent_too_large',
      rule: 'BR-08',
      message: `งานด่วนมีได้ไม่เกิน ${LIMITS.URGENT_MAX_RECEIPTS} ใบ (ชุดนี้มี ${receiptCount} ใบ) กรุณาแยกใบที่ด่วนออกเป็นชุดใหม่`,
      limit: LIMITS.URGENT_MAX_RECEIPTS,
    };
  }

  // ----- BR-09 · งานด่วนไม่เกิน 5 งานต่อวันปฏิทิน (เวลาไทย) -------------------
  /** นับงานที่ตั้งด่วนในวันปฏิทินไทยเดียวกับ `now` จากรายการ `urgent_set_at` */
  function countUrgentToday(
    urgentSetAts: ReadonlyArray<Date | string | number | null | undefined>,
    now: Date | string | number,
  ): number {
    const { start, end } = bangkokDayRange(now);
    let n = 0;
    for (const at of urgentSetAts) {
      if (at === null || at === undefined) continue;
      const t = toDate(at).getTime();
      if (t >= start.getTime() && t < end.getTime()) n++;
    }
    return n;
  }

  /** `usedToday` = งานด่วนที่ตั้งไปแล้วในวันนี้ (เวลาไทย) ก่อนงานที่กำลังขอ */
  function canSetUrgent(usedToday: number): boolean {
    const used = Math.max(0, Math.trunc(Number(usedToday) || 0));
    return bug ? !(used > LIMITS.URGENT_MAX_PER_DAY) : used < LIMITS.URGENT_MAX_PER_DAY;
  }

  function checkUrgentQuota(usedToday: number): RuleResult {
    if (canSetUrgent(usedToday)) return pass;
    return {
      ok: false,
      status: 409,
      error: 'urgent_quota',
      rule: 'BR-09',
      message: `วันนี้ตั้งงานด่วนครบ ${LIMITS.URGENT_MAX_PER_DAY} งานแล้ว ตั้งเพิ่มได้อีกครั้งพรุ่งนี้ (เวลาไทย)`,
      limit: LIMITS.URGENT_MAX_PER_DAY,
    };
  }

  /** ตรวจการตั้งด่วนทั้ง BR-08 และ BR-09 */
  function checkUrgent(receiptCount: number, usedToday: number): RuleResult {
    const size = checkUrgentSize(receiptCount);
    if (!size.ok) return size;
    return checkUrgentQuota(usedToday);
  }

  // ----- BR-12 · นาทีที่ให้ลองใหม่ -------------------------------------------
  /**
   * จำนวน Worker ที่ใช้คิดอัตรา: 0 · ไม่ทราบ · ไม่ใช่จำนวนเต็มบวก
   * หรือค่าเก่ากว่า 30 วินาที (เมื่อส่ง updatedAt + now) → ใช้ 1 ตัว
   */
  function effectiveWorkers(
    workersAlive: number | null | undefined,
    updatedAt?: Date | string | number | null,
    now?: Date | string | number,
  ): number {
    const w = typeof workersAlive === 'number' ? Math.floor(workersAlive) : NaN;
    if (!Number.isFinite(w) || w < 1) return 1;
    if (updatedAt !== undefined && now !== undefined) {
      if (updatedAt === null) return 1;
      const age = toDate(now).getTime() - toDate(updatedAt).getTime();
      if (!Number.isFinite(age) || age > LIMITS.WORKERS_STALE_MS) return 1;
    }
    return w;
  }

  /**
   * N = ปัดขึ้น((ค้าง + ใหม่ − 400) ÷ (4 × จำนวน Worker)) อย่างน้อย 1
   * ใช้จำนวนเต็มล้วน ไม่มีปัญหา float
   */
  function retryAfterMinutes(pendingNormal: number, newCount: number, workers: number | null | undefined): number {
    const excess = Math.max(0, Math.trunc(pendingNormal) + Math.trunc(newCount) - LIMITS.NORMAL_QUEUE_CAP);
    const rate = LIMITS.READS_PER_MINUTE_PER_WORKER * effectiveWorkers(workers);
    const n = Math.floor((excess + rate - 1) / rate);
    return Math.max(1, n);
  }

  function queueFullMessage(minutes: number): string {
    return `ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก ${minutes} นาที`;
  }

  // ----- BR-11 · ใบงานปกติค้าง + ชุดใหม่ ไม่เกิน 400 --------------------------
  function hasQueueRoom(pendingNormal: number, newCount: number, urgent = false): boolean {
    if (urgent) return true;
    return Math.trunc(pendingNormal) + Math.trunc(newCount) <= LIMITS.NORMAL_QUEUE_CAP;
  }

  function checkQueueCapacity(input: QueueCapacityInput): RuleResult {
    if (hasQueueRoom(input.pendingNormal, input.newCount, input.urgent === true)) return pass;
    const workers = effectiveWorkers(input.workersAlive, input.workersUpdatedAt, input.now);
    const minutes = retryAfterMinutes(input.pendingNormal, input.newCount, workers);
    return {
      ok: false,
      status: 429,
      error: 'queue_full',
      rule: 'BR-11',
      message: queueFullMessage(minutes),
      retryAfterMinutes: minutes,
      pending: input.pendingNormal,
      limit: LIMITS.NORMAL_QUEUE_CAP,
    };
  }

  // ----- BR-13 · งานปกติค้างเกิน 120 นาที -----------------------------------
  /** นาทีเต็มที่ผ่านไปนับจากรับแล้ว (ปัดลง · ไม่ติดลบ) */
  function minutesWaiting(acceptedAt: Date | string | number, now: Date | string | number): number {
    return Math.floor(msWaiting(acceptedAt, now) / 60_000);
  }

  /** มิลลิวินาทีที่รอมาแล้วนับจากรับแล้ว (ไม่ติดลบ · ค่าเสียเป็น 0) */
  function msWaiting(acceptedAt: Date | string | number, now: Date | string | number): number {
    const ms = toDate(now).getTime() - toDate(acceptedAt).getTime();
    return Number.isFinite(ms) && ms > 0 ? ms : 0;
  }

  /**
   * ค้างเกินกำหนด = ใบงานปกติที่ยังไม่มีผล (queued/processing) และรอมา "เกิน" 120 นาที
   * เทียบละเอียดถึงมิลลิวินาที: 120:00.000 → ปกติ · 120:00.001 ขึ้นไป → ค้างทันที
   * (REQUIREMENTS BR-13: 119 → ปกติ · 120 → ปกติ · 121 → ค้าง)
   * ข้อควรระวังสำหรับข้อมูลทดสอบ: แถวที่ใส่ไว้ "120 นาทีก่อน" พอดีจะกลายเป็นค้างทันทีที่เวลาผ่านไป
   * การทดสอบแถว TD-BR13-b จึงต้องกำหนด `now` ตายตัว (ดู rules.test.ts)
   */
  function isOverdue(receipt: OverdueInput, now: Date | string | number): boolean {
    if (receipt.priority !== 'normal') return false;
    if (receipt.status !== 'queued' && receipt.status !== 'processing') return false;
    return msWaiting(receipt.acceptedAt, now) > LIMITS.OVERDUE_MINUTES * 60_000;
  }

  /** รายการค้างเกินกำหนด เรียงจากรอนานที่สุด พร้อมนาทีที่รอ (นาทีเต็ม ปัดลง) */
  function listOverdue<T extends OverdueInput>(
    receipts: ReadonlyArray<T>,
    now: Date | string | number,
  ): Array<T & { minutesWaiting: number }> {
    return receipts
      .filter((r) => isOverdue(r, now))
      .map((r) => ({ r, ms: msWaiting(r.acceptedAt, now) }))
      .sort((a, b) => b.ms - a.ms)
      .map(({ r, ms }) => ({ ...r, minutesWaiting: Math.floor(ms / 60_000) }));
  }

  /**
   * ใช้กรองใน SQL: `accepted_at < overdueCutoff(now)` ⇔ isOverdue (รอเกิน 120 นาที)
   * = now − 120 นาที (ห้ามใช้ `<=` เพราะ 120 นาทีพอดียังไม่ค้าง)
   */
  function overdueCutoff(now: Date | string | number): Date {
    return new Date(toDate(now).getTime() - LIMITS.OVERDUE_MINUTES * 60_000);
  }

  // ----- BR-14 · นับเดือนตามวันที่บนใบเสร็จ ---------------------------------
  /** ช่วงวันที่ของเดือน (รวมทั้งสองปลาย) ใช้กับ SQL `receipt_date BETWEEN startDate AND endDate` */
  function monthBounds(month: string): MonthBounds {
    if (!isValidMonth(month)) throw new RangeError(`month ต้องเป็นรูปแบบ YYYY-MM: ${month}`);
    const [y, m] = month.split('-').map(Number);
    const first = bug ? 2 : 1;
    return {
      month,
      startDate: `${month}-${pad2(first)}`,
      endDate: `${month}-${pad2(daysInMonth(y, m))}`,
    };
  }

  /** เดือน 'YYYY-MM' ของวันที่บนใบ */
  function monthOf(receiptDate: Date | string | null | undefined): string | null {
    const key = toDateKey(receiptDate);
    if (!key) return null;
    const month = key.slice(0, 7);
    const b = monthBounds(month);
    return key >= b.startDate && key <= b.endDate ? month : null;
  }

  function isInMonth(receiptDate: Date | string | null | undefined, month: string): boolean {
    return monthOf(receiptDate) === month;
  }

  /** สรุปรายเดือน: เฉพาะใบที่ยืนยันแล้ว และวันที่บนใบอยู่ในเดือน (FR-28 · BR-14) */
  function summarizeMonth(receipts: ReadonlyArray<MonthlyReceiptInput>, month: string): MonthlySummary {
    monthBounds(month);
    const byCategory: MonthlySummary['byCategory'] = {};
    let count = 0;
    let totalSatang = 0;
    for (const r of receipts) {
      if (r.status !== 'confirmed') continue;
      if (!isInMonth(r.receiptDate, month)) continue;
      const s = toSatang(r.total) ?? 0;
      count++;
      totalSatang += s;
      if (r.categoryId !== null && r.categoryId !== undefined) {
        const k = String(r.categoryId);
        const c = (byCategory[k] ??= { count: 0, totalSatang: 0, total: '0.00' });
        c.count++;
        c.totalSatang += s;
        c.total = satangToBaht(c.totalSatang);
      }
    }
    return { month, count, totalSatang, total: satangToBaht(totalSatang), byCategory };
  }

  return Object.freeze({
    bugMode: bug,
    // BR-07 · BR-10 (แบบจำลองอ้างอิงของฝั่ง AI)
    readAttemptOutcome,
    canRetryRead,
    nextQueue,
    planReadOrder,
    // BR-01 – BR-03
    checkBatchSize,
    isFileSizeOk,
    checkFileSize,
    isPdfPageCountOk,
    checkFileType,
    checkFile,
    validateUpload,
    // BR-04 – BR-05
    isLowConfidence,
    itemsDiffSatang,
    isMismatch,
    computeFlags,
    // BR-06
    isConfirmableTotal,
    checkConfirmTotal,
    // BR-08 – BR-09
    checkUrgentSize,
    countUrgentToday,
    canSetUrgent,
    checkUrgentQuota,
    checkUrgent,
    // BR-11 – BR-12
    hasQueueRoom,
    checkQueueCapacity,
    effectiveWorkers,
    retryAfterMinutes,
    queueFullMessage,
    // BR-13
    minutesWaiting,
    isOverdue,
    listOverdue,
    overdueCutoff,
    // BR-14
    monthBounds,
    monthOf,
    isInMonth,
    summarizeMonth,
  });
}

export type Rules = ReturnType<typeof createRules>;

// ---------------------------------------------------------------------------
// ชุดกฎที่ใช้จริง: อ่าน BUG_MODE ครั้งเดียวตอนโหลดโมดูล
// ---------------------------------------------------------------------------

function readModeFromEnv(): boolean {
  const env = typeof process !== 'undefined' && process.env ? process.env.BUG_MODE : undefined;
  return String(env ?? '0').trim() === '1';
}

export const rules: Rules = createRules({ bugMode: readModeFromEnv() });

export const {
  checkBatchSize,
  isFileSizeOk,
  checkFileSize,
  isPdfPageCountOk,
  checkFileType,
  checkFile,
  validateUpload,
  isLowConfidence,
  itemsDiffSatang,
  isMismatch,
  computeFlags,
  isConfirmableTotal,
  checkConfirmTotal,
  checkUrgentSize,
  countUrgentToday,
  canSetUrgent,
  checkUrgentQuota,
  checkUrgent,
  hasQueueRoom,
  checkQueueCapacity,
  effectiveWorkers,
  retryAfterMinutes,
  queueFullMessage,
  minutesWaiting,
  isOverdue,
  listOverdue,
  overdueCutoff,
  monthBounds,
  monthOf,
  isInMonth,
  summarizeMonth,
} = rules;

export default rules;
