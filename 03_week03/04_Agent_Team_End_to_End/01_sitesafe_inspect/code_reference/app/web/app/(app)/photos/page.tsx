// /photos — every photo, filterable by date, site, result and status (FR-12).
import Forbidden from '@/components/Forbidden';
import PhotoList from '@/components/PhotoList';
import { photoListProps } from '@/components/server/photo-filters';
import { can, requireUser } from '@/components/server/session';

export const dynamic = 'force-dynamic';

export default async function PhotosPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const user = await requireUser();
  if (!can(user, 'photo.view')) return <Forbidden />;
  const { key, ...props } = await photoListProps(user, await searchParams);
  return (
    <>
      <h1>รูปทั้งหมด</h1>
      <PhotoList key={key} mode="all" {...props} />
    </>
  );
}
