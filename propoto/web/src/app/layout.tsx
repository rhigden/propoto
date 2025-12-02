import type { Metadata } from "next";
import { Roboto_Slab } from "next/font/google";
import "./globals.css";
import ConvexClientProvider from "./ConvexClientProvider";

const robotoSlab = Roboto_Slab({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-roboto-slab",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "Propoto",
  description: "Turn a URL into a $10K proposal in 60 seconds",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={robotoSlab.variable}>
      <body className={`${robotoSlab.className} antialiased tracking-tight subpixel-antialiased`}>
        <ConvexClientProvider>{children}</ConvexClientProvider>
      </body>
    </html>
  );
}
