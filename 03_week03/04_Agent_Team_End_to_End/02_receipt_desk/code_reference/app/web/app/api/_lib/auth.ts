/**
 * Session + สิทธิ์ 4 บทบาท (FR-01 · FR-02 · FR-19 · FR-24 · DESIGN 8, 9.1, 9.2)
 *
 * - session เก็บในตาราง `sessions` (token สุ่ม 32 ไบต์) · cookie `rd_session` เป็น httpOnly
 * - ถ้าตั้ง SESSION_SECRET ค่า cookie = token + "." + HMAC-SHA256(token) และตรวจลายเซ็นทุกครั้ง
 * - บัญชีลูกค้า: ทุกคำสั่งอ่านข้อมูลกรองด้วย `client_id` ของ session ที่ฝั่ง server
 */
import { createHmac, randomBytes, timingSafeEqual } from 'node:crypto';
import type { PoolClient } from 'pg';
import { query, queryOne } from './db';
import { forbidden, unauthenticated } from './http';

export type Role = 'staff' | 'lead' | 'owner' | 'client';

export interface SessionUser {
  id: string;
  email: string;
  displayName: string;
  role: Role;
  clientId: string | null;
  clientName: string | null;
  token: string;
}

export const SESSION_COOKIE = 'rd_session';
export const SESSION_TTL_HOURS = 12;

/** กลุ่มบทบาทที่ใช้บ่อย */
export const OFFICE: readonly Role[] = ['staff', 'lead', 'owner'];
export const EDITORS: readonly Role[] = ['staff', 'lead'];
export const LEAD_ONLY: readonly Role[] = ['lead'];
export const ALL_ROLES: readonly Role[] = ['staff', 'lead', 'owner', 'client'];

function sign(token: string): string {
  const secret = process.env.SESSION_SECRET;
  if (!secret) return token;
  const mac = createHmac('sha256', secret).update(token).digest('base64url');
  return `${token}.${mac}`;
}

function unsign(value: string): string | null {
  const secret = process.env.SESSION_SECRET;
  if (!secret) return /^[A-Za-z0-9_-]{20,}$/.test(value) ? value : null;
  const dot = value.lastIndexOf('.');
  if (dot <= 0) return null;
  const token = value.slice(0, dot);
  const given = Buffer.from(value.slice(dot + 1));
  const expected = Buffer.from(createHmac('sha256', secret).update(token).digest('base64url'));
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) return null;
  return token;
}

export function readCookie(request: Request, name: string): string | null {
  const header = request.headers.get('cookie');
  if (!header) return null;
  for (const part of header.split(';')) {
    const eq = part.indexOf('=');
    if (eq < 0) continue;
    if (part.slice(0, eq).trim() === name) {
      try {
        return decodeURIComponent(part.slice(eq + 1).trim());
      } catch {
        return null;
      }
    }
  }
  return null;
}

function isSecure(request: Request): boolean {
  if (process.env.COOKIE_SECURE === '1') return true;
  if (process.env.COOKIE_SECURE === '0') return false;
  const proto = request.headers.get('x-forwarded-proto');
  if (proto) return proto.split(',')[0].trim() === 'https';
  return new URL(request.url).protocol === 'https:';
}

export function sessionCookie(request: Request, value: string, maxAgeSeconds: number): string {
  const parts = [
    `${SESSION_COOKIE}=${encodeURIComponent(value)}`,
    'Path=/',
    'HttpOnly',
    'SameSite=Lax',
    `Max-Age=${maxAgeSeconds}`,
  ];
  if (isSecure(request)) parts.push('Secure');
  return parts.join('; ');
}

export function clearSessionCookie(request: Request): string {
  return sessionCookie(request, '', 0);
}

interface UserRow {
  id: string;
  email: string;
  display_name: string;
  role: Role;
  client_id: string | null;
  client_name: string | null;
}

function toSessionUser(row: UserRow, token: string): SessionUser {
  return {
    id: row.id,
    email: row.email,
    displayName: row.display_name,
    role: row.role,
    clientId: row.client_id,
    clientName: row.client_name,
    token,
  };
}

/** ตรวจอีเมล + รหัสผ่าน (bcrypt ของ pgcrypto `crypt()` ตามข้อมูลตั้งต้น) แล้วสร้าง session */
export async function login(email: string, password: string): Promise<{ user: SessionUser; cookieValue: string } | null> {
  const row = await queryOne<UserRow>(
    `SELECT u.id, u.email, u.display_name, u.role, u.client_id, c.name AS client_name
       FROM users u LEFT JOIN clients c ON c.id = u.client_id
      WHERE lower(u.email) = lower($1)
        AND u.password_hash = crypt($2, u.password_hash)`,
    [email.trim(), password],
  );
  if (!row) return null;
  const token = randomBytes(32).toString('base64url');
  await query(`DELETE FROM sessions WHERE expires_at < now()`);
  await query(
    `INSERT INTO sessions (token, user_id, expires_at)
     VALUES ($1, $2, now() + make_interval(hours => $3))`,
    [token, row.id, SESSION_TTL_HOURS],
  );
  return { user: toSessionUser(row, token), cookieValue: sign(token) };
}

export async function logout(user: SessionUser): Promise<void> {
  await query('DELETE FROM sessions WHERE token = $1', [user.token]);
}

/** session ปัจจุบัน หรือ null */
export async function currentUser(request: Request): Promise<SessionUser | null> {
  const raw = readCookie(request, SESSION_COOKIE);
  if (!raw) return null;
  const token = unsign(raw);
  if (!token) return null;
  const row = await queryOne<UserRow>(
    `SELECT u.id, u.email, u.display_name, u.role, u.client_id, c.name AS client_name
       FROM sessions s
       JOIN users u ON u.id = s.user_id
       LEFT JOIN clients c ON c.id = u.client_id
      WHERE s.token = $1 AND s.expires_at > now()`,
    [token],
  );
  return row ? toSessionUser(row, token) : null;
}

/**
 * ต้องเข้าสู่ระบบ (ไม่มี → 401 unauthenticated) และบทบาทต้องอยู่ใน `roles` (ไม่อยู่ → 403 forbidden)
 */
export async function requireUser(request: Request, roles: readonly Role[] = ALL_ROLES): Promise<SessionUser> {
  const user = await currentUser(request);
  if (!user) throw unauthenticated();
  if (!roles.includes(user.role)) throw forbidden();
  return user;
}

export function isClient(user: SessionUser): boolean {
  return user.role === 'client';
}

/**
 * client_id ที่ผู้ใช้นี้มีสิทธิ์เห็น: ลูกค้า = ร้านของตัวเองเท่านั้น · สำนักงาน = null (ทุกร้าน)
 */
export function scopeClientId(user: SessionUser): string | null {
  return user.role === 'client' ? user.clientId : null;
}

/** ตรวจว่าร้านมีอยู่จริง (ใช้ตอนสำนักงานระบุ clientId) */
export async function clientExists(clientId: string, client?: PoolClient): Promise<boolean> {
  const sql = 'SELECT 1 FROM clients WHERE id = $1';
  if (client) return ((await client.query(sql, [clientId])).rowCount ?? 0) > 0;
  return (await query(sql, [clientId])).length > 0;
}
