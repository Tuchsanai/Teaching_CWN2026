import type { Metadata } from "next";
import Link from "next/link";
import { Noto_Sans_Thai } from "next/font/google";
import "./globals.css";

const font = Noto_Sans_Thai({ subsets: ["thai", "latin"], weight: ["400", "500", "700"], display: "swap" });

export const metadata: Metadata = {
  title: "สมุดรายจ่ายจากใบเสร็จ",
  description: "อัปโหลดรูปใบเสร็จ ให้ VLM อ่านเป็นรายการและยอดรวม แล้วบันทึกเป็นรายจ่าย",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body className={font.className}>
        <header className="top">
          <div className="brand">
            <span className="logo">฿</span>
            <div>
              <b>สมุดรายจ่ายจากใบเสร็จ</b>
              <small>อัปโหลดรูปใบเสร็จ ให้ VLM อ่านเป็นรายการและยอดรวม</small>
            </div>
          </div>
          <nav>
            <Link href="/">อ่านใบเสร็จ</Link>
            <Link href="/expenses">รายจ่าย</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
