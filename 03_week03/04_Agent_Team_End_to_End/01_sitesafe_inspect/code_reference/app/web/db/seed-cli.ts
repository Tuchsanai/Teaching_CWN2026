/** `npm run seed` — same work as POST /api/test/reset (DESIGN §7.2). */
import { ownerPool, pool } from '../lib/db';
import { resetAndSeed } from './seed';

resetAndSeed()
  .then(async (r) => {
    console.log(JSON.stringify({ reset: true, ...r }));
    await ownerPool().end();
    if (process.env.DATABASE_URL) await pool().end().catch(() => undefined);
  })
  .catch((e) => {
    console.error('seed failed:', e instanceof Error ? e.message : e);
    process.exit(1);
  });
