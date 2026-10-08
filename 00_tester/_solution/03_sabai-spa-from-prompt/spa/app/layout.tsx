import type { Metadata, Viewport } from "next";
import { cookies } from "next/headers";
import { Cormorant_Garamond, Noto_Sans_SC, Noto_Sans_Thai, Prompt } from "next/font/google";
import { AppProvider } from "@/components/AppProvider";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatBot } from "@/components/ChatBot";
import { isLang } from "@/lib/i18n";
import "./globals.css";

export const dynamic = "force-dynamic";

const sans = Noto_Sans_Thai({ subsets: ["thai", "latin"], weight: ["300", "400", "500", "600", "700"], variable: "--font-sans", display: "swap" });
const serif = Prompt({ subsets: ["thai", "latin"], weight: ["400", "500", "600"], variable: "--font-serif", display: "swap" });
const display = Cormorant_Garamond({ subsets: ["latin"], weight: ["500", "600", "700"], style: ["normal", "italic"], variable: "--font-display", display: "swap" });
const sc = Noto_Sans_SC({ weight: ["400", "500", "700"], variable: "--font-sc", display: "swap", preload: false });

export const metadata: Metadata = {
  title: "สบายใจ สปา · Sabai Jai Wellness Spa",
  description: "Contemporary Thai spa in Bangkok — Thai massage, herbal compress, facials, couple suite. Open daily 10:00–22:00.",
  icons: { icon: "/assets/brand/logo.png" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#2F5D3A",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const c = (await cookies()).get("lang")?.value;
  const lang = isLang(c) ? c : "th";
  const bugMode = process.env.BUG_MODE === "1" ? "1" : "0";
  return (
    <html
      lang={lang === "zh" ? "zh-CN" : lang}
      data-ready="false"
      data-bug-mode={bugMode}
      className={`${sans.variable} ${serif.variable} ${display.variable} ${sc.variable}`}
      suppressHydrationWarning
    >
      <body>
        <AppProvider initialLang={lang}>
          <Header />
          <main id="main" className="site-main">
            {children}
          </main>
          <Footer />
          <ChatBot />
        </AppProvider>
      </body>
    </html>
  );
}
