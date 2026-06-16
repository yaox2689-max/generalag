from fastapi import FastAPI

from config import settings

app = FastAPI(title="General Agent", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.llm_model}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
