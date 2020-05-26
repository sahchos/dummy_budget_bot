import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
from mongoengine import connect

import exceptions
from models.Category import Category
from middlewares import AccessMiddleware
from expenses import expense_service, expense_stats


DB_NAME = os.environ.get('DB_NAME', 'budget_bot')
DB_HOST = os.environ.get('MONGODB_URI', 'mongodb')
API_TOKEN = os.environ.get('API_TOKEN')
ACCESS_IDS = os.environ.get('ACCESS_IDS', '')
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', 'dummybudgetbot')
WEB_HOOK_URL = f'https://{HEROKU_APP_NAME}.herokuapp.com'

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
        'Добавить расход: 1500 дом',
        '/categories - список доступных категорий',
        '/today - статистика расходов за сегодня',
        '/today_pie - график расходов за сегодня (пирог)',
        '/prev_month - статистика расходов за прошлый месяц',
        '/prev_month_pie - график расходов за прошлый месяц (пирог)',
        '/month - статистика расходов за текущий месяц',
        '/month_pie - график расходов за текущий месяц (пирог)',
        '/prev - график планируемого и фактического расхода, прошлый месяц',
        '/current - график планируемого и фактического расхода, текущий месяц',
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


@dp.message_handler(commands=['today'])
async def get_today_stats(message: types.Message):
    await message.answer(expense_stats.today_by_categories())


@dp.message_handler(commands=['today_pie'])
async def get_today_stats_pie(message: types.Message):
    img = expense_stats.today_by_categories_pie()
    await message.reply_photo(img, caption='Статистика за сегодня')


@dp.message_handler(commands=['month'])
async def get_month_stats(message: types.Message):
    await message.answer(expense_stats.month_by_categories())


@dp.message_handler(commands=['month_pie'])
async def get_month_stats_pie(message: types.Message):
    img = expense_stats.month_by_categories_pie()
    await message.reply_photo(img, caption='Статистика за месяц')


@dp.message_handler(commands=['prev_month'])
async def get_prev_month_stats(message: types.Message):
    await message.answer(expense_stats.month_by_categories(prev=True))


@dp.message_handler(commands=['prev_month_pie'])
async def get_prev_month_stats_pie(message: types.Message):
    img = expense_stats.month_by_categories_pie(prev=True)
    await message.reply_photo(img, caption='Статистика за прошлый месяц')


@dp.message_handler(commands=['current'])
async def get_current_status_chart(message: types.Message):
    img = expense_stats.month_status()
    await message.reply_photo(img, caption='Планируемый и фактический расход')


@dp.message_handler(commands=['prev'])
async def get_prev_status_chart(message: types.Message):
    img = expense_stats.month_status(prev=True)
    await message.reply_photo(
        img, caption='Планируемый и фактический расход за прошый месяц'
    )


@dp.message_handler()
async def add_expense(message: types.Message):
    """Parse message and add expense"""
    # TODO: test app wake up with webhook
    await message.answer(message.text)
    return

    try:
        expense = expense_service.add(message.text)
    except (exceptions.InvalidMessage, exceptions.InvalidCategory) as e:
        await message.answer(str(e))
        return

    await message.answer(f'Добавлено: {expense.amount}\n'
                         f'Категория: {expense.category.name}\n'
                         f'Удалить: /del{expense.get_id_str()}')


async def on_startup(dp):
    logging.info('Starting...')
    await bot.set_webhook(WEB_HOOK_URL, max_connections=1)


async def on_shutdown(dp):
    logging.warning('Shutting down...')
    # Remove web hook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    # db = connect(DB_NAME, host=DB_HOST)
    start_webhook(
        dispatcher=dp,
        webhook_path='',
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
