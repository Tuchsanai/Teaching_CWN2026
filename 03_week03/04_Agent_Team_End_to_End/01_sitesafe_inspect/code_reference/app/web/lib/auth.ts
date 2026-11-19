/**
 * Login and sessions (DESIGN §10, FR-18, NFR-06).
 * - Passwords: argon2id hashes only (users.password_hash).
 * - Session token: 256 random bits, sent only in an HttpOnly + Secure + SameSite=Lax cookie;
 *   the database keeps only SHA-256(token) in sessions.token_hash.
 */
import { createHash, randomBytes } from 'node:crypto';
import { hash as argonHash, verify as argonVerify } from '@node-rs/argon2';
import type { NextRequest, NextResponse } from 'next/server';
import { pool } from './db';
import { SESSION_COOKIE, SESSION_COOKIE_OPTIONS, SESSION_TTL_SECONDS } from './session-cookie';

export type Role = 'manager' | 'supervisor' | 'executive';

export type SessionUser = {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  site_id: number | null;
  site_code: string | null;
  site_name: string | null;
};

export const ARGON2_OPTIONS = {
  algorithm: 2, // Algorithm.Argon2id (const enum, not importable with isolatedModules)
  memoryCost: 19456,
  timeCost: 2,
  parallelism: 1,
} as const;

export function hashPassword(password: string): Promise<string> {
  return argonHash(password, ARGON2_OPTIONS);
}

export function newSessionToken(): string {
  return randomBytes(32).toString('base64url'); // 256 bits
}

export function hashToken(token: string): string {
  return createHash('sha256').update(token, 'utf8').digest('hex');
}

let dummyHash: Promise<string> | null = null;
function getDummyHash(): Promise<string> {
  return (dummyHash ??= hashPassword(randomBytes(16).toString('hex')));
}

async function verifyPassword(stored: string | null, password: string): Promise<boolean> {
  // Always run one argon2 verification so a wrong e-mail and a wrong password take similar time.
  const target = stored && stored.startsWith('$argon2id$') ? stored : await getDummyHash();
  let ok = false;
  try {
    ok = await argonVerify(target, password);
  } catch {
    ok = false;
  }
  return ok && target === stored;
}

const USER_COLUMNS = `u.id, u.email, u.full_name, u.role, u.site_id, s.code AS site_code, s.name AS site_name`;

/** Check e-mail + password. Returns the user or null (same result for unknown e-mail and wrong password). */
export async function authenticate(email: unknown, password: unknown): Promise<SessionUser | null> {
  if (typeof email !== 'string' || typeof password !== 'string') return null;
  if (email.length > 320 || password.length > 1024 || password.length === 0) {
    await verifyPassword(null, 'x');
    return null;
  }
  const r = await pool().query<SessionUser & { password_hash: string; is_active: boolean }>(
    `SELECT ${USER_COLUMNS}, u.password_hash, u.is_active
       FROM users u LEFT JOIN sites s ON s.id = u.site_id
      WHERE lower(u.email) = lower($1)`,
    [email.trim()],
  );
  const row = r.rows[0];
  const ok = await verifyPassword(row?.password_hash ?? null, password);
  if (!row || !ok || !row.is_active) return null;
  const { password_hash: _h, is_active: _a, ...user } = row;
  return user;
}

/** Create a session row and return the raw token (only the hash is stored). */
export async function createSession(userId: number): Promise<string> {
  const token = newSessionToken();
  await pool().query(`DELETE FROM sessions WHERE expires_at < now()`);
  await pool().query(
    `INSERT INTO sessions (token_hash, user_id, expires_at)
     VALUES ($1, $2, now() + make_interval(secs => $3))`,
    [hashToken(token), userId, SESSION_TTL_SECONDS],
  );
  return token;
}

export function readSessionToken(req: NextRequest): string | null {
  const v = req.cookies.get(SESSION_COOKIE)?.value;
  return v && v.length >= 32 && v.length <= 128 ? v : null;
}

/** Resolve the logged-in user of a request (server side, every request). */
export async function getSessionUser(req: NextRequest): Promise<SessionUser | null> {
  const token = readSessionToken(req);
  if (!token) return null;
  const r = await pool().query<SessionUser>(
    `SELECT ${USER_COLUMNS}
       FROM sessions x
       JOIN users u ON u.id = x.user_id
       LEFT JOIN sites s ON s.id = u.site_id
      WHERE x.token_hash = $1 AND x.expires_at > now() AND u.is_active`,
    [hashToken(token)],
  );
  return r.rows[0] ?? null;
}

export async function destroySession(token: string): Promise<void> {
  await pool().query(`DELETE FROM sessions WHERE token_hash = $1`, [hashToken(token)]);
}

export function setSessionCookie(res: NextResponse, token: string): void {
  res.cookies.set(SESSION_COOKIE, token, { ...SESSION_COOKIE_OPTIONS, maxAge: SESSION_TTL_SECONDS });
}

export function clearSessionCookie(res: NextResponse): void {
  res.cookies.set(SESSION_COOKIE, '', { ...SESSION_COOKIE_OPTIONS, maxAge: 0 });
}
