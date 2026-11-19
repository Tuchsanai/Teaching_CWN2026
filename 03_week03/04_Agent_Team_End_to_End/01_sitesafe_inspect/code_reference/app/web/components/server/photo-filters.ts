// Builds the props of <PhotoList> on the server: filter values from the URL and
// option labels from lib/rules (client code never imports lib/rules at runtime).
import type { SessionUser } from '@/lib/auth';
import { PHOTO_STATUSES, RESULTS, RESULT_LABELS, STATUS_LABELS } from '@/lib/rules';
import type { Filters, Option } from '@/components/PhotoList';
import { visibleSites } from './session';

type SP = Record<string, string | string[] | undefined>;

function one(v: string | string[] | undefined): string {
  return typeof v === 'string' ? v : '';
}

export async function photoListProps(user: SessionUser, sp: SP) {
  const pageNum = Number(one(sp.page) || '1');
  const initial: Filters = {
    date: one(sp.date),
    site: one(sp.site),
    result: one(sp.result).toUpperCase(),
    status: one(sp.status).toUpperCase(),
    page: Number.isSafeInteger(pageNum) && pageNum > 0 ? pageNum : 1,
  };
  const sites: Option[] = (await visibleSites(user)).map((s) => ({ value: s.code, label: s.name }));
  const resultOptions: Option[] = RESULTS.map((r) => ({ value: r, label: RESULT_LABELS[r] }));
  const statusOptions: Option[] = PHOTO_STATUSES.map((s) => ({ value: s, label: STATUS_LABELS[s] }));
  const key = JSON.stringify(initial);
  return { initial, sites, resultOptions, statusOptions, resultLabels: { ...RESULT_LABELS }, key };
}
