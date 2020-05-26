import re
from dataclasses import dataclass

import exceptions
from models.Category import Category
from models.Expense import Expense


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


expense_service = ExpenseService()
