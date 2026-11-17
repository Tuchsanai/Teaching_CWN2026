import Link from "next/link";
import BoxedImage from "@/components/BoxedImage";
import { listInspections, stats } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function History() {
  const [rows, s] = await Promise.all([listInspections(), stats()]);
  return (
    <>
      <div className="page-head">
        <h1>ประวัติการตรวจ</h1>
        <p className="muted">ผลตรวจทุกครั้งเก็บไว้ในฐานข้อมูล PostgreSQL ของเว็บ</p>
      </div>
      <div className="tiles tiles-wide">
        <div className="tile">
          <span className="tile-num">{s.total}</span>
          <span className="tile-lbl">ตรวจทั้งหมด (รูป)</span>
        </div>
        <div className="tile ok">
          <span className="tile-num">{s.passed}</span>
          <span className="tile-lbl">ผ่าน</span>
        </div>
        <div className="tile bad">
          <span className="tile-num">{s.total - s.passed}</span>
          <span className="tile-lbl">ไม่ผ่าน</span>
        </div>
        <div className="tile">
          <span className="tile-num">{s.avg_ms == null ? "-" : `${s.avg_ms.toFixed(1)}`}</span>
          <span className="tile-lbl">เวลาโมเดลเฉลี่ย (ms/รูป)</span>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="card empty">
          ยังไม่มีประวัติ — <Link href="/">ไปตรวจรูปแรก</Link>
        </div>
      ) : (
        <div className="card table-card">
          <table className="hist">
            <thead>
              <tr>
                <th>#</th>
                <th>รูป</th>
                <th>วันเวลา</th>
                <th>ผล</th>
                <th>คนไม่สวมหมวก</th>
                <th>ไม่สวมเสื้อสะท้อนแสง</th>
                <th>เวลาโมเดล</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td className="muted">{r.id}</td>
                  <td>
                    <Link href={`/history/${r.id}`} className="thumb">
                      <BoxedImage
                        src={`/api/image/${r.id}`}
                        width={r.width}
                        height={r.height}
                        detections={r.detections}
                        hide={["Person"]}
                        showLabels={false}
                      />
                    </Link>
                    <div className="fname">{r.file_name}</div>
                  </td>
                  <td>{r.created_at}</td>
                  <td>
                    <span className={`badge ${r.passed ? "pass" : "fail"}`}>{r.passed ? "ผ่าน" : "ไม่ผ่าน"}</span>
                  </td>
                  <td className={r.no_hardhat ? "num bad-text" : "num"}>{r.no_hardhat} คน</td>
                  <td className="num">{r.no_vest} คน</td>
                  <td className="num">{r.inference_ms.toFixed(1)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
