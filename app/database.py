from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import SQLALCHEMY_DATABASE_URI
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

sqlite_url = f"sqlite+aiosqlite:///{SQLALCHEMY_DATABASE_URI}"

engine = create_async_engine(sqlite_url, echo=False)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
