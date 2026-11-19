/** `/reports` — ไฟล์สรุปรายเดือน CSV · พนักงาน · หัวหน้าทีม · เจ้าของ (DESIGN 9.1 · FR-28 · BR-14) */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import ReportsView from './ReportsView';

export const dynamic = 'force-dynamic';

export default async function ReportsPage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/reports'], '/reports');
  if (!allowed) return <Forbidden user={user} page="สรุปรายเดือน" />;
  return (
    <main className="page">
      <h1>ไฟล์สรุปรายเดือน</h1>
      <p className="muted">
        นับเฉพาะใบที่ยืนยันแล้ว และนับเดือนตามวันที่บนใบเสร็จ (ไม่ใช่วันที่อัปโหลด) · ไฟล์ CSV เข้ารหัส UTF-8 เปิดใน Excel ได้
      </p>
      <ReportsView />
    </main>
  );
}
