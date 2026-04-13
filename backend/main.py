from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router

app = FastAPI(
    title="LiteLLM UI Backend",
    description="Backend API for the LiteLLM multi-provider chat UI.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "LiteLLM UI Backend",
        "status": "ok",
        "docs": "/docs",
    }
