import asyncio
import contextlib
from datetime import datetime
import functools
import inspect
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

    def schedule(self, task_id: t.Hashable, coroutine: t.Coroutine) -> None:
        """
        Schedule the execution of a coroutine.

        If a task with `task_id` already exists, the coroutine will be closed
        instead of scheduling it. This prevents unawaited coroutine warnings.
        """
        self.log.trace(f'Scheduling task #{task_id}.')

        msg = f'Cannot schedule an already started coroutine for #{task_id}'
        assert inspect.getcoroutinestate(coroutine) == 'CORO_CREATED', msg

        if task_id in self:
            self.log.debug(f'Task #{task_id} was not scheduled; already scheduled.')
            coroutine.close()
            return

        task = asyncio.create_task(coroutine, name=f'{self.name}_{task_id}')
        task.add_done_callback(
            functools.partial(self._task_done_callback, task_id)
        )

        self[task_id] = task
        self.log.debug(f'Scheduled task #{task_id}.')

    def schedule_at(self, datetime_: datetime, task_id: t.Hashable, coroutine: t.Coroutine) -> None:
        """
        Schedule a coroutine to be awaited at `datetime`.

        If a task with `task_id` already exists, the coroutine will be closed
        instead of scheduling it. This prevents unawaited coroutine warnings.
        """
        seconds = (datetime_ - datetime.now()).total_seconds()

        if seconds > 0:
            coroutine = self._future_await(seconds, task_id, coroutine)

        self.schedule(task_id, coroutine)

    def schedule_in(self, seconds: t.Union[int, float], task_id: t.Hashable, coroutine: t.Coroutine) -> None:
        """
        Schedule a coroutine to be awaited for `seconds` seconds.

        If a task with `task_id` already exists, the coroutine will be closed
        instead of scheduling it. This prevents unawaited coroutine warnings.
        """
        self.schedule(task_id, self._future_await(seconds, task_id, coroutine))

    def cancel(self, task_id: t.Hashable) -> None:
        """Unschedule the task mapped to `task_id`."""
        self.log.trace(f'Cancelling task #{task_id}')

        try:
            task = self.tasks.pop(task_id)

        except KeyError:
            self.log.warning(f'Failed to unschedule task #{task_id}; task was not found.')

        else:
            task.cancel()
            self.log.debug(f'Task #{task_id} successfully unscheduled.')

    def cancel_all(self) -> None:
        """Unschedule all tasks."""
        self.log.debug('Unscheduling all tasks..')

        for task_id in self.tasks.copy():
            self.cancel(task_id)

    async def _future_await(self, delay: t.Union[int, float], task_id: t.Hashable, coroutine: t.Coroutine) -> None:
        try:
            self.log.trace(f'Waiting {delay} seconds before awaiting task #{task_id}.')
            await asyncio.sleep(delay)

            # Shield to prevent coroutine from cancelling itself
            self.log.trace(f'Finished waiting for #{task_id}; awaiting coroutine now.')
            await asyncio.shield(coroutine)

        finally:
            # Close to prevent unawaited coroutine warnings
            # Happens if task was cancelled while sleeping
            state = inspect.getcoroutinestate(coroutine)

            if state == 'CORO_CREATED':
                self.log.debug(f'Explicitly closing task #{task_id}.')
                coroutine.close()

            else:
                self.log.debug(f'Finally block reached for #{task_id}; {state=}')

    def _task_done_callback(self, task_id: t.Hashable, done_task: asyncio.Task) -> None:
        """
        Deletes the task and raises its exception if one exists.

        If `done_task` and the task mapped to `task_id` are not the same,
        then the latter will not be deleted. In this case, a new task was
        most likely scheduled with the same ID.
        """
        self.log.trace(f'Performing done callback for #{task_id}.')

        scheduled_task = self.get(task_id)

        if scheduled_task is not None and done_task is scheduled_task:
            # A task for this ID exists and is the same as `done_task`
            self.log.trace(f'Deleting task #{task_id}.')
            del self[task_id]

        elif scheduled_task is not None:
            # A new task was most likely scheduled with the same ID
            self.log.debug(
                f'Task #{task_id} has changed; another task was likely scheduled with the same ID.'
            )

        elif not done_task.cancelled():
            self.log.warning(
                f'Task #{task_id} not found while handling task {id(done_task)}! '
                f'A task was somehow unscheduled improperly.'
            )

        with contextlib.suppress(asyncio.CancelledError):
            exception = done_task.exception()

            if exception is not None:
                self.log.error(f'Error in task #{task_id}!', exc_info=exception)
