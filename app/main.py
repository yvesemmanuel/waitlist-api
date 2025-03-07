from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from app.endpoints import users, appointments
from app.config import settings
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing barbershop waitlist",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(appointments.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Barbershop Waitlist API!"}


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
