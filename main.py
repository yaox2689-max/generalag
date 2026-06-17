from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from config import settings
from api.routes import router as api_router

app = FastAPI(title="General Agent", version="0.1.0")

# API routes
app.include_router(api_router)

# Frontend static files (production mode)
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    @app.get("/")
    async def serve_frontend():
        return FileResponse(FRONTEND_DIST / "index.html")

    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
