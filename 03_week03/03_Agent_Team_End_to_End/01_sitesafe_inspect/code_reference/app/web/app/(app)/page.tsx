import { redirect } from 'next/navigation';
import { homePathFor, requireUser } from '@/components/server/session';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const user = await requireUser();
  redirect(homePathFor(user));
}
