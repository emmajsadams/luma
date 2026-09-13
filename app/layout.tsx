import type { Metadata, Viewport } from "next";
import { Shell } from "../components/shell";
import "./globals.css";
export const metadata: Metadata = {
  title: "Luma · your everyday orbit",
  description: "A little space for your tasks, thoughts, and time.",
  applicationName: "Luma",
  appleWebApp: { capable: true, title: "Luma", statusBarStyle: "default" },
};
export const viewport: Viewport = { themeColor: "#182b2a" };
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
