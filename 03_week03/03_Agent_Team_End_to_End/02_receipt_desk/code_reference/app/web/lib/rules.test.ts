/**
 * ชุดทดสอบโมดูลกฎ — 62 กรณีขอบของ TEST-DATA หัวข้อ 6 (1 test ต่อ 1 แถว ชื่อขึ้นต้นด้วยรหัสแถว)
 * แล้วตามด้วยกรณีเสริมความทนทาน (BR-03 PDF เสีย · BR-13 ละเอียดระดับวินาที · BR-14 เวลาไทย)
 *
 * รัน:  node --experimental-strip-types --test web/lib/rules.test.ts
 *       (หรือ npx tsx --test web/lib/rules.test.ts)
 *
 * ใช้ชุดกฎตาม `BUG_MODE` ของสภาพแวดล้อม (DESIGN 9.6): BUG_MODE=0 ต้องผ่านครบ
 * BUG_MODE=1 ใช้ฝึกหาข้อผิดพลาด — แถวที่กฎถูกทำให้ผิดจะไม่ผ่าน ซึ่งเป็นผลที่ตั้งใจ
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
// @ts-ignore TS5097 — ต้องใส่นามสกุล .ts เพื่อให้ node --experimental-strip-types หาไฟล์เจอ
import rulesDefault, { createRules, inspectPdf, LIMITS, type UploadFileInput, type OverdueInput } from './rules.ts';

const rules = rulesDefault as ReturnType<typeof createRules>;

// ---------------------------------------------------------------------------
// ตัวช่วยสร้างไฟล์ทดสอบ
// ---------------------------------------------------------------------------

const enc = (s: string): Uint8Array => new TextEncoder().encode(s);
const JPG = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00]);
const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13]);
const GIF = enc('GIF89a\x01\x00\x01\x00\x00\x00\x00;');

/** สร้าง PDF จากรายการเนื้อวัตถุ (วัตถุที่ 1 = Catalog) พร้อม xref + trailer ที่ถูกต้อง */
function buildPdf(objects: string[], trailerExtra = ''): Uint8Array {
  let out = '%PDF-1.4\n';
  const offsets: number[] = [];
  objects.forEach((body, i) => {
    offsets.push(out.length);
    out += `${i + 1} 0 obj\n${body}\nendobj\n`;
  });
  const xref = out.length;
  out += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const o of offsets) out += `${String(o).padStart(10, '0')} 00000 n \n`;
  out += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R${trailerExtra} >>\nstartxref\n${xref}\n%%EOF\n`;
  return enc(out);
}

function pdfWithPages(n: number): Uint8Array {
  const kids = Array.from({ length: n }, (_, i) => `${i + 3} 0 R`).join(' ');
  const pages = Array.from(
    { length: n },
    () => '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << >> >>',
  );
  return buildPdf(['<< /Type /Catalog /Pages 2 0 R >>', `<< /Type /Pages /Kids [${kids}] /Count ${n} >>`, ...pages]);
}

const file = (name: string, bytes: Uint8Array, size = bytes.length): UploadFileInput => ({ name, size, bytes });
const many = (n: number): UploadFileInput[] =>
  Array.from({ length: n }, (_, i) => file(`ok-100__${String(i + 1).padStart(3, '0')}.jpg`, JPG));

function expectReject(r: ReturnType<typeof rules.validateUpload>, status: number, error: string, fileName?: string) {
  assert.equal(r.ok, false);
  if (r.ok) return;
  assert.equal(r.status, status);
  assert.equal(r.error, error);
  if (fileName) {
    assert.equal(r.file, fileName);
    assert.ok(r.message.includes(fileName), `ข้อความต้องบอกชื่อไฟล์ ${fileName}`);
  }
}

/** เวลาไทย 'YYYY-MM-DD HH:mm' → Date */
const bkk = (s: string): Date => new Date(`${s.replace(' ', 'T')}:00+07:00`);
const minutesBefore = (now: Date, min: number): Date => new Date(now.getTime() - min * 60_000);

// ---------------------------------------------------------------------------
// TEST-DATA หัวข้อ 6 · 62 แถว
// ---------------------------------------------------------------------------

describe('BR-01 · ชุดละ 1–100 ไฟล์', () => {
  test('TD-BR01-a · 99 ไฟล์ → รับ 99', () => {
    const files = many(99);
    assert.equal(rules.validateUpload(files).ok, true);
    assert.equal(files.length, 99);
  });
  test('TD-BR01-b · 100 ไฟล์ → รับ 100', () => {
    assert.equal(rules.validateUpload(many(100)).ok, true);
  });
  test('TD-BR01-c · 101 ไฟล์ → 422 batch_size', () => {
    expectReject(rules.validateUpload(many(101)), 422, 'batch_size');
  });
  test('TD-BR01-d · 0 ไฟล์ → 422 batch_size', () => {
    expectReject(rules.validateUpload([]), 422, 'batch_size');
  });
});

describe('BR-02 · ไฟล์ไม่เกิน 10.00 MB', () => {
  test('TD-BR02-a · 10,485,759 ไบต์ → รับ', () => {
    assert.equal(rules.validateUpload([file('size-under.jpg', JPG, 10_485_759)]).ok, true);
  });
  test('TD-BR02-b · 10,485,760 ไบต์ → รับ', () => {
    assert.equal(rules.validateUpload([file('size-equal.jpg', JPG, 10_485_760)]).ok, true);
  });
  test('TD-BR02-c · 10,485,761 ไบต์ → 422 file_too_large บอกชื่อไฟล์ · ชุดไม่ถูกรับ', () => {
    const r = rules.validateUpload([file('ok-1.jpg', JPG), file('size-over.jpg', JPG, 10_485_761)]);
    expectReject(r, 422, 'file_too_large', 'size-over.jpg');
  });
});

describe('BR-03 · ชนิดไฟล์ และ PDF 1 หน้า', () => {
  test('TD-BR03-a · page-0.pdf (เสีย 0 หน้า) → 422 pdf_pages', () => {
    const broken = enc('%PDF-1.4\n%\xe2\xe3\n1 0 obj\n<< /Type /Catalog');
    expectReject(rules.validateUpload([file('page-0.pdf', broken)]), 422, 'pdf_pages', 'page-0.pdf');
  });
  test('TD-BR03-b · page-1.pdf → รับ', () => {
    assert.equal(rules.validateUpload([file('page-1.pdf', pdfWithPages(1))]).ok, true);
  });
  test('TD-BR03-c · page-2.pdf → 422 pdf_pages', () => {
    expectReject(rules.validateUpload([file('page-2.pdf', pdfWithPages(2))]), 422, 'pdf_pages', 'page-2.pdf');
  });
  test('TD-BR03-d · JPG → รับ', () => {
    assert.equal(rules.validateUpload([file('ok-100.jpg', JPG)]).ok, true);
  });
  test('TD-BR03-e · PNG → รับ', () => {
    assert.equal(rules.validateUpload([file('ok-100.png', PNG)]).ok, true);
  });
  test('TD-BR03-f · GIF → 422 file_type บอกชื่อไฟล์', () => {
    expectReject(rules.validateUpload([file('anim.gif', GIF)]), 422, 'file_type', 'anim.gif');
  });
});

describe('BR-04 · ความมั่นใจของยอดรวมต่ำกว่า 0.90 → ติดธง', () => {
  const items = ['45.00', '30.00', '25.00'];
  const flags = (c: number, it = items, total = '100.00') =>
    rules.computeFlags({ totalConfidence: c, itemPrices: it, total });
  test('TD-BR04-a · 0.89 → ติด', () => {
    const f = flags(0.89);
    assert.equal(f.lowConfidence, true);
    assert.equal(f.mismatch, false);
  });
  test('TD-BR04-b · 0.90 → ไม่ติด', () => {
    assert.equal(flags(0.9).lowConfidence, false);
    assert.equal(flags(0.9).flagged, false);
  });
  test('TD-BR04-c · 0.91 → ไม่ติด', () => {
    assert.equal(flags(0.91).flagged, false);
  });
  test('TD-BR04-d · 0.8999 → ติด (ไม่ปัดก่อนเทียบ)', () => {
    assert.equal(flags(0.8999).lowConfidence, true);
  });
  test('TD-BR04-e · 0.50 + ต่าง 5.00 → ติดทั้ง 2 ธง · นับเป็น 1 ใบ', () => {
    const f = flags(0.5, ['45.00', '30.00', '20.00']);
    assert.equal(f.lowConfidence, true);
    assert.equal(f.mismatch, true);
    assert.equal(f.flagged, true);
    assert.equal(f.diffSatang, 500);
    const flaggedReceipts = [f].filter((x) => x.flagged).length;
    assert.equal(flaggedReceipts, 1);
  });
});

describe('BR-05 · ผลรวมรายการต่างจากยอดรวมเกิน 1.00 บาท → ติดธง', () => {
  const flags = (it: string[]) => rules.computeFlags({ totalConfidence: 0.99, itemPrices: it, total: '100.00' });
  test('TD-BR05-a · ต่าง 0.99 → ไม่ติด', () => {
    const f = flags(['45.00', '30.00', '24.01']);
    assert.equal(f.diffSatang, 99);
    assert.equal(f.mismatch, false);
  });
  test('TD-BR05-b · ต่าง 1.00 → ไม่ติด', () => {
    const f = flags(['45.00', '30.00', '24.00']);
    assert.equal(f.diffSatang, 100);
    assert.equal(f.mismatch, false);
  });
  test('TD-BR05-c · ต่าง 1.01 → ติด', () => {
    const f = flags(['45.00', '30.00', '23.99']);
    assert.equal(f.diffSatang, 101);
    assert.equal(f.mismatch, true);
  });
  test('TD-BR05-d · รายการมากกว่ายอดรวม 1.01 → ติด', () => {
    const f = flags(['60.00', '41.01']);
    assert.equal(f.diffSatang, 101);
    assert.equal(f.mismatch, true);
  });
  test('TD-BR05-e · ต่าง 1.49 → ติด', () => {
    const f = flags(['50.00', '48.51']);
    assert.equal(f.diffSatang, 149);
    assert.equal(f.mismatch, true);
  });
});

describe('BR-06 · ยืนยันได้เมื่อยอดรวมตั้งแต่ 0.01 บาท', () => {
  test('TD-BR06-a · 0.00 → 422 total_invalid', () => {
    const r = rules.checkConfirmTotal('0.00');
    assert.equal(r.ok, false);
    if (!r.ok) assert.deepEqual([r.status, r.error], [422, 'total_invalid']);
  });
  test('TD-BR06-b · 0.01 → ยืนยันได้', () => {
    assert.equal(rules.checkConfirmTotal('0.01').ok, true);
  });
  test('TD-BR06-c · 0.02 → ยืนยันได้', () => {
    assert.equal(rules.checkConfirmTotal(0.02).ok, true);
  });
  test('TD-BR06-d · −5.00 → 422 total_invalid', () => {
    const r = rules.checkConfirmTotal('-5.00');
    assert.equal(r.ok, false);
    if (!r.ok) assert.equal(r.error, 'total_invalid');
  });
});

describe('BR-07 · อ่านได้ไม่เกิน 3 ครั้ง (แบบจำลองอ้างอิงของฝั่ง AI)', () => {
  test('TD-BR07-a · ล้มเหลว 1 แล้วสำเร็จ → รอตรวจ attempts = 2', () => {
    assert.deepEqual(rules.readAttemptOutcome(1), { attempts: 2, status: 'review' });
  });
  test('TD-BR07-b · ล้มเหลว 2 แล้วสำเร็จ → รอตรวจ attempts = 3', () => {
    assert.deepEqual(rules.readAttemptOutcome(2), { attempts: 3, status: 'review' });
    assert.equal(rules.canRetryRead(2), true);
  });
  test('TD-BR07-c · ล้มเหลวทุกครั้ง → อ่านไม่ได้ attempts = 3 ไม่มีครั้งที่ 4', () => {
    assert.deepEqual(rules.readAttemptOutcome(Infinity), { attempts: 3, status: 'unreadable' });
    assert.equal(rules.canRetryRead(3), false);
  });
});

describe('BR-08 · งานด่วนไม่เกิน 10 ใบ', () => {
  test('TD-BR08-a · 9 ใบ → ตั้งด่วนได้', () => {
    assert.equal(rules.checkUrgentSize(9).ok, true);
  });
  test('TD-BR08-b · 10 ใบ → ตั้งด่วนได้', () => {
    assert.equal(rules.checkUrgentSize(10).ok, true);
  });
  test('TD-BR08-c · 11 ใบ → 422 urgent_too_large', () => {
    const r = rules.checkUrgentSize(11);
    assert.equal(r.ok, false);
    if (!r.ok) assert.deepEqual([r.status, r.error], [422, 'urgent_too_large']);
  });
});

describe('BR-09 · งานด่วนไม่เกิน 5 งานต่อวัน (เวลาไทย)', () => {
  const now = bkk('2026-11-19 10:00');
  const today = (n: number) => Array.from({ length: n }, (_, i) => bkk(`2026-11-19 0${i}:30`));
  test('TD-BR09-a · ตั้งไปแล้ว 4 → งานที่ 5 ตั้งได้ (รวม 5)', () => {
    const used = rules.countUrgentToday(today(4), now);
    assert.equal(used, 4);
    assert.equal(rules.checkUrgent(5, used).ok, true);
    assert.equal(used + 1, 5);
  });
  test('TD-BR09-b · ตั้งไปแล้ว 5 → 409 urgent_quota', () => {
    const used = rules.countUrgentToday(today(5), now);
    assert.equal(used, 5);
    const r = rules.checkUrgent(5, used);
    assert.equal(r.ok, false);
    if (!r.ok) assert.deepEqual([r.status, r.error], [409, 'urgent_quota']);
  });
  test('TD-BR09-c · เมื่อวาน 23:59 มี 5 · วันนี้ 0 → ตั้งได้ (รวม 1)', () => {
    const yesterday = Array.from({ length: 5 }, () => bkk('2026-11-18 23:59'));
    const used = rules.countUrgentToday(yesterday, bkk('2026-11-19 00:00'));
    assert.equal(used, 0);
    assert.equal(rules.checkUrgent(5, used).ok, true);
  });
});

describe('BR-10 · อ่านใบด่วนติดกันไม่เกิน 4 ใบเมื่อมีใบปกติรอ (แบบจำลองอ้างอิงของฝั่ง AI)', () => {
  test('TD-BR10-a · ด่วน 3 ปกติ 2', () => {
    assert.deepEqual(rules.planReadOrder(3, 2), ['U1', 'U2', 'U3', 'N1', 'N2']);
  });
  test('TD-BR10-b · ด่วน 4 ปกติ 2', () => {
    assert.deepEqual(rules.planReadOrder(4, 2), ['U1', 'U2', 'U3', 'U4', 'N1', 'N2']);
  });
  test('TD-BR10-c · ด่วน 5 ปกติ 2 → ใบที่ 5 ต้องเป็นปกติ', () => {
    assert.deepEqual(rules.planReadOrder(5, 2), ['U1', 'U2', 'U3', 'U4', 'N1', 'U5', 'N2']);
  });
  test('TD-BR10-d · ด่วน 5 ปกติ 0 → ด่วนติดกัน 5 ได้', () => {
    assert.deepEqual(rules.planReadOrder(5, 0), ['U1', 'U2', 'U3', 'U4', 'U5']);
  });
});

describe('BR-11 · ใบงานปกติค้าง + ชุดใหม่ ไม่เกิน 400', () => {
  const cap = (pendingNormal: number, newCount: number, urgent = false) =>
    rules.checkQueueCapacity({ pendingNormal, newCount, urgent, workersAlive: 2 });
  test('TD-BR11-a · 299 + 100 = 399 → รับ', () => {
    assert.equal(cap(299, 100).ok, true);
  });
  test('TD-BR11-b · 300 + 100 = 400 → รับ', () => {
    assert.equal(cap(300, 100).ok, true);
  });
  test('TD-BR11-c · 301 + 100 = 401 → 429 queue_full', () => {
    const r = cap(301, 100);
    assert.equal(r.ok, false);
    if (!r.ok) assert.deepEqual([r.status, r.error], [429, 'queue_full']);
  });
  test('TD-BR11-d · 395 + 5 = 400 → รับ', () => {
    assert.equal(cap(395, 5).ok, true);
  });
  test('TD-BR11-e · ค้าง 400 + งานด่วน 10 → รับ (งานด่วนไม่นับ)', () => {
    assert.equal(cap(400, 10, true).ok, true);
  });
});

describe('BR-12 · นาทีที่ให้ลองใหม่', () => {
  const rows: Array<[string, number, number, number]> = [
    ['TD-BR12-a', 301, 2, 1],
    ['TD-BR12-b', 307, 2, 1],
    ['TD-BR12-c', 308, 2, 1],
    ['TD-BR12-d', 309, 2, 2],
    ['TD-BR12-e', 380, 2, 10],
    ['TD-BR12-f', 400, 2, 13],
    ['TD-BR12-g', 309, 1, 3],
    ['TD-BR12-h', 380, 0, 20],
  ];
  for (const [id, pending, workers, expected] of rows) {
    test(`${id} · ค้าง ${pending} + 100 · Worker ${workers} → ${expected} นาที`, () => {
      const r = rules.checkQueueCapacity({ pendingNormal: pending, newCount: 100, workersAlive: workers });
      assert.equal(r.ok, false);
      if (r.ok) return;
      assert.equal(r.status, 429);
      assert.equal(r.retryAfterMinutes, expected);
      assert.ok(r.message.includes(`${expected} นาที`));
    });
  }
});

describe('BR-13 · งานปกติค้างเกิน 120 นาที', () => {
  const now = bkk('2026-11-19 15:00');
  const rows: Array<OverdueInput & { id: string }> = [
    { id: 'TD-BR13-a', priority: 'normal', status: 'queued', acceptedAt: minutesBefore(now, 119) },
    { id: 'TD-BR13-b', priority: 'normal', status: 'queued', acceptedAt: minutesBefore(now, 120) },
    { id: 'TD-BR13-c', priority: 'normal', status: 'queued', acceptedAt: minutesBefore(now, 121) },
    { id: 'TD-BR13-d', priority: 'normal', status: 'review', acceptedAt: minutesBefore(now, 121) },
  ];
  const list = rules.listOverdue(rows, now);
  const sqlFilter = (r: OverdueInput) =>
    (r.status === 'queued' || r.status === 'processing') &&
    r.priority === 'normal' &&
    new Date(r.acceptedAt).getTime() < rules.overdueCutoff(now).getTime();
  test('TD-BR13-a · 119 นาที → ไม่อยู่', () => {
    assert.equal(rules.isOverdue(rows[0], now), false);
    assert.equal(sqlFilter(rows[0]), false);
  });
  test('TD-BR13-b · 120 นาทีพอดี → ไม่อยู่', () => {
    assert.equal(rules.isOverdue(rows[1], now), false);
    assert.equal(sqlFilter(rows[1]), false);
  });
  test('TD-BR13-c · 121 นาที → อยู่ · แสดง 121 นาที · รายการมี 1 ใบ', () => {
    assert.equal(rules.isOverdue(rows[2], now), true);
    assert.equal(sqlFilter(rows[2]), true);
    assert.equal(list.length, 1);
    assert.equal(list[0].id, 'TD-BR13-c');
    assert.equal(list[0].minutesWaiting, 121);
  });
  test('TD-BR13-d · รอตรวจแล้ว (มีผล) → ไม่อยู่', () => {
    assert.equal(rules.isOverdue(rows[3], now), false);
    assert.equal(sqlFilter(rows[3]), false);
  });
});

describe('BR-14 · นับเดือนตามวันที่บนใบเสร็จ', () => {
  // ข้อมูลตั้งต้นของ CL-01 (TEST-DATA หัวข้อ 2)
  const cl01 = [
    { id: 'S-01', receiptDate: '2026-10-31', total: '150.00', categoryId: 'CAT-01', status: 'confirmed' as const },
    { id: 'S-02', receiptDate: '2026-11-01', total: '200.50', categoryId: 'CAT-01', status: 'confirmed' as const },
    { id: 'S-03', receiptDate: '2026-11-02', total: '99.50', categoryId: 'CAT-03', status: 'confirmed' as const },
    { id: 'S-04', receiptDate: '2026-11-30', total: '1000.00', categoryId: 'CAT-01', status: 'confirmed' as const },
    { id: 'S-05', receiptDate: '2026-12-01', total: '75.25', categoryId: 'CAT-02', status: 'confirmed' as const },
    { id: 'S-06', receiptDate: '2026-11-15', total: '500.00', categoryId: null, status: 'review' as const },
    { id: 'S-07', receiptDate: '2026-11-10', total: '40.00', categoryId: 'CAT-02', status: 'confirmed' as const },
  ];
  const e02 = () => rules.summarizeMonth(cl01, '2026-11');
  test('TD-BR14-a · S-01 2026-10-31 → 2026-10 · E-01 = 150.00', () => {
    assert.equal(rules.monthOf('2026-10-31'), '2026-10');
    const e01 = rules.summarizeMonth(cl01, '2026-10');
    assert.deepEqual([e01.total, e01.count], ['150.00', 1]);
  });
  test('TD-BR14-b · S-02 2026-11-01 → 2026-11 · E-02 = 1,340.00', () => {
    assert.equal(rules.monthOf('2026-11-01'), '2026-11');
    assert.deepEqual([e02().total, e02().count], ['1340.00', 4]);
  });
  test('TD-BR14-c · S-03 2026-11-02 → 2026-11', () => {
    assert.equal(rules.monthOf('2026-11-02'), '2026-11');
    assert.equal(e02().total, '1340.00');
  });
  test('TD-BR14-d · S-04 2026-11-30 → 2026-11', () => {
    assert.equal(rules.monthOf('2026-11-30'), '2026-11');
    assert.equal(rules.monthBounds('2026-11').endDate, '2026-11-30');
    assert.equal(e02().total, '1340.00');
  });
  test('TD-BR14-e · S-05 2026-12-01 → 2026-12 · E-03 = 75.25 และไม่อยู่ใน E-02', () => {
    assert.equal(rules.monthOf('2026-12-01'), '2026-12');
    assert.equal(rules.isInMonth('2026-12-01', '2026-11'), false);
    const e03 = rules.summarizeMonth(cl01, '2026-12');
    assert.deepEqual([e03.total, e03.count], ['75.25', 1]);
  });
});

// ---------------------------------------------------------------------------
// กรณีเสริม (ไม่นับใน 62 แถว)
// ---------------------------------------------------------------------------

describe('เสริม · BR-03 PDF ที่เปิดไม่ได้', () => {
  const rejects = (name: string, bytes: Uint8Array) =>
    expectReject(rules.validateUpload([file(name, bytes)]), 422, 'pdf_pages', name);
  test('มีแค่หัว PDF + /Count 1 + %%EOF → ปฏิเสธ', () => {
    rejects('fake.pdf', enc('%PDF-1.4\n/Count 1\n%%EOF\n'));
  });
  test('/Kids อ้างวัตถุหน้าว่าง << >> → ปฏิเสธ', () => {
    const pdf = buildPdf(['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [3 0 R] /Count 1 >>', '<< >>']);
    assert.equal(inspectPdf(pdf).openable, false);
    rejects('empty-page.pdf', pdf);
  });
  test('/Kids อ้างพจนานุกรมที่ไม่ระบุ /Type → ปฏิเสธ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /MediaBox [0 0 10 10] >>',
    ]);
    rejects('untyped-page.pdf', pdf);
  });
  test('/Kids อ้างวัตถุที่ไม่มี → ปฏิเสธ', () => {
    rejects('missing.pdf', buildPdf(['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [9 0 R] /Count 1 >>']));
  });
  test('ต้นไม้หน้าวนซ้ำ → ปฏิเสธ', () => {
    rejects('loop.pdf', buildPdf(['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [2 0 R] /Count 1 >>']));
  });
  test('/Kids ว่าง (0 หน้า) → ปฏิเสธ', () => {
    rejects('zero.pdf', buildPdf(['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [] /Count 0 >>']));
  });
  test('/Count โกหกว่า 1 แต่มีจริง 2 หน้า → ปฏิเสธ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 2 0 R >>',
      '<< /Type /Page /Parent 2 0 R >>',
    ]);
    assert.equal(inspectPdf(pdf).pages, 2);
    rejects('lying-count.pdf', pdf);
  });
  test('ต้นไม้ซ้อนสองชั้น 1 หน้า → รับ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type /Pages /Parent 2 0 R /Kids [4 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 3 0 R /MediaBox [0 0 10 10] >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
  });
  test('PDF 1 หน้าที่มีคอมเมนต์คั่นระหว่าง /Type กับ /Page → รับ', () => {
    const pdf = buildPdf([
      '<< /Type % catalog\n/Catalog /Pages % ref\n2 0 R >>',
      '<< /Type %c\r/Pages /Kids [3 0 R % only page\n] /Count 1 >>',
      '<< /Type % comment between key and value\n/Page /Parent 2 0 R /MediaBox [0 0 595 842] >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
    assert.equal(rules.validateUpload([file('commented.pdf', pdf)]).ok, true);
  });
  test('PDF 2 หน้าที่มีคอมเมนต์คั่น /Type กับ /Page → ยังนับได้ 2 หน้าและปฏิเสธ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>',
      '<< /Type %x\n/Page /Parent 2 0 R >>',
      '<< /Type %y\n/Page /Parent 2 0 R >>',
    ]);
    assert.equal(inspectPdf(pdf).pages, 2);
    rejects('commented-2.pdf', pdf);
  });
  test('PDF 1 หน้าที่คอมเมนต์คั่น /Type กับ /Page มีคำ endobj (`/Type % endobj` ขึ้นบรรทัดใหม่ `/Page`) → รับ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type % endobj\n/Page /Parent 2 0 R /MediaBox [0 0 595 842] >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
    assert.equal(rules.validateUpload([file('comment-endobj.pdf', pdf)]).ok, true);
  });
  test('คอมเมนต์ที่มีคำ stream / endobj / หัววัตถุปลอม และสตริงที่มี endobj → ยังเป็น PDF 1 หน้า', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog % stream\n/Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 % 9 0 obj endobj\n>>',
      '<< /Title (fake endobj stream) /Type %endobj stream\r\n/Page /Parent 2 0 R >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
    assert.equal(rules.validateUpload([file('comment-keywords.pdf', pdf)]).ok, true);
  });
  test('PDF 2 หน้าที่คอมเมนต์มีคำ endobj → ยังนับ 2 หน้าและปฏิเสธ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>',
      '<< /Type % endobj\n/Page /Parent 2 0 R >>',
      '<< /Type % endobj\n/Page /Parent 2 0 R >>',
    ]);
    assert.equal(inspectPdf(pdf).pages, 2);
    rejects('comment-endobj-2.pdf', pdf);
  });
  test('PDF 1 หน้าที่คอมเมนต์คั่น /Type กับ /Page มีคำ /Encrypt (`/Type % /Encrypt 9 0 R` ขึ้นบรรทัดใหม่ `/Page`) → รับ', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type % /Encrypt 9 0 R\n/Page /Parent 2 0 R /MediaBox [0 0 595 842] >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
    assert.equal(rules.validateUpload([file('comment-encrypt.pdf', pdf)]).ok, true);
  });
  test('/Encrypt ในคอมเมนต์ของ trailer หรือในสตริง → ไม่ถือว่าเข้ารหัส', () => {
    const pdf = buildPdf(
      [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Title (/Encrypt 9 0 R) /Type /Page /Parent 2 0 R >>',
      ],
      ' % /Encrypt 9 0 R\n',
    );
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
    assert.equal(rules.validateUpload([file('encrypt-text.pdf', pdf)]).ok, true);
  });
  test('trailer มี /Encrypt จริง → เปิดไม่ได้ (pdf_pages)', () => {
    const objs = [
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 2 0 R >>',
      '<< /Filter /Standard /V 2 /R 3 >>',
    ];
    assert.deepEqual(inspectPdf(buildPdf(objs, ' /Encrypt 4 0 R')), { openable: false, pages: 0, reason: 'encrypted' });
    assert.equal(inspectPdf(buildPdf(objs, ' /Encrypt << /Filter /Standard >>')).reason, 'encrypted');
    rejects('encrypted.pdf', buildPdf(objs, ' /Encrypt 4 0 R'));
  });
  test('XRef stream มี /Encrypt → เปิดไม่ได้', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 2 0 R >>',
      '<< /Type /XRef /Size 5 /Root 1 0 R /Encrypt 5 0 R /Length 0 >>\nstream\n\nendstream',
    ]);
    assert.equal(inspectPdf(pdf).reason, 'encrypted');
  });
  test('% ในสตริงไม่ถือเป็นคอมเมนต์ (ไม่ตัด /Type /Page ที่ตามมาทิ้ง)', () => {
    const pdf = buildPdf([
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /T (100% \\) done) /Type /Page /Parent 2 0 R >>',
    ]);
    assert.deepEqual(inspectPdf(pdf), { openable: true, pages: 1 });
  });
  test('ไฟล์ทั้งชุดถูกปฏิเสธและรายงานทุกไฟล์ที่ไม่ผ่าน', () => {
    const r = rules.validateUpload([file('ok.jpg', JPG), file('anim.gif', GIF), file('page-2.pdf', pdfWithPages(2))]);
    assert.equal(r.ok, false);
    if (!r.ok) assert.deepEqual(r.files?.map((f) => [f.index, f.error]), [[1, 'file_type'], [2, 'pdf_pages']]);
  });
});

describe('เสริม · BR-13 เทียบละเอียดระดับวินาที', () => {
  const now = bkk('2026-11-19 15:00');
  const at = (ms: number): OverdueInput => ({ priority: 'normal', status: 'processing', acceptedAt: new Date(now.getTime() - ms) });
  test('120 นาที 1 วินาที → ค้างทันที', () => {
    assert.equal(rules.isOverdue(at(120 * 60_000 + 1000), now), true);
    assert.equal(rules.listOverdue([at(120 * 60_000 + 1000)], now)[0].minutesWaiting, 120);
  });
  test('120 นาที 1 มิลลิวินาที → ค้าง · 120 นาทีพอดี → ไม่ค้าง', () => {
    assert.equal(rules.isOverdue(at(120 * 60_000 + 1), now), true);
    assert.equal(rules.isOverdue(at(120 * 60_000), now), false);
  });
  test('overdueCutoff = now − 120 นาที และสอดคล้องกับ isOverdue', () => {
    const cutoff = rules.overdueCutoff(now);
    assert.equal(cutoff.getTime(), now.getTime() - 120 * 60_000);
    for (const ms of [0, 119 * 60_000, 120 * 60_000 - 1, 120 * 60_000, 120 * 60_000 + 1, 121 * 60_000, 500 * 60_000]) {
      const r = at(ms);
      assert.equal(new Date(r.acceptedAt).getTime() < cutoff.getTime(), rules.isOverdue(r, now), `ms=${ms}`);
    }
  });
  test('งานด่วนไม่นับเป็นค้างเกินกำหนด', () => {
    assert.equal(rules.isOverdue({ ...at(300 * 60_000), priority: 'urgent' }, now), false);
  });
  test('ค่าเวลาแบบข้อความ ISO ให้ผลเท่ากับ Date', () => {
    const r: OverdueInput = { priority: 'normal', status: 'queued', acceptedAt: '2026-11-19T05:59:00Z' };
    assert.equal(rules.isOverdue(r, '2026-11-19T08:00:00Z'), true);
    assert.equal(rules.isOverdue(r, new Date('2026-11-19T08:00:00Z')), true);
  });
});

describe('เสริม · BR-09/BR-14 เวลาไทย', () => {
  test('เที่ยงคืนไทย (17:00Z) เป็นวันใหม่ของ BR-09', () => {
    assert.equal(rules.countUrgentToday(['2026-11-18T16:59:59Z'], '2026-11-18T17:00:00Z'), 0);
    assert.equal(rules.countUrgentToday(['2026-11-18T17:00:00Z'], '2026-11-18T23:00:00Z'), 1);
  });
  test('timestamp ISO และ Date ของเที่ยงคืนไทยเข้าเดือนเดียวกัน', () => {
    assert.equal(rules.monthOf('2026-10-31T17:00:00Z'), '2026-11');
    assert.equal(rules.monthOf(new Date('2026-10-31T17:00:00Z')), '2026-11');
  });
  test('ค่าเงินจาก PostgreSQL เป็นข้อความเทียบเป็นสตางค์ ไม่มีปัญหา float', () => {
    assert.equal(rules.itemsDiffSatang(['0.10', '0.20'], '0.30'), 0);
    assert.equal(LIMITS.MAX_ITEMS_DIFF_SATANG, 100);
  });
});
