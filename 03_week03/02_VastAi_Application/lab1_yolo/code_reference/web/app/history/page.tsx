import Link from "next/link";
import { pool, ready } from "@/lib/db";

export const dynamic = "force-dynamic";

const fmt = (d: Date) => d.toLocaleString("th-TH", { timeZone: "Asia/Bangkok", dateStyle: "medium", timeStyle: "medium" });

export default async function History() {
  await ready();
  const [{ rows }, tot] = await Promise.all([
    pool.query(`SELECT id, created_at, filename, passed, persons, hardhat, no_hardhat, no_vest, inference_ms, roundtrip_ms
                FROM inspections ORDER BY id DESC LIMIT 200`),
    pool.query(`SELECT count(*)::int AS total, count(*) FILTER (WHERE passed)::int AS pass, count(*) FILTER (WHERE NOT passed)::int AS fail FROM inspections`),
  ]);
  const t = tot.rows[0] as { total: number; pass: number; fail: number };

  return (
    <>
      <div className="page-head">
        <h1>ประวัติการตรวจ</h1>
        <p className="muted">ผลตรวจทุกครั้งถูกบันทึกในฐานข้อมูล กดที่รายการเพื่อดูรายละเอียด</p>
      </div>
      <div className="totals">
        <div className="total-card"><div className="stat-value">{t.total}</div><div className="stat-label">ตรวจทั้งหมด</div></div>
        <div className="total-card good"><div className="stat-value">{t.pass}</div><div className="stat-label">ผ่าน</div></div>
        <div className="total-card bad"><div className="stat-value">{t.fail}</div><div className="stat-label">ไม่ผ่าน</div></div>
      </div>
      <section className="card">
        {rows.length === 0 ? (
          <div className="empty">ยังไม่มีประวัติ — <Link className="link" href="/">ไปตรวจภาพแรก</Link></div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th><th>เวลา</th><th>ไฟล์</th><th>ผล</th><th className="num">คน</th><th className="num">สวมหมวก</th>
                  <th className="num">ไม่สวมหมวก</th><th className="num">ไม่สวมเสื้อสะท้อนแสง</th><th className="num">โมเดล (ms)</th><th className="num">ไป-กลับ (ms)</th><th />
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td className="nowrap">{fmt(r.created_at)}</td>
                    <td className="file">{r.filename}</td>
                    <td><span className={`pill ${r.passed ? "pass" : "fail"}`}>{r.passed ? "ผ่าน" : "ไม่ผ่าน"}</span></td>
                    <td className="num">{r.persons}</td>
                    <td className="num">{r.hardhat}</td>
                    <td className="num">{r.no_hardhat}</td>
                    <td className="num">{r.no_vest}</td>
                    <td className="num">{Number(r.inference_ms).toFixed(1)}</td>
                    <td className="num">{Math.round(r.roundtrip_ms)}</td>
                    <td><Link className="link" href={`/history/${r.id}`}>ดู →</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
