"use client";
// หน้าตรวจรูป: อัปโหลดหรือเลือกรูปตัวอย่าง → ส่งตรวจ → แสดงกรอบและสรุปผล
import { useRef, useState } from "react";
import BoxedImage from "./BoxedImage";
import ResultPanel from "./ResultPanel";
import { SAMPLES, type Detection, type Summary } from "@/lib/ppe";

type Result = {
  id: number;
  model: string;
  width: number;
  height: number;
  inference_ms: number;
  roundtrip_ms: number;
  detections: Detection[];
  summary: Summary;
};

export default function Inspector() {
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [hidePerson, setHidePerson] = useState(true);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function inspect(file: File) {
    setPreview(URL.createObjectURL(file));
    setFileName(file.name);
    setResult(null);
    setError("");
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch("/api/detect", { method: "POST", body: fd });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || "ตรวจไม่สำเร็จ");
      setResult(j);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function pickSample(file: string) {
    const blob = await (await fetch(`/samples/${file}`)).blob();
    inspect(new File([blob], file, { type: blob.type || "image/jpeg" }));
  }

  return (
    <div className="grid">
      <section className="card">
        <h2>1. เลือกรูปหน้างาน</h2>
        <div
          className={`drop ${drag ? "drag" : ""}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            const f = e.dataTransfer.files[0];
            if (f) inspect(f);
          }}
        >
          <div className="drop-icon">⬆</div>
          <div className="drop-title">อัปโหลดรูป</div>
          <div className="muted">คลิกหรือลากไฟล์ JPG / PNG มาวาง (ไม่เกิน 8 MB)</div>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png"
            hidden
            data-testid="file-input"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) inspect(f);
              e.target.value = "";
            }}
          />
        </div>

        <div className="samples-head">
          <span>หรือกดรูปตัวอย่างจาก Test Set</span>
        </div>
        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s.file} className="sample" onClick={() => pickSample(s.file)} disabled={busy} data-testid={s.file}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`/samples/${s.file}`} alt={s.title} />
              <span>{s.title}</span>
            </button>
          ))}
        </div>
        <p className="credit">
          รูปตัวอย่างจาก Construction Site Safety (Roboflow Universe) · CC BY 4.0
        </p>
      </section>

      <section className="card">
        <div className="card-head">
          <h2>2. ผลตรวจ</h2>
          {result && (
            <label className="toggle">
              <input type="checkbox" checked={hidePerson} onChange={(e) => setHidePerson(e.target.checked)} />
              ซ่อนกรอบ &quot;คน&quot;
            </label>
          )}
        </div>
        {!preview && (
          <div className="empty">
            <div className="empty-icon">⛑</div>
            <div>เลือกรูปทางซ้ายเพื่อเริ่มตรวจ</div>
            <div className="muted">ระบบจะหาคนที่ไม่สวมหมวกนิรภัยและเสื้อสะท้อนแสง</div>
          </div>
        )}
        {preview && (
          <div className="result-layout">
          <div className="stage">
            {result ? (
              <BoxedImage
                src={preview}
                width={result.width}
                height={result.height}
                detections={result.detections}
                hide={hidePerson ? ["Person"] : []}
              />
            ) : (
              <div className={`boxed ${busy ? "scanning" : ""}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={preview} alt={fileName} />
              </div>
            )}
            {busy && <div className="busy">กำลังส่งรูปให้ AI server ตรวจ…</div>}
          </div>
          <div>
            {error && <div className="error">{error}</div>}
            {result && (
              <ResultPanel
                summary={result.summary}
                detections={result.detections}
                inference_ms={result.inference_ms}
                roundtrip_ms={result.roundtrip_ms}
                model={result.model}
              />
            )}
          </div>
          </div>
        )}
      </section>
    </div>
  );
}
