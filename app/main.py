"""
Main file for the application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.session import engine

from app.routers.routers import router
from app.models.base import Base
from app.config import settings

import uvicorn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing appointment scheduling with service accounts",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.APP_NAME}!"}


if __name__ == "__main__":
    if settings.ENV == "dev":
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            workers=settings.WORKERS,
        )
    else:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            workers=settings.WORKERS,
            log_level="info",
        )
