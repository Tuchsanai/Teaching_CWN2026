import { readSample, mimeOf } from "@/lib/samples";
export const dynamic = "force-dynamic";
export async function GET(_req, { params }) {
  const { name } = await params;
  const buf = await readSample(name);
  if (!buf) return new Response("not found", { status: 404 });
  return new Response(buf, { headers: { "Content-Type": mimeOf(name), "Cache-Control": "public, max-age=3600" } });
}
