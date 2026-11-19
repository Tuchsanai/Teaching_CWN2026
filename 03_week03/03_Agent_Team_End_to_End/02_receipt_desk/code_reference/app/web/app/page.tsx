/** `/` → หน้าแรกของบทบาท (ไม่มี session → /login) */
import { redirect } from 'next/navigation';
import { getPageUser, homeFor } from './_ui/session';

export const dynamic = 'force-dynamic';

export default async function Home() {
  const user = await getPageUser();
  redirect(user ? homeFor(user.role) : '/login');
}
