"use client";

import { Fragment, useEffect, useState } from "react";

type Item = { name: string; qty: number | null; price: number | null };
type Expense = { id: number; created_at: string; model: "base" | "ft"; source: string; items: Item[]; subtotal: string | null; tax: string | null; total: string | null; thumb: string };

const num = (v: number | string | null) => (v === null ? "–" : Number(v).toLocaleString("en-US"));

export default function Expenses() {
  const [rows, setRows] = useState<Expense[] | null>(null);
  const [open, setOpen] = useState<number | null>(null);

  const load = () => fetch("/api/expenses").then((r) => r.json()).then((j) => setRows(j.expenses));
  useEffect(() => {
    load();
  }, []);

  async function remove(id: number) {
    await fetch(`/api/expenses?id=${id}`, { method: "DELETE" });
    load();
  }

  if (!rows) return <div className="panel empty">กำลังโหลด…</div>;
  const sum = rows.reduce((a, r) => a + Number(r.total ?? 0), 0);
  const nItems = rows.reduce((a, r) => a + r.items.length, 0);

  return (
    <div className="expenses">
      <div className="stats">
        <div className="stat"><small>ใบเสร็จที่บันทึก</small><b data-testid="count">{rows.length}</b><span>ใบ</span></div>
        <div className="stat"><small>รายการสินค้า</small><b>{nItems}</b><span>รายการ</span></div>
        <div className="stat main"><small>รายจ่ายรวม</small><b data-testid="sum">{num(sum)}</b><span>Rp</span></div>
      </div>
      <section className="panel">
        <h2>รายจ่ายทั้งหมด</h2>
        {rows.length === 0 ? (
          <div className="empty">ยังไม่มีรายจ่าย — ไปที่หน้า “อ่านใบเสร็จ” แล้วกดบันทึก</div>
        ) : (
          <table className="list">
            <thead>
              <tr><th></th><th>เวลา</th><th>ใบเสร็จ</th><th>อ่านด้วย</th><th className="n">รายการ</th><th className="n">ยอดรวม (Rp)</th><th></th></tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <Fragment key={r.id}>
                  <tr onClick={() => setOpen(open === r.id ? null : r.id)} className="row">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <td>{r.thumb && <img className="thumb" src={r.thumb} alt="" />}</td>
                    <td>{new Date(r.created_at).toLocaleString("th-TH", { dateStyle: "medium", timeStyle: "short" })}</td>
                    <td>{r.source}</td>
                    <td><span className={`badge ${r.model}`}>{r.model === "ft" ? "Fine-tuned" : "Base"}</span></td>
                    <td className="n">{r.items.length}</td>
                    <td className="n total">{num(r.total)}</td>
                    <td className="n"><button className="del" onClick={(e) => { e.stopPropagation(); remove(r.id); }}>ลบ</button></td>
                  </tr>
                  {open === r.id && (
                    <tr className="detail">
                      <td></td>
                      <td colSpan={6}>
                        {r.items.map((it, i) => (
                          <div key={i} className="line"><span>{it.name}</span><span>× {num(it.qty)}</span><span>{num(it.price)}</span></div>
                        ))}
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
