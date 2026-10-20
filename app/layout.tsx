import type { Metadata, Viewport } from "next";
import { Shell } from "../components/shell";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { DataProvider } from "../components/data-provider";
import { setupAvailable } from "../lib/setup";
export const dynamic = "force-dynamic";
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
        {setupAvailable() ? (
          <ClerkProvider signInUrl="/sign-in" signUpUrl="/sign-up" signInFallbackRedirectUrl="/tasks" signUpFallbackRedirectUrl="/tasks">
            <DataProvider><Shell>{children}</Shell></DataProvider>
          </ClerkProvider>
        ) : <main id="main" className="content"><section className="intro"><h1>Setup unavailable</h1><p>Luma requires authentication and cloud persistence configuration before use.</p><p>No demo session is active. No personal data is available.</p></section></main>}
      </body>
    </html>
  );
}
