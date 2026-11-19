// /uploads/{batchId} — status of every accepted photo, refreshed every 2 seconds
// so each result appears as soon as that photo is done (FR-05, FR-06, FR-10).
import Forbidden from '@/components/Forbidden';
import BatchStatus from '@/components/BatchStatus';
import { can, requireUser } from '@/components/server/session';
import { STATUS_LABELS } from '@/lib/rules';

export const dynamic = 'force-dynamic';

export default async function BatchPage({ params }: { params: Promise<{ batchId: string }> }) {
  const user = await requireUser();
  if (!can(user, 'upload.view')) return <Forbidden />;
  const { batchId } = await params;
  return (
    <>
      <h1>สถานะการตรวจรูป</h1>
      <BatchStatus batchId={batchId} statusLabels={{ ...STATUS_LABELS }} />
    </>
  );
}
