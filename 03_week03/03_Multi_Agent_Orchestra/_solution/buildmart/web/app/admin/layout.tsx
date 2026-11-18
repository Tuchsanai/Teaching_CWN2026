// app/admin/layout.tsx (B3) — ทุกหน้า /admin/** : ยังไม่ล็อกอิน → ฟอร์มรหัสผ่าน · ล็อกอินแล้ว → แถบเมนูหลังร้าน + เนื้อหา
import type { Metadata } from 'next';
import { isAdmin } from '@/app/api/admin/_auth';
import AdminLogin from './AdminLogin';
import AdminNav from './AdminNav';
import './admin.css';

export const dynamic = 'force-dynamic';
export const metadata: Metadata = { title: 'หลังร้าน — บ้านช่าง BuildMart' };

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  if (!isAdmin()) return <AdminLogin />;
  return (
    <div className="adm">
      <AdminNav />
      {children}
    </div>
  );
}
