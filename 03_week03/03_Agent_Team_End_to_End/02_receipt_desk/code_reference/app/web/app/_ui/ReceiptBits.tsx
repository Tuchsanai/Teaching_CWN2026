/**
 * ชิ้นส่วนที่ใช้ร่วมในตารางใบเสร็จของสำนักงาน (/batches/[id] · /receipts)
 * - receipt-status-{id}: ข้อความสถานะภาษาไทย · attribute `data-status` = รหัสสถานะ (queued|processing|review|confirmed|unreadable)
 * - receipt-flag-{id}: มีเฉพาะใบติดธง (FR-09) ข้อความ = เหตุผลของธง · `data-flags` = low-confidence และ/หรือ mismatch
 */

export interface Flags {
  lowConfidence: boolean;
  mismatch: boolean;
  flagged: boolean;
  reasons: string[];
}

export function StatusCell({ id, status, label }: { id: string; status: string; label: string }) {
  return (
    <span data-testid={`receipt-status-${id}`} data-status={status} className={`badge status-${status}`}>
      {label}
    </span>
  );
}

export function FlagCell({ id, flags }: { id: string; flags: Flags | null | undefined }) {
  if (!flags?.flagged) return null;
  const kinds = [flags.lowConfidence ? 'low-confidence' : null, flags.mismatch ? 'mismatch' : null].filter(Boolean).join(' ');
  return (
    <span data-testid={`receipt-flag-${id}`} data-flags={kinds} className="badge warn" title={flags.reasons.join(' · ')}>
      ระบบไม่แน่ใจ{flags.reasons.length ? `: ${flags.reasons.join(' · ')}` : ''}
    </span>
  );
}
