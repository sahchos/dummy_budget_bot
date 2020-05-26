import calendar
import io
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict

import matplotlib.pyplot as plt

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
    def today_by_categories(self) -> str:
        expenses = self._get_today_expenses(total=True)

        return '\n'.join([
            f'{category}: {expenses[category]}' for category in expenses
        ])

    def month_by_categories(self) -> str:
        expenses = self._get_month_expenses(total=True)

        return '\n'.join([
            f'{category}: {expenses[category]}' for category in expenses
        ])

    def today_by_categories_pie(self) -> io.BytesIO:
        return self._get_pie(self._get_today_expenses())

    def month_by_categories_pie(self) -> io.BytesIO:
        return self._get_pie(self._get_month_expenses())

    @staticmethod
    def _get_expenses_by_categories(date_from: datetime.date,
                                    date_to: datetime.date,
                                    total: bool = False) -> Dict[str, int]:
        """
        For specified range get expenses grouped by category.
        :param datetime.date date_from: range start inclusive
        :param datetime.date date_to: range end exclusive
        :param bool total: flag to indicate if Total should be included
        :return dict: {<category_name>: <total>} sorted by total
        """
        qs = Expense.objects.filter(
            date__gte=date_from,
            date__lt=date_to
        )
        result = {
            category['_id']: category['total']
            for category in qs.aggregate([{
                '$group': {
                    '_id': '$category',
                    'total': {'$sum': '$amount'}
                }
            }])
        }
        categories_by_id = Category.objects.in_bulk(list(result.keys()))

        expenses = {}
        if total:
            expenses['Всего'] = qs.sum('amount')

        expenses.update({
            categories_by_id[category].name: result[category]
            for category in sorted(result, key=result.get, reverse=True)
        })

        return expenses

    def _get_today_expenses(self, total: bool = False) -> Dict[str, int]:
        now = datetime.utcnow().date()
        return self._get_expenses_by_categories(
            date_from=now,
            date_to=now + timedelta(days=1),
            total=total
        )

    def _get_month_expenses(self, total: bool = False) -> Dict[str, int]:
        now = datetime.utcnow().date()
        return self._get_expenses_by_categories(
            date_from=now.replace(day=1),
            date_to=now.replace(
                day=calendar.monthrange(now.year, now.month)[1]
            ) + timedelta(days=1),
            total=total
        )

    def _get_pie(self, expenses: Dict[str, int]) -> io.BytesIO:
        figure, ax = plt.subplots()
        ax.pie(list(expenses.values()),
               labels=list(expenses.keys()),
               autopct='%1.1f%%',
               shadow=True,
               startangle=90)
        ax.axis('equal')
        img = io.BytesIO()
        figure.savefig(img, format='png')
        img.seek(0)

        return img


expense_service = ExpenseService()
expense_stats = ExpenseStats()
