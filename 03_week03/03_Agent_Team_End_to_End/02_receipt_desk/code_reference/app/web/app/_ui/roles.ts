/**
 * บทบาท ↔ หน้า (DESIGN 9.1) — ไฟล์นี้ไม่มี import ฝั่ง server จึงใช้ได้ทั้ง server และ client component
 */
export type Role = 'staff' | 'lead' | 'owner' | 'client';

/** ข้อมูลผู้ใช้ที่ส่งให้ client component ได้ (ไม่มี token) */
export interface PageUser {
  id: string;
  email: string;
  displayName: string;
  role: Role;
  roleLabel: string;
  clientId: string | null;
  clientName: string | null;
}

export const ROLE_LABEL: Record<Role, string> = {
  staff: 'พนักงานบัญชี',
  lead: 'หัวหน้าทีมบัญชี',
  owner: 'เจ้าของสำนักงาน',
  client: 'ลูกค้า',
};

/** สิทธิ์ของหน้า (DESIGN 9.1) — ใช้ทั้งตัวกันหน้าและเมนู */
export const PAGE_ROLES = {
  '/upload': ['staff', 'lead'],
  '/batches': ['staff', 'lead', 'owner'],
  '/receipts': ['staff', 'lead', 'owner'],
  '/unreadable': ['staff', 'lead', 'owner'],
  '/overdue': ['lead', 'owner'],
  '/reports': ['staff', 'lead', 'owner'],
  '/insights': ['lead', 'owner'],
  '/portal': ['client'],
} as const satisfies Record<string, readonly Role[]>;

export type PagePath = keyof typeof PAGE_ROLES;

export function canOpen(role: Role, path: PagePath): boolean {
  return (PAGE_ROLES[path] as readonly Role[]).includes(role);
}

/** หน้าแรกของแต่ละบทบาท (หลังเข้าสู่ระบบ และเมื่อเปิด `/`) */
export function homeFor(role: Role): string {
  if (role === 'client') return '/portal';
  if (role === 'owner') return '/batches';
  return '/upload';
}

