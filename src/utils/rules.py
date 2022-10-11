import json
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle_types.events import Event


class CustomRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        if event.payload and json.loads(event.payload)["command"] == self.command_name:
            return True
        return False

    def __init__(self, command_name):
        super().__init__()
        self.command_name = command_name

