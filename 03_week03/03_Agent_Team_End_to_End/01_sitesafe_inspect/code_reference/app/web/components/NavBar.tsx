// Top bar of every logged-in page (DESIGN 7.4). Server Component: the menu is
// built from canAccess() on the server; entries the role may not use are not rendered.
import Link from 'next/link';
import type { SessionUser } from '@/lib/auth';
import { ROLE_LABELS } from '@/lib/views';
import { menuFor } from '@/components/server/session';
import LogoutButton from '@/components/LogoutButton';

export default function NavBar({ user }: { user: SessionUser }) {
  const m = menuFor(user);
  return (
    <header className="topbar">
      <Link href="/" className="brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="SiteSafe Inspect" />
        <span>SiteSafe Inspect</span>
      </Link>
      <nav>
        {m.upload && (
          <Link href="/upload" data-testid="nav-upload">
            อัปโหลดรูป
          </Link>
        )}
        {m.photos && (
          <Link href="/photos" data-testid="nav-photos">
            รูปทั้งหมด
          </Link>
        )}
        {m.problems && (
          <Link href="/photos/problems" data-testid="nav-problems">
            รูปที่มีปัญหา
          </Link>
        )}
        {m.report && (
          <Link href="/reports/daily" data-testid="nav-report">
            รายงานรายวัน
          </Link>
        )}
      </nav>
      <div className="user">
        <strong data-testid="nav-user-name">{user.full_name}</strong>
        <span data-testid="nav-user-role" data-role={user.role}>
          {ROLE_LABELS[user.role]}
        </span>
        <span data-testid="nav-user-site" data-site={user.site_code ?? ''}>
          {user.site_name ?? 'ทุกไซต์'}
        </span>
        <LogoutButton />
      </div>
    </header>
  );
}
