/** `/unreadable` — อ่านไม่ได้ ให้คนพิมพ์เอง · พนักงาน · หัวหน้าทีม · เจ้าของ (DESIGN 9.1 · FR-16 · FR-17) */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import UnreadableView from './UnreadableView';

export const dynamic = 'force-dynamic';

export default async function UnreadablePage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/unreadable'], '/unreadable');
  if (!allowed) return <Forbidden user={user} page="อ่านไม่ได้" />;
  return (
    <main className="page">
      <h1>อ่านไม่ได้ ให้คนพิมพ์เอง</h1>
      <p className="muted">
        ใบที่ระบบอ่านไม่สำเร็จครบ 3 ครั้ง (Dead-letter Queue) ไม่ถูกส่งกลับไปอ่านใหม่ เปิดใบเพื่อพิมพ์ 5 ช่องเองแล้วยืนยัน
        {user.role === 'owner' ? ' (บัญชีเจ้าของดูได้อย่างเดียว)' : ''}
      </p>
      <UnreadableView />
    </main>
  );
}
