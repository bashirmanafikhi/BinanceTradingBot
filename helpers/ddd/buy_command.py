from helpers.ddd.command import Command


class BuyCommand(Command):
    def __call__(self, price, quantity, type):
        return super().__call__(price, quantity, type)