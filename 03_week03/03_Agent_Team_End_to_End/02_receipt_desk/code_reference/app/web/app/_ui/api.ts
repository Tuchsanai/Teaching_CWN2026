'use client';
/**
 * ตัวเรียก API ของเว็บจากฝั่ง browser (B11) — cookie `rd_session` ไปกับคำขอเองเพราะอยู่ origin เดียวกัน
 * - 401 → กลับไป /login?next=<หน้าปัจจุบัน>
 * - คำตอบผิดกฎตาม DESIGN 9.2: { error, rule?, message, ...extra }
 */

export interface ApiErrorBody {
  error: string;
  rule?: string;
  message?: string;
  retryAfterMinutes?: number;
  files?: { index: number; name: string; error: string; rule: string; message: string }[];
  file?: string;
  usedToday?: number;
  [key: string]: unknown;
}

export type ApiResult<T> =
  | { ok: true; status: number; data: T; headers: Headers }
  | { ok: false; status: number; error: ApiErrorBody; headers: Headers };

export async function api<T>(url: string, init?: RequestInit): Promise<ApiResult<T>> {
  let res: Response;
  try {
    res = await fetch(url, { cache: 'no-store', credentials: 'same-origin', ...init });
  } catch {
    return {
      ok: false,
      status: 0,
      error: { error: 'network', message: 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ กรุณาลองใหม่' },
      headers: new Headers(),
    };
  }
  if (res.status === 401 && !url.startsWith('/api/auth/login')) {
    const next = window.location.pathname + window.location.search;
    window.location.href = `/login?next=${encodeURIComponent(next)}`;
  }
  let body: unknown = null;
  const type = res.headers.get('content-type') ?? '';
  if (type.includes('application/json')) {
    try {
      body = await res.json();
    } catch {
      body = null;
    }
  }
  if (res.ok) return { ok: true, status: res.status, data: body as T, headers: res.headers };
  const err = (body && typeof body === 'object' ? body : {}) as ApiErrorBody;
  if (!err.error) err.error = `http_${res.status}`;
  if (!err.message) err.message = `เกิดข้อผิดพลาด (HTTP ${res.status})`;
  return { ok: false, status: res.status, error: err, headers: res.headers };
}

/** ข้อความภาษาไทยของคำตอบผิด (ใช้ message จาก server ก่อน) */
export function errorText(e: ApiErrorBody): string {
  if (e.message) return e.message;
  return e.error;
}
