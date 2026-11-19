/**
 * Session ฝั่งหน้าเว็บ (server component) — B11
 *
 * ใช้ตรรกะเดียวกับ API (web/app/api/_lib/auth.ts ของ B04): อ่าน cookie `rd_session` แล้วหา session ในฐานข้อมูล
 * DESIGN 8: ทุกหน้าต้องมี session ยกเว้น /login · ไม่มี session → ส่งไป /login?next=<path>
 * DESIGN 9.1: บทบาทที่ไม่อยู่ในตารางของหน้านั้น → แสดง <Forbidden/> (ไม่โหลดข้อมูลใด ๆ)
 */
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { SESSION_COOKIE, currentUser } from '../api/_lib/auth';
import type { SessionUser } from '../api/_lib/auth';
import { ROLE_LABEL } from './roles';
import type { PageUser, Role } from './roles';

export * from './roles';

function toPageUser(u: SessionUser): PageUser {
  return {
    id: u.id,
    email: u.email,
    displayName: u.displayName,
    role: u.role,
    roleLabel: ROLE_LABEL[u.role],
    clientId: u.clientId,
    clientName: u.clientName,
  };
}

/** ผู้ใช้ของคำขอนี้ หรือ null */
export async function getPageUser(): Promise<PageUser | null> {
  const store = await cookies();
  const raw = store.get(SESSION_COOKIE)?.value;
  if (!raw) return null;
  // currentUser() ของ B04 รับ Request จึงสร้างคำขอจำลองที่มีเฉพาะ cookie นี้
  const req = new Request('http://receiptdesk.local/', {
    headers: { cookie: `${SESSION_COOKIE}=${encodeURIComponent(raw)}` },
  });
  try {
    const user = await currentUser(req);
    return user ? toPageUser(user) : null;
  } catch {
    return null;
  }
}

/**
 * ตัวกันหน้า: ไม่มี session → redirect ไป /login?next=<path>
 * มี session แต่บทบาทไม่อยู่ใน `roles` → `{ user, allowed: false }` ให้หน้าแสดง <Forbidden/>
 */
export async function requirePageUser(
  roles: readonly Role[],
  path: string,
): Promise<{ user: PageUser; allowed: boolean }> {
  const user = await getPageUser();
  if (!user) redirect(`/login?next=${encodeURIComponent(path)}`);
  return { user, allowed: roles.includes(user.role) };
}
