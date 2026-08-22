import {
  DEMO_OTP_CODE,
  demoAuthEnabled,
  demoCookie,
  demoUserFor,
} from "@/features/auth/server/demo-session";
import { fail, ok } from "@/shared/api/responses";
import type { User } from "@/shared/contracts";

/**
 * `POST /api/auth/otp-verify` — exchange a code for a session.
 *
 * A local route rather than a BFF passthrough because the backend's response
 * carries the token pair, and those must become httpOnly cookies on the server
 * rather than be handed to the browser.
 *
 * Two modes, and the split is the security boundary:
 *
 * - **sample** (`BLOGS_DATA_SOURCE=fixtures`) — any email plus `000000` signs
 *   in as a demo reader. There is no backend and no real account, so there is
 *   nothing here to reach beyond invented articles.
 * - **api** — refuses, pending the real exchange in Phase 2. It fails closed
 *   rather than falling back to the demo path, because a fixed code that
 *   worked against real data would be an unauthenticated sign-in as anyone.
 */
export async function POST(request: Request) {
  if (!demoAuthEnabled()) {
    return fail(
      501,
      "INTERNAL_ERROR",
      "Sign-in is not connected yet. Set BLOGS_DATA_SOURCE=fixtures for sample mode.",
      { stage: "AUTH" },
    );
  }

  let body: { email?: unknown; code?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return fail(400, "REQUEST_INVALID", "Expected a JSON body.");
  }

  const email = typeof body.email === "string" ? body.email.trim() : "";
  const code = typeof body.code === "string" ? body.code.trim() : "";

  if (!email.includes("@")) {
    return fail(400, "REQUEST_INVALID", "Enter a valid email address.", {
      details: { fields: [{ field: "email", reason: "INVALID" }] },
    });
  }

  if (code !== DEMO_OTP_CODE) {
    // The same category and wording the backend uses for a wrong code — the
    // demo path should not teach a different vocabulary from the real one.
    return fail(400, "OTP_INVALID", "That code is not correct.", { stage: "AUTH" });
  }

  const cookie = demoCookie(email);
  const response = ok<User>(demoUserFor(email));
  response.cookies.set(cookie.name, cookie.value, cookie.options);

  return response;
}
