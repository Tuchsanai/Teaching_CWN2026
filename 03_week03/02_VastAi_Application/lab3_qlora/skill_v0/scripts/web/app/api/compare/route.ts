import { pool, getServices, getShopInfo } from "@/lib/db";
import { buildSystemPrompt } from "@/lib/prompt";
import { callLLMTimed, stripThink } from "@/lib/llm";
import { checkBookingTag, displayText } from "@/lib/booking";
import { ensureTables, MODEL_KEYS, MODEL_LABEL, modelName } from "@/lib/models";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// GET  /api/compare               -> คำถามที่เทียบล่าสุด 10 ข้อ
// POST /api/compare {"question"}  -> ถามทั้ง 2 โมเดลด้วยคำถามเดียวกัน แล้วเก็บผลลง PostgreSQL
export async function GET() {
  await ensureTables();
  const r = await pool.query(
    `SELECT id, question, result,
            to_char(created_at AT TIME ZONE 'Asia/Bangkok', 'YYYY-MM-DD HH24:MI') AS created_at
     FROM compare_runs ORDER BY id DESC LIMIT 10`
  );
  return Response.json({ runs: r.rows });
}

export async function POST(req: Request) {
  const body = (await req.json().catch(() => ({}))) as { question?: string };
  const question = String(body.question ?? "").trim().slice(0, 2000);
  if (!question) return Response.json({ error: "กรุณาพิมพ์คำถาม" }, { status: 400 });

  await ensureTables();
  const [services, info] = await Promise.all([getServices(), getShopInfo()]);
  const messages = [
    { role: "system" as const, content: buildSystemPrompt(services, info) },
    { role: "user" as const, content: question },
  ];

  // ถามทีละโมเดล (ไม่ยิงพร้อมกัน) เพื่อให้ความเร็ว token/วินาทีของแต่ละตัวเทียบกันได้ตรง ๆ
  const answers = [];
  for (const k of MODEL_KEYS) {
    try {
      const r = await callLLMTimed(messages, modelName(k));
      const full = stripThink(r.text).trim();
      answers.push({
        key: k,
        label: MODEL_LABEL[k],
        model: modelName(k),
        answer: displayText(full),
        raw: full,
        ms: r.ms,
        tokens: r.tokens,
        tps: Math.round(r.tps * 10) / 10,
        tag: checkBookingTag(full, services),
      });
    } catch (e) {
      answers.push({ key: k, label: MODEL_LABEL[k], model: modelName(k), error: (e as Error).message });
    }
  }

  const ins = await pool.query<{ id: number; created_at: string }>(
    `INSERT INTO compare_runs (question, result) VALUES ($1, $2)
     RETURNING id, to_char(created_at AT TIME ZONE 'Asia/Bangkok', 'YYYY-MM-DD HH24:MI') AS created_at`,
    [question, JSON.stringify({ answers })]
  );
  return Response.json({ id: ins.rows[0].id, created_at: ins.rows[0].created_at, question, result: { answers } });
}
