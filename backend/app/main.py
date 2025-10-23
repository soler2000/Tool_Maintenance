"""FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

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

    static_directory = Path(__file__).resolve().parent / "static"
    application.mount("/static", StaticFiles(directory=static_directory), name="static")

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

    @application.get("/", include_in_schema=False)
    async def root() -> FileResponse:
        """Serve a static landing page for the Tool Maintenance Portal."""

        return FileResponse(static_directory / "index.html", media_type="text/html")

    @application.get("/health", include_in_schema=False)
    async def healthcheck() -> JSONResponse:
        """Expose a lightweight JSON healthcheck for automation tooling."""

        payload = {"service": settings.app_name, "status": "ok"}
        return JSONResponse(content=payload)

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port, reload=settings.debug)
