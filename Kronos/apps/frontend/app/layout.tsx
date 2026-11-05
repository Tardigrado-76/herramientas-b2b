import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tavilga Cronos | Gestión de Producción Sevilla",
  description: "Optimización industrial 4.0 para carpintería tecnológica en Sevilla. Seguimiento de producción y ERP ligero para Aznalcóllar.",
  manifest: "/manifest.json",
  keywords: ["gestión de producción Sevilla", "ERP carpintería", "Tavilga Cronos", "artesanía digital", "Muebles a medida Sevilla Aznalcóllar"],
  authors: [{ name: "Tavilga" }],
};

const JSON_LD = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Tavilga Cronos",
  "operatingSystem": "All",
  "applicationCategory": "BusinessApplication",
  "description": "Sistema de gestión de tiempos y producción para la cooperativa industrial Tavilga en Aznalcóllar, Sevilla.",
  "publisher": {
    "@type": "LocalBusiness",
    "name": "Tavilga Mobiliario",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Calle Mina Silillos 127",
      "addressLocality": "Aznalcóllar",
      "addressRegion": "Sevilla",
      "postalCode": "41870",
      "addressCountry": "ES"
    },
    "telephone": "+34955446532"
  },
  "areaServed": ["Sevilla", "Huelva", "Málaga"]
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
      </head>
      <body className="antialiased">
        <div className={`${geistSans.variable} ${geistMono.variable}`}>
          {children}
        </div>
      </body>
    </html>
  );
}
