/**
 * `npm run migrate` — apply schema.sql and convert an existing database to it
 * without deleting any data (unlike `npm run seed`, which resets everything).
 */
import { ownerPool } from '../lib/db';
import { applySchema } from './migrate';

applySchema(ownerPool())
  .then(async () => {
    console.log(JSON.stringify({ migrated: true }));
    await ownerPool().end();
  })
  .catch((e) => {
    console.error('migrate failed:', e instanceof Error ? e.message : e);
    process.exit(1);
  });
