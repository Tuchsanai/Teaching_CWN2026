// /upload — supervisor uploads many photos at once (FR-01–FR-03, BR-05, BR-06).
// The limits and messages come from lib/rules on the server; the page never
// writes a threshold itself, and POST /api/uploads still makes the final decision.
import Forbidden from '@/components/Forbidden';
import UploadForm from '@/components/UploadForm';
import { can, requireUser } from '@/components/server/session';
import {
  FILE_TOO_LARGE_MESSAGE,
  MAX_FILE_MB,
  MAX_PHOTOS_PER_UPLOAD,
  TOO_FEW_PHOTOS_MESSAGE,
  TOO_MANY_PHOTOS_MESSAGE,
  uploadLimits,
} from '@/lib/rules';

export const dynamic = 'force-dynamic';

export default async function UploadPage() {
  const user = await requireUser();
  if (!can(user, 'upload.create')) return <Forbidden />;
  const limits = uploadLimits();
  return (
    <>
      <h1>อัปโหลดรูปหน้างาน</h1>
      <p className="muted">
        ไซต์: <strong>{user.site_name}</strong> · ส่งได้ครั้งละไม่เกิน {MAX_PHOTOS_PER_UPLOAD} รูป · ไฟล์ JPG หรือ PNG
        ขนาดไม่เกิน {MAX_FILE_MB} MB ต่อรูป
      </p>
      <UploadForm
        limits={limits}
        messages={{
          tooFew: TOO_FEW_PHOTOS_MESSAGE,
          tooMany: TOO_MANY_PHOTOS_MESSAGE,
          tooLarge: FILE_TOO_LARGE_MESSAGE,
        }}
      />
    </>
  );
}
