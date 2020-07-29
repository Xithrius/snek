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

    def __contains__(self, task_id: t.Hashable) -> bool:
        """Checks whether or not `task_id` is currently scheduled."""
        return task_id in self.tasks

    def __getitem__(self, task_id: t.Hashable) -> asyncio.Task:
        """Returns the coroutine mapped to `task_id`; Raises a `KeyError` if not found."""
        return self.tasks[task_id]

    def __setitem__(self, task_id: t.Hashable, task: asyncio.Task) -> None:
        """Sets the coroutine to the `task_id`."""
        self.tasks[task_id] = task

    def get(self, task_id: t.Hashable) -> t.Optional[asyncio.Task]:
        """Returns the coroutine mapped to `task_id`; Returns `None` if not found."""
        return self.tasks.get(task_id)
