"""The application factory. One app, one port, N uvicorn workers.

``create_app()`` for tests (which can supply their own settings), plus a
module-level ``app`` for ``uvicorn ai_auditor.main:app``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from ai_auditor.api.errors import register_exception_handlers
from ai_auditor.api.routers import (
    agent,
    assets,
    chat,
    conversations,
    health,
    instructions,
    memory,
    projects,
    sprints,
    threads,
)
from ai_auditor.api.routers import (
    settings as settings_router,
)
from ai_auditor.bootstrap import build_container, close_container
from ai_auditor.core.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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

    app = FastAPI(
        title="AI Auditor",
        version="0.1.0",
        description="Multi-agent SDLC document generation and audit.",
        # orjson is measurably faster than the stdlib encoder on the payload
        # shapes here (lists of models with datetimes and UUIDs).
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # Registered before any router, so a failure inside a route is always shaped.
    register_exception_handlers(app)

    if resolved.debug:
        # Wide open in development only. In production the Next.js proxy makes
        # the browser same-origin, so no CORS is needed at all.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    prefix = resolved.api_v1_prefix
    app.include_router(health.router)
    # The hierarchy, outermost first — the same order as the scope ladder, so the
    # generated OpenAPI reads top-down the way the model does.
    app.include_router(settings_router.router, prefix=prefix)
    app.include_router(projects.router, prefix=prefix)
    app.include_router(sprints.router, prefix=prefix)
    app.include_router(conversations.router, prefix=prefix)
    app.include_router(threads.router, prefix=prefix)
    # Scoped content: every one of these hangs off a level of the ladder above.
    app.include_router(instructions.router, prefix=prefix)
    app.include_router(memory.router, prefix=prefix)
    app.include_router(assets.router, prefix=prefix)
    # The agent surfaces.
    app.include_router(agent.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    # Unprefixed: the frontend connects to /ws/{actor_id} at the origin root.
    app.include_router(ws.router)

    return app


app = create_app()
