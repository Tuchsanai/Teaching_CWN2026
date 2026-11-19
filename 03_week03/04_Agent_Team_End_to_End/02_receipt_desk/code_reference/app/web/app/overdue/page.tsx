/** `/overdue` — ค้างเกินกำหนด · หัวหน้าทีม · เจ้าของ (พนักงาน → ไม่มีสิทธิ์) (DESIGN 9.1 · FR-21 · BR-13) */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import OverdueView from './OverdueView';

export const dynamic = 'force-dynamic';

export default async function OverduePage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/overdue'], '/overdue');
  if (!allowed) return <Forbidden user={user} page="ค้างเกินกำหนด" />;
  return (
    <main className="page">
      <h1>งานปกติค้างเกินกำหนด</h1>
      <p className="muted">ใบของงานปกติที่ยังรออ่านหรือกำลังอ่าน และรับมาแล้วเกิน 120 นาที เรียงจากรอนานที่สุด</p>
      <OverdueView />
    </main>
  );
}
