from typing import Callable

# Event class to manage handlers
class Event:
    def __init__(self):
        self.handlers = []

    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)