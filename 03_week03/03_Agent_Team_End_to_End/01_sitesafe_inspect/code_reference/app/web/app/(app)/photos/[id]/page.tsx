// /photos/{id} — photo with boxes drawn from the stored coordinates (D-08), H, V,
// model result, latest result, override form and override history (FR-07, FR-08, FR-13, FR-14).
// The site check runs on the server first: another site's photo answers 404 (FR-20).
import { notFound } from 'next/navigation';
import Forbidden from '@/components/Forbidden';
import PhotoDetail from '@/components/PhotoDetail';
import { can, requireUser } from '@/components/server/session';
import { findPhotoInScope } from '@/lib/photo-query';
import { RESULTS, RESULT_LABELS } from '@/lib/rules';

export const dynamic = 'force-dynamic';

export default async function PhotoPage({ params }: { params: Promise<{ id: string }> }) {
  const user = await requireUser();
  if (!can(user, 'photo.view')) return <Forbidden />;
  const { id } = await params;
  const photo = await findPhotoInScope(user, id);
  if (!photo || !can(user, 'photo.view', photo.site_id)) notFound();
  return (
    <>
      <h1>รายละเอียดรูป</h1>
      <PhotoDetail
        photoId={photo.id}
        resultOptions={RESULTS.map((r) => ({ value: r, label: RESULT_LABELS[r] }))}
      />
    </>
  );
}
