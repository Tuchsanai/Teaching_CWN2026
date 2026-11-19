/** `/login` — ทุกบทบาท · ไม่ต้องมี session (DESIGN 8, 9.1) · มี session อยู่แล้ว → ไปหน้าแรกของบทบาท */
import { redirect } from 'next/navigation';
import { getPageUser, homeFor } from '../_ui/session';
import LoginForm from './LoginForm';

export const dynamic = 'force-dynamic';

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string | string[] }> }) {
  const user = await getPageUser();
  const sp = await searchParams;
  const next = typeof sp.next === 'string' ? sp.next : '';
  if (user) redirect(homeFor(user.role));
  return (
    <main className="page" style={{ maxWidth: 420 }}>
      <div style={{ textAlign: 'center', marginBottom: 8 }}>
        <img src="/logo.png" alt="ReceiptDesk" width={96} height={96} data-testid="login-logo" />
      </div>
      <h1>เข้าสู่ระบบ ReceiptDesk</h1>
      <LoginForm next={next} />
    </main>
  );
}
