/**
 * รูปแบบการแสดงผล (B11)
 * - องค์ประกอบที่มี data-testid ของตัวเลขเงินแสดงค่าดิบจาก API เช่น `1340.00` (ไม่มีจุลภาค ไม่มีหน่วย) เพื่อให้ทดสอบเทียบได้ตรง
 *   หน่วย "บาท" อยู่นอกองค์ประกอบนั้น
 * - เวลาแสดงเป็นเวลาไทย (Asia/Bangkok)
 */

export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return '—';
  const n = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(n)) return String(value);
  return n.toFixed(2);
}

export function dateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString('th-TH', {
    timeZone: 'Asia/Bangkok',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

/** เดือนปัจจุบันตามเวลาไทย รูป YYYY-MM */
export function currentBangkokMonth(now: Date = new Date()): string {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Bangkok', year: 'numeric', month: '2-digit' }).formatToParts(now);
  const y = parts.find((p) => p.type === 'year')?.value ?? '1970';
  const m = parts.find((p) => p.type === 'month')?.value ?? '01';
  return `${y}-${m}`;
}

export const STATUS_OPTIONS = [
  { value: 'queued', label: 'รออ่าน' },
  { value: 'processing', label: 'กำลังอ่าน' },
  { value: 'review', label: 'รอตรวจ' },
  { value: 'confirmed', label: 'ยืนยันแล้ว' },
  { value: 'unreadable', label: 'อ่านไม่ได้' },
] as const;

export const PRIORITY_LABEL: Record<string, string> = { normal: 'ปกติ', urgent: 'ด่วน' };
