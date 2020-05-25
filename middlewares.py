from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_ids: str):
        self.access_ids = [
            int(access_id) for access_id in access_ids.split(',')
        ]
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) not in self.access_ids:
            await message.answer("Access Denied")
            raise CancelHandler()
