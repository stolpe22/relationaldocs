import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routers import connections, health, tables  # noqa: E402
from api.state import app_state  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    # Shutdown: fecha túnel e libera recursos
    if app_state.tunnel and app_state.tunnel.is_active:
        app_state.tunnel.close()


app = FastAPI(
    title="Relationals Doc API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
_env = os.getenv("ENV", "development")
_cors_origins_raw = os.getenv("CORS_ORIGINS", "")
if _env == "development":
    _cors_origins: list[str] = ["*"]
elif _cors_origins_raw:
    _cors_origins = [o.strip() for o in _cors_origins_raw.split(",")]
else:
    raise RuntimeError("CORS_ORIGINS deve ser definido em produção.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(connections.router)
app.include_router(tables.router)
