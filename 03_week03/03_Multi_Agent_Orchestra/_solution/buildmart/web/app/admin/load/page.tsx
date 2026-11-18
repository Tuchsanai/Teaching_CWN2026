// /admin/load (v3) — ผลทดสอบรับโหลด (ตรวจสิทธิ์ที่ admin/layout.tsx)
import LoadDashboard from './LoadDashboard';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Load test — หลังร้าน BuildMart' };

export default function LoadPage() {
  return <LoadDashboard />;
}
