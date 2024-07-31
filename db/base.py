from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import get_settings


settings = get_settings()
SQLALCHEMY_DATABASE_URL_SYNC = f"mysql://{settings.db_user}:{settings.db_passwd}@{settings.db_host}/{settings.db_name}"
SQLALCHEMY_DATABASE_URL_ASYNC = f"mysql+aiomysql://{settings.db_user}:{settings.db_passwd}@{settings.db_host}/{settings.db_name}"

sync_engine = create_engine(
    SQLALCHEMY_DATABASE_URL_SYNC,
    max_overflow=5,
)

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL_ASYNC,
    max_overflow=5,
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine
)

Base = declarative_base()


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
