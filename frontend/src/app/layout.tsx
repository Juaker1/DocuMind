import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { AuthProvider } from "@/features/auth/AuthProvider";

export const metadata: Metadata = {
  title: "DocuMind - Chat con tus PDFs",
  description: "Sistema inteligente para chatear con documentos PDF usando IA",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="min-h-screen bg-gray-50 dark:bg-gray-950 antialiased transition-colors duration-200">
        <ThemeProvider>
          <AuthProvider>
            <Header />
            <main className="pb-12">
              {children}
            </main>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
