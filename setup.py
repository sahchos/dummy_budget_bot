import os

from mongoengine import connect

from models.Category import Category


def _create_categories():
    categories = [
        Category(id="coffee",
                 name="Кофе",
                 is_base_expenses=False,
                 aliases=['coffee', 'кофе', 'tea', 'чай']),
        Category(id="cafe",
                 name="Кафе и рестораны",
                 is_base_expenses=False,
                 aliases=['cafe', 'кафе', 'ресторан', 'рестик', 'мак']),
        Category(id="base",
                 name="Базовые расходы",
                 is_base_expenses=True,
                 aliases=['food', 'еда', 'продукты', 'быт', 'base']),
        Category(id="subs",
                 name="Подписки, телеком",
                 is_base_expenses=True,
                 aliases=[
                     'subs', 'phone', 'телефон', 'комуналка', 'инет'
                 ]),
        Category(id="house",
                 name="Дом, покупки",
                 is_base_expenses=True,
                 aliases=[
                     'house', 'ремонт', 'дом', 'покупки'
                 ]),
        Category(id="other",
                 name="Прочее",
                 is_base_expenses=False,
                 aliases=['other', 'прочее']),
    ]
    Category.drop_collection()
    Category.objects.insert(categories)


if __name__ == '__main__':
    print("Setup started.")
    DB_NAME = os.environ.get('DB_NAME', 'budget_bot')
    DB_HOST = os.environ.get('MONGODB_URI', 'mongodb')
    connect(DB_NAME, host=DB_HOST)
    _create_categories()
    print("Setup finished.")
