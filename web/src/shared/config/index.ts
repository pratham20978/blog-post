import type { OAuthProviderName } from "@/shared/contracts";

/**
 * Runtime configuration.
 *
 * `readServerConfig` runs on the server only and reads `process.env`. The
 * result is handed to `ConfigProvider` as a prop, so client components read it
 * from context rather than from `process.env` directly. That keeps every
 * environment lookup in one auditable place and makes config trivially
 * stubbable in tests.
 */

/** Search has no backend endpoint yet. `mock` filters the cached feed
 *  client-side; `http` targets `GET /api/v1/search` once it exists. */
export type SearchAdapterKind = "mock" | "http";

/**
 * Where article data comes from.
 *
 * `fixtures` renders the whole site from typed sample data with no backend
 * running — which is what lets the design be built and reviewed first. `api`
 * talks to FastAPI. The switch is explicit rather than a silent fallback: a
 * production site quietly serving sample articles because the database was
 * unreachable would be far worse than an error page.
 */
export type DataSource = "fixtures" | "api";

export interface AppConfig {
  readonly siteName: string;
  readonly siteUrl: string;
  readonly searchAdapter: SearchAdapterKind;
  readonly dataSource: DataSource;
  /** Only providers the backend actually has credentials for. Offering one it
   *  lacks produces a 404 `OAUTH_PROVIDER_UNKNOWN` at the worst moment. */
  readonly oauthProviders: readonly OAuthProviderName[];
}

/**
 * Read on the server by the data layer, which cannot use React context.
 *
 * Deliberately NOT a `NEXT_PUBLIC_` variable. Those are inlined into the
 * bundle at build time, which would bake the choice into the artifact — the
 * same build could not be pointed at fixtures in review and at the API in
 * production. This is read at request time on the server and reaches the
 * browser through `ConfigProvider` as a value, not as an environment lookup.
 */
export function dataSource(): DataSource {
  return process.env.BLOGS_DATA_SOURCE === "api" ? "api" : "fixtures";
}

/** Server-side only. Calling this from a client component is a build error in
 *  practice, because `process.env` is not populated there. */
export function readServerConfig(): AppConfig {
  const providers = (process.env.NEXT_PUBLIC_OAUTH_PROVIDERS ?? "google,github")
    .split(",")
    .map((value) => value.trim().toLowerCase())
    .filter((value): value is OAuthProviderName => value === "google" || value === "github");

  return {
    siteName: process.env.NEXT_PUBLIC_SITE_NAME ?? "Canerly",
    siteUrl: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
    searchAdapter: process.env.NEXT_PUBLIC_SEARCH_ADAPTER === "http" ? "http" : "mock",
    dataSource: dataSource(),
    oauthProviders: providers,
  };
}

/**
 * The backend origin. Server-side only, and deliberately not `NEXT_PUBLIC_`:
 * the browser never talks to FastAPI directly, it goes through the BFF proxy.
 */
export function apiOrigin(): string {
  return process.env.BLOGS_API_URL ?? "http://localhost:8000";
}

/** Everything the backend serves lives under this prefix. */
export const API_PREFIX = "/api/v1";

/**
 * The sign-in code accepted in sample mode, with any email address.
 *
 * Lives here rather than in `features/auth/server/demo-session.ts` so the code
 * screen can show it to the reviewer — that module is `server-only`. It is a
 * constant, not a secret: it unlocks invented articles and only when
 * `BLOGS_DATA_SOURCE=fixtures`, which is the guard that makes it safe.
 */
export const DEMO_OTP_CODE = "000000";
