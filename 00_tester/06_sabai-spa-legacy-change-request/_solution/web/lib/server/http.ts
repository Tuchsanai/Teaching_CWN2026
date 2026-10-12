// ตัวช่วย route handler: error เป็น JSON {error, message} ตามภาษาใน cookie lang
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { LANG_COOKIE, normalizeLang, SHOP_PHONE, t, type Lang } from "../i18n.ts";

export class ApiError extends Error {
  status: number;
  code: string;
  extra?: Record<string, unknown>;
  constructor(status: number, code: string, extra?: Record<string, unknown>) {
    super(code);
    this.status = status;
    this.code = code;
    this.extra = extra;
  }
}

const WITH_PHONE = new Set(["GROUP_CALL_SHOP", "CANCEL_TOO_LATE", "RESCHEDULE_TOO_LATE"]);

export async function getLang(override?: unknown): Promise<Lang> {
  if (override === "th" || override === "en" || override === "zh") return override;
  const c = await cookies();
  return normalizeLang(c.get(LANG_COOKIE)?.value);
}

export function errorBody(lang: Lang, code: string, extra?: Record<string, unknown>) {
  return {
    error: code,
    message: t(lang, `err.${code}`, {
      ...(extra?.existing ? { code: String(extra.existing) } : {}),
      ...(extra?.name ? { name: String(extra.name) } : {}), // CR-04 SHOP_CLOSED
      ...(WITH_PHONE.has(code) ? { phone: SHOP_PHONE } : {}), // CR-01 RESCHEDULE_TOO_LATE "{phone}"
    }),
    ...(WITH_PHONE.has(code) ? { phone: SHOP_PHONE } : {}),
    ...(extra ?? {}),
  };
}

export async function handle(fn: () => Promise<Response>): Promise<Response> {
  try {
    return await fn();
  } catch (e) {
    const lang = await getLang().catch(() => "th" as Lang);
    if (e instanceof ApiError) return NextResponse.json(errorBody(lang, e.code, e.extra), { status: e.status });
    // pg exclusion violation (กดพร้อมกัน NFR-12) → 409
    if ((e as { code?: string })?.code === "23P01") return NextResponse.json(errorBody(lang, "SLOT_TAKEN"), { status: 409 });
    console.error(e);
    return NextResponse.json(errorBody(lang, "SERVER"), { status: 500 });
  }
}

export async function readJson(req: Request): Promise<Record<string, unknown>> {
  try {
    const v = await req.json();
    return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

export function json(data: unknown, status = 200): Response {
  return NextResponse.json(data, { status });
}
