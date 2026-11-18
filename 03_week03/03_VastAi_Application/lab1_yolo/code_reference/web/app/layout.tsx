import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import HealthBadge from "@/components/HealthBadge";

export const metadata: Metadata = { title: "SiteSafe — ตรวจความปลอดภัยหน้างาน", description: "ตรวจการสวมหมวกนิรภัยจากภาพด้วย AI" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body>
        <header className="topbar">
          <div className="wrap topbar-in">
            <Link href="/" className="brand">
              <span className="logo">⛑</span> SiteSafe
            </Link>
            <nav>
              <Link href="/">ตรวจภาพ</Link>
              <Link href="/history">ประวัติ</Link>
            </nav>
            <HealthBadge />
          </div>
        </header>
        <main className="wrap">{children}</main>
        <footer className="wrap footer muted small">SiteSafe · ตรวจหมวกนิรภัยด้วยโมเดล YOLO บน AI server</footer>
      </body>
    </html>
  );
}
