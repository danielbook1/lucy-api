from fastapi import FastAPI
from .api import api_router
from .database import *
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Initialize app.
app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Lucy API!",
        "endpoints": {
            "api": "/api/",
        },
    }
