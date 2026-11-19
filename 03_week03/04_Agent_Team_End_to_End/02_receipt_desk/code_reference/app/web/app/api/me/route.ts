/**
 * W5 · GET /api/me — ผู้เข้าสู่ระบบ · บัญชีและบทบาทของตัวเอง
 */
import { requireUser } from '../_lib/auth';
import { handle, json } from '../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ROLE_LABEL = { staff: 'พนักงานบัญชี', lead: 'หัวหน้าทีมบัญชี', owner: 'เจ้าของสำนักงาน', client: 'ลูกค้า' } as const;

export const GET = handle(async (request: Request) => {
  const user = await requireUser(request);
  return json({
    user: {
      id: user.id,
      email: user.email,
      displayName: user.displayName,
      role: user.role,
      roleLabel: ROLE_LABEL[user.role],
      clientId: user.clientId,
      clientName: user.clientName,
    },
    permissions: {
      upload: user.role !== 'owner',
      setUrgent: user.role === 'lead',
      review: user.role === 'staff' || user.role === 'lead',
      reopen: user.role === 'lead',
      overdue: user.role === 'lead' || user.role === 'owner',
      reviewTime: user.role === 'lead' || user.role === 'owner',
      gpuReport: user.role === 'owner',
      portal: user.role === 'client',
    },
  });
});
