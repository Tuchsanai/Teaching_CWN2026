// /login — e-mail + password (FR-18). The only page that does not need a session.
import { redirect } from 'next/navigation';
import LoginForm from '@/components/LoginForm';
import { currentUser, homePathFor, safeNextPath } from '@/components/server/session';

export const dynamic = 'force-dynamic';

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const next = safeNextPath(sp.next);
  const user = await currentUser();
  if (user) redirect(next ?? homePathFor(user));

  return (
    <main className="page">
      <div className="card login-box">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img className="logo" src="/logo.png" alt="SiteSafe Inspect" />
        <h1 style={{ textAlign: 'center' }}>เข้าสู่ระบบ SiteSafe Inspect</h1>
        <LoginForm next={next} />
      </div>
    </main>
  );
}
