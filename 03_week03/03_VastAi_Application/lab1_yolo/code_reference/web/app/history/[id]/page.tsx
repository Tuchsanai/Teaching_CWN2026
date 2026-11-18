import Link from "next/link";
import { notFound } from "next/navigation";
import BoxedImage from "@/components/BoxedImage";
import ResultPanel from "@/components/ResultPanel";
import { pool, ready } from "@/lib/db";
import { CLASS_TH, type Detection } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function Detail({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  if (!Number.isInteger(id)) notFound();
  await ready();
  const { rows } = await pool.query(
    `SELECT id, created_at, filename, model, width, height, passed, persons, hardhat, no_hardhat, no_vest, inference_ms, roundtrip_ms, detections
     FROM inspections WHERE id=$1`, [id]);
  if (!rows.length) notFound();
  const r = rows[0];
  const dets = r.detections as Detection[];

  return (
    <>
      <div className="page-head">
        <Link className="link small" href="/history">← กลับไปประวัติ</Link>
        <h1>ผลตรวจ #{r.id}</h1>
        <p className="muted">{r.filename} · {new Date(r.created_at).toLocaleString("th-TH", { timeZone: "Asia/Bangkok", dateStyle: "long", timeStyle: "medium" })}</p>
      </div>
      <div className="grid">
        <section className="card">
          <BoxedImage src={`/api/image/${r.id}`} width={r.width} height={r.height} detections={dets} />
        </section>
        <section className="card">
          <ResultPanel
            s={{ persons: r.persons, hardhat: r.hardhat, noHardhat: r.no_hardhat, noVest: r.no_vest, passed: r.passed }}
            inferenceMs={Number(r.inference_ms)} roundtripMs={Number(r.roundtrip_ms)} model={r.model} />
          <h3>กรอบที่ตรวจพบ ({dets.length})</h3>
          <div className="table-wrap">
            <table>
              <thead><tr><th>#</th><th>ประเภท</th><th className="num">ความมั่นใจ</th><th>กรอบ (x1, y1, x2, y2)</th></tr></thead>
              <tbody>
                {dets.map((d, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td>{CLASS_TH[d.class] ?? d.class} <span className="muted small">({d.class})</span></td>
                    <td className="num">{(d.confidence * 100).toFixed(1)}%</td>
                    <td className="mono small">{d.box.map((v) => Math.round(v)).join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </>
  );
}
