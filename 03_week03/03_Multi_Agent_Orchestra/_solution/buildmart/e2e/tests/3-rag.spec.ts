// 📄 RAG R01–R08 — ข้อมูลมีแค่ใน PDF · ต้องมีป้าย chat-cite ชี้ไฟล์ที่ถูก
import path from 'node:path';
import type { Page } from '@playwright/test';
import { bmCase, expect, intro, ask, expectAnswer, expectCite, say, show, hold, highlight, adminLogin, attachJson, ROOT, type Check } from './_bm';

function rag(id: string, q: string, checks: Check[], file: string) {
  bmCase(id, async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    const ans = await ask(page, info, q);
    expectAnswer(ans.text, checks);
    expectCite(ans, file);
  });
}

// ai: คำตอบผ่าน norm() แล้ว (comma/เลขไทย/ช่องว่าง) · ยอมคำพ้องที่ความหมายเดียวกัน · cite ต้องมีไฟล์ที่ถูกเสมอ (ข้อกำหนดของ RAG)
rag('R01', 'ปูนซีเมนต์เก็บได้นานแค่ไหนครับ', [{ mock: /3\s*เดือน/, ai: /(^|\D)3\s*เดือน|สามเดือน|90\s*วัน/ }], 'BM-DS-CEM.pdf');
rag('R02', 'สีทาภายนอกรับประกันกี่ปี', [{ mock: /8\s*ปี/, ai: /(^|\D)8\s*ปี|แปดปี/ }], 'BM-DS-PNT.pdf');
rag('R03', 'กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม', [/ได้/, /0\.5\s*%|R\s?10/], 'BM-DS-TIL.pdf');
rag('R04', 'ซื้อปูนไปแล้วเปิดถุง ขอคืนได้ไหม', [/คืน(?:สินค้า)?ไม่ได้|ไม่สามารถ(?:ขอ|รับ)?(?:คืน|เปลี่ยน)|ไม่รับคืน|ไม่(?:รับ)?(?:เปลี่ยน)?คืน/], 'BM-POLICY.pdf');
rag('R05', 'ทาบเหล็ก DB12 ต้องยาวเท่าไร', [/(^|\D)48(\D|$)/], 'BM-DS-STL.pdf');
rag('R06', 'สาย THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ แล้วเบรกเกอร์ 16A ราคาเท่าไร', [/16/, /(^|\D)145(\D|$)/], 'BM-DS-ELC-PIP.pdf');
// R08 อ่านจากตารางหัว 2 ชั้น (ตารางที่ 5 ใน BM-DS-CEM: 60x60 → เกรียงฟัน 10 มม. → 5.5 กก./ตร.ม.) · เล่นก่อน R07 (R07 อัปโหลด/ลบเอกสาร)
rag(
  'R08',
  'ปูกระเบื้อง 60x60 ด้วยปูนกาว ต้องใช้เกรียงฟันกี่มิล และใช้ปูนกาวกี่กิโลต่อตารางเมตร',
  [/(^|[^\d.x])10(?![\d.x])/, /(^|[^\d.])5\.5(?!\d)/],
  'BM-DS-CEM.pdf',
);

const PROMO = 'BM-PROMO-NOV.pdf';
const PROMO_PATH = path.join(ROOT, 'tests', 'fixtures', PROMO);

/** ลบ BM-PROMO-NOV.pdf ทิ้ง (ปุ่มลบในหน้า /admin/docs ถ้าไม่ได้ใช้ API) */
async function removePromo(page: Page, viaUi: boolean) {
  const row = page.locator(`[data-testid="doc-row"][data-filename="${PROMO}"]`);
  if (viaUi) {
    await page.goto('/admin/docs');
    if (await row.count()) {
      await say(page, `ล้างข้อมูล: ลบ ${PROMO} ออกจากระบบ`);
      await row.getByTestId('doc-delete').click();
      await row.getByTestId('doc-delete-confirm').click();
      await expect(row).toHaveCount(0, { timeout: 15_000 });
      await hold(page, 2000);
      return;
    }
  }
  // fallback: API (cookie bm_admin อยู่ใน context เดียวกัน)
  const r = await page.request.get('/api/admin/docs');
  if (!r.ok()) return;
  const j = await r.json();
  const list = Array.isArray(j) ? j : j.docs || j.items || [];
  for (const d of list) if (d.filename === PROMO) await page.request.delete(`/api/admin/docs/${d.id}`);
}

bmCase(
  'R07',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    await adminLogin(page);
    await removePromo(page, false); // เผื่อรอบก่อนค้าง
    try {
      await page.goto('/admin/docs');
      await say(page, `อัปโหลด ${PROMO} เข้าคิว rag.ingest`);
      await show(page, page.getByTestId('doc-row'), 2000);
      await page.getByTestId('doc-upload-input').setInputFiles(PROMO_PATH);
      await hold(page, 1000);
      await page.getByTestId('doc-upload-btn').click();
      const row = page.locator(`[data-testid="doc-row"][data-filename="${PROMO}"]`);
      await expect(row).toBeVisible({ timeout: 20_000 });
      await say(page, 'รอ rag-worker อ่าน PDF → ตัด chunk → ทำเวกเตอร์ (queued → processing → ready)');
      await highlight(row);
      const t0 = Date.now();
      await expect(row.getByTestId('doc-status')).toHaveAttribute('data-status', 'ready', { timeout: 180_000 });
      const chunks = (await row.getByTestId('doc-chunks').innerText().catch(() => '')).trim();
      await attachJson(info, 'checked', { upload: PROMO, status: 'ready', chunks, ingestMs: Date.now() - t0 });
      await say(page, `สถานะ ready · ${chunks} chunk`);
      await show(page, row);

      await page.goto('/');
      const ans = await ask(page, info, 'เดือนพฤศจิกายนมีโปรอะไร');
      expectAnswer(ans.text, [/ลวดผูกเหล็ก/]);
      expectCite(ans, PROMO);
    } finally {
      await removePromo(page, true).catch(() => removePromo(page, false));
    }
  },
  { timeout: 8 * 60_000 },
);
