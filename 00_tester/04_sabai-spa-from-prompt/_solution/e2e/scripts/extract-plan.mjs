// อ่านตารางหัวข้อ 5 ของ ../TEST-PLAN.md → plan-cases.json (ใช้ตั้งชื่อ test, tag, annotation และสร้างรายงาน)
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const md = readFileSync(join(root, '..', 'TEST-PLAN.md'), 'utf8');
const sec5 = md.split('## 5. Test cases')[1].split('### สรุปจำนวน')[0];
const clean = (s) => s.replace(/\*\*/g, '').replace(/`/g, '').trim();

// รหัสโมดูลสั้นสำหรับ tag (พิมพ์ใน PowerShell ง่าย) ↔ ชื่อโมดูลในแผน
const API_ONLY = ['TC-BOOK-06', 'TC-SEC-01', 'TC-SEC-02', 'TC-SEC-03', 'TC-SEC-04', 'TC-SEC-05']; // หัวข้อ 6.2 กติกาข้อ 3
const cases = [];
for (const line of sec5.split('\n')) {
  if (!line.startsWith('| TC-')) continue;
  const c = line.split('|').slice(1, -1).map(clean);
  const [id, module, what, refs, technique, priority, data, expected, source] = c;
  cases.push({
    id, module, moduleCode: id.split('-')[1], what: what.replace(/\s*—\s*\*[^*]*\*\s*$/, '').replace(/\s*⚠️\s*$/, ''), refs, technique, priority, data, expected, source,
    apiOnly: API_ONLY.includes(id),
  });
}
writeFileSync(join(root, 'plan-cases.json'), JSON.stringify(cases, null, 2) + '\n');
const p = (x) => cases.filter((c) => c.priority === x).length;
console.log(`plan-cases.json: ${cases.length} TC · P1 ${p('P1')} · P2 ${p('P2')} · P3 ${p('P3')}`);
