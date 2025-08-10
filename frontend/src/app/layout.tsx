import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import { ThemeProvider } from "@/components/theme-provider";
import TanstackProvider from "@/components/tanstack-provider";
import { UserNav } from "@/components/user-nav";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "G-AI",
  description: "Your intelligent enterprise chat.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <TanstackProvider>
            <div className="flex flex-col min-h-screen">
              <header className="border-b">
                <div className="container mx-auto flex h-16 items-center justify-between px-4">
                  <div className="font-bold">G-AI</div>
                  <UserNav />
                </div>
              </header>
              <main className="flex-grow container mx-auto px-4 py-8">
                {children}
              </main>
            </div>
            <Toaster />
          </TanstackProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
