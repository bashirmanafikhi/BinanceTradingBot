from other_services.ddd.command import Command
from settings.constants import ORDER_TYPE_LIMIT


class SellCommand(Command):
    def __call__(self, price, quantity, type):
        return super().__call__(price, quantity, type)