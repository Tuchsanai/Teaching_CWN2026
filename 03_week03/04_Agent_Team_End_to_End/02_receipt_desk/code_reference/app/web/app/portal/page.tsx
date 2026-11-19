/**
 * `/portal` — หน้าลูกค้า: ส่งใบ · ใบของร้าน · สรุปแยกหมวด · ลูกค้าเท่านั้น (DESIGN 9.1 · FR-24 – FR-27 · FR-29)
 * ข้อมูลทุกอย่างมาจาก API ที่กรอง client_id ของ session ที่ server (ร้านอื่นได้ 404) และไม่มีตัวเลขของใบที่ยังไม่ยืนยัน
 */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import PortalView from './PortalView';

export const dynamic = 'force-dynamic';

export default async function PortalPage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/portal'], '/portal');
  if (!allowed) return <Forbidden user={user} page="ลูกค้า" />;
  return (
    <main className="page">
      <h1>ใบเสร็จของ {user.clientName ?? 'ร้าน'}</h1>
      <PortalView />
    </main>
  );
}
