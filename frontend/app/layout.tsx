import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";
import { WalletProviders } from "@/components/WalletProviders";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Commitment Broker",
  description: "AI agent system for financial goal commitment tracking",
  icons: {
    icon: "/assets/commitmentbroker.png",
    apple: "/assets/commitmentbroker.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <WalletProviders>
          <Navigation />
          {children}
        </WalletProviders>
      </body>
    </html>
  );
}
