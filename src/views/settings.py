import math
from vkbottle.bot import Message, Bot, BotBlueprint
from vkbottle import Keyboard, KeyboardButtonColor, Text
from models import Lesson, ReplacementLesson, Timetable, User
from models.enums import GroupNumbers
from utils.iterator import AsyncIterator

BUTTONS_COUNT = 6
WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


async def settings_view(message: Message, bot: BotBlueprint, user: User, is_subscribed):
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("Поставить избранное расписание ⭐️", payload={"command": "favourite_timetable"}),
                 color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    if not user.is_subscribed:
        keyboard.add(Text("Подписаться на расписание 📅", payload={"command": "settings", "set_is_subscribed": True}),
                     color=KeyboardButtonColor.POSITIVE)
    else:
        keyboard.add(Text("Отписаться от расписания 📅", payload={"command": "settings", "set_is_subscribed": False}),
                     color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Text("Назад", payload={"command": "start"}), color=KeyboardButtonColor.SECONDARY)

    text = "Настройки"
    if is_subscribed is True:
        text = "Вы подписались на расписание 📅"
    elif is_subscribed is False:
        text = "Вы отписаны от расписания 📅"
    await message.answer(message=text, keyboard=keyboard.get_json())


async def favourite_timetable_view(message: Message, bot: BotBlueprint, page: int, user: User):
    keyboard = Keyboard(one_time=False, inline=False)

    group_numbers = [group_number.value async for group_number in AsyncIterator(list(GroupNumbers))]
    group_numbers = group_numbers[BUTTONS_COUNT * (page - 1): BUTTONS_COUNT * page]
    async for counter, group_number in AsyncIterator(enumerate(group_numbers)):
        if counter == 3:
            keyboard.row()
        keyboard.add(Text(group_number, payload={"command": "set_group_number", "group_number": group_number}),
                     color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    use_row = False
    if page != 1:
        use_row = True
        keyboard.add(Text(" <- ", payload={"command": "favourite_timetable", "page": page - 1}),
                     color=KeyboardButtonColor.SECONDARY)

    if page < math.ceil(len(list(GroupNumbers)) / BUTTONS_COUNT):
        use_row = True
        keyboard.add(Text(" -> ", payload={"command": "favourite_timetable", "page": page + 1}),
                     color=KeyboardButtonColor.SECONDARY)
    if use_row:
        keyboard.row()
    keyboard.add(Text("Назад", payload={"command": "settings"}), color=KeyboardButtonColor.NEGATIVE)
    text = "Какую группу вы хотите?"
    if user.group_number:
        text += f" (Сейчас {user.group_number})"
    await message.answer(message=text, keyboard=keyboard.get_json())


async def set_group_number_view(message: Message, bot: BotBlueprint, group_number: int):
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("В настройки ⚙️", payload={"command": "settings"}), color=KeyboardButtonColor.PRIMARY)
    await message.answer(message=f"Теперь ваша группа {group_number}", keyboard=keyboard.get_json())
