import { NextResponse } from "next/server";

import { demoCookieName } from "@/features/auth/server/demo-session";
import { COOKIE, cookieOptions } from "@/shared/api/cookies";
import type { APIResponse } from "@/shared/contracts";

/**
 * `POST /api/auth/sign-out` — clear the session cookies.
 *
 * Clears all four unconditionally, including the demo cookie: sign-out should
 * never leave a credential behind because of which mode the site happens to be
 * running in, and expiring a cookie that was not set is harmless.
 *
 * The actor cookie is deliberately *kept*. It is not a credential — it is the
 * anonymous identity that owns the visitor's reading history, and clearing it
 * on sign-out would orphan everything they read before signing in, which is
 * exactly what the merge-on-login exists to preserve.
 */
export async function POST() {
  const response = NextResponse.json<APIResponse<null>>({
    success: true,
    message: "Signed out.",
    data: null,
    error: null,
  });

  response.cookies.set(COOKIE.access, "", cookieOptions.clear());
  response.cookies.set(COOKIE.refresh, "", cookieOptions.clear());
  response.cookies.set(demoCookieName, "", cookieOptions.clear());

  return response;
}
