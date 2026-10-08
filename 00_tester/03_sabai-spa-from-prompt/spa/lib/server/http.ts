import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { errorText, isLang, type Lang } from "../i18n";

export async function reqLang(): Promise<Lang> {
  const v = (await cookies()).get("lang")?.value;
  return isLang(v) ? v : "th";
}

export function json(data: unknown, status = 200) {
  return NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });
}

/** error response: { ok:false, error: CODE, message: <text in the visitor's language> } */
export async function fail(code: string, status = 400, extra: Record<string, unknown> = {}) {
  const lang = await reqLang();
  return json({ ok: false, error: code, message: errorText(lang, code), ...extra }, status);
}

export class AppError extends Error {
  constructor(public code: string, public status = 400) {
    super(code);
  }
}

export async function handle(fn: () => Promise<Response>): Promise<Response> {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof AppError) return fail(e.code, e.status);
    console.error("[api]", e);
    return fail("SERVER", 500);
  }
}

export async function body<T = Record<string, unknown>>(req: Request): Promise<T> {
  try {
    return (await req.json()) as T;
  } catch {
    return {} as T;
  }
}
