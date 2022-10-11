import json
from sqlalchemy import select
from vkbottle import ABCRule
from vkbottle.bot import Blueprint, Message
from utils.middleware import Context
from models import User, ScheduleDay, ReplacementLesson, Lesson, Timetable, Holiday
import datetime
from utils.rules import CustomRule
from views import start_view, timetable_view, get_timetable_view
from utils.iterator import AsyncIterator
from typing import List


bp = Blueprint("start")


@bp.on.message(CustomRule("start"))
async def start_handler(message: Message, context: Context):
    await start_view(message, bp, context.user)


@bp.on.message(CustomRule("timetable"))
async def timetable_handler(message: Message, context: Context):
    page: int = json.loads(message.payload).get('page', 1)
    await timetable_view(message, bp, page)


@bp.on.message(CustomRule("get_timetable"))
async def get_timetable_handler(message: Message, context: Context):
    group_number: int = json.loads(message.payload).get('group_number', 1)
    today = datetime.datetime.fromisoformat(
        json.loads(message.payload).get('date', datetime.datetime.today().isoformat())
    )
    date = today.date()
    week_day = today.isoweekday()
    schedule_day: ScheduleDay = \
        await ScheduleDay.get_object(context.session, day_of_the_week=week_day, group_number=group_number)
    replacement_lessons = await context.session.execute(select(ReplacementLesson).where(
        ReplacementLesson.schedule_day_id == schedule_day.id,
        ReplacementLesson.date == date
    ))
    holiday = await Holiday.get_object(context.session, date=date)
    if holiday:
        timetable = holiday.timetable
    else:
        timetable = await Timetable.get_object(context.session, title="Обычное")
    await get_timetable_view(message, bp, schedule_day.lessons, replacement_lessons.scalars().all(), date, week_day,
                             group_number, timetable)








