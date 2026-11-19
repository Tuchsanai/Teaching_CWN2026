/**
 * `/receipts` — รายการใบ (กรองสถานะ · ธง · ลูกค้า) · พนักงาน · หัวหน้าทีม · เจ้าของ (DESIGN 9.1 · FR-09 · FR-10)
 * หมายเหตุ: `/receipts/[id]` (หน้าตรวจแก้) เป็นของบล็อก B12 ไม่อยู่ในไฟล์นี้
 */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import ReceiptsView from './ReceiptsView';

export const dynamic = 'force-dynamic';

type SP = Promise<Record<string, string | string[] | undefined>>;

export default async function ReceiptsPage({ searchParams }: { searchParams: SP }) {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/receipts'], '/receipts');
  if (!allowed) return <Forbidden user={user} page="รายการใบ" />;
  const sp = await searchParams;
  const one = (v: string | string[] | undefined) => (typeof v === 'string' ? v : '');
  return (
    <main className="page">
      <h1>รายการใบเสร็จ</h1>
      <ReceiptsView
        initial={{ status: one(sp.status), flagged: one(sp.flagged) === 'true', clientId: one(sp.clientId) }}
      />
    </main>
  );
}
