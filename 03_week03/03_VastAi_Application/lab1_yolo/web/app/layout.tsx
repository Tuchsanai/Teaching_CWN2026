import type { Metadata } from "next";
import Link from "next/link";
import ServerStatus from "@/components/ServerStatus";
import "./globals.css";

export const metadata: Metadata = {
  title: "SiteSafe — ตรวจความปลอดภัยหน้างาน",
  description: "ตรวจหมวกนิรภัยและเสื้อสะท้อนแสงจากรูปถ่ายหน้างานด้วยโมเดล YOLO",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body>
        <header className="top">
          <div className="wrap top-in">
            <Link href="/" className="brand">
              <span className="logo">⛑</span>
              <span>
                <b>SiteSafe</b>
                <small>ตรวจความปลอดภัยหน้างาน</small>
              </span>
            </Link>
            <nav>
              <Link href="/">ตรวจรูป</Link>
              <Link href="/history">ประวัติ</Link>
            </nav>
            <ServerStatus />
          </div>
        </header>
        <main className="wrap">{children}</main>
      </body>
    </html>
  );
}
