import math
from vkbottle.bot import Message, Bot, BotBlueprint
from vkbottle import Keyboard, KeyboardButtonColor, Text
from models.enums import GroupNumbers
import datetime
from utils.iterator import AsyncIterator
from typing import List
from models import Lesson, ReplacementLesson, Timetable, User

BUTTONS_COUNT = 6
WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


async def start_view(message: Message, bot: BotBlueprint, user: User):
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("Посмотреть расписание 📅", payload={"command": "timetable"}), color=KeyboardButtonColor.PRIMARY)
    if user.group_number:
        keyboard.row()
        keyboard.add(Text("Избранное расписание ⭐️",
                          payload={"command": "get_timetable", "group_number": user.group_number}),
                     color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("Настройки ⚙️", payload={"command": "settings"}), color=KeyboardButtonColor.SECONDARY)
    await message.answer(message="Привет, что вам нужно?", keyboard=keyboard.get_json())


async def timetable_view(message: Message, bot: BotBlueprint, page: int):
    keyboard = Keyboard(one_time=False, inline=False)

    group_numbers = [group_number.value async for group_number in AsyncIterator(list(GroupNumbers))]
    group_numbers = group_numbers[BUTTONS_COUNT * (page - 1): BUTTONS_COUNT * page]
    async for counter, group_number in AsyncIterator(enumerate(group_numbers)):
        if counter == 3:
            keyboard.row()
        keyboard.add(Text(group_number, payload={"command": "get_timetable", "group_number": group_number}),
                     color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    use_row = False
    if page != 1:
        use_row = True
        keyboard.add(Text(" <- ", payload={"command": "timetable", "page": page - 1}),
                     color=KeyboardButtonColor.SECONDARY)

    if page < math.ceil(len(list(GroupNumbers)) / BUTTONS_COUNT):
        use_row = True
        keyboard.add(Text(" -> ", payload={"command": "timetable", "page": page + 1}),
                     color=KeyboardButtonColor.SECONDARY)
    if use_row:
        keyboard.row()
    keyboard.add(Text("Назад", payload={"command": "start"}), color=KeyboardButtonColor.NEGATIVE)
    await message.answer(message="Выберете группу", keyboard=keyboard.get_json())


async def create_text_for_timetable(lesson: Lesson | ReplacementLesson) -> str:
    """ example return 'Физика - 336' """
    text = f"{lesson.title} {lesson.cabinet_number}"
    return text


async def delete_last_empty_lessons(lessons: List[str]) -> List[str]:
    """ example get ['1. Физика - 213', '2. ']
        return ['1. Физика - 213'] """
    count = 0
    while True:
        if lessons[-1 - count][-2:] == ". ":
            count += 1
            continue
        else:
            break
    if count != 0:
        return lessons[: -count]
    return lessons


async def get_timetable_view(message: Message, bot: BotBlueprint, lessons: List[Lesson],
                             replacement_lessons: List[ReplacementLesson], date: datetime.date, week_day: int,
                             group_number: int, timetable: Timetable):
    keyboard = Keyboard(one_time=False, inline=False)

    past_date = date - datetime.timedelta(days=1) if week_day != 1 else date - datetime.timedelta(days=2)

    keyboard.add(Text(" <- ", payload={"command": "get_timetable", "group_number": group_number,
                                       "date": past_date.isoformat()}),
                 color=KeyboardButtonColor.SECONDARY)

    next_date = date + datetime.timedelta(days=1) if week_day != 6 else date + datetime.timedelta(days=2)
    keyboard.add(Text(" -> ", payload={"command": "get_timetable", "group_number": group_number,
                                       "date": next_date.isoformat()}),
                 color=KeyboardButtonColor.SECONDARY)

    keyboard.row()
    keyboard.add(Text("Назад", payload={"command": "start"}),
                 color=KeyboardButtonColor.NEGATIVE)

    lessons = {lesson.lesson_number.value: await create_text_for_timetable(lesson)
               async for lesson in AsyncIterator(lessons)}

    async for replacement_lesson in AsyncIterator(replacement_lessons):
        lessons[replacement_lesson.lesson_number.value] =\
            f"({lessons[replacement_lesson.lesson_number.value]}) {await create_text_for_timetable(replacement_lesson)}"

    now = datetime.datetime.now().time()
    if datetime.datetime.now().date() == date:
        async for timetable_lesson in AsyncIterator(timetable.timetable_lessons):
            if lessons.get(timetable_lesson.lesson_number.value):
                if now < timetable_lesson.start_time:
                    lessons[timetable_lesson.lesson_number.value] += " ☑️"
                elif timetable_lesson.end_time > now > timetable_lesson.start_time:
                    lessons[timetable_lesson.lesson_number.value] += " ✍️"
                else:
                    lessons[timetable_lesson.lesson_number.value] += " ✅"

    lessons_list =\
        await delete_last_empty_lessons([f'{i}. {lessons.get(i, "")}' async for i in AsyncIterator(range(1, 10))])

    timetable_lessons = sorted(timetable.timetable_lessons, key=lambda x: x.lesson_number.value, reverse=False)
    async for counter, lesson in AsyncIterator(enumerate(lessons_list)):
        lessons_list[counter] = \
            f"{timetable_lessons[counter].start_time.strftime('%H:%M')} - " \
            f"{timetable_lessons[counter].end_time.strftime('%H:%M')}\n{lesson}\n"

    text = "\n".join(lessons_list)
    text = f"{date} {WEEK[week_day - 1]}\n" + text

    await message.answer(message=text, keyboard=keyboard.get_json())
