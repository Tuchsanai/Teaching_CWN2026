import * as fs from 'fs';
import * as path from 'path';
export const ROOT = path.resolve(__dirname, '..', '..', '..', '..');   // 02_receipt_desk
function readVar(file: string, key: string): string {
  try {
    const m = fs.readFileSync(file, 'utf8').match(new RegExp(`^${key}=(.*)$`, 'm'));
    return m ? m[1].trim() : '';
  } catch { return ''; }
}
export function loadTokens() {
  process.env.MOCK_RESET_TOKEN ||= readVar(path.join(ROOT, 'app', '.env.mock'), 'TEST_RESET_TOKEN');
  process.env.REAL_RESET_TOKEN ||= readVar(path.join(ROOT, 'app', '.env'), 'TEST_RESET_TOKEN');
}
