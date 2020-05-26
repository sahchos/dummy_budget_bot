import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from mongoengine import QuerySet

import exceptions
from models.Category import Category
from models.Expense import Expense


__all__ = ['expense_stats', 'expense_service']


class ExpenseService:
    @dataclass
    class ParsedMessage:
        amount: int
        category_text: str

    def _parse_expense_msg(self, msg: str) -> ParsedMessage:
        regexp_result = re.match(r"([\d ]+) (.*)", msg)
        if (not regexp_result or not regexp_result.group(0)
                or not regexp_result.group(1) or not regexp_result.group(2)):
            raise exceptions.InvalidMessage(
                "Не могу понять сообщение. Пример:\n1500 дом"
            )

        amount = int(regexp_result.group(1).replace(" ", ""))
        category_text = regexp_result.group(2).strip().lower()

        return self.ParsedMessage(amount=amount, category_text=category_text)

    def add(self, msg: str) -> Expense:
        parsed_expense = self._parse_expense_msg(msg)
        category = Category.get_category_by_text(parsed_expense.category_text)
        return Expense.create(
            amount=parsed_expense.amount,
            category=category
        )

    def delete(self, expense_id: str):
        Expense.objects.filter(id=expense_id).delete()


class ExpenseStats:
    def _get_today_expenses(self) -> QuerySet:
        return Expense.objects.filter(
            date__gt=datetime.utcnow().date(),
            date__lt=datetime.utcnow().date() + timedelta(days=1)
        )

    def today_by_categories(self) -> str:
        today_qs = self._get_today_expenses()
        result = {
            category['_id']: category['total']
            for category in today_qs.aggregate([{
                '$group': {
                    '_id': '$category',
                    'total': {'$sum': '$amount'}
                }
            }])
        }
        categories_by_id = Category.objects.in_bulk(list(result.keys()))

        return '\n'.join([
            f'Total: {today_qs.sum("amount")}',
            *[f'{categories_by_id[category].name}: {result[category]}'
              for category in sorted(result, key=result.get, reverse=True)]
        ])


expense_service = ExpenseService()
expense_stats = ExpenseStats()
