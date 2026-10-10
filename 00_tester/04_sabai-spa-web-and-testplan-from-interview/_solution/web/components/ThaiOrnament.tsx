// ลวดลายไทย (FR-32): ดอกบัว ดอกกล้วยไม้ และเส้นกนกสีทอง วาดด้วย SVG
export function Lotus({ size = 64, className = "" }: { size?: number; className?: string }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round">
        <path d="M32 10c6 8 6 20 0 30-6-10-6-22 0-30z" fill="var(--lotus-fill, rgba(201,163,78,.18))" />
        <path d="M32 40c-4-9-12-15-22-16 2 10 10 17 22 16z" />
        <path d="M32 40c4-9 12-15 22-16-2 10-10 17-22 16z" />
        <path d="M32 40c-8-4-17-4-26 0 8 6 18 6 26 0z" />
        <path d="M32 40c8-4 17-4 26 0-8 6-18 6-26 0z" />
        <path d="M14 50c12 4 24 4 36 0" />
      </g>
    </svg>
  );
}

export function Orchid({ size = 64, className = "" }: { size?: number; className?: string }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round">
        <path d="M32 30c-3-9-1-17 0-20 1 3 3 11 0 20z" fill="rgba(160,90,160,.15)" />
        <path d="M32 30c-8-5-17-4-21 0 5 5 13 6 21 0z" fill="rgba(160,90,160,.12)" />
        <path d="M32 30c8-5 17-4 21 0-5 5-13 6-21 0z" fill="rgba(160,90,160,.12)" />
        <path d="M32 30c-6 4-9 12-7 20 5-3 8-10 7-20z" />
        <path d="M32 30c6 4 9 12 7 20-5-3-8-10-7-20z" />
        <circle cx="32" cy="31" r="2.5" fill="currentColor" />
        <path d="M32 50v10" />
      </g>
    </svg>
  );
}

/** แถบลายกนกทองคั่นหัวข้อ */
export function GoldDivider() {
  return (
    <div className="gold-divider" aria-hidden="true">
      <span />
      <Lotus size={28} />
      <span />
    </div>
  );
}
