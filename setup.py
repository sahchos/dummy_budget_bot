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
                     'subs', 'phone', 'телефон', 'инет'
                 ]),
        Category(id="house",
                 name="Дом, покупки",
                 is_base_expenses=True,
                 aliases=[
                     'house', 'ремонт', 'дом', 'покупки', 'комуналка'
                 ]),
        Category(id="transport",
                 name="Машина, транспорт",
                 is_base_expenses=True,
                 aliases=[
                     'car', 'машина', 'сто', 'то', 'такси', 'проезд'
                 ]),
        Category(id="rest",
                 name="Отдых, поездки, путешествия",
                 is_base_expenses=True,
                 aliases=[
                     'отдых', 'поездки', 'путешествия', 'отпуск'
                 ]),
        Category(id="beauty",
                 name="Красота, уход, здоровье",
                 is_base_expenses=True,
                 aliases=[
                     'beauty', 'красота', 'маник', 'ногти', 'аптека'
                 ]),
        Category(id="self-improvement",
                 name="Саморазвитие",
                 is_base_expenses=True,
                 aliases=[
                     'англ', 'курсы', 'треша', 'треня',
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
    connect(DB_NAME, host=f'{DB_HOST}?retryWrites=false')
    _create_categories()
    print("Setup finished.")
