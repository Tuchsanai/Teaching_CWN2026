/**
 * `/insights` — เวลาตรวจ · GPU 1 เทียบ 2 ใบ (DESIGN 9.1 · FR-30 · FR-31 · NFR-08 · NFR-09)
 * หัวหน้าทีม: เฉพาะเวลาตรวจ · เจ้าของ: เวลาตรวจ + GPU · พนักงานและลูกค้า: ไม่มีสิทธิ์
 */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import InsightsView from './InsightsView';

export const dynamic = 'force-dynamic';

export default async function InsightsPage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/insights'], '/insights');
  if (!allowed) return <Forbidden user={user} page="เวลาตรวจ · GPU" />;
  return (
    <main className="page">
      <h1>{user.role === 'owner' ? 'เวลาตรวจ · GPU 1 เทียบ 2 ใบ' : 'เวลาตรวจของทีม'}</h1>
      <InsightsView showGpu={user.role === 'owner'} />
    </main>
  );
}
