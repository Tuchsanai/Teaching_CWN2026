// Hand-drawn Thai-style ornaments (inline SVG — no images or icon fonts from the internet).

export function PrajamYam({ size = 18, className = "" }: { size?: number; className?: string }) {
  // four-petal "prajam yam" flower used in Thai textile patterns
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M20 2 C26 10 26 14 20 20 C14 14 14 10 20 2Z" />
        <path d="M38 20 C30 26 26 26 20 20 C26 14 30 14 38 20Z" />
        <path d="M20 38 C14 30 14 26 20 20 C26 26 26 30 20 38Z" />
        <path d="M2 20 C10 14 14 14 20 20 C14 26 10 26 2 20Z" />
        <circle cx="20" cy="20" r="2.6" fill="currentColor" />
      </g>
    </svg>
  );
}

export function ThaiDivider({ className = "" }: { className?: string }) {
  return (
    <div className={`thai-divider ${className}`} aria-hidden="true">
      <span className="thai-divider__line" />
      <svg width="64" height="24" viewBox="0 0 64 24" focusable="false">
        <g fill="none" stroke="currentColor" strokeWidth="1.4">
          <path d="M32 2 C36 8 36 12 32 22 C28 12 28 8 32 2Z" />
          <path d="M32 22 C26 18 20 16 12 17 C18 12 26 13 32 22Z" />
          <path d="M32 22 C38 18 44 16 52 17 C46 12 38 13 32 22Z" />
          <circle cx="4" cy="17" r="1.6" fill="currentColor" />
          <circle cx="60" cy="17" r="1.6" fill="currentColor" />
        </g>
      </svg>
      <span className="thai-divider__line" />
    </div>
  );
}

/** Lotus-petal corner ornament used on cards and frames */
export function KranokCorner({ className = "" }: { className?: string }) {
  return (
    <svg className={className} width="56" height="56" viewBox="0 0 56 56" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="1.3">
        <path d="M2 54 V18 C2 8 8 2 18 2 H54" />
        <path d="M8 54 V22 C8 13 13 8 22 8 H54" opacity=".55" />
        <path d="M14 30 C14 20 20 14 30 14 C24 18 20 24 22 32 C18 30 16 30 14 30Z" />
        <circle cx="30" cy="30" r="2" fill="currentColor" />
      </g>
    </svg>
  );
}

type IconName =
  | "clock" | "phone" | "pin" | "leaf" | "star" | "music" | "music-off" | "menu" | "close" | "chat" | "send" | "arrow" | "check"
  | "car" | "gift" | "spark" | "user" | "calendar" | "drag" | "left" | "right" | "play" | "pause" | "shield";

const P: Record<IconName, string> = {
  clock: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 4v5l3.5 2",
  phone: "M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z",
  pin: "M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21Zm0-9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z",
  leaf: "M5 19C5 10 11 4 20 4c0 9-6 15-15 15Zm0 0 8-8",
  star: "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z",
  music: "M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm11-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z",
  "music-off": "M9 18V6l11-2v8M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM3 3l18 18",
  menu: "M4 7h16M4 12h16M4 17h16",
  close: "M6 6l12 12M18 6 6 18",
  chat: "M4 5h16v11H9l-5 4V5Z",
  send: "M4 12 20 4l-6 16-3-7-7-1Z",
  arrow: "M5 12h14m-5-5 5 5-5 5",
  check: "M5 12.5 10 17l9-10",
  car: "M5 16V11l2-5h10l2 5v5M5 16h14M5 16v2m14-2v2M7.5 13.5h.01M16.5 13.5h.01",
  gift: "M4 10h16v10H4zM3 7h18v3H3zM12 7v13M12 7c-2-4-6-3-5 0m5 0c2-4 6-3 5 0",
  spark: "M12 3v4m0 10v4M3 12h4m10 0h4M6 6l2.5 2.5m7 7L18 18M6 18l2.5-2.5m7-7L18 6",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 9a7 7 0 0 1 14 0",
  calendar: "M4 6h16v14H4zM4 10h16M8 3v4m8-4v4",
  drag: "M8 12h8M5 9l-3 3 3 3m14-6 3 3-3 3",
  left: "M15 5l-7 7 7 7",
  right: "M9 5l7 7-7 7",
  play: "M7 5v14l12-7Z",
  pause: "M7 5h3v14H7zm7 0h3v14h-3z",
  shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6Z",
};

export function Icon({ name, size = 20, className = "" }: { name: IconName; size?: number; className?: string }) {
  const filled = name === "star" || name === "play" || name === "pause";
  return (
    <svg className={`icon ${className}`} width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" focusable="false"
      fill={filled ? "currentColor" : "none"} stroke={filled ? "none" : "currentColor"} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d={P[name]} />
    </svg>
  );
}

export function Stars({ value, size = 16 }: { value: number | null; size?: number }) {
  const v = value ?? 0;
  return (
    <span className="stars" aria-hidden="true">
      {[1, 2, 3, 4, 5].map((i) => {
        const fill = Math.max(0, Math.min(1, v - (i - 1)));
        return (
          <span key={i} className="stars__one" style={{ width: size, height: size }}>
            <Icon name="star" size={size} className="stars__bg" />
            <span className="stars__fg" style={{ width: `${fill * 100}%` }}>
              <Icon name="star" size={size} />
            </span>
          </span>
        );
      })}
    </span>
  );
}
