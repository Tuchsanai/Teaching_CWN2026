'use client';

// Draws the problem boxes over the original photo from the coordinates stored in
// the database (D-08): no second image file is created. Box = [x1, y1, x2, y2] in
// pixels of the original; positions are converted to percentages of the image size.

import { useState } from 'react';

export type Detection = {
  id: number;
  cls: string;
  label: string;
  confidence: number;
  box: [number, number, number, number];
};

export default function PhotoWithBoxes({
  src,
  alt,
  imageW,
  imageH,
  detections,
}: {
  src: string;
  alt: string;
  imageW: number | null;
  imageH: number | null;
  detections: Detection[];
}) {
  const [natural, setNatural] = useState<{ w: number; h: number } | null>(null);
  const [failed, setFailed] = useState(false);
  // Size of the original: from the database, else from the loaded image, else (image
  // not loaded yet / unreadable) the extent of the boxes so every box is still shown.
  const extentW = Math.max(1, ...detections.map((d) => Math.max(d.box[0], d.box[2])));
  const extentH = Math.max(1, ...detections.map((d) => Math.max(d.box[1], d.box[3])));
  const w = imageW ?? natural?.w ?? extentW;
  const h = imageH ?? natural?.h ?? extentH;

  return (
    <div className="photo-frame">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        data-testid="photo-image"
        src={src}
        alt={alt}
        onLoad={(e) => setNatural({ w: e.currentTarget.naturalWidth, h: e.currentTarget.naturalHeight })}
        onError={() => setFailed(true)}
      />
      {failed && (
        <p className="error" style={{ lineHeight: 1.5 }}>
          เปิดไฟล์รูปไม่ได้
        </p>
      )}
      {w > 0 &&
        h > 0 &&
        detections.map((d, i) => {
          const [x1, y1, x2, y2] = d.box;
          const left = (Math.min(x1, x2) / w) * 100;
          const top = (Math.min(y1, y2) / h) * 100;
          const width = (Math.abs(x2 - x1) / w) * 100;
          const height = (Math.abs(y2 - y1) / h) * 100;
          return (
            <div
              key={d.id}
              className={`photo-box ${d.cls}`}
              data-testid={`photo-box-${i}`}
              data-cls={d.cls}
              style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }}
              title={`${d.label} (${(d.confidence * 100).toFixed(0)}%)`}
            >
              <span className="label" data-testid={`photo-box-label-${i}`}>
                {d.label}
              </span>
            </div>
          );
        })}
    </div>
  );
}
