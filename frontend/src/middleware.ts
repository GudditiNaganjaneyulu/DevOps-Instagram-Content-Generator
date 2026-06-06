import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PRIVATE_PATHS = ["/dashboard", "/generate", "/gallery", "/incidents", "/trends", "/settings", "/admin"];

export default auth((req) => {
  const { pathname } = req.nextUrl;
  const isPrivate = PRIVATE_PATHS.some((p) => pathname.startsWith(p));

  if (isPrivate && !req.auth) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect logged-in users away from /login
  if (pathname === "/login" && req.auth) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
