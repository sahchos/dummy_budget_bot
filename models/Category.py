from mongoengine import Document, StringField, BooleanField, ListField


class Category(Document):
    id = StringField(primary_key=True)
    name = StringField()
    is_base_expenses = BooleanField(default=False)
    aliases = ListField(StringField())
