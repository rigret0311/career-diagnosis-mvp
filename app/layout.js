import { Shippori_Mincho, Zen_Kaku_Gothic_New } from "next/font/google";
import "./globals.css";

const sans = Zen_Kaku_Gothic_New({
  variable: "--font-sans",
  weight: ["400", "500", "700", "900"],
  subsets: ["latin"],
  display: "swap",
});

const serif = Shippori_Mincho({
  variable: "--font-serif",
  weight: ["500", "700", "800"],
  subsets: ["latin"],
  display: "swap",
});

export const metadata = {
  title: "キャリア現在地診断 | 3分で次の一手がわかる",
  description: "9つの質問から市場価値ランク、想定年収レンジ、狙い目の職種、30日アクションを無料で整理します。",
  openGraph: {
    title: "キャリア現在地診断",
    description: "今のままでいいのかを、3分で言葉にする。",
    type: "website",
    locale: "ja_JP",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="ja">
      <body className={`${sans.variable} ${serif.variable}`}>{children}</body>
    </html>
  );
}
