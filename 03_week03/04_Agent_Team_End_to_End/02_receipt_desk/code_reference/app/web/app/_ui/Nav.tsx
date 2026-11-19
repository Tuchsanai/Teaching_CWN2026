/**
 * เมนูทุกหน้า (DESIGN 9.5 "ทุกหน้า") — แสดงเฉพาะลิงก์ของหน้าที่บทบาทนี้เปิดได้ตาม 9.1
 * nav-upload · nav-batches · nav-receipts · nav-unreadable · nav-overdue · nav-reports · nav-insights · nav-portal
 * nav-user-name · nav-user-role · logout-button
 */
import Link from 'next/link';
import LogoutButton from './LogoutButton';
import OverdueBadge from './OverdueBadge';
import { canOpen } from './roles';
import type { PagePath, PageUser } from './roles';

const LINKS: { path: PagePath; testid: string; label: string }[] = [
  { path: '/upload', testid: 'nav-upload', label: 'อัปโหลดชุด' },
  { path: '/batches', testid: 'nav-batches', label: 'ชุดใบเสร็จ' },
  { path: '/receipts', testid: 'nav-receipts', label: 'รายการใบ' },
  { path: '/unreadable', testid: 'nav-unreadable', label: 'อ่านไม่ได้' },
  { path: '/overdue', testid: 'nav-overdue', label: 'ค้างเกินกำหนด' },
  { path: '/reports', testid: 'nav-reports', label: 'สรุปรายเดือน' },
  { path: '/insights', testid: 'nav-insights', label: 'เวลาตรวจ · GPU' },
  { path: '/portal', testid: 'nav-portal', label: 'ใบเสร็จของร้าน' },
];

export default function Nav({ user }: { user: PageUser }) {
  return (
    <header className="nav">
      <Link href="/" className="brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="" width={28} height={28} />
        <span>ReceiptDesk</span>
      </Link>
      <nav>
        {LINKS.filter((l) => canOpen(user.role, l.path)).map((l) => (
          <Link key={l.path} href={l.path} data-testid={l.testid}>
            {l.label}
            {l.path === '/overdue' ? <OverdueBadge /> : null}
          </Link>
        ))}
      </nav>
      <div className="who">
        <span data-testid="nav-user-name">{user.displayName}</span>
        <span className="role" data-testid="nav-user-role" data-role={user.role}>
          {user.roleLabel}
          {user.clientName ? ` · ${user.clientName}` : ''}
        </span>
        <LogoutButton />
      </div>
    </header>
  );
}
