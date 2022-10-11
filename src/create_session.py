from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base

# docker run --name pg -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres -d postgres
sync_engine = create_engine(f"postgresql://postgres:postgres@localhost:5432/postgres", echo=True)
Base.metadata.create_all(sync_engine) # todo make with async_engine
sync_engine.dispose()
async_engine = create_async_engine(f"postgresql+asyncpg://postgres:postgres@localhost:5432/postgres", echo=True)
async_session = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
