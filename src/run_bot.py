from vkbottle import Bot, load_blueprints_from_package
from config import bot_token1
import asyncio
from utils.middleware import MessageContextMiddleware, RowEventMiddleware
from monitor_timetable import monitoring_timetable


bot = Bot(token=bot_token1)


for bp in load_blueprints_from_package("handlers"):
    bp.load(bot)


async def run():
    bot.labeler.message_view.register_middleware(MessageContextMiddleware)
    bot.labeler.raw_event_view.register_middleware(RowEventMiddleware)
    print("Запустила")
    await asyncio.gather(bot.run_polling(), monitoring_timetable(bot))

if __name__ == "__main__":
    asyncio.run(run())
