// db/migrate.ts: databases created with limits inside CHECK constraints are converted
// to the positive-value checks of schema.sql, without touching any row.
import { describe, expect, it } from 'vitest';
import { relaxLegacyChecks } from '@/db/migrate';

type Con = { conname: string; def: string };

function fakeDb(state: Record<string, Con[]>) {
  const log: string[] = [];
  const db = {
    async query(sql: string, params?: unknown[]) {
      log.push(sql.replace(/\s+/g, ' ').trim());
      if (sql.includes('FROM pg_constraint')) {
        const table = String(params?.[0]).replace('public.', '');
        return { rows: state[`${table}.${params?.[1]}`] ?? [] };
      }
      return { rows: [] };
    },
  };
  return { db: db as never, log };
}

describe('relaxLegacyChecks', () => {
  it('replaces CHECKs that repeat the BR-05 / BR-06 limits', async () => {
    const { db, log } = fakeDb({
      'upload_batches.declared_count': [
        { conname: 'upload_batches_declared_count_check', def: 'CHECK (((declared_count >= 1) AND (declared_count <= 50)))' },
      ],
      'photos.size_bytes': [
        { conname: 'photos_size_bytes_check', def: 'CHECK (((size_bytes >= 1) AND (size_bytes <= 15728640)))' },
      ],
    });
    expect(await relaxLegacyChecks(db)).toEqual(['upload_batches.declared_count', 'photos.size_bytes']);
    const ddl = log.filter((s) => s.startsWith('ALTER'));
    expect(ddl).toEqual([
      'ALTER TABLE upload_batches DROP CONSTRAINT "upload_batches_declared_count_check"',
      'ALTER TABLE upload_batches ADD CONSTRAINT "upload_batches_declared_count_check" CHECK ((declared_count >= 1))',
      'ALTER TABLE photos DROP CONSTRAINT "photos_size_bytes_check"',
      'ALTER TABLE photos ADD CONSTRAINT "photos_size_bytes_check" CHECK ((size_bytes >= 1))',
    ]);
    expect(log.some((s) => /DELETE|TRUNCATE|UPDATE/i.test(s))).toBe(false);
  });

  it('does nothing on a database that is already current', async () => {
    const { db, log } = fakeDb({
      'upload_batches.declared_count': [{ conname: 'upload_batches_declared_count_check', def: 'CHECK ((declared_count >= 1))' }],
      'photos.size_bytes': [{ conname: 'photos_size_bytes_check', def: 'CHECK ((size_bytes >= 1))' }],
    });
    expect(await relaxLegacyChecks(db)).toEqual([]);
    expect(log.filter((s) => s.startsWith('ALTER'))).toEqual([]);
  });
});
