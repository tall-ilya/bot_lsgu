import logging
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from create_session import async_session
from models import User
from typing import Optional


@dataclass
class Context:
    user: Optional[User]
    session: AsyncSession


class MessageContextMiddleware(BaseMiddleware):

    async def pre(self):
        session = async_session()
        user = await User.get_or_create(session, vk_id=self.event.from_id)
        context = Context(user=user, session=session)
        self.send({"context": context})

    async def post(self):
        session: AsyncSession = self.context_update['context'].session
        await session.close()
        del self.context_update['context']


class RowEventMiddleware(BaseMiddleware):

    async def pre(self):
        session = async_session()
        context = Context(user=None, session=session)
        self.send({"context": context})

    async def post(self):
        session: AsyncSession = self.context_update['context'].session
        await session.close()
        del self.context_update['context']
