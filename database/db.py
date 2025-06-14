from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# from ..config import INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_URL, SQLITE_FILENAME
from typing import Optional

# if SQLITE_FILENAME is None:
#     print("No sqlite filename detected. Please check environment variables.")

SQLITE_FILENAME = "database.db"

sqlite_url = f"sqlite+aiosqlite:///{SQLITE_FILENAME}"

engine = create_async_engine(sqlite_url, echo=False)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
