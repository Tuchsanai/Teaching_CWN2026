# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 51_upload.spec.ts >> 5.1 รับรูป และไฟล์ที่ไม่รับ >> TC-1-05 [P1] จำนวนรูปต่อครั้ง 0 · 1 · 49 · 50 · 51 และไฟล์ที่ 51 ใน batch 50 (ตรวจฝั่ง server)
- Location: tests\51_upload.spec.ts:218:3

# Error details

```
Error: count = 51 (51 > 50) ต้องได้ 422

expect(received).toBe(expected) // Object.is equality

Expected: 422
Received: 201
```

```
Error: count = 51 ต้องได้ error TOO_MANY_PHOTOS

expect(received).toBe(expected) // Object.is equality

Expected: "TOO_MANY_PHOTOS"
Received: undefined
```

```
Error: count = 51 ข้อความต้องมี "กรุณาแบ่งส่ง"

expect(received).toContain(expected) // indexOf

Expected substring: "กรุณาแบ่งส่ง"
Received string:    " "
```

```
Error: count = 51 ต้องไม่ได้ batch_id (upload_batches +0 ทางอ้อม)

expect(received).toBeFalsy()

Received: "3f94343f-ad83-4cc0-83c4-9cd790a67ab8"
```

# Test source

```ts
  139 |   test('TC-1-03 [P1] รับ JPG และ PNG เก็บต้นฉบับตรง sha256 ทั้งก่อนและหลังรีสตาร์ต web', async ({ page }, testInfo) => {
  140 |     test.setTimeout(180_000);
  141 |     let cookie = await start();
  142 |     const date = await today();
  143 |     const files = [F.F5.file, F.F6.file];
  144 |     const src = files.map(f => ({ file: f, sha256: sha256(fs.readFileSync(fixture(f))), magic: hex(head(f, 4)) }));
  145 |     expect.soft(head(F.F5.file, 3).equals(JPG_MAGIC), 'F-5 ไบต์ต้นไฟล์ต้องเป็น FF D8 FF (E-3)').toBe(true);
  146 |     expect.soft(head(F.F6.file, 4).equals(PNG_MAGIC), 'F-6 ไบต์ต้นไฟล์ต้องเป็น 89 50 4E 47 (E-3)').toBe(true);
  147 |     const rowsBefore = await rows(cookie, date);
  148 | 
  149 |     const { batchId, items } = await upload(cookie, files.map(f => ({ path: fixture(f) })));
  150 |     // immediately after 201: read the stored original back
  151 |     const before = [] as Awaited<ReturnType<typeof imageSha>>[];
  152 |     for (const it of items) before.push(it.photoId ? await imageSha(cookie, it.photoId) : { status: 0, sha256: null, bytes: 0 });
  153 |     const rowsAfter = await rows(cookie, date);
  154 | 
  155 |     items.forEach((it, i) => {
  156 |       expect.soft(it.status, `${files[i]} (ชนิดที่รับ) ต้องได้ 201`).toBe(201);
  157 |       expect.soft(before[i].status, `${files[i]} GET /image ทันทีหลัง 201 ต้องได้ 200`).toBe(200);
  158 |       expect.soft(before[i].sha256, `${files[i]} sha256 ที่อ่านกลับทันทีหลัง 201 ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
  159 |       if (it.json?.sha256 !== undefined) expect.soft(it.json.sha256, `${files[i]} sha256 ในคำตอบ 201 ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
  160 |     });
  161 |     expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +2').toBe(2);
  162 | 
  163 |     // docker compose restart web
  164 |     docker(`restart ${WEB_CONTAINER}`);
  165 |     await waitHealthy(90_000);
  166 |     cookie = await login('U2');
  167 |     const after = [] as Awaited<ReturnType<typeof imageSha>>[];
  168 |     for (const it of items) after.push(it.photoId ? await imageSha(cookie, it.photoId) : { status: 0, sha256: null, bytes: 0 });
  169 |     const rowsAfterRestart = await rows(cookie, date);
  170 |     items.forEach((_, i) => {
  171 |       expect.soft(after[i].status, `${files[i]} GET /image หลังรีสตาร์ต web ต้องได้ 200`).toBe(200);
  172 |       expect.soft(after[i].sha256, `${files[i]} sha256 ที่อ่านกลับหลังรีสตาร์ต ต้อง = sha256 ต้นทาง`).toBe(src[i].sha256);
  173 |     });
  174 |     expect.soft(rowsAfterRestart - rowsBefore, 'หลังรีสตาร์ต แถว photos ยัง +2').toBe(2);
  175 | 
  176 |     await evidence(testInfo, 'evidence', {
  177 |       date, batchId, source: src,
  178 |       uploads: items.map((it, i) => ({ file: files[i], status: it.status, photoId: it.photoId, response: it.json })),
  179 |       readBackBeforeRestart: before, readBackAfterRestart: after,
  180 |       rows: { before: rowsBefore, after: rowsAfter, afterRestart: rowsAfterRestart, expectedDiff: 2 },
  181 |       restart: `docker restart ${WEB_CONTAINER} then /api/health db ok, login U-2 again`,
  182 |     });
  183 |     await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-restart');
  184 |     if (items[1].photoId) { await uiAs(page, cookie, `/photos/${items[1].photoId}`); await shot(testInfo, page, 'photo-png-after-restart'); }
  185 |   });
  186 | 
  187 |   test('TC-1-04 [P1] GIF PDF และไฟล์ข้อความนามสกุล .jpg ต้องได้ 415 ไม่เก็บไฟล์', async ({ page }, testInfo) => {
  188 |     const cookie = await start();
  189 |     const date = await today();
  190 |     const files = [F.F7.file, F.F8.file, F.F9.file];
  191 |     expect.soft(fs.statSync(fixture(F.F9.file)).size, 'F-9 fake.jpg ต้องเป็น 1,000 ไบต์ (E-3)').toBe(F.F9.size);
  192 |     const magic = files.map(f => ({ file: f, head: hex(head(f, 4)), isJpg: head(f, 3).equals(JPG_MAGIC), isPng: head(f, 4).equals(PNG_MAGIC) }));
  193 |     magic.forEach(m => expect.soft(m.isJpg || m.isPng, `${m.file} ไบต์ต้นไฟล์ต้องไม่ใช่ FF D8 FF / 89 50 4E 47 (เงื่อนไขของข้อมูล)`).toBe(false));
  194 |     const rowsBefore = await rows(cookie, date);
  195 |     const filesBefore = volumeFiles();
  196 | 
  197 |     const { batchId, items } = await upload(cookie, files.map(f => ({ path: fixture(f) })));
  198 | 
  199 |     const rowsAfter = await rows(cookie, date);
  200 |     const filesAfter = volumeFiles();
  201 |     items.forEach((it, i) => {
  202 |       expect.soft(it.status, `${files[i]} (ไม่ใช่ JPG/PNG ตามเนื้อไฟล์) ต้องได้ 415`).toBe(415);
  203 |       expect.soft(errText(it.json), `${files[i]} ข้อความเหตุผลต้องมี "${MSG_TYPE}"`).toContain(MSG_TYPE);
  204 |       expect.soft(it.photoId, `${files[i]} ต้องไม่ได้ photoId`).toBeFalsy();
  205 |     });
  206 |     expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +0').toBe(0);
  207 |     expect.soft(filesAfter - filesBefore, 'ไฟล์ใน volume photos ต้อง +0').toBe(0);
  208 | 
  209 |     await evidence(testInfo, 'evidence', {
  210 |       date, batchId, magic,
  211 |       files: items.map((it, i) => ({ file: files[i], status: it.status, photoId: it.photoId ?? null, response: it.json })),
  212 |       rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 0 },
  213 |       volumeFiles: { before: filesBefore, after: filesAfter, diff: filesAfter - filesBefore, expected: 0 },
  214 |     });
  215 |     await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-415');
  216 |   });
  217 | 
  218 |   test('TC-1-05 [P1] จำนวนรูปต่อครั้ง 0 · 1 · 49 · 50 · 51 และไฟล์ที่ 51 ใน batch 50 (ตรวจฝั่ง server)', async ({ page }, testInfo) => {
  219 |     test.setTimeout(600_000);
  220 |     const ev: any = { note: 'upload_batches ไม่มี API รายการ จึงตรวจทางอ้อม: คำขอถูกปฏิเสธและไม่มี batch_id ในคำตอบ' };
  221 |     const jpg = fixture(F.F5.file);
  222 |     const nameOf = (i: number) => `h0_v0_${String(i).padStart(3, '0')}.jpg`;
  223 | 
  224 |     // (ก) count = 0 และ 51 → 422 · upload_batches +0 · photos +0
  225 |     ev.reject = [];
  226 |     for (const n of [0, 51]) {
  227 |       const cookie = await start();
  228 |       const date = await today();
  229 |       const rowsBefore = await rows(cookie, date);
  230 |       const r = await openBatch(cookie, n);
  231 |       const rowsAfter = await rows(cookie, date);
  232 |       if (n === 0) {
  233 |         expect.soft(r.status, 'count = 0 (0 < 1) ต้องได้ 422').toBe(422);
  234 |       } else {
  235 |         expect.soft(r.status, 'count = 51 (51 > 50) ต้องได้ 422').toBe(422);
  236 |         expect.soft(r.json?.error, 'count = 51 ต้องได้ error TOO_MANY_PHOTOS').toBe('TOO_MANY_PHOTOS');
  237 |         expect.soft(errText(r.json), `count = 51 ข้อความต้องมี "${MSG_SPLIT}"`).toContain(MSG_SPLIT);
  238 |       }
> 239 |       expect.soft(r.json?.batch_id, `count = ${n} ต้องไม่ได้ batch_id (upload_batches +0 ทางอ้อม)`).toBeFalsy();
      |                                                                                                     ^ Error: count = 51 ต้องไม่ได้ batch_id (upload_batches +0 ทางอ้อม)
  240 |       expect.soft(rowsAfter - rowsBefore, `count = ${n} แถว photos ต้อง +0 (ไม่ใช่ +50)`).toBe(0);
  241 |       ev.reject.push({ count: n, status: r.status, response: r.json, rows: { before: rowsBefore, after: rowsAfter } });
  242 |     }
  243 | 
  244 |     // (ข) count = 1 · 49 · 50 แล้วส่ง h0_v0.jpg ตามจำนวน → แถว +n
  245 |     ev.accept = [];
  246 |     for (const n of [1, 49, 50]) {
  247 |       const cookie = await start();
  248 |       const date = await today();
  249 |       const rowsBefore = await rows(cookie, date);
  250 |       const b = await openBatch(cookie, n);
  251 |       expect.soft(b.status, `count = ${n} (1 ≤ ${n} ≤ 50) ต้องได้ 201`).toBe(201);
  252 |       const statuses: number[] = [];
  253 |       if (b.json?.batch_id) for (let i = 1; i <= n; i++) statuses.push((await sendFile(cookie, b.json.batch_id, jpg, nameOf(i))).status);
  254 |       const rowsAfter = await rows(cookie, date);
  255 |       expect.soft(statuses.filter(s => s === 201).length, `count = ${n} ไฟล์ที่ได้ 201 ต้องเป็น ${n}`).toBe(n);
  256 |       expect.soft(rowsAfter - rowsBefore, `count = ${n} แถว photos ต้อง +${n}`).toBe(n);
  257 |       ev.accept.push({ count: n, openStatus: b.status, batchId: b.json?.batch_id, fileStatuses: statuses, rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: n } });
  258 |       if (n === 50) await batchShot(testInfo, page, cookie, b.json?.batch_id, 'batch-page-50-photos');
  259 |     }
  260 | 
  261 |     // (ค) count = 50 ส่งครบ 50 แล้วส่งไฟล์ที่ 51 ใน batch เดิม → 1–50 201 · ไฟล์ที่ 51 422 · batch มี 50 รูป
  262 |     {
  263 |       const cookie = await start();
  264 |       const date = await today();
  265 |       const rowsBefore = await rows(cookie, date);
  266 |       const b = await openBatch(cookie, MAX_PHOTOS);
  267 |       expect.soft(b.status, 'count = 50 ต้องได้ 201').toBe(201);
  268 |       const batchId = b.json?.batch_id as string;
  269 |       const statuses: number[] = []; const ids: string[] = [];
  270 |       let extra: any = null;
  271 |       if (batchId) {
  272 |         for (let i = 1; i <= MAX_PHOTOS; i++) { const s = await sendFile(cookie, batchId, jpg, nameOf(i)); statuses.push(s.status); if (s.photoId) ids.push(s.photoId); }
  273 |         extra = await sendFile(cookie, batchId, jpg, nameOf(51));
  274 |       }
  275 |       const bs = batchId ? await batchStatus(cookie, batchId) : null;
  276 |       const rowsAfter = await rows(cookie, date);
  277 |       expect.soft(statuses.filter(s => s === 201).length, 'ไฟล์ 1–50 ต้องได้ 201 ครบ 50').toBe(50);
  278 |       expect.soft(extra?.status, 'ไฟล์ที่ 51 > declared_count 50 ต้องได้ 422').toBe(422);
  279 |       expect.soft(extra?.photoId, 'ไฟล์ที่ 51 ต้องไม่ได้ photoId').toBeFalsy();
  280 |       expect.soft((bs?.json?.photos || []).length, 'batch ต้องมี 50 รูป').toBe(50);
  281 |       expect.soft(rowsAfter - rowsBefore, 'แถว photos ต้อง +50').toBe(50);
  282 |       ev.overflow = { batchId, fileStatuses: statuses, photoIds: ids, file51: { status: extra?.status, response: extra?.json }, batchPhotos: (bs?.json?.photos || []).length, batchCounts: bs?.json?.counts, rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 50 } };
  283 |       await batchShot(testInfo, page, cookie, batchId, 'batch-page-after-file-51');
  284 |     }
  285 |     await evidence(testInfo, 'evidence', ev);
  286 |   });
  287 | 
  288 |   test('TC-1-06 [P2] หน้าอัปโหลดไม่มีช่องเลือกไซต์ รูปได้ไซต์ SITE-A และวันที่ 2026-11-19', async ({ page }, testInfo) => {
  289 |     const NOW = '2026-11-19T10:00:00+07:00';
  290 |     const EXPECT_DATE = '2026-11-19';
  291 |     const cookie = await start(NOW);
  292 |     const health = await http('GET', '/api/health');
  293 |     const rowsBefore = await rows(cookie, EXPECT_DATE);
  294 | 
  295 |     await uiAs(page, cookie, '/upload');
  296 |     await expect(page.getByTestId('upload-file-input')).toBeVisible();
  297 |     const main = page.locator('main');
  298 |     const siteControls = {
  299 |       selects: await main.locator('select').count(),
  300 |       siteTestIds: await main.locator('[data-testid*="site"]').count(),
  301 |       siteInputs: await main.locator('input[name*="site" i], select[name*="site" i], [role="combobox"], [role="listbox"]').count(),
  302 |     };
  303 |     expect.soft(siteControls.selects + siteControls.siteTestIds + siteControls.siteInputs, 'หน้าอัปโหลดต้องไม่มีช่องเลือกไซต์ (0 ช่อง)').toBe(0);
  304 |     await shot(testInfo, page, 'upload-page-no-site-select');
  305 | 
  306 |     // upload h0_v0.jpg (1 photo) through the page
  307 |     await page.getByTestId('upload-file-input').setInputFiles(fixture(F.F5.file));
  308 |     await page.getByTestId('upload-submit').click();
  309 |     let batchId: string | undefined;
  310 |     try {
  311 |       await page.waitForURL(u => u.pathname.startsWith('/uploads/'), { timeout: 30_000 });
  312 |       batchId = new URL(page.url()).pathname.split('/')[2];
  313 |     } catch { /* fall back to the API below */ }
  314 |     let via = 'ui';
  315 |     let photoId: string | undefined;
  316 |     if (batchId) {
  317 |       const bs = await batchStatus(cookie, batchId);
  318 |       photoId = bs.json?.photos?.[0]?.id;
  319 |     }
  320 |     if (!photoId) {
  321 |       via = 'api (หน้าไม่พาไป /uploads/{batchId})';
  322 |       const up = await upload(cookie, [{ path: fixture(F.F5.file) }]);
  323 |       batchId = up.batchId; photoId = up.items[0].photoId;
  324 |     }
  325 |     const detail = photoId ? await http('GET', `/api/photos/${photoId}`, { cookie }) : null;
  326 |     const photo = detail?.json?.photo ?? detail?.json;
  327 |     const rowsAfter = await rows(cookie, EXPECT_DATE);
  328 |     expect.soft(via, 'อัปโหลดผ่านหน้า /upload ต้องพาไปหน้าสถานะ /uploads/{batchId}').toBe('ui');
  329 |     expect.soft(detail?.status, 'GET /api/photos/{photoId} ต้องได้ 200').toBe(200);
  330 |     expect.soft(photo?.site?.code, 'ไซต์ของรูปต้องเป็น SITE-A (ไซต์ของ U-2)').toBe(SITE);
  331 |     expect.soft(photo?.upload_date, `upload_date ต้องเป็น ${EXPECT_DATE}`).toBe(EXPECT_DATE);
  332 |     expect.soft(rowsAfter - rowsBefore, 'แถว photos ของ 2026-11-19 SITE-A ต้อง +1').toBe(1);
  333 | 
  334 |     await evidence(testInfo, 'evidence', {
  335 |       resetNow: NOW, healthTime: health.json?.time, siteControls, via, batchId, photoId,
  336 |       photo: photo ? { id: photo.id, site: photo.site, upload_date: photo.upload_date, status: photo.status, original_filename: photo.original_filename } : null,
  337 |       rows: { before: rowsBefore, after: rowsAfter, diff: rowsAfter - rowsBefore, expected: 1 },
  338 |     });
  339 |     await batchShot(testInfo, page, cookie, batchId, 'batch-page-one-photo');
```