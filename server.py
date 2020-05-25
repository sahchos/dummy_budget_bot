import os
import logging

from aiogram import Bot, Dispatcher, executor, types

from middlewares import AccessMiddleware

API_TOKEN = os.environ.get('API_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(os.environ.get('ACCESS_IDS', '')))


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
