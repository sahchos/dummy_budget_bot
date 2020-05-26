import logging
import uuid
from datetime import datetime

import mongoengine
from mongoengine import *

import exceptions


class Expense(Document):
    id = StringField(primary_key=True)
    date = DateTimeField(default=datetime.utcnow)
    category = ReferenceField('Category')
    raw_text = StringField()
    amount = IntField()

    def get_id_str(self):
        return self.id.replace('-', '_')

    @classmethod
    def create(cls, **kwargs):
        try:
            expense = cls.objects.create(
                id=str(uuid.uuid4()),
                **kwargs
            )
        except mongoengine.errors.ValidationError:
            logging.error('Invalid data for expense', **kwargs)
            raise exceptions.InvalidMessage("Не удалось сохранить расход")

        return expense
