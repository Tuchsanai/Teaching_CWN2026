/** JSON shapes returned by the API (shared by several Route Handlers). */
import type { SessionUser } from './auth';
import { RESULT_LABELS, STATUS_LABELS, type PhotoStatus, type Result } from './rules';

export const ROLE_LABELS: Record<SessionUser['role'], string> = {
  manager: 'ผู้จัดการความปลอดภัย',
  supervisor: 'หัวหน้างานไซต์',
  executive: 'ผู้บริหาร',
};

export function publicUser(u: SessionUser) {
  return {
    id: u.id,
    email: u.email,
    full_name: u.full_name,
    role: u.role,
    role_label: ROLE_LABELS[u.role],
    site: u.site_id === null ? null : { id: u.site_id, code: u.site_code, name: u.site_name },
  };
}

/** Columns selected for photo rows (alias p = photos, s = sites). */
export const PHOTO_COLUMNS = `
  p.id, p.batch_id, p.site_id, s.code AS site_code, s.name AS site_name,
  to_char(p.upload_date, 'YYYY-MM-DD') AS upload_date,
  p.original_filename, p.mime, p.size_bytes, p.status, p.fail_reason,
  p.model_h, p.model_v, p.model_result, p.current_result, p.is_overridden,
  p.model_version, p.conf_threshold, p.image_w, p.image_h,
  p.accepted_at, p.finished_at`;

export type PhotoRow = {
  id: string;
  batch_id: string;
  site_id: number;
  site_code: string;
  site_name: string;
  upload_date: string;
  original_filename: string;
  mime: string;
  size_bytes: string | number;
  status: PhotoStatus;
  fail_reason: string | null;
  model_h: number | null;
  model_v: number | null;
  model_result: Result | null;
  current_result: Result | null;
  is_overridden: boolean;
  model_version: string | null;
  conf_threshold: string | number | null;
  image_w: number | null;
  image_h: number | null;
  accepted_at: Date;
  finished_at: Date | null;
};

export function photoView(r: PhotoRow) {
  return {
    id: r.id,
    batch_id: r.batch_id,
    site: { id: r.site_id, code: r.site_code, name: r.site_name },
    upload_date: r.upload_date,
    original_filename: r.original_filename,
    mime: r.mime,
    size_bytes: Number(r.size_bytes),
    status: r.status,
    status_label: STATUS_LABELS[r.status],
    fail_reason: r.fail_reason,
    h: r.model_h,
    v: r.model_v,
    model_result: r.model_result,
    model_result_label: r.model_result ? RESULT_LABELS[r.model_result] : null,
    current_result: r.current_result,
    current_result_label: r.current_result ? RESULT_LABELS[r.current_result] : null,
    is_overridden: r.is_overridden,
    model_version: r.model_version,
    conf_threshold: r.conf_threshold === null ? null : Number(r.conf_threshold),
    image_w: r.image_w,
    image_h: r.image_h,
    accepted_at: r.accepted_at,
    finished_at: r.finished_at,
    image_url: `/api/photos/${r.id}/image`,
  };
}

export const DETECTION_LABELS: Record<string, string> = {
  NO_HARDHAT: 'ไม่ใส่หมวก',
  NO_VEST: 'ไม่ใส่เสื้อสะท้อนแสง',
};
