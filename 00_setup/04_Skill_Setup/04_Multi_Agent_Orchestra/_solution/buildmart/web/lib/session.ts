// lib/session.ts — session ของลูกค้า (cookie `bm_sid` · httpOnly)
// middleware.ts สร้าง cookie ให้ทุก request แล้ว จึงอ่านได้ทั้งใน Server Component และ Route Handler
import { cookies } from 'next/headers';
import { randomUUID } from 'node:crypto';

export const SESSION_COOKIE = 'bm_sid';
export const SESSION_MAX_AGE = 60 * 60 * 24 * 30;

/** คืน session id (ถ้ายังไม่มีจะสร้าง + set cookie — set ได้เฉพาะใน Route Handler / Server Action) */
export function getSessionId(): string {
  const jar = cookies();
  let sid = jar.get(SESSION_COOKIE)?.value;
  if (!sid) {
    sid = randomUUID();
    try {
      jar.set(SESSION_COOKIE, sid, { httpOnly: true, sameSite: 'lax', path: '/', maxAge: SESSION_MAX_AGE });
    } catch {
      /* Server Component set cookie ไม่ได้ — middleware จะ set ให้ใน request ถัดไป */
    }
  }
  return sid;
}

/** อ่านอย่างเดียว ไม่สร้างใหม่ */
export function peekSessionId(): string | null {
  return cookies().get(SESSION_COOKIE)?.value ?? null;
}
