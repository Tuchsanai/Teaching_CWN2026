import { readFile } from "node:fs/promises";
import { basename, join } from "node:path";
import { ApiError, handle } from "@/lib/server/http.ts";
import { photoForViewer } from "@/lib/server/store.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

const PHOTO_DIR = process.env.PHOTO_DIR ?? join(process.cwd(), "private", "photos");

/** GET /api/photos/:id — รูป before/after เฉพาะเจ้าของ (NFR-11): ไม่ล็อกอิน 401 · คนอื่น 403 */
export async function GET(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const { id } = await ctx.params;
    const n = Number(id);
    if (!Number.isInteger(n) || n <= 0) throw new ApiError(404, "NOT_FOUND");
    const key = await photoForViewer(n, await getSession());
    let data: Buffer;
    try {
      data = await readFile(join(PHOTO_DIR, basename(key)));
    } catch {
      throw new ApiError(404, "NOT_FOUND");
    }
    const type = key.endsWith(".svg") ? "image/svg+xml" : key.endsWith(".png") ? "image/png" : "image/webp";
    return new Response(new Uint8Array(data), {
      headers: { "Content-Type": type, "Cache-Control": "private, no-store" },
    });
  });
}
