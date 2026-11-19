// DESIGN §8, §9: lib/rules is the only file that reads the service-mode variable and the only place
// that holds the BR-05 byte limit. Scans every source file of web/ (code and SQL).
import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

const ROOT = path.resolve(__dirname, '..');
const SKIP_DIRS = new Set(['node_modules', '.next', 'tests', '.git']);
const EXTS = new Set(['.ts', '.tsx', '.js', '.mjs', '.cjs', '.sql']);
const RULES_FILE = path.join('lib', 'rules.ts');

function sourceFiles(dir: string, out: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const abs = path.join(dir, name);
    if (statSync(abs).isDirectory()) {
      if (!SKIP_DIRS.has(name)) sourceFiles(abs, out);
    } else if (EXTS.has(path.extname(name)) && !name.endsWith('.d.ts')) {
      out.push(path.relative(ROOT, abs));
    }
  }
  return out;
}

const files = sourceFiles(ROOT);

function filesMatching(re: RegExp): string[] {
  return files.filter((f) => re.test(readFileSync(path.join(ROOT, f), 'utf8'))).sort();
}

describe('single source of the Business Rules', () => {
  it('scans the web sources', () => {
    expect(files).toContain(RULES_FILE);
    expect(files).toContain(path.join('db', 'schema.sql'));
  });

  it('the service-mode variable appears only in lib/rules.ts', () => {
    // Name built from parts so that this test file itself never matches a search for it.
    const name = ['BUG', 'MODE'].join('_');
    expect(filesMatching(new RegExp(`\\b${name}\\b`))).toEqual([RULES_FILE]);
  });

  it('the 15 MB limit in bytes appears only in lib/rules.ts', () => {
    expect(filesMatching(/15_?728_?640|1_?048_?576/)).toEqual([RULES_FILE]);
  });

  it('the database schema repeats no upload limit', () => {
    const sql = readFileSync(path.join(ROOT, 'db', 'schema.sql'), 'utf8');
    expect(sql).not.toMatch(/declared_count[^,\n]*\b50\b/);
    expect(sql).not.toMatch(/size_bytes[^,\n]*BETWEEN/i);
  });
});
