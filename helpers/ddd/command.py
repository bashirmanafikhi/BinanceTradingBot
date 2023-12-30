from abc import ABC
import logging
from typing import Callable, Tuple

from helpers.settings.constants import ACTION_BUY, ACTION_SELL

class Command(ABC):
    def __init__(self):
        self.handler = None

    def __call__(self, *args, **kwargs):
        if self.handler:
            return self.handler(*args, **kwargs)
        else:
            logging.warning("No handler registered.")

    def set_handler(self, handler: Callable):
        self.handler = handler
