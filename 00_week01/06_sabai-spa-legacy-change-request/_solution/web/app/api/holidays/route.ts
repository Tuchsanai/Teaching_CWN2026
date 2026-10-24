import { getLang, handle, json } from "@/lib/server/http.ts";
import { holidayName, listHolidays } from "@/lib/server/holiday.ts";

export const dynamic = "force-dynamic";

/** CR-04 รายการวันหยุดร้าน เรียงตามวันที่ */
export async function GET(req: Request) {
  return handle(async () => {
    const lang = await getLang(new URL(req.url).searchParams.get("lang"));
    const rows = await listHolidays();
    return json({
      holidays: rows.map((h) => ({ date: h.holiday_date, name: holidayName(h, lang), nameTh: h.name_th, nameEn: h.name_en, nameZh: h.name_zh })),
    });
  });
}
