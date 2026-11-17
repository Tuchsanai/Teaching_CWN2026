import Link from "next/link";
import { notFound } from "next/navigation";
import BoxedImage from "@/components/BoxedImage";
import ResultPanel from "@/components/ResultPanel";
import { getInspection } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function Detail({ params }: { params: { id: string } }) {
  const r = await getInspection(Number(params.id));
  if (!r) notFound();
  return (
    <>
      <div className="page-head">
        <Link href="/history" className="back">
          ← กลับไปหน้าประวัติ
        </Link>
        <h1>ผลตรวจ #{r.id}</h1>
        <p className="muted">
          {r.file_name} · {r.created_at}
        </p>
      </div>
      <div className="grid">
        <section className="card">
          <BoxedImage src={`/api/image/${r.id}`} width={r.width} height={r.height} detections={r.detections} hide={["Person"]} />
        </section>
        <section className="card">
          <ResultPanel
            summary={{ persons: r.persons, hardhat: r.hardhat, no_hardhat: r.no_hardhat, no_vest: r.no_vest, passed: r.passed }}
            detections={r.detections}
            inference_ms={r.inference_ms}
            roundtrip_ms={r.roundtrip_ms}
            model={r.model}
          />
        </section>
      </div>
    </>
  );
}
