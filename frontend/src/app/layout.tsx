import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "DevOps Runtime Emotions AI Studio",
  description: "Auto-generate DevOps-themed Instagram humor powered by free AI",
  keywords: ["DevOps", "Kubernetes", "memes", "AI", "Instagram", "humor"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
