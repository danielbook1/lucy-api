from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
