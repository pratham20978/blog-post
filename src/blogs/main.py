"""The application factory. One app, one port, N uvicorn workers.

``create_app()`` for tests (which can supply their own settings), plus a
module-level ``app`` for ``uvicorn blogs.main:app``.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from blogs.api.errors import register_exception_handlers
from blogs.api.middleware import IdentityMiddleware
from blogs.api.routers import (
    admin_blogs,
    admin_console,
    analytics,
    auth,
    blogs,
    health,
    interaction,
    taxonomy,
)
from blogs.bootstrap import build_container, close_container
from blogs.core.settings import Settings

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        """Assemble on startup, release on shutdown.

        Everything lives on ``app.state`` rather than in module globals, so two
        apps can exist in one process — which is what lets a test build an app
        with fakes without the import having already opened a pool.
        """
        container = await build_container(resolved)
        app.state.container = container
        try:
            yield
        finally:
            await close_container(container)

    # `debug` implies it, so a clone still gets docs with no configuration; a
    # deployment that wants them without debug's wildcard CORS sets the flag.
    serve_docs = resolved.debug or resolved.docs_enabled

    app = FastAPI(
        title="Blogs",
        version="0.1.0",
        description=(
            "Core blog platform: stateless auth, single-admin Markdown authoring, "
            "reader interaction, and the append-only engagement log."
        ),
        # No custom response class: this FastAPI serialises declared return
        # types straight to JSON bytes through pydantic, which is faster than
        # routing them through an encoder and deprecates ORJSONResponse.
        lifespan=lifespan,
        # Admin routes are excluded from the schema below, so /openapi.json
        # never names the secret admin prefix — the one thing the prefix exists
        # to withhold — however this resolves. What publishing it does reveal is
        # the shape of every other endpoint, which for a public API is ordinary.
        openapi_url="/openapi.json" if serve_docs else None,
        docs_url="/docs" if serve_docs else None,
        redoc_url="/redoc" if serve_docs else None,
    )

    # Registered before any router, so a failure inside a route is always shaped.
    register_exception_handlers(app)

    # Identity is resolved here, once per request, before any route runs.
    # Added after the exception handlers and before CORS so that it sits inside
    # the handler stack: a credential failure it defers is raised by the
    # `principal` dependency and still becomes a proper envelope.
    app.add_middleware(IdentityMiddleware)

    if resolved.debug:
        # Wide open in development only. `X-Actor-Token` must be exposed or a
        # browser client cannot read the actor it was just issued, and every
        # anonymous visitor would get a new identity on every request.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Actor-Token", "X-Correlation-ID", "ETag"],
        )

    # Unprefixed: probes are infrastructure, not part of the versioned API.
    app.include_router(health.router)

    # The public API. Everything here is reachable at a predictable URL, which
    # is correct: readers need to find it.
    app.include_router(auth.router, prefix=API_PREFIX)
    app.include_router(blogs.router, prefix=API_PREFIX)
    app.include_router(interaction.router, prefix=API_PREFIX)
    app.include_router(taxonomy.router, prefix=API_PREFIX)

    # The admin surface, mounted only under the secret prefix — nothing
    # admin-shaped answers at a guessable path. Scanners sweeping /admin find a
    # 404 because there is genuinely no route there, not because one refused
    # them. The real control is still `require_admin` on every route below;
    # this only removes the surface from discovery.
    #
    # `include_in_schema=False` keeps these paths out of /openapi.json. The
    # schema enumerates every route, so listing them would publish the secret
    # prefix to anyone who asked for the schema.
    admin_prefix = resolved.admin_path_prefix
    app.include_router(admin_console.router, prefix=admin_prefix, include_in_schema=False)
    app.include_router(admin_blogs.router, prefix=admin_prefix, include_in_schema=False)
    app.include_router(analytics.router, prefix=admin_prefix, include_in_schema=False)

    return app


app = create_app()
