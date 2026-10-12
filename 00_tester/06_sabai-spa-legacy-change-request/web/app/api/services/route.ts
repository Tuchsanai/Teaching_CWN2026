import { listServices } from "@/lib/server/catalog.ts";
import { getLang, handle, json } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  return handle(async () => {
    const lang = await getLang(new URL(req.url).searchParams.get("lang"));
    return json({ services: await listServices(lang) });
  });
}
