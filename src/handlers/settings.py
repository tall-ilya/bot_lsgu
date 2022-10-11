import json
from sqlalchemy import select
from vkbottle import ABCRule
from vkbottle.bot import Blueprint, Message
from utils.middleware import Context
from models import User, ScheduleDay, ReplacementLesson, Lesson, Timetable
import datetime
from utils.rules import CustomRule
from views import settings_view, favourite_timetable_view, set_group_number_view
from utils.iterator import AsyncIterator
from typing import List


bp = Blueprint("settings")


@bp.on.message(CustomRule("settings"))
async def settings_handler(message: Message, context: Context):
    is_subscribed = json.loads(message.payload).get('set_is_subscribed', None)
    user = context.user
    if is_subscribed is not None:
        await user.update(context.session, is_subscribed=is_subscribed)
    await settings_view(message, bp, user, is_subscribed)


@bp.on.message(CustomRule("favourite_timetable"))
async def favourite_timetable_handler(message: Message, context: Context):
    page: int = json.loads(message.payload).get('page', 1)
    await favourite_timetable_view(message, bp, page, context.user)


@bp.on.message(CustomRule("set_group_number"))
async def set_group_number_handler(message: Message, context: Context):
    group_number = json.loads(message.payload).get('group_number')
    await context.user.update(context.session, group_number=group_number)
    await set_group_number_view(message, bp, group_number)
