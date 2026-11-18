"use client";
import { Fragment, useEffect, useState } from "react";
import { rp, type Item } from "@/lib/receipt";

type Row = { id: number; title: string; model: string; items: Item[]; subtotal: number | null; tax: number | null; total: number | null; seconds: number | null; created_at: string };

export default function ExpensesPage() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [open, setOpen] = useState<number | null>(null);
  const load = () => fetch("/api/expenses", { cache: "no-store" }).then((r) => r.json()).then(setRows);
  useEffect(() => { load(); }, []);

  async function remove(id: number) {
    await fetch(`/api/expenses/${id}`, { method: "DELETE" });
    if (open === id) setOpen(null);
    load();
  }
  const sum = (rows ?? []).reduce((a, r) => a + (r.total ?? r.subtotal ?? 0), 0);
  const fmtDate = (s: string) => new Date(s).toLocaleString("th-TH", { dateStyle: "medium", timeStyle: "short" });

  return (
    <>
      <h1>รายจ่าย</h1>
      <p className="sub">ใบเสร็จที่บันทึกไว้ทั้งหมด</p>
      <div className="stats">
        <div className="card stat"><div className="k">จำนวนใบเสร็จ</div><div className="v">{rows ? rows.length : "…"} ใบ</div></div>
        <div className="card stat"><div className="k">รายจ่ายรวม</div><div className="v">{rows ? rp(sum) : "…"}</div></div>
      </div>
      <section className="card">
        <table>
          <thead>
            <tr><th></th><th>ใบเสร็จ</th><th>บันทึกเมื่อ</th><th>อ่านด้วย</th><th className="num">รายการ</th><th className="num">ยอดรวม</th><th></th></tr>
          </thead>
          <tbody>
            {rows?.length === 0 && (
              <tr><td colSpan={7} className="empty">ยังไม่มีรายจ่าย · ไปที่ <a href="/read" style={{ textDecoration: "underline" }}>อ่านใบเสร็จ</a></td></tr>
            )}
            {rows?.map((r) => (
              <Fragment key={r.id}>
                <tr>
                  <td><img className="thumb" src={`/api/expenses/${r.id}/image`} alt="" /></td>
                  <td><b>{r.title}</b></td>
                  <td>{fmtDate(r.created_at)}</td>
                  <td><span className={"badge " + (r.model === "Base" ? "base" : "ft")}>{r.model}</span></td>
                  <td className="num">{r.items.length}</td>
                  <td className="num"><b>{rp(r.total ?? r.subtotal)}</b></td>
                  <td className="num">
                    <button className="btn ghost small" onClick={() => setOpen(open === r.id ? null : r.id)}>{open === r.id ? "ซ่อน" : "ดูรายการ"}</button>{" "}
                    <button className="btn danger small" onClick={() => remove(r.id)}>ลบ</button>
                  </td>
                </tr>
                {open === r.id && (
                  <tr className="detail">
                    <td></td>
                    <td colSpan={6}>
                      <table>
                        <thead><tr><th>รายการ</th><th className="num">จำนวน</th><th className="num">ราคา</th></tr></thead>
                        <tbody>
                          {r.items.map((it, i) => (
                            <tr key={i}><td>{it.name}</td><td className="num">{it.qty}</td><td className="num">{rp(it.price)}</td></tr>
                          ))}
                          <tr><td colSpan={2}>ยอดก่อนภาษี / ภาษี</td><td className="num">{rp(r.subtotal)} / {rp(r.tax)}</td></tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
