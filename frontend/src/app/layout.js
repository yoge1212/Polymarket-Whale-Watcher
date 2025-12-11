import { IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "./components/Navbar";

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-berkle-mono",
});

export const metadata = {
  title: "Polymarket Whale Watcher",
  description: "Track whale activity on Polymarket",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${ibmPlexMono.variable} antialiased`}>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
