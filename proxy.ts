import { clerkMiddleware } from "@clerk/nextjs/server";
import { NextResponse, type NextRequest, type NextFetchEvent } from "next/server";
import { setupAvailable } from "./lib/setup";
const protectedRoutes = clerkMiddleware(async (auth, req) => {
  if (!/^\/sign-(in|up)(\/|$)/.test(req.nextUrl.pathname)) await auth.protect();
}, { signInUrl: "/sign-in", signUpUrl: "/sign-up" });
export default function proxy(req: NextRequest, event: NextFetchEvent) {
  if (!setupAvailable()) {
    if (/^\/(api|trpc)(\/|$)/.test(req.nextUrl.pathname))
      return NextResponse.json({ error: "Authentication setup unavailable" }, { status: 503 });
    // Layout renders only the setup screen, never protected children.
    return NextResponse.next();
  }
  return protectedRoutes(req, event);
}
export const config = { matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|webmanifest)).*)", "/(api|trpc)(.*)"] };
