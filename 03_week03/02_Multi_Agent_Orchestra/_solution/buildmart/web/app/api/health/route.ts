import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { getChannel, instanceId } from '@/lib/amqp';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  let db = false;
  let mq = false;
  try {
    await query('SELECT 1');
    db = true;
  } catch {}
  try {
    await Promise.race([getChannel(), new Promise((_, rej) => setTimeout(() => rej(new Error('t')), 3000))]);
    mq = true;
  } catch {}
  return NextResponse.json({ ok: db, db, mq, instanceId }, { status: db ? 200 : 503 });
}
