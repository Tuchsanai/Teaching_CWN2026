import { checkReportRange, salesReport, salesReportCsv } from "@/lib/server/admin.ts";
import { ApiError, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/admin/report?from=YYYY-MM-DD&to=YYYY-MM-DD[&format=csv] — รายงานยอด CR-05 (owner เท่านั้น · ≤ 92 วัน) */
export async function GET(req: Request) {
  return handle(async () => {
    const s = await getSession();
    if (!s) throw new ApiError(401, "LOGIN_REQUIRED");
    if (s.role !== "owner") throw new ApiError(403, "FORBIDDEN");
    const sp = new URL(req.url).searchParams;
    const { from, to } = checkReportRange(sp.get("from"), sp.get("to"));
    if (sp.get("format") === "csv") {
      return new Response(await salesReportCsv(from, to), {
        status: 200,
        headers: {
          "Content-Type": "text/csv; charset=utf-8",
          "Content-Disposition": `attachment; filename="sabai-report-${from}_${to}.csv"`,
          "Cache-Control": "no-store",
        },
      });
    }
    return json(await salesReport(from, to));
  });
}
