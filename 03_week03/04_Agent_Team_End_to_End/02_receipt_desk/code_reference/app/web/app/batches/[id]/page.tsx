/** `/batches/[id]` — ชุด 1 ชุด (สถานะทีละใบ) · พนักงาน · หัวหน้าทีม (ปุ่มงานด่วน) · เจ้าของ (DESIGN 9.1 · FR-07 · FR-18) */
import Forbidden from '../../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../../_ui/session';
import BatchView from './BatchView';

export const dynamic = 'force-dynamic';

export default async function BatchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/batches'], `/batches/${id}`);
  if (!allowed) return <Forbidden user={user} page="ชุดใบเสร็จ" />;
  return (
    <main className="page">
      <BatchView id={id} isLead={user.role === 'lead'} />
    </main>
  );
}
