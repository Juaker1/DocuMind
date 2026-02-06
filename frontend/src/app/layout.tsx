import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout";

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
    <html lang="es">
      <body className="min-h-screen bg-gray-50 antialiased">
        <Header />
        <main className="pb-12">
          {children}
        </main>
      </body>
    </html>
  );
}
