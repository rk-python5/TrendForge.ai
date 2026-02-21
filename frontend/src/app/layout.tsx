import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Sidebar } from "@/components/layout/sidebar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "TrendForge AI — LinkedIn Content Engine",
  description:
    "AI-powered LinkedIn content generation platform. Create, manage, and publish high-quality posts with trending topics and AI assistance.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 lg:ml-64">
              <div className="mx-auto max-w-6xl px-4 py-6 pt-16 sm:px-6 sm:py-8 lg:pt-8">{children}</div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
