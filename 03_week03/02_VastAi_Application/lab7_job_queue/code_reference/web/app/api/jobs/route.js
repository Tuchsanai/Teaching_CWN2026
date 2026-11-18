import { gw, errorJson } from "@/lib/gateway";
import { readSample, mimeOf } from "@/lib/samples";
export const dynamic = "force-dynamic";

// GET /api/jobs?limit=40  -> latest jobs from the gateway
export async function GET(req) {
  const limit = Math.max(1, Math.min(500, Number(new URL(req.url).searchParams.get("limit")) || 40));
  try {
    const { status, body } = await gw(`/jobs?limit=${limit}`);
    return Response.json(body, { status });
  } catch (e) { return errorJson(e); }
}

// POST /api/jobs  (multipart: sample=<name>..., file=<image>..., copies=N)
// every receipt image x copies -> one gateway job each (1 receipt per job)
export async function POST(req) {
  let form;
  try { form = await req.formData(); } catch { return errorJson(new Error("ส่งข้อมูลแบบ multipart เท่านั้น"), 400); }
  const copies = Math.max(1, Math.min(50, Number(form.get("copies")) || 1));
  const images = [];
  for (const name of form.getAll("sample")) {
    const buf = await readSample(String(name));
    if (!buf) return errorJson(new Error(`ไม่พบใบเสร็จตัวอย่าง ${name}`), 400);
    images.push({ name: String(name), blob: new Blob([buf], { type: mimeOf(String(name)) }) });
  }
  for (const f of form.getAll("file")) {
    if (typeof f === "string" || !f.size) continue;
    if (!/^image\//.test(f.type)) return errorJson(new Error(`${f.name} ไม่ใช่ไฟล์รูปภาพ`), 400);
    if (f.size > 10 * 1024 * 1024) return errorJson(new Error(`${f.name} ใหญ่เกิน 10 MB`), 400);
    images.push({ name: f.name.replace(/[^\w.\-ก-๙]/g, "_"), blob: f });
  }
  if (!images.length) return errorJson(new Error("เลือกใบเสร็จอย่างน้อย 1 ใบ"), 400);

  const tasks = [];
  for (let r = 0; r < copies; r++) for (const img of images) tasks.push(img);
  if (tasks.length > 300) return errorJson(new Error("ส่งได้ครั้งละไม่เกิน 300 งาน"), 400);

  const out = new Array(tasks.length);
  let next = 0;
  async function worker() {
    while (next < tasks.length) {
      const i = next++;
      const { name, blob } = tasks[i];
      const fd = new FormData();
      fd.append("files", blob, name);
      try {
        const { status, body } = await gw("/jobs", { method: "POST", body: fd, timeoutMs: 60000 });
        out[i] = status === 202 ? { file: name, job_id: body.job_id }
                                : { file: name, error: body.detail || `HTTP ${status}` };
      } catch (e) { out[i] = { file: name, error: e.message }; }
    }
  }
  await Promise.all(Array.from({ length: Math.min(6, tasks.length) }, worker));
  const submitted = out.filter((x) => x.job_id);
  return Response.json({ submitted, failed: out.filter((x) => x.error) },
                       { status: submitted.length ? 202 : 502 });
}
