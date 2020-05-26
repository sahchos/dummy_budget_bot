import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from mongoengine import connect

import exceptions
from models.Category import Category
from middlewares import AccessMiddleware
from expenses import expense_service

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
async def welcome(message: types.Message):
    await message.answer('\n'.join([
        'Комманды:',
        '/categories - список доступных категорий'
    ]))


@dp.message_handler(commands=['categories'])
async def list_categories(message: types.Message):
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


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def delete_expense(message: types.Message):
    try:
        expense_id = message.text.split('/del')[1].replace('_', '-')
    except IndexError:
        await message.answer('ID расхода отсутствует')
        return

    expense_service.delete(expense_id)
    await message.answer('Удалено')


@dp.message_handler()
async def add_expense(message: types.Message):
    """Parse message and add expense"""
    try:
        expense = expense_service.add(message.text)
    except (exceptions.InvalidMessage, exceptions.InvalidCategory) as e:
        await message.answer(str(e))
        return

    await message.answer(f'Добавлено: {expense.amount}\n'
                         f'Категория: {expense.category.name}\n'
                         f'Удалить: /del{expense.get_id_str()}')


if __name__ == '__main__':
    db = connect(DB_NAME, host=DB_HOST)
    executor.start_polling(dp, skip_updates=True)
