/** `/batches` — รายการชุด + ยอดตรวจนับ · พนักงาน · หัวหน้าทีม · เจ้าของ (DESIGN 9.1 · FR-08) */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import BatchesView from './BatchesView';

export const dynamic = 'force-dynamic';

export default async function BatchesPage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/batches'], '/batches');
  if (!allowed) return <Forbidden user={user} page="รายการชุด" />;
  return (
    <main className="page">
      <h1>ชุดใบเสร็จ</h1>
      <BatchesView />
    </main>
  );
}
