import Link from "next/link";
import { pool } from "@/lib/db";

export const dynamic = "force-dynamic";

type Row = {
  id: number;
  customer_name: string;
  phone: string;
  service_name: string | null;
  price_thb: number | null;
  booking_time: string;
  status: string;
  created_at: string;
};

export default async function BookingsPage() {
  let rows: Row[] = [];
  let error = "";
  try {
    const r = await pool.query<Row>(
      `SELECT b.id, b.customer_name, b.phone, s.name_th AS service_name, s.price_thb,
              to_char(b.booking_time, 'YYYY-MM-DD HH24:MI') AS booking_time, b.status,
              to_char(b.created_at AT TIME ZONE 'Asia/Bangkok', 'YYYY-MM-DD HH24:MI') AS created_at
       FROM bookings b LEFT JOIN services s ON s.id = b.service_id
       ORDER BY b.id DESC`
    );
    rows = r.rows;
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <main className="page wide">
      <header className="topbar">
        <div className="brand">
          <span className="logo">🌿</span>
          <div>
            <h1>รายการจองคิว</h1>
            <p>ข้อมูลจากตาราง bookings ใน PostgreSQL</p>
          </div>
        </div>
        <Link href="/" className="navlink" data-testid="nav-chat">
          ← กลับไปหน้าแชท
        </Link>
      </header>

      <section className="card tablecard">
        {error && <p className="error">เชื่อมต่อฐานข้อมูลไม่ได้: {error}</p>}
        {!error && rows.length === 0 && (
          <p className="empty" data-testid="bookings-empty">
            ยังไม่มีการจอง ลองจองผ่านหน้าแชทดูนะคะ
          </p>
        )}
        {rows.length > 0 && (
          <div className="tablewrap">
            <table data-testid="bookings-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>ชื่อลูกค้า</th>
                  <th>เบอร์โทร</th>
                  <th>บริการ</th>
                  <th>วันเวลานัด</th>
                  <th>สถานะ</th>
                  <th>จองเมื่อ</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} data-testid="booking-row" data-booking-id={r.id}>
                    <td>{r.id}</td>
                    <td data-testid="booking-row-name">{r.customer_name}</td>
                    <td data-testid="booking-row-phone">{r.phone}</td>
                    <td data-testid="booking-row-service">
                      {r.service_name ?? "-"}
                      {r.price_thb != null && <span className="muted"> ({r.price_thb} ฿)</span>}
                    </td>
                    <td data-testid="booking-row-time">{r.booking_time}</td>
                    <td>
                      <span className={`badge ${r.status}`}>{r.status}</span>
                    </td>
                    <td className="muted">{r.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
