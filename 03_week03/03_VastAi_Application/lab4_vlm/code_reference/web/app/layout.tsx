import "./globals.css";
import Nav from "./nav";

export const metadata = { title: "สมุดรายจ่ายจากใบเสร็จ", description: "อ่านใบเสร็จด้วย AI แล้วบันทึกเป็นรายจ่าย" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet" />
      </head>
      <body>
        <header className="top">
          <div className="wrap top-in">
            <a href="/read" className="brand"><span className="logo">🧾</span> สมุดรายจ่ายจากใบเสร็จ</a>
            <Nav />
          </div>
        </header>
        <main className="wrap">{children}</main>
        <footer className="wrap foot">อ่านใบเสร็จด้วย Qwen3-VL-2B บน AI server (Vast.ai) · ราคาเป็นรูเปียห์อินโดนีเซีย (Rp)</footer>
      </body>
    </html>
  );
}
