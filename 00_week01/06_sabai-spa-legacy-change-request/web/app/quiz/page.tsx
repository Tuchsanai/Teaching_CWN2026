import { Quiz } from "@/components/Quiz.tsx";
import { Orchid } from "@/components/ThaiOrnament.tsx";
import { QUIZ } from "@/lib/bot/quiz.ts";
import { t } from "@/lib/i18n.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function QuizPage() {
  const lang = await getLang();
  return (
    <>
      <div className="page-head">
        <Orchid className="orn sway" size={40} />
        <h1>{t(lang, "quiz.title")}</h1>
      </div>
      <Quiz questions={QUIZ.map((q) => ({ id: q.id, text: q.text[lang], options: q.options.map((o) => ({ value: o.value, label: o.label[lang] })) }))} />
    </>
  );
}
