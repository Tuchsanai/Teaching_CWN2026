// /photos/problems — only photos whose latest result is FAIL or WARN (FR-11).
import Forbidden from '@/components/Forbidden';
import PhotoList from '@/components/PhotoList';
import { photoListProps } from '@/components/server/photo-filters';
import { can, requireUser } from '@/components/server/session';

export const dynamic = 'force-dynamic';

export default async function ProblemsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const user = await requireUser();
  if (!can(user, 'photo.view')) return <Forbidden />;
  const { key, ...props } = await photoListProps(user, await searchParams);
  return (
    <>
      <h1>รูปที่มีปัญหา</h1>
      <p className="muted">แสดงเฉพาะรูปที่ผลล่าสุดเป็น “{props.resultLabels.FAIL}” และ “{props.resultLabels.WARN}”</p>
      <PhotoList key={key} mode="problems" {...props} />
    </>
  );
}
