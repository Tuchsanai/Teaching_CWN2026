import type { Metadata, Viewport } from 'next';
import Header from '@/components/Header';
import ChatWidget from '@/components/ChatWidget';
import Interactions from '@/components/Interactions';
import './globals.css';

export const metadata: Metadata = {
  title: 'บ้านช่าง BuildMart — ร้านวัสดุก่อสร้างออนไลน์',
  description: 'ปูน เหล็ก อิฐ กระเบื้อง สี ประปา ไฟฟ้า ราคาส่งตามจำนวน ส่งถึงหน้างาน',
};
export const viewport: Viewport = { width: 'device-width', initialScale: 1, themeColor: '#10141C', colorScheme: 'dark' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@500;600;700&family=Sarabun:wght@400;500;600;700;800&display=swap"
        />
      </head>
      <body>
        <div className="strip no-print">
          <div className="container">
            เปิด จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00 · LINE @buildmart-demo
          </div>
        </div>
        <Header />
        <main className="container">{children}</main>
        <footer className="site-footer no-print">
          <div className="container">
            <div>
              <b>บ้านช่าง BuildMart</b> · ราคาสินค้ายังไม่รวม VAT 7%
            </div>
            <div>ลาดกระบัง 02-111-0001 · บางนา 02-111-0002 · รังสิต 02-111-0003</div>
          </div>
        </footer>
        {/* แชทบอทลอยมุมขวาล่าง (C1) */}
        <ChatWidget />
        {/* เอฟเฟกต์การ์ดเอียง + reveal ตอนเลื่อน (v3) */}
        <Interactions />
      </body>
    </html>
  );
}
