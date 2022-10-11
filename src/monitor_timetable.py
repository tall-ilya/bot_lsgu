import datetime

from vkbottle import Bot

from create_session import async_session
import asyncio
from models import Timetable, Holiday, TimetableLesson
from typing import List
from utils.iterator import AsyncIterator
from make_mailing_list import make_mailing_list


BEFORE_THE_LESSON = 120 # in seconds


async def sleep_until_some_seconds(session: async_session, seconds: int, bot):
    await session.close()
    return asyncio.create_task(monitoring_timetable(bot, seconds))


async def sleep_until_next_day(session: async_session, now, bot):
    sleep = 86400 - (now.time().second + now.time().minute * 60 + now.time().hour * 3600) + 1
    return sleep_until_some_seconds(session, sleep, bot)


async def get_time_in_seconds(now):
    return now.time().second + now.time().minute * 60 + now.time().hour * 3600


async def get_lesson_time_in_second(lesson: TimetableLesson, is_start: bool = True):
    if is_start:
        return lesson.start_time.second + lesson.start_time.minute * 60 + lesson.start_time.hour * 3600
    return lesson.end_time.second + lesson.end_time.minute * 60 + lesson.end_time.hour * 3600


async def monitoring_timetable(bot: Bot, sleep: int = 0):
    print(f"Проверяю и ложусь спать на {sleep}| время {datetime.datetime.now().time()}")
    await asyncio.sleep(sleep)
    session = async_session()
    now = datetime.datetime.now()
    if now.isoweekday() == 7:
        task = await sleep_until_next_day(session, now, bot)
        await task
        return
    print("Не воскресенье")
    holiday = await Holiday.get_object(session, date=now.date())
    if holiday:
        timetable = holiday.timetable
    else:
        timetable = await Timetable.get_object(session, title="Обычное")
    print(f"расписание - {timetable.title}")
    timetable_lessons: List[TimetableLesson] =\
        sorted(timetable.timetable_lessons, key=lambda x: x.lesson_number.value, reverse=False)
    print(f"расписание получено - {timetable_lessons}")
    async for counter, lesson in AsyncIterator(enumerate(timetable_lessons)):
        time_in_seconds = await get_time_in_seconds(now)
        start_time_difference = await get_lesson_time_in_second(lesson) - time_in_seconds
        if start_time_difference < 0:
            end_time_difference = await get_lesson_time_in_second(lesson, is_start=False) - time_in_seconds
            if end_time_difference < 0:
                if counter + 1 == len(timetable_lessons):
                    task = await sleep_until_next_day(session, now, bot)
                    print("ложусь спать до следущего дня")
                    await task
                    return
                else:
                    print("конт")
                    continue
            else:
                difference = await get_lesson_time_in_second(lesson, is_start=False) -\
                             await get_time_in_seconds(datetime.datetime.now())
                if difference <= 0:
                    print(f"Урок закончен {datetime.datetime.now().time()}")
                    task = await sleep_until_some_seconds(session, 1, bot)
                    if counter != 8:
                        asyncio.create_task(make_mailing_list(session, lesson.end_time, bot, timetable_lessons[counter + 1].start_time))
                    else:
                        asyncio.create_task(make_mailing_list(session, lesson.end_time, bot))
                    await task
                    return
                else:
                    task = await sleep_until_some_seconds(session, difference, bot)
                    print("ложусь спать до того как урок не закончится")
                    await task
                    return
        else:
            if start_time_difference <= BEFORE_THE_LESSON:
                task = await sleep_until_some_seconds(session, 121, bot)
                asyncio.create_task(make_mailing_list(session, lesson.start_time, bot))
                print("рассылаю письма что урок начался")
                await task
                return
            else:
                task = await sleep_until_some_seconds(session, start_time_difference - BEFORE_THE_LESSON, bot)
                print("ложусь спать пока урок не начнется")
                await task
                return




