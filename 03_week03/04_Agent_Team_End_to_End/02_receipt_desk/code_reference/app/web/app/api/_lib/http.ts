/**
 * รูปแบบคำตอบของ API เว็บ (DESIGN 9.2)
 * ผิดกฎ: {"error":"<รหัส>","rule":"BR-xx","message":"<ข้อความภาษาไทย>"}
 */
import { NextResponse } from 'next/server';
import type { RuleViolation } from '../../../lib/rules';

export class ApiError extends Error {
  status: number;
  body: Record<string, unknown>;
  headers: Record<string, string>;

  constructor(status: number, error: string, message: string, extra: Record<string, unknown> = {}, headers: Record<string, string> = {}) {
    super(message);
    this.status = status;
    this.body = { error, message, ...extra };
    this.headers = headers;
  }
}

const NO_STORE = { 'Cache-Control': 'no-store' };

export function json(body: unknown, status = 200, headers: Record<string, string> = {}): NextResponse {
  return NextResponse.json(body, { status, headers: { ...NO_STORE, ...headers } });
}

export const unauthenticated = () => new ApiError(401, 'unauthenticated', 'กรุณาเข้าสู่ระบบก่อน');
export const forbidden = () => new ApiError(403, 'forbidden', 'บัญชีนี้ไม่มีสิทธิ์ทำรายการนี้');
export const notFound = () => new ApiError(404, 'not_found', 'ไม่พบข้อมูล');
export const badRequest = (detail: string) => new ApiError(400, 'bad_request', detail);

/** แปลงผลผิดกฎจาก rules.ts เป็น ApiError — รหัส HTTP และเนื้อหามาจากโมดูลกฎ */
export function ruleError(v: RuleViolation, extra: Record<string, unknown> = {}): ApiError {
  const { ok: _ok, status, error, message, ...rest } = v;
  void _ok;
  const headers: Record<string, string> = {};
  if (status === 429 && typeof v.retryAfterMinutes === 'number') {
    headers['Retry-After'] = String(v.retryAfterMinutes * 60);
  }
  return new ApiError(status, error, message, { ...rest, ...extra }, headers);
}

export function errorResponse(error: unknown): NextResponse {
  if (error instanceof ApiError) return json(error.body, error.status, error.headers);
  console.error('[api] unexpected error:', error instanceof Error ? error.message : String(error));
  return json({ error: 'internal_error', message: 'ระบบขัดข้อง กรุณาลองใหม่' }, 500);
}

/** ครอบ handler: ApiError → คำตอบตามรหัส · อย่างอื่น → 500 (ไม่พิมพ์เนื้อหาใบเสร็จลง log) */
export function handle<A extends unknown[]>(fn: (...args: A) => Promise<Response>) {
  return async (...args: A): Promise<Response> => {
    try {
      return await fn(...args);
    } catch (error) {
      return errorResponse(error);
    }
  };
}

/** อ่าน JSON body · ว่างได้ถ้า `allowEmpty` */
export async function readJson(request: Request, allowEmpty = false): Promise<Record<string, unknown>> {
  const text = await request.text();
  if (!text.trim()) {
    if (allowEmpty) return {};
    throw badRequest('ต้องส่งเนื้อหาแบบ JSON');
  }
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw badRequest('เนื้อหาไม่ใช่ JSON ที่ถูกต้อง');
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw badRequest('เนื้อหาต้องเป็น JSON object');
  return data as Record<string, unknown>;
}

/** params ของ dynamic route (Next.js 15+ ส่งเป็น Promise) */
export type IdContext = { params: Promise<{ id: string }> };

export async function paramId(ctx: IdContext): Promise<string> {
  const p = await ctx.params;
  return p.id;
}

export function boolParam(value: string | null | undefined): boolean | undefined {
  if (value === null || value === undefined || value === '') return undefined;
  const v = value.trim().toLowerCase();
  if (v === 'true' || v === '1' || v === 'yes' || v === 'on') return true;
  if (v === 'false' || v === '0' || v === 'no' || v === 'off') return false;
  throw badRequest(`ค่า boolean ไม่ถูกต้อง: ${value}`);
}
