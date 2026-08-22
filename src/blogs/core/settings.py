"""Configuration, read from the environment once at assembly.

Every value is validated here rather than at the call site, so a misconfigured
deployment fails at startup with a named field instead of at 3am with a
``TypeError`` deep inside a request.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BLOGS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Environment.LOCAL
    debug: bool = True

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql://lucifer:password123@127.0.0.1:5432/blogs"
    #: The server allows 100 connections in total and is shared with another
    #: application, so the default ceiling here is deliberately modest.
    db_min_pool_size: int = Field(default=2, ge=1)
    db_max_pool_size: int = Field(default=10, ge=1)
    db_connect_timeout_s: float = Field(default=10.0, gt=0)
    db_pool_timeout_s: float = Field(default=10.0, gt=0)
    #: A query that runs longer than this is a bug, and killing it protects the
    #: pool from being drained by one pathological statement.
    db_statement_timeout_ms: int = Field(default=15_000, gt=0)
    db_idle_in_transaction_timeout_ms: int = Field(default=30_000, gt=0)
    db_max_lifetime_s: float = Field(default=3600.0, gt=0)
    db_max_idle_s: float = Field(default=600.0, gt=0)

    # ── Object store (MinIO) ────────────────────────────────────────────────
    object_store_endpoint: str = "127.0.0.1:9002"
    object_store_access_key: SecretStr = SecretStr("lucifer")
    object_store_secret_key: SecretStr = SecretStr("password123")
    object_store_bucket: str = "blogs"
    object_store_secure: bool = False
    object_store_region: str | None = None

    # ── Tokens ──────────────────────────────────────────────────────────────
    #: HS256 over a shared secret. Asymmetric signing only earns its complexity
    #: when a second service must verify without being able to mint, and there
    #: is exactly one service here.
    jwt_secret: SecretStr = SecretStr("dev-insecure-change-me-jwt-secret-value")
    jwt_issuer: str = "blogs"
    access_token_ttl_s: int = Field(default=900, gt=0)
    refresh_token_ttl_s: int = Field(default=60 * 60 * 24 * 30, gt=0)

    #: A separate key from the JWT one: an actor token asserts far less, lives
    #: far longer, and must never be confusable with an access token.
    actor_token_secret: SecretStr = SecretStr("dev-insecure-change-me-actor-secret")
    actor_token_ttl_s: int = Field(default=60 * 60 * 24 * 365, gt=0)

    # ── OTP ─────────────────────────────────────────────────────────────────
    otp_length: int = Field(default=6, ge=4, le=10)
    otp_ttl_s: int = Field(default=600, gt=0)
    otp_max_attempts: int = Field(default=5, ge=1)
    otp_resend_cooldown_s: int = Field(default=60, ge=0)
    #: Mixed into the code before hashing, so a leaked database alone does not
    #: let an attacker precompute the 10^6 possible six-digit codes.
    otp_pepper: SecretStr = SecretStr("dev-insecure-change-me-otp-pepper")
    #: Development convenience: log the code so a local sign-in works before F2
    #: exists to email it. Refused in production by the validator below.
    otp_log_codes: bool = True

    # ── OAuth ───────────────────────────────────────────────────────────────
    oauth_redirect_base_url: str = "http://127.0.0.1:8080"
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    github_client_id: str | None = None
    github_client_secret: SecretStr | None = None

    # ── Content ─────────────────────────────────────────────────────────────
    max_markdown_bytes: int = Field(default=2 * 1024 * 1024, gt=0)
    default_page_size: int = Field(default=20, ge=1, le=100)
    max_page_size: int = Field(default=100, ge=1, le=500)

    # ── Bootstrap ───────────────────────────────────────────────────────────
    #: The single admin, seeded at startup if no admin exists. The partial
    #: unique index is the real guarantee; this only decides who it is.
    admin_email: str | None = None

    #: The admin's initial password, set once at seed time and then forgotten —
    #: it is hashed into `users.password_hash` and this value is never read
    #: again. Leave unset to seed an admin who cannot password-log-in yet.
    admin_initial_password: SecretStr | None = None

    # ── Admin surface ───────────────────────────────────────────────────────
    #: The unguessable path the admin surface is mounted under, e.g.
    #: "/k3f9x2qp/console-7a1b". Every admin route — including admin sign-in —
    #: lives below it, and nothing admin-shaped is reachable at a guessable URL.
    #:
    #: This is obscurity, and obscurity is not authentication: the real control
    #: is still `require_admin`, which checks a signed token on every request
    #: and is what actually stops a non-admin. What the secret prefix buys is
    #: that automated scanners never find a login form to attack in the first
    #: place, which removes essentially all of the background credential-
    #: stuffing traffic. Defence in depth, not the defence.
    admin_path_prefix: str = "/admin-console"

    #: Admin password sign-in throttling. Stricter than OTP because the secret
    #: being guessed is long-lived rather than valid for ten minutes.
    admin_max_failed_logins: int = Field(default=5, ge=1)
    admin_lockout_window_s: int = Field(default=900, gt=0)

    # ── Outbox worker ───────────────────────────────────────────────────────
    outbox_batch_size: int = Field(default=50, ge=1)
    outbox_poll_interval_s: float = Field(default=1.0, gt=0)
    outbox_max_attempts: int = Field(default=8, ge=1)
    engagement_partition_months_ahead: int = Field(default=3, ge=1)

    @model_validator(mode="after")
    def _production_refuses_dev_defaults(self) -> Self:
        """Fail at assembly rather than ship the placeholder secrets.

        These defaults exist so a clone runs with no configuration at all. That
        convenience is only safe if it cannot survive into production, so the
        check lives here and not in a deployment checklist somebody forgets.
        """
        if self.environment is not Environment.PRODUCTION:
            return self

        insecure = [
            name
            for name in ("jwt_secret", "actor_token_secret", "otp_pepper")
            if "dev-insecure" in getattr(self, name).get_secret_value()
        ]
        if insecure:
            raise ValueError(
                f"refusing to start in production with development secrets: {sorted(insecure)}"
            )
        if self.otp_log_codes:
            raise ValueError("refusing to start in production with otp_log_codes enabled")
        if self.db_min_pool_size > self.db_max_pool_size:
            raise ValueError("db_min_pool_size cannot exceed db_max_pool_size")
        # A default or short admin prefix is guessable, which is the one thing
        # the prefix exists to prevent. Refused here rather than documented,
        # because a documented convention is one nobody checks on deploy day.
        if self.admin_path_prefix.strip("/") in ("admin", "admin-console", ""):
            raise ValueError(
                "refusing to start in production with a guessable admin_path_prefix; "
                "set BLOGS_ADMIN_PATH_PREFIX to a secret path"
            )
        if len(self.admin_path_prefix.strip("/")) < 16:
            raise ValueError(
                "admin_path_prefix must be at least 16 characters to be unguessable"
            )
        return self

    @model_validator(mode="after")
    def _normalise_admin_prefix(self) -> Self:
        """A leading slash and no trailing one, so route paths concatenate cleanly."""
        cleaned = "/" + self.admin_path_prefix.strip().strip("/")
        if cleaned != self.admin_path_prefix:
            object.__setattr__(self, "admin_path_prefix", cleaned)
        return self
