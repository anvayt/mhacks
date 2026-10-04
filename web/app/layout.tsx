import type { Metadata } from "next";
import { Anton, IBM_Plex_Mono, Instrument_Serif, Inter } from "next/font/google";
import "./globals.css";

const anton = Anton({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-anton",
});

const plex = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-plex",
});

const instrument = Instrument_Serif({
  weight: "400",
  style: "italic",
  subsets: ["latin"],
  variable: "--font-instrument",
});

const inter = Inter({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Hidden Rent",
  description: "The rent you don't see. The energy bill a rental listing leaves out.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${anton.variable} ${plex.variable} ${instrument.variable} ${inter.variable}`}>
      <body>{children}</body>
    </html>
  );
}
