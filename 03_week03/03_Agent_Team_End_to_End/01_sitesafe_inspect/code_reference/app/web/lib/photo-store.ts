/**
 * Receiving and storing original photos (DESIGN §1 volume, §9.3 · FR-02, BR-05, NFR-04).
 * - File type from magic bytes only (JPG FF D8 FF · PNG 89 50 4E 47), never the extension.
 * - Size counted from bytes actually received; receiving stops as soon as the limit is passed.
 * - Rejected files are never written to the photos volume (kept in memory until accepted).
 * - Accepted files are written + fsync'ed under PHOTOS_DIR/{site}/{yyyy-mm-dd}/{photo_id}.{ext}.
 */
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { Readable } from 'node:stream';
import busboy from 'busboy';
import { MAX_FILE_BYTES, isSizeAllowed } from './rules';

export type ImageKind = { mime: 'image/jpeg' | 'image/png'; ext: 'jpg' | 'png' };

export function sniffImage(head: Uint8Array): ImageKind | null {
  if (head.length >= 3 && head[0] === 0xff && head[1] === 0xd8 && head[2] === 0xff) {
    return { mime: 'image/jpeg', ext: 'jpg' };
  }
  if (head.length >= 4 && head[0] === 0x89 && head[1] === 0x50 && head[2] === 0x4e && head[3] === 0x47) {
    return { mime: 'image/png', ext: 'png' };
  }
  return null;
}

export type ReceivedFile = {
  filename: string;
  data: Buffer;
  size: number;
  sha256: string;
  kind: ImageKind;
};

export type ReceiveResult =
  | { ok: true; file: ReceivedFile }
  | { ok: false; reason: 'TOO_LARGE' | 'UNSUPPORTED_TYPE' | 'NO_FILE' | 'MULTIPLE_FILES' | 'BAD_REQUEST' };

function cleanFilename(name: string | undefined): string {
  const base = (name ?? '').split(/[\\/]/).pop() ?? '';
  // eslint-disable-next-line no-control-regex
  const safe = base.replace(/[\u0000-\u001f\u007f]/g, '').trim().slice(0, 255);
  return safe || 'photo';
}

/**
 * Read exactly one file part from a multipart/form-data body (any field name).
 * Stops reading the moment the file passes MAX_FILE_BYTES or its first bytes
 * are not JPG/PNG. A body with a second file part is rejected as a whole
 * (MULTIPLE_FILES): the caller then stores nothing, not even the first file.
 * The result is only decided once the whole body has been parsed.
 */
export async function receiveSingleImage(
  body: ReadableStream<Uint8Array> | null,
  contentType: string | null,
): Promise<ReceiveResult> {
  if (!body || !contentType || !/^multipart\/form-data/i.test(contentType)) {
    return { ok: false, reason: 'BAD_REQUEST' };
  }
  let bb: busboy.Busboy;
  try {
    bb = busboy({
      headers: { 'content-type': contentType },
      // busboy signals 'limit' when the count REACHES fileSize, so give it one byte of
      // headroom and let isSizeAllowed() (BR-05) decide on the bytes counted below.
      limits: { files: 1, fileSize: MAX_FILE_BYTES + 1, fields: 20, fieldSize: 4096, parts: 25 },
    });
  } catch {
    return { ok: false, reason: 'BAD_REQUEST' };
  }

  const source = Readable.fromWeb(body as unknown as import('node:stream/web').ReadableStream<Uint8Array>);

  return new Promise<ReceiveResult>((resolve) => {
    let settled = false;
    let sawFile = false;
    let result: ReceiveResult | null = null;

    const finish = (r: ReceiveResult) => {
      if (settled) return;
      settled = true;
      if (!r.ok) {
        // Stop receiving immediately: no more bytes are parsed or kept.
        source.unpipe(bb);
        source.destroy();
        bb.removeAllListeners('file');
        bb.on('error', () => undefined);
      }
      resolve(r);
    };

    bb.on('file', (_field, stream, info) => {
      if (sawFile) {
        // Not reached with limits.files = 1 (busboy emits 'filesLimit'); kept as a guard.
        stream.resume();
        finish({ ok: false, reason: 'MULTIPLE_FILES' });
        return;
      }
      sawFile = true;
      const chunks: Buffer[] = [];
      let size = 0;
      let kind: ImageKind | null = null;
      let head = Buffer.alloc(0);
      const hash = createHash('sha256');

      stream.on('data', (chunk: Buffer) => {
        if (settled) return;
        size += chunk.length;
        if (!isSizeAllowed(size)) {
          finish({ ok: false, reason: 'TOO_LARGE' });
          return;
        }
        if (!kind) {
          head = Buffer.concat([head, chunk]).subarray(0, 8);
          if (head.length >= 4) {
            kind = sniffImage(head);
            if (!kind) {
              finish({ ok: false, reason: 'UNSUPPORTED_TYPE' });
              return;
            }
          }
        }
        chunks.push(chunk);
        hash.update(chunk);
      });
      stream.on('limit', () => finish({ ok: false, reason: 'TOO_LARGE' }));
      stream.on('error', () => finish({ ok: false, reason: 'BAD_REQUEST' }));
      stream.on('end', () => {
        if (settled) return;
        if (!kind) kind = sniffImage(head);
        if (size === 0 || !kind) {
          result = { ok: false, reason: 'UNSUPPORTED_TYPE' };
          return;
        }
        result = {
          ok: true,
          file: {
            filename: cleanFilename(info.filename),
            data: Buffer.concat(chunks, size),
            size,
            sha256: hash.digest('hex'),
            kind,
          },
        };
      });
    });
    // A second file part → reject the whole request; too many parts/fields → malformed.
    bb.on('filesLimit', () => finish({ ok: false, reason: 'MULTIPLE_FILES' }));
    bb.on('partsLimit', () => finish({ ok: false, reason: 'BAD_REQUEST' }));
    bb.on('fieldsLimit', () => finish({ ok: false, reason: 'BAD_REQUEST' }));
    bb.on('close', () => finish(result ?? { ok: false, reason: sawFile ? 'UNSUPPORTED_TYPE' : 'NO_FILE' }));
    bb.on('error', () => finish({ ok: false, reason: 'BAD_REQUEST' }));
    source.on('error', () => finish({ ok: false, reason: 'BAD_REQUEST' }));
    source.pipe(bb);
  });
}

export function photosDir(): string {
  return path.resolve(process.env.PHOTOS_DIR || '/data/photos');
}

/** Relative storage path: {siteCode}/{yyyy-mm-dd}/{photoId}.{ext} */
export function storagePathFor(siteCode: string, uploadDate: string, photoId: string, ext: string): string {
  const safeSite = siteCode.replace(/[^A-Za-z0-9_-]/g, '_');
  return path.posix.join(safeSite, uploadDate, `${photoId}.${ext}`);
}

/** Absolute path inside PHOTOS_DIR; throws if the stored path would escape it. */
export function absolutePhotoPath(storagePath: string): string {
  const root = photosDir();
  const abs = path.resolve(root, storagePath);
  if (abs !== root && !abs.startsWith(root + path.sep)) throw new Error('storage path outside PHOTOS_DIR');
  return abs;
}

/** Write the file durably (temp file + fsync + rename + dir fsync). */
export async function writePhotoFile(storagePath: string, data: Buffer): Promise<void> {
  const abs = absolutePhotoPath(storagePath);
  const dir = path.dirname(abs);
  await fs.mkdir(dir, { recursive: true });
  const tmp = `${abs}.part-${process.pid}-${Date.now()}`;
  const fh = await fs.open(tmp, 'wx', 0o640);
  try {
    await fh.writeFile(data);
    await fh.sync();
  } finally {
    await fh.close();
  }
  try {
    await fs.rename(tmp, abs);
  } catch (e) {
    await fs.rm(tmp, { force: true });
    throw e;
  }
  try {
    const d = await fs.open(dir, 'r');
    try {
      await d.sync();
    } finally {
      await d.close();
    }
  } catch {
    /* directory fsync is best effort on some filesystems */
  }
}

export async function removePhotoFile(storagePath: string): Promise<void> {
  try {
    await fs.rm(absolutePhotoPath(storagePath), { force: true });
  } catch {
    /* ignore */
  }
}
