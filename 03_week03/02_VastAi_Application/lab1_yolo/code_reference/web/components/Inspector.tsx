"use client";
import { useRef, useState } from "react";
import BoxedImage from "./BoxedImage";
import ResultPanel from "./ResultPanel";
import type { Detection, Summary } from "@/lib/types";

const SAMPLES = ["no_hardhat_1", "no_hardhat_2", "no_hardhat_3", "all_hardhat_1", "all_hardhat_2", "all_hardhat_3"];
type Result = { id: number; model: string; width: number; height: number; inference_ms: number; roundtrip_ms: number; detections: Detection[]; summary: Summary };

export default function Inspector() {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [preview, setPreview] = useState("");
  const [res, setRes] = useState<Result | null>(null);
  const [drag, setDrag] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  async function send(file: File) {
    if (!file.type.startsWith("image/")) return setErr("รองรับเฉพาะไฟล์รูปภาพ");
    setErr(""); setRes(null); setBusy(true);
    setPreview((old) => { if (old.startsWith("blob:")) URL.revokeObjectURL(old); return URL.createObjectURL(file); });
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch("/api/detect", { method: "POST", body: fd });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || "ตรวจไม่สำเร็จ");
      setRes(j);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "ตรวจไม่สำเร็จ");
    } finally {
      setBusy(false);
    }
  }

  async function sample(name: string) {
    const b = await (await fetch(`/samples/${name}.jpg`)).blob();
    send(new File([b], `${name}.jpg`, { type: "image/jpeg" }));
  }

  return (
    <div className="grid">
      <section className="card">
        <h2>ตรวจภาพหน้างาน</h2>
        <div
          className={`drop ${drag ? "drag" : ""}`}
          onClick={() => input.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) send(f); }}
        >
          <div className="drop-icon">⬆</div>
          <div><b>คลิกเพื่อเลือกรูป</b> หรือลากรูปมาวางที่นี่</div>
          <div className="muted small">JPG / PNG ไม่เกิน 10 MB</div>
          <input ref={input} type="file" accept="image/*" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) send(f); e.target.value = ""; }} />
        </div>
        <h3>หรือเลือกรูปตัวอย่าง</h3>
        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s} className="sample" disabled={busy} onClick={() => sample(s)} title={s}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`/samples/${s}.jpg`} alt={s} />
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>ผลการตรวจ</h2>
        {err && <div className="alert">{err}</div>}
        {!preview && !err && <div className="empty">อัปโหลดรูปหรือเลือกรูปตัวอย่างเพื่อเริ่มตรวจ</div>}
        {preview && (
          <>
            {res ? (
              <BoxedImage src={preview} width={res.width} height={res.height} detections={res.detections} />
            ) : (
              <div className="boxed loading">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={preview} alt="รูปที่ส่งตรวจ" />
                {busy && <div className="spinner-wrap"><div className="spinner" /> กำลังตรวจ…</div>}
              </div>
            )}
            {res && <ResultPanel s={res.summary} inferenceMs={res.inference_ms} roundtripMs={res.roundtrip_ms} model={res.model} />}
            {res && <a className="link small" href={`/history/${res.id}`}>บันทึกเป็นรายการ #{res.id} · ดูรายละเอียด →</a>}
          </>
        )}
      </section>
    </div>
  );
}
