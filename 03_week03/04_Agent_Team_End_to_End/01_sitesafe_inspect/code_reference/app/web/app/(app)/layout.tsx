// Layout of every logged-in page. The middleware already sends requests without a
// session cookie to /login; here the session itself is checked in the database,
// so an expired or forged cookie also ends at /login (FR-18).
import type { ReactNode } from 'react';
import NavBar from '@/components/NavBar';
import { requireUser } from '@/components/server/session';

export const dynamic = 'force-dynamic';

export default async function AppLayout({ children }: { children: ReactNode }) {
  const user = await requireUser();
  return (
    <>
      <NavBar user={user} />
      <main className="page">{children}</main>
    </>
  );
}
