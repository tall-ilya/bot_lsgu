from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from utils.iterator import AsyncIterator


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    async def create(cls, session: AsyncSession, class_obj):
        session.add(class_obj)
        await session.commit()
        return class_obj

    @classmethod
    async def get_all(cls, session: AsyncSession, **kwargs):
        result = await session.execute(select(cls).distinct(cls.id))
        return result.scalars().all()

    @classmethod
    async def get_object(cls, session: AsyncSession, **kwargs):
        parameters = [getattr(cls, parameter) == value async for parameter, value in AsyncIterator(kwargs.items())]
        result = await session.execute(select(cls).distinct(cls.id).where(*parameters))
        return result.scalars().first()

    @classmethod
    async def get_or_create(cls, session: AsyncSession, **kwargs):
        if _object := await cls.get_object(session, **kwargs):
            return _object
        class_obj = cls(**kwargs)
        return await cls.create(session, class_obj)

    async def update(self, session: AsyncSession, **kwargs):
        async for parameter, value in AsyncIterator(kwargs.items()):
            setattr(self, parameter, value)
        await session.commit()
        return self

