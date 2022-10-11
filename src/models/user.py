from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, BigInteger, TIMESTAMP, BOOLEAN, DECIMAL, Table, \
    select, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from sqlalchemy.orm import relationship
from .base import BaseModel, Base


class User(BaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vk_id = Column(BigInteger, nullable=False, unique=True)
    date_of_creation = Column(DateTime, nullable=False)
    last_joining = Column(DateTime, nullable=False)
    is_active = Column(BOOLEAN, default=True)
    teacher_lessons = relationship("Lesson", back_populates="teacher")
    group_number = Column(Integer, nullable=True)
    is_subscribed = Column(BOOLEAN, default=False)

    @classmethod
    async def get_object(cls, session: AsyncSession, **kwargs):
        if user := await super().get_object(session, **kwargs):
            await user.update(session, last_joining=datetime.datetime.now())
            return user

    @classmethod
    async def create(cls, session: AsyncSession, user: 'User'):
        user.date_of_creation = datetime.datetime.now()
        user.last_joining = datetime.datetime.now()
        return await super().create(session, user)

