import type { Metadata, Viewport } from "next";
import { Noto_Sans_Thai } from "next/font/google";
import "./globals.css";

const font = Noto_Sans_Thai({ subsets: ["thai", "latin"], weight: ["400", "500", "700"], display: "swap" });

export const metadata: Metadata = {
  title: "สบายใจ นวดแผนไทย | แชทสอบถาม & จองคิว",
  description: "แชทบอทร้านสบายใจ นวดแผนไทย สอบถามราคา เวลาเปิดปิด และจองคิวออนไลน์",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#7a4b2a" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body className={font.className}>{children}</body>
    </html>
  );
}
