/** Small helpers shared by the Route Handlers under app/api. */
import { NextResponse } from 'next/server';

const NO_STORE = { 'Cache-Control': 'no-store' };

export function json(body: unknown, status = 200, headers: Record<string, string> = {}): NextResponse {
  return NextResponse.json(body, { status, headers: { ...NO_STORE, ...headers } });
}

export function apiError(status: number, error: string, message: string, extra: Record<string, unknown> = {}): NextResponse {
  return json({ error, message, ...extra }, status);
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isUuid(v: unknown): v is string {
  return typeof v === 'string' && UUID_RE.test(v);
}

/** Parse a JSON request body; returns undefined when it is not valid JSON. */
export async function readJson(req: Request, maxBytes = 64 * 1024): Promise<unknown> {
  const text = await req.text();
  if (text.length > maxBytes) return undefined;
  if (text.trim() === '') return {};
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

export function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

/** Log an unexpected error without request data (no keys, no cookies). */
export function serverError(where: string, err: unknown): NextResponse {
  const msg = err instanceof Error ? err.message : String(err);
  console.error(`[api] ${where}: ${msg}`);
  return apiError(500, 'INTERNAL_ERROR', 'ระบบขัดข้อง กรุณาลองใหม่');
}
