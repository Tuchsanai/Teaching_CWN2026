/** `/upload` — อัปโหลดชุด · พนักงาน · หัวหน้าทีม (ตั้งด่วนได้) (DESIGN 9.1) */
import Forbidden from '../_ui/Forbidden';
import { PAGE_ROLES, requirePageUser } from '../_ui/session';
import UploadForm from './UploadForm';

export const dynamic = 'force-dynamic';

export default async function UploadPage() {
  const { user, allowed } = await requirePageUser(PAGE_ROLES['/upload'], '/upload');
  if (!allowed) return <Forbidden user={user} page="อัปโหลดชุด" />;
  return (
    <main className="page">
      <h1>อัปโหลดชุดใบเสร็จ</h1>
      <UploadForm canSetUrgent={user.role === 'lead'} />
    </main>
  );
}
