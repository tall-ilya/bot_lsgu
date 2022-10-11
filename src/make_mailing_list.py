import datetime
import math
import random
from sqlalchemy import select, join, true
from create_session import async_session
import asyncio
from models import Timetable, Holiday, TimetableLesson, ScheduleDay, ReplacementLesson, User, Lesson
from typing import List
from utils.iterator import AsyncIterator
from vkbottle import Bot


async def make_mails_for_user(session: async_session, group_number: int, message: str, bot: Bot):
    print("вызываю рассылку писем")
    result = await session.execute(select(User).where(
        User.group_number == group_number,
        User.is_subscribed == true()
    ))

    user_ids = list(map(lambda user: user.vk_id, result.scalars().all()))

    print(f"рассылка vk_ids {user_ids}")
    async for i in AsyncIterator(range(math.ceil(len(user_ids) / 100))):
        await bot.api.messages.send(peer_ids=user_ids[i * 100:(i + 1) * 100], message=message,
                                    random_id=random.randint(0, 100), ignore_error=True)
    await session.close()


async def make_message_for_user(new_lesson: ReplacementLesson | Lesson = None, time: datetime.time = None,
                                old_lesson=None, is_end=False):
    if is_end:
        return f"Закончился последний урок)"
    if old_lesson is None:
        return f"У вас {new_lesson.title} в {new_lesson.cabinet_number} ({time.strftime('%H:%M')})"
    return f"Закончился урок {old_lesson.title}.\nСледущий урок {new_lesson.title} ({time.strftime('%H:%M')})"


async def make_mailing_list(session: async_session, time: datetime.time, bot: Bot, new_start_time: datetime.time = None):
    print(f"найти урок у которого {new_start_time} - {time}")
    if new_start_time is None:
        timetable_lesson: TimetableLesson = await TimetableLesson.get_object(session, start_time=time)
    else:
        timetable_lesson: TimetableLesson = await TimetableLesson.get_object(session, end_time=time)

    now = datetime.datetime.now()

    use_group_numbers = []

    result = await session.execute(select(ReplacementLesson).join(ReplacementLesson.schedule_day).where(
        ReplacementLesson.lesson_number == timetable_lesson.lesson_number,
        ReplacementLesson.date == now.date(),
        ScheduleDay.day_of_the_week == now.isoweekday(),
    ))

    result = result.scalars().all()

    async for replacement_lesson in AsyncIterator(result):
        use_group_numbers.append(replacement_lesson.schedule_day.group_number.value)
        if new_start_time is None:
            message = await make_message_for_user(replacement_lesson, time)
            await make_mails_for_user(session, replacement_lesson.schedule_day.group_number.value, message, bot)
        else:
            async for lesson_number in AsyncIterator(range(replacement_lesson.lesson_number.value + 1, 10)):
                if next_lesson := await ReplacementLesson.get_object(session, lesson_number=lesson_number):
                    message = await make_message_for_user(new_lesson=next_lesson, time=new_start_time,
                                                          old_lesson=replacement_lesson)
                    await make_mails_for_user(session, replacement_lesson.schedule_day.group_number.value, message, bot)
                    break
                if next_lesson := await Lesson.get_object(session, lesson_number=lesson_number):
                    message = await make_message_for_user(new_lesson=next_lesson, time=new_start_time,
                                                          old_lesson=replacement_lesson)
                    await make_mails_for_user(session, replacement_lesson.schedule_day.group_number.value, message,
                                              bot)
                    break
            else:
                message = await make_message_for_user(is_end=True)
                await make_mails_for_user(session, replacement_lesson.schedule_day.group_number.value, message, bot)

    result = await session.execute(select(Lesson).join(Lesson.schedule_day).where(
        Lesson.lesson_number == timetable_lesson.lesson_number,
        ScheduleDay.day_of_the_week == now.isoweekday(),
    ))

    result = result.scalars().all()

    async for lesson in AsyncIterator(result):
        if lesson.schedule_day.group_number.value not in use_group_numbers:
            if new_start_time is None:
                message = await make_message_for_user(new_lesson=lesson, time=time)
                await make_mails_for_user(session, lesson.schedule_day.group_number.value, message, bot)
            else:
                async for lesson_number in AsyncIterator(range(lesson.lesson_number.value + 1, 10)):
                    if next_lesson := await Lesson.get_object(session, lesson_number=lesson_number):
                        message = await make_message_for_user(new_lesson=next_lesson, time=new_start_time,
                                                              old_lesson=lesson)
                        await make_mails_for_user(session, lesson.schedule_day.group_number.value, message,
                                                  bot)
                        break
                    if next_lesson := await ReplacementLesson.get_object(session, lesson_number=lesson_number):
                        message = await make_message_for_user(new_lesson=next_lesson, time=new_start_time,
                                                              old_lesson=lesson)
                        await make_mails_for_user(session, lesson.schedule_day.group_number.value, message,
                                                  bot)
                        break
                else:
                    message = await make_message_for_user(is_end=True)
                    await make_mails_for_user(session, lesson.schedule_day.group_number.value, message, bot)


