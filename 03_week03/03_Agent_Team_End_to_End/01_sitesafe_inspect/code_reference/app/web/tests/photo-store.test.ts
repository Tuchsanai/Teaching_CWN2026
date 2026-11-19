// FR-02 (magic bytes) and BR-05 (bytes actually received) — TEST-DATA §5.
import { describe, expect, it } from 'vitest';
import { receiveSingleImage, sniffImage, storagePathFor, absolutePhotoPath } from '@/lib/photo-store';

const JPG_HEAD = [0xff, 0xd8, 0xff, 0xe0];
const PNG_HEAD = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fileOf(head: number[], size: number): Uint8Array<ArrayBuffer> {
  const b = new Uint8Array(new ArrayBuffer(size));
  b.set(head.slice(0, size));
  return b;
}

async function send(bytes: Uint8Array<ArrayBuffer>, name: string) {
  const fd = new FormData();
  fd.append('file', new Blob([bytes]), name);
  const req = new Request('http://localhost/api/uploads/x/photos', { method: 'POST', body: fd });
  return receiveSingleImage(req.body, req.headers.get('content-type'));
}

describe('sniffImage', () => {
  it('accepts JPG and PNG signatures only', () => {
    expect(sniffImage(Uint8Array.from(JPG_HEAD))?.mime).toBe('image/jpeg');
    expect(sniffImage(Uint8Array.from(PNG_HEAD))?.mime).toBe('image/png');
    expect(sniffImage(Uint8Array.from([0x47, 0x49, 0x46, 0x38]))).toBeNull(); // GIF
    expect(sniffImage(Uint8Array.from([0x25, 0x50, 0x44, 0x46]))).toBeNull(); // PDF
    expect(sniffImage(new TextEncoder().encode('hello'))).toBeNull(); // fake.jpg
  });
});

describe('receiveSingleImage', () => {
  it('F-2: exactly 15,728,640 bytes is accepted', async () => {
    const r = await send(fileOf(JPG_HEAD, 15_728_640), 'h0_v0_15_0mb.jpg');
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.file.size).toBe(15_728_640);
      expect(r.file.kind.mime).toBe('image/jpeg');
      expect(r.file.filename).toBe('h0_v0_15_0mb.jpg');
      expect(r.file.sha256).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it('F-1: 15,623,782 bytes is accepted', async () => {
    const r = await send(fileOf(JPG_HEAD, 15_623_782), 'h0_v0_14_9mb.jpg');
    expect(r.ok).toBe(true);
  });

  it('F-3: 15,728,641 bytes is rejected as too large', async () => {
    const r = await send(fileOf(JPG_HEAD, 15_728_641), 'h0_v0_15mb_plus1.jpg');
    expect(r).toEqual({ ok: false, reason: 'TOO_LARGE' });
  });

  it('F-4: 15,833,498 bytes is rejected as too large', async () => {
    const r = await send(fileOf(JPG_HEAD, 15_833_498), 'h0_v0_15_1mb.jpg');
    expect(r).toEqual({ ok: false, reason: 'TOO_LARGE' });
  });

  it('F-6: PNG is accepted', async () => {
    const r = await send(fileOf(PNG_HEAD, 300_000), 'h0_v0.png');
    expect(r.ok && r.file.kind.mime).toBe('image/png');
  });

  it('F-7 / F-8 / F-9: GIF, PDF and a renamed text file are rejected', async () => {
    expect(await send(fileOf([0x47, 0x49, 0x46, 0x38, 0x39, 0x61], 100_000), 'site.gif')).toEqual({ ok: false, reason: 'UNSUPPORTED_TYPE' });
    expect(await send(fileOf([0x25, 0x50, 0x44, 0x46, 0x2d], 100_000), 'plan.pdf')).toEqual({ ok: false, reason: 'UNSUPPORTED_TYPE' });
    expect(await send(new TextEncoder().encode('x'.repeat(1000)), 'fake.jpg')).toEqual({ ok: false, reason: 'UNSUPPORTED_TYPE' });
  });

  it('F-10: a truncated JPG with a valid header is accepted (fails later in the AI)', async () => {
    const r = await send(fileOf(JPG_HEAD, 100_000), 'corrupt_half.jpg');
    expect(r.ok).toBe(true);
  });

  it('empty file and missing file are rejected', async () => {
    expect(await send(new Uint8Array(0), 'empty.jpg')).toEqual({ ok: false, reason: 'UNSUPPORTED_TYPE' });
    const fd = new FormData();
    fd.append('note', 'no file');
    const req = new Request('http://localhost/', { method: 'POST', body: fd });
    expect(await receiveSingleImage(req.body, req.headers.get('content-type'))).toEqual({ ok: false, reason: 'NO_FILE' });
    expect(await receiveSingleImage(null, null)).toEqual({ ok: false, reason: 'BAD_REQUEST' });
  });
});

describe('storage paths', () => {
  it('photos/{site}/{yyyy-mm-dd}/{photo_id}.{ext} and never outside PHOTOS_DIR', () => {
    process.env.PHOTOS_DIR = '/data/photos';
    expect(storagePathFor('SITE-A', '2026-11-18', 'abc', 'jpg')).toBe('SITE-A/2026-11-18/abc.jpg');
    expect(absolutePhotoPath('SITE-A/2026-11-18/abc.jpg')).toBe('/data/photos/SITE-A/2026-11-18/abc.jpg');
    expect(() => absolutePhotoPath('../etc/passwd')).toThrow();
  });
});

describe('one file per request (nothing is stored when a request carries more)', () => {
  it('two file parts → MULTIPLE_FILES, even when both are valid images', async () => {
    const fd = new FormData();
    fd.append('file', new Blob([fileOf(JPG_HEAD, 2_000)]), 'h0_v0_a.jpg');
    fd.append('file', new Blob([fileOf(JPG_HEAD, 2_000)]), 'h0_v0_b.jpg');
    const req = new Request('http://localhost/', { method: 'POST', body: fd });
    expect(await receiveSingleImage(req.body, req.headers.get('content-type'))).toEqual({
      ok: false,
      reason: 'MULTIPLE_FILES',
    });
  });

  it('two file parts under different field names → MULTIPLE_FILES', async () => {
    const fd = new FormData();
    fd.append('a', new Blob([fileOf(PNG_HEAD, 2_000)]), 'h0_v0.png');
    fd.append('b', new Blob([fileOf(JPG_HEAD, 2_000)]), 'h1_v0.jpg');
    const req = new Request('http://localhost/', { method: 'POST', body: fd });
    expect(await receiveSingleImage(req.body, req.headers.get('content-type'))).toEqual({
      ok: false,
      reason: 'MULTIPLE_FILES',
    });
  });

  it('one file plus text fields is accepted', async () => {
    const fd = new FormData();
    fd.append('note', 'site photo');
    fd.append('file', new Blob([fileOf(JPG_HEAD, 2_000)]), 'h0_v0.jpg');
    fd.append('index', '3');
    const req = new Request('http://localhost/', { method: 'POST', body: fd });
    const r = await receiveSingleImage(req.body, req.headers.get('content-type'));
    expect(r.ok && r.file.filename).toBe('h0_v0.jpg');
  });
});
