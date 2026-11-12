// app/api/admin/_auth.ts (B3) — สิทธิ์หลังร้าน: cookie `bm_admin` = HMAC ของ ADMIN_PASSWORD (ไม่เก็บรหัสผ่านตรง ๆ)
// โฟลเดอร์/ไฟล์ขึ้นต้น _ ไม่ถูกสร้างเป็น route · ใช้ได้ทั้งใน route handler และ server component ของ /admin
import { createHmac, timingSafeEqual } from 'node:crypto';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export const ADMIN_COOKIE = 'bm_admin';
export const ADMIN_MAX_AGE = 60 * 60 * 12; // 12 ชม.

const password = () => process.env.ADMIN_PASSWORD || 'admin1234';

/** ค่า token ที่ถูกต้อง (เปลี่ยน ADMIN_PASSWORD → token เก่าใช้ไม่ได้ทันที) */
export function adminToken(): string {
  return createHmac('sha256', password()).update('buildmart-admin-v1').digest('hex');
}

function safeEqual(a: string, b: string) {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

export function checkPassword(input: unknown): boolean {
  return typeof input === 'string' && safeEqual(input, password());
}

export function isAdmin(): boolean {
  const v = cookies().get(ADMIN_COOKIE)?.value;
  return !!v && safeEqual(v, adminToken());
}

/** ใช้ต้น route handler: `const deny = requireAdmin(); if (deny) return deny;` */
export function requireAdmin(): NextResponse | null {
  return isAdmin() ? null : NextResponse.json({ error: 'unauthorized' }, { status: 401 });
}
