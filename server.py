import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from mongoengine import connect

from models.Category import Category
from middlewares import AccessMiddleware

DB_NAME = os.environ.get('DB_NAME', 'budget_bot')
DB_HOST = os.environ.get('MONGODB_URI', 'mongodb')
API_TOKEN = os.environ.get('API_TOKEN')
ACCESS_IDS = os.environ.get('ACCESS_IDS', '')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_IDS))


@dp.message_handler(commands=['start', 'help'])
async def echo(message: types.Message):
    await message.answer('\n'.join([
        'Комманды:',
        '/categories - список доступных категорий'
    ]))


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Returns a list of categories"""
    categories = Category.objects.all()
    answer_message = '\n'.join([
        'Категории: ',
        '\n\n'.join([
            f"Код: {category.id}\n"
            f"Имя: {category.name}\n"
            f"Базовые траты: {'+' if category.is_base_expenses else '-'}\n"
            f"Алиасы: {','.join(category.aliases)}" for category in categories
        ])
    ])
    await message.answer(answer_message)


if __name__ == '__main__':
    db = connect(DB_NAME, host=DB_HOST)
    executor.start_polling(dp, skip_updates=True)
