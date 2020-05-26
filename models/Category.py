from mongoengine import Document, StringField, BooleanField, ListField, Q

import exceptions


class Category(Document):
    id = StringField(primary_key=True)
    name = StringField()
    is_base_expenses = BooleanField(default=False)
    aliases = ListField(StringField())

    @classmethod
    def get_category_by_text(cls, category_text: str) -> 'Category':
        try:
            category = cls.objects.get(
                Q(name=category_text) |
                Q(aliases=category_text.lower())
            )
        except Category.DoesNotExist:
            raise exceptions.InvalidCategory(
                'Нет такой категории по имени или алиасам'
            )

        return category
