import { QUIZ, quizResult, validateAnswers } from "@/lib/bot/quiz.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { ApiError, getLang, handle, json, readJson } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/quiz — คำถาม 4 ข้อ */
export async function GET(req: Request) {
  return handle(async () => {
    const lang = await getLang(new URL(req.url).searchParams.get("lang"));
    return json({
      questions: QUIZ.map((q) => ({ id: q.id, text: q.text[lang], options: q.options.map((o) => ({ value: o.value, label: o.label[lang] })) })),
    });
  });
}

/** POST /api/quiz {answers:{goal,time,pressure,stay}} → แพ็กเกจแนะนำ 1 รายการ + เหตุผล (FR-28) */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    const lang = await getLang(body.lang);
    if (!validateAnswers(body.answers)) throw new ApiError(422, "BAD_REQUEST", { field: "answers" });
    const r = quizResult(body.answers, lang);
    const svc = (await listServices(lang)).find((s) => s.code === r.code)!;
    return json({ code: r.code, name: svc.name, price: svc.price, image: svc.image, reason: r.reason });
  });
}
