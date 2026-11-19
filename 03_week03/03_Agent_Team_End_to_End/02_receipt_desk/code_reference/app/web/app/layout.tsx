/**
 * Root layout (B11) — เมนูตามบทบาทอยู่ทุกหน้าที่มี session (DESIGN 9.5 "ทุกหน้า")
 * หน้า /login (ไม่มี session) ไม่มีเมนู
 */
import type { Metadata } from 'next';
import Nav from './_ui/Nav';
import { getPageUser } from './_ui/session';
import './globals.css';

export const metadata: Metadata = {
  title: 'ReceiptDesk',
  description: 'ระบบอ่านใบเสร็จสำหรับสำนักงานบัญชี',
  icons: { icon: '/logo.png', apple: '/logo.png' },
};

export const dynamic = 'force-dynamic';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const user = await getPageUser();
  return (
    <html lang="th">
      <body>
        {user ? <Nav user={user} /> : null}
        {children}
      </body>
    </html>
  );
}
