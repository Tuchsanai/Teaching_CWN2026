import { listSamples } from "@/lib/samples";
export const dynamic = "force-dynamic";
export async function GET() { return Response.json({ samples: await listSamples() }); }
