"""FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_models
from .routers import actions, auth, failures, maintenance, shot_counters, tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise application resources."""

    await init_models()
    yield


def create_app() -> FastAPI:
    """Instantiate the FastAPI application."""

    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.api_prefix
    application.include_router(auth.router, prefix=api_prefix)
    application.include_router(tools.router, prefix=api_prefix)
    application.include_router(shot_counters.router, prefix=api_prefix)
    application.include_router(maintenance.router, prefix=api_prefix)
    application.include_router(failures.router, prefix=api_prefix)
    application.include_router(actions.router, prefix=api_prefix)

    @application.get("/")
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "status": "ok"}

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port, reload=settings.debug)
