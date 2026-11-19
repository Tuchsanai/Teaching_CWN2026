// Group 5.1 รับรูป และไฟล์ที่ไม่รับ (BR-05 · BR-06 · FR-01–FR-04 · NFR-04) · ผู้ทำ U-2
// Expected values come from test/TEST-PLAN.md 5.1 and docs/TEST-DATA.md sections 5–6 (computed), never from the site.
import { test, expect, type Page, type TestInfo } from '@playwright/test';
import * as fs from 'node:fs';
import {
  UI, WEB_CONTAINER, reset, login, cookieToContext, fixture, sha256, openBatch, sendFile, upload,
  batchStatus, countPhotos, http, docker, waitHealthy, noGpuForThisFile, evidence, shot,
} from './helpers';

// ---------------- values computed from the plan / test data ----------------
const MB = 1_048_576;
const MAX_BYTES = 15 * MB;                 // 15,728,640 (BR-05)
const MAX_PHOTOS = 50;                     // BR-06
const SITE = 'SITE-A';                     // site of U-2
const JPG_MAGIC = Buffer.from([0xff, 0xd8, 0xff]);
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47]);
const MSG_SIZE = 'ขนาดสูงสุด 15 MB';
const MSG_TYPE = 'รับเฉพาะไฟล์ JPG และ PNG';
const MSG_SPLIT = 'กรุณาแบ่งส่ง';

const F = {
  F1: { file: 'h0_v0_14_9mb.jpg', size: 15_623_782 },
  F2: { file: 'h0_v0_15_0mb.jpg', size: 15_728_640 },
  F3: { file: 'h0_v0_15mb_plus1.jpg', size: 15_728_641 },
  F4: { file: 'h0_v0_15_1mb.jpg', size: 15_833_498 },
  F5: { file: 'h0_v0.jpg' },
  F6: { file: 'h0_v0.png' },
  F7: { file: 'site.gif' },
  F8: { file: 'plan.pdf' },
  F9: { file: 'fake.jpg', size: 1_000 },
};

// ---------------- local helpers (helpers.ts is shared, not edited) ----------------
/** "Today" of the system clock (Asia/Bangkok) as reported by /api/health after reset. */
async function today(): Promise<string> {
  const h = await http('GET', '/api/health');
  return String(h.json?.time || '').slice(0, 10);
}
/** Rows of photos for U-2's site on a date (GET /api/photos total). */
async function rows(cookie: string, date: string): Promise<number> {
  const r = await countPhotos(cookie, `date=${date}&site=${SITE}`);
  expect(r.status, 'GET /api/photos ต้องได้ 200').toBe(200);
  return r.total;
}
/** Number of files in the photos volume of the web container. */
function volumeFiles(): number {
  return Number(docker(`exec ${WEB_CONTAINER} sh -c "find /data/photos -type f | wc -l"`).trim());
}
function head(file: string, n: number) { return fs.readFileSync(fixture(file)).subarray(0, n); }
function hex(b: Buffer) { return [...b].map(x => x.toString(16).padStart(2, '0').toUpperCase()).join(' '); }
function errText(json: any) { return `${json?.error ?? ''} ${json?.message ?? ''}`; }
/** Fresh start for a TC: common step 1 (reset) + login U-2 again (reset logs everyone out). */
async function start(now?: string) {
  await reset(now);
  return login('U2');
}
async function uiAs(page: Page, cookie: string, pathName: string) {
  await cookieToContext(page.context(), cookie);
  await page.goto(UI + pathName);
  await page.waitForLoadState('networkidle');
}
async function imageSha(cookie: string, photoId: string) {
  const r = await http('GET', `/api/photos/${photoId}/image`, { cookie });
  return { status: r.status, sha256: r.status === 200 ? sha256(r.bytes) : null, bytes: r.bytes.length };
}
async function batchShot(testInfo: TestInfo, page: Page, cookie: string, batchId: string | undefined, name: string) {
  await uiAs(page, cookie, batchId ? `/uploads/${batchId}` : '/upload');
  await shot(testInfo, page, name);
}

test.describe('5.1 รับรูป และไฟล์ที่ไม่รับ', () => {
  noGpuForThisFile();

  test('TC-1-01 [P1] ไฟล์ 14.9 MB และ 15.0 MB (เท่าเพดานพอดี) ต้องรับทั้งคู่', async ({ page }, testInfo) => {
    const cookie = await start();
    const date = await today();
    // precondition E-3: fixture sizes exact
    for (const f of [F.F1, F.F2]) expect.soft(fs.statSync(fixture(f.file)).size, `ขนาดไฟล์ ${f.file} ต้องเป็น ${f.size} ไบต์ (E-3)`).toBe(f.size);
    const rowsBefore = await rows(cookie, date);
    const filesBefore = volumeFiles();

    const { batchId, items } = await upload(cookie, [{ path: fixture(F.F1.file) }, { path: fixture(F.F2.file) }]);

    const rowsAfter = await rows(cookie, date);
    const filesAfter = volumeFiles();
    // F-1: 15,623,782 ≤ 15,728,640 → 201 · F-2: 15,728,640 ≤ 15,728,640 → 201
    expect.soft(F.F1.size <= MAX_BYTES && F.F2.size <= MAX_BYTES, 'คำนวณ: ทั้ง 2 ไฟล์ ≤ 15,728,640').toBe(true);
    expect.soft(items[0].status, 'F-1 (15,623,782 ≤ 15,728,640) ต้องได้ 201').toBe(201);
    expect.soft(items[1].status, 'F-2 (15,728,640 ≤ 15,728,640 เท่าเพดาน) ต้องได้ 201').toBe(201);
    expect.soft(items[0].photoId, 'F-1 ต้องได้ photoId').toBeTruthy();
    expect.soft(items[1].photoId, 'F-2 ต้องได้ photoId').toBeTruthy();
    expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +2').toBe(2);

    await evidence(testInfo, 'evidence', {
      date, batchId,
      files: items.map((it, i) => ({ file: [F.F1, F.F2][i].file, bytes: [F.F1, F.F2][i].size, status: it.status, photoId: it.photoId, response: it.json })),
      rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 2 },
      volumeFiles: { before: filesBefore, after: filesAfter, diff: filesAfter - filesBefore },
    });
    await batchShot(testInfo, page, cookie, batchId, 'batch-page-F1-F2');
  });

  test('TC-1-02 [P1] ไฟล์ 15 MB + 1 ไบต์ และ 15.1 MB ต้องถูกปฏิเสธ 413 ไม่เก็บไฟล์', async ({ page }, testInfo) => {
    const cookie = await start();
    const date = await today();
    for (const f of [F.F3, F.F4]) expect.soft(fs.statSync(fixture(f.file)).size, `ขนาดไฟล์ ${f.file} ต้องเป็น ${f.size} ไบต์ (E-3)`).toBe(f.size);
    const rowsBefore = await rows(cookie, date);
    const filesBefore = volumeFiles();

    const { batchId, items } = await upload(cookie, [{ path: fixture(F.F3.file) }, { path: fixture(F.F4.file) }]);

    const rowsAfter = await rows(cookie, date);
    const filesAfter = volumeFiles();
    // F-3: 15,728,640 + 1 > 15,728,640 → 413 · F-4: 15.1 × 1,048,576 = 15,833,497.6 → 15,833,498 > 15,728,640 → 413
    expect.soft(F.F3.size > MAX_BYTES && F.F4.size > MAX_BYTES, 'คำนวณ: ทั้ง 2 ไฟล์ > 15,728,640').toBe(true);
    expect.soft(items[0].status, 'F-3 (15,728,641 > 15,728,640) ต้องได้ 413').toBe(413);
    expect.soft(items[1].status, 'F-4 (15,833,498 > 15,728,640) ต้องได้ 413').toBe(413);
    expect.soft(errText(items[0].json), `F-3 ข้อความต้องมี "${MSG_SIZE}"`).toContain(MSG_SIZE);
    expect.soft(errText(items[1].json), `F-4 ข้อความต้องมี "${MSG_SIZE}"`).toContain(MSG_SIZE);
    expect.soft(items[0].photoId, 'F-3 ต้องไม่ได้ photoId').toBeFalsy();
    expect.soft(items[1].photoId, 'F-4 ต้องไม่ได้ photoId').toBeFalsy();
    expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +0').toBe(0);
    expect.soft(filesAfter - filesBefore, 'ไฟล์ใน volume photos ต้อง +0').toBe(0);

    await evidence(testInfo, 'evidence', {
      date, batchId,
      files: items.map((it, i) => ({ file: [F.F3, F.F4][i].file, bytes: [F.F3, F.F4][i].size, status: it.status, photoId: it.photoId ?? null, response: it.json })),
      rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 0 },
      volumeFiles: { before: filesBefore, after: filesAfter, diff: filesAfter - filesBefore, expected: 0 },
    });
    // UI evidence: select the two oversize files on /upload (no submit) and show what the page says
    await uiAs(page, cookie, '/upload');
    await page.getByTestId('upload-file-input').setInputFiles([fixture(F.F3.file), fixture(F.F4.file)]);
    await page.waitForTimeout(500);
    await shot(testInfo, page, 'upload-page-F3-F4-selected');
    await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-413');
  });

  test('TC-1-03 [P1] รับ JPG และ PNG เก็บต้นฉบับตรง sha256 ทั้งก่อนและหลังรีสตาร์ต web', async ({ page }, testInfo) => {
    test.setTimeout(180_000);
    let cookie = await start();
    const date = await today();
    const files = [F.F5.file, F.F6.file];
    const src = files.map(f => ({ file: f, sha256: sha256(fs.readFileSync(fixture(f))), magic: hex(head(f, 4)) }));
    expect.soft(head(F.F5.file, 3).equals(JPG_MAGIC), 'F-5 ไบต์ต้นไฟล์ต้องเป็น FF D8 FF (E-3)').toBe(true);
    expect.soft(head(F.F6.file, 4).equals(PNG_MAGIC), 'F-6 ไบต์ต้นไฟล์ต้องเป็น 89 50 4E 47 (E-3)').toBe(true);
    const rowsBefore = await rows(cookie, date);

    const { batchId, items } = await upload(cookie, files.map(f => ({ path: fixture(f) })));
    // immediately after 201: read the stored original back
    const before = [] as Awaited<ReturnType<typeof imageSha>>[];
    for (const it of items) before.push(it.photoId ? await imageSha(cookie, it.photoId) : { status: 0, sha256: null, bytes: 0 });
    const rowsAfter = await rows(cookie, date);

    items.forEach((it, i) => {
      expect.soft(it.status, `${files[i]} (ชนิดที่รับ) ต้องได้ 201`).toBe(201);
      expect.soft(before[i].status, `${files[i]} GET /image ทันทีหลัง 201 ต้องได้ 200`).toBe(200);
      expect.soft(before[i].sha256, `${files[i]} sha256 ที่อ่านกลับทันทีหลัง 201 ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
      if (it.json?.sha256 !== undefined) expect.soft(it.json.sha256, `${files[i]} sha256 ในคำตอบ 201 ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
    });
    expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +2').toBe(2);

    // docker compose restart web
    docker(`restart ${WEB_CONTAINER}`);
    await waitHealthy(90_000);
    cookie = await login('U2');
    const after = [] as Awaited<ReturnType<typeof imageSha>>[];
    for (const it of items) after.push(it.photoId ? await imageSha(cookie, it.photoId) : { status: 0, sha256: null, bytes: 0 });
    const rowsAfterRestart = await rows(cookie, date);
    items.forEach((_, i) => {
      expect.soft(after[i].status, `${files[i]} GET /image หลังรีสตาร์ต web ต้องได้ 200`).toBe(200);
      expect.soft(after[i].sha256, `${files[i]} sha256 ที่อ่านกลับหลังรีสตาร์ต ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
    });
    expect.soft(rowsAfterRestart - rowsBefore, 'หลังรีสตาร์ต แถว photos ยัง +2').toBe(2);

    await evidence(testInfo, 'evidence', {
      date, batchId, source: src,
      uploads: items.map((it, i) => ({ file: files[i], status: it.status, photoId: it.photoId, response: it.json })),
      readBackBeforeRestart: before, readBackAfterRestart: after,
      rows: { before: rowsBefore, after: rowsAfter, afterRestart: rowsAfterRestart, expectedDiff: 2 },
      restart: `docker restart ${WEB_CONTAINER} then /api/health db ok, login U-2 again`,
    });
    await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-restart');
    if (items[1].photoId) { await uiAs(page, cookie, `/photos/${items[1].photoId}`); await shot(testInfo, page, 'photo-png-after-restart'); }
  });

  test('TC-1-04 [P1] GIF PDF และไฟล์ข้อความนามสกุล .jpg ต้องได้ 415 ไม่เก็บไฟล์', async ({ page }, testInfo) => {
    const cookie = await start();
    const date = await today();
    const files = [F.F7.file, F.F8.file, F.F9.file];
    expect.soft(fs.statSync(fixture(F.F9.file)).size, 'F-9 fake.jpg ต้องเป็น 1,000 ไบต์ (E-3)').toBe(F.F9.size);
    const magic = files.map(f => ({ file: f, head: hex(head(f, 4)), isJpg: head(f, 3).equals(JPG_MAGIC), isPng: head(f, 4).equals(PNG_MAGIC) }));
    magic.forEach(m => expect.soft(m.isJpg || m.isPng, `${m.file} ไบต์ต้นไฟล์ต้องไม่ใช่ FF D8 FF / 89 50 4E 47 (เงื่อนไขของข้อมูล)`).toBe(false));
    const rowsBefore = await rows(cookie, date);
    const filesBefore = volumeFiles();

    const { batchId, items } = await upload(cookie, files.map(f => ({ path: fixture(f) })));

    const rowsAfter = await rows(cookie, date);
    const filesAfter = volumeFiles();
    items.forEach((it, i) => {
      expect.soft(it.status, `${files[i]} (ไม่ใช่ JPG/PNG ตามเนื้อไฟล์) ต้องได้ 415`).toBe(415);
      expect.soft(errText(it.json), `${files[i]} ข้อความเหตุผลต้องมี "${MSG_TYPE}"`).toContain(MSG_TYPE);
      expect.soft(it.photoId, `${files[i]} ต้องไม่ได้ photoId`).toBeFalsy();
    });
    expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +0').toBe(0);
    expect.soft(filesAfter - filesBefore, 'ไฟล์ใน volume photos ต้อง +0').toBe(0);

    await evidence(testInfo, 'evidence', {
      date, batchId, magic,
      files: items.map((it, i) => ({ file: files[i], status: it.status, photoId: it.photoId ?? null, response: it.json })),
      rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 0 },
      volumeFiles: { before: filesBefore, after: filesAfter, diff: filesAfter - filesBefore, expected: 0 },
    });
    await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-415');
  });

  test('TC-1-05 [P1] จำนวนรูปต่อครั้ง 0 · 1 · 49 · 50 · 51 และไฟล์ที่ 51 ใน batch 50 (ตรวจฝั่ง server)', async ({ page }, testInfo) => {
    test.setTimeout(600_000);
    const ev: any = { note: 'upload_batches ไม่มี API รายการ จึงตรวจทางอ้อม: คำขอถูกปฏิเสธและไม่มี batch_id ในคำตอบ' };
    const jpg = fixture(F.F5.file);
    const nameOf = (i: number) => `h0_v0_${String(i).padStart(3, '0')}.jpg`;

    // (ก) count = 0 และ 51 → 422 · upload_batches +0 · photos +0
    ev.reject = [];
    for (const n of [0, 51]) {
      const cookie = await start();
      const date = await today();
      const rowsBefore = await rows(cookie, date);
      const r = await openBatch(cookie, n);
      const rowsAfter = await rows(cookie, date);
      if (n === 0) {
        expect.soft(r.status, 'count = 0 (0 < 1) ต้องได้ 422').toBe(422);
      } else {
        expect.soft(r.status, 'count = 51 (51 > 50) ต้องได้ 422').toBe(422);
        expect.soft(r.json?.error, 'count = 51 ต้องได้ error TOO_MANY_PHOTOS').toBe('TOO_MANY_PHOTOS');
        expect.soft(errText(r.json), `count = 51 ข้อความต้องมี "${MSG_SPLIT}"`).toContain(MSG_SPLIT);
      }
      expect.soft(r.json?.batch_id, `count = ${n} ต้องไม่ได้ batch_id (upload_batches +0 ทางอ้อม)`).toBeFalsy();
      expect.soft(rowsAfter - rowsBefore, `count = ${n} แถว photos ต้อง +0 (ไม่ใช่ +50)`).toBe(0);
      ev.reject.push({ count: n, status: r.status, response: r.json, rows: { before: rowsBefore, after: rowsAfter } });
    }

    // (ข) count = 1 · 49 · 50 แล้วส่ง h0_v0.jpg ตามจำนวน → แถว +n
    ev.accept = [];
    for (const n of [1, 49, 50]) {
      const cookie = await start();
      const date = await today();
      const rowsBefore = await rows(cookie, date);
      const b = await openBatch(cookie, n);
      expect.soft(b.status, `count = ${n} (1 ≤ ${n} ≤ 50) ต้องได้ 201`).toBe(201);
      const statuses: number[] = [];
      if (b.json?.batch_id) for (let i = 1; i <= n; i++) statuses.push((await sendFile(cookie, b.json.batch_id, jpg, nameOf(i))).status);
      const rowsAfter = await rows(cookie, date);
      expect.soft(statuses.filter(s => s === 201).length, `count = ${n} ไฟล์ที่ได้ 201 ต้องเป็น ${n}`).toBe(n);
      expect.soft(rowsAfter - rowsBefore, `count = ${n} แถว photos ต้อง +${n}`).toBe(n);
      ev.accept.push({ count: n, openStatus: b.status, batchId: b.json?.batch_id, fileStatuses: statuses, rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: n } });
      if (n === 50) await batchShot(testInfo, page, cookie, b.json?.batch_id, 'batch-page-50-photos');
    }

    // (ค) count = 50 ส่งครบ 50 แล้วส่งไฟล์ที่ 51 ใน batch เดิม → 1–50 201 · ไฟล์ที่ 51 422 · batch มี 50 รูป
    {
      const cookie = await start();
      const date = await today();
      const rowsBefore = await rows(cookie, date);
      const b = await openBatch(cookie, MAX_PHOTOS);
      expect.soft(b.status, 'count = 50 ต้องได้ 201').toBe(201);
      const batchId = b.json?.batch_id as string;
      const statuses: number[] = []; const ids: string[] = [];
      let extra: any = null;
      if (batchId) {
        for (let i = 1; i <= MAX_PHOTOS; i++) { const s = await sendFile(cookie, batchId, jpg, nameOf(i)); statuses.push(s.status); if (s.photoId) ids.push(s.photoId); }
        extra = await sendFile(cookie, batchId, jpg, nameOf(51));
      }
      const bs = batchId ? await batchStatus(cookie, batchId) : null;
      const rowsAfter = await rows(cookie, date);
      expect.soft(statuses.filter(s => s === 201).length, 'ไฟล์ 1–50 ต้องได้ 201 ครบ 50').toBe(50);
      expect.soft(extra?.status, 'ไฟล์ที่ 51 > declared_count 50 ต้องได้ 422').toBe(422);
      expect.soft(extra?.photoId, 'ไฟล์ที่ 51 ต้องไม่ได้ photoId').toBeFalsy();
      expect.soft((bs?.json?.photos || []).length, 'batch ต้องมี 50 รูป').toBe(50);
      expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +50').toBe(50);
      ev.overflow = { batchId, fileStatuses: statuses, photoIds: ids, file51: { status: extra?.status, response: extra?.json }, batchPhotos: (bs?.json?.photos || []).length, batchCounts: bs?.json?.counts, rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 50 } };
      await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-file-51');
    }
    await evidence(testInfo, 'evidence', ev);
  });

  test('TC-1-06 [P2] หน้าอัปโหลดไม่มีช่องเลือกไซต์ รูปได้ไซต์ SITE-A และวันที่ 2026-11-19', async ({ page }, testInfo) => {
    const NOW = '2026-11-19T10:00:00+07:00';
    const EXPECT_DATE = '2026-11-19';
    const cookie = await start(NOW);
    const health = await http('GET', '/api/health');
    const rowsBefore = await rows(cookie, EXPECT_DATE);

    await uiAs(page, cookie, '/upload');
    await expect(page.getByTestId('upload-file-input')).toBeVisible();
    const main = page.locator('main');
    const siteControls = {
      selects: await main.locator('select').count(),
      siteTestIds: await main.locator('[data-testid*="site"]').count(),
      siteInputs: await main.locator('input[name*="site" i], select[name*="site" i], [role="combobox"], [role="listbox"]').count(),
    };
    expect.soft(siteControls.selects + siteControls.siteTestIds + siteControls.siteInputs, 'หน้าอัปโหลดต้องไม่มีช่องเลือกไซต์ (0 ช่อง)').toBe(0);
    await shot(testInfo, page, 'upload-page-no-site-select');

    // upload h0_v0.jpg (1 photo) through the page
    await page.getByTestId('upload-file-input').setInputFiles(fixture(F.F5.file));
    await page.getByTestId('upload-submit').click();
    let batchId: string | undefined;
    try {
      await page.waitForURL(u => u.pathname.startsWith('/uploads/'), { timeout: 30_000 });
      batchId = new URL(page.url()).pathname.split('/')[2];
    } catch { /* fall back to the API below */ }
    let via = 'ui';
    let photoId: string | undefined;
    if (batchId) {
      const bs = await batchStatus(cookie, batchId);
      photoId = bs.json?.photos?.[0]?.id;
    }
    if (!photoId) {
      via = 'api (หน้าไม่พาไป /uploads/{batchId})';
      const up = await upload(cookie, [{ path: fixture(F.F5.file) }]);
      batchId = up.batchId; photoId = up.items[0].photoId;
    }
    const detail = photoId ? await http('GET', `/api/photos/${photoId}`, { cookie }) : null;
    const photo = detail?.json?.photo ?? detail?.json;
    const rowsAfter = await rows(cookie, EXPECT_DATE);
    expect.soft(via, 'อัปโหลดผ่านหน้า /upload ต้องพาไปหน้าสถานะ /uploads/{batchId}').toBe('ui');
    expect.soft(detail?.status, 'GET /api/photos/{photoId} ต้องได้ 200').toBe(200);
    expect.soft(photo?.site?.code, 'ไซต์ของรูปต้องเป็น SITE-A (ไซต์ของ U-2)').toBe(SITE);
    expect.soft(photo?.upload_date, `upload_date ต้องเป็น ${EXPECT_DATE}`).toBe(EXPECT_DATE);
    expect.soft(rowsAfter - rowsBefore, 'แถว photos ของ 2026-11-19 SITE-A ต้อง +1').toBe(1);

    await evidence(testInfo, 'evidence', {
      resetNow: NOW, healthTime: health.json?.time, siteControls, via, batchId, photoId,
      photo: photo ? { id: photo.id, site: photo.site, upload_date: photo.upload_date, status: photo.status, original_filename: photo.original_filename } : null,
      rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 1 },
    });
    await batchShot(testInfo, page, cookie, batchId, 'batch-page-one-photo');
  });
});

