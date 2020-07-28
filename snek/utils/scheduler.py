import asyncio
import logging
import typing as t


class Scheduler:
    """
    Schedules and tracks the execution of coroutines.

    The give name is for logging purposes. Using the name of the class
    or module is strongly suggested.

    Each coroutine needs a unique ID in ordre to keep track of them.

    Any exception raised in a scheduled task is logged when the task is done.
    """

    def __init__(self, name: str) -> None:
        self.name = name

        self.log = logging.getLogger(f'{name} {type(self).__name__}')
        self.tasks: t.Dict[t.Hashable, asyncio.Task] = dict()
