import asyncio
import logging
import os
import typing as t
from urllib.parse import quote

import aiohttp

log = logging.getLogger(__name__)


class ResponseCodeError(ValueError):
    """Raised when a non-ok HTTP status code is received."""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        response_json: t.Optional[t.Dict] = None,
        response_text: str = ''
    ):
        self.response = response
        self.status = response.status

        self.response_json = response_json or dict()
        self.response_text = response_text

    def __str__(self) -> str:
        return f'Status: {self.status} Response: {self.response_json or self.response_text}'


class APIClient:
    """Snek Site API Wrapper."""

    def __init__(self, loop: asyncio.AbstractEventLoop, **kwargs) -> None:
        if token := os.environ.get('SNEK_API_TOKEN'):
            headers = {
                'Authorization': f'Token {token}'
            }

            if 'headers' in kwargs:
                kwargs['headers'].update(headers)
            else:
                kwargs['headers'] = headers

        else:
            log.critical(
                'Could not find "SNEK_API_TOKEN" environment variable '
                '- WILL NOT BE ABLE TO COMMUNICATE WITH THE SNEK API!!'
            )

        self.loop = loop
        self.session = None

        self.ready = asyncio.Event(loop=loop)
        self._creation_task = None
        self._default_session_kwargs = kwargs

        self.recreate()

    async def _create_session(self, **session_kwargs) -> None:
        """Create the aiohttp session with `session_kwargs` and set the ready event."""
        await self.close()
        self.session = aiohttp.ClientSession(**{**self._default_session_kwargs, **session_kwargs})
        self.ready.set()

    async def close(self) -> None:
        """Close the aiohttp session and clear the ready event."""
        if self.session:
            await self.session.close()

        self.ready.clear()

    def recreate(self, force: bool = False, **session_kwargs) -> None:
        """
        Schedules the aiohttp session to be created with `session_kwargs` if it is closed.

        If `force` is True, the session will be recreated even if one is open. If a task
        to create the session is pending, it will be cancelled.
        """
        if force or self.session is None or self.session.closed:
            # Cancel creation task if one exists
            if force and self._creation_task:
                self._creation_task.cancel()

            # Don't schedule a task if one is already in progress
            if force or self._creation_task is None or self._creation_task.done():
                self._creation_task = self.loop.create_task(self._create_session(**session_kwargs))

    async def maybe_raise_for_status(self, response: aiohttp.ClientResponse, should_raise: bool) -> None:
        """Raise ResponseCodeError for non-OK response if an exception should be raised."""
        if should_raise and response.status >= 400:
            try:
                response_json = await response.json()
                raise ResponseCodeError(response=response, response_json=response_json)

            except aiohttp.ContentTypeError:
                response_text = await response.text()
                raise ResponseCodeError(response=response, response_text=response_text)

    @staticmethod
    def endpoint_url(endpoint: str) -> str:
        return f'{os.environ.get("SNEK_SITE_URL", "https://sneknetwork.com")}/api/{quote(endpoint)}'

    async def request(self, method: str, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Dict:
        """Send an HTTP request to the Snek API and return the JSON response."""
        await self.ready.wait()

        async with self.session.request(method.upper(), self.endpoint_url(endpoint), **kwargs) as resp:
            await self.maybe_raise_for_status(resp, raise_for_status)
            return await resp.json()

    async def get(self, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Dict:
        """Snek API GET request."""
        return await self.request("GET", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def post(self, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Dict:
        """Snek API POST request."""
        return await self.request("POST", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def put(self, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Dict:
        """Snek API PUT request."""
        return await self.request("PUT", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def patch(self, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Dict:
        """Snek API PATCH request."""
        return await self.request("PATCH", endpoint, raise_for_status=raise_for_status, **kwargs)

    async def delete(self, endpoint: str, raise_for_status: bool = True, **kwargs) -> t.Optional[t.Dict]:
        """Snek API DELETE request."""
        await self.ready.wait()

        async with self.session.delete(self.endpoint_url(endpoint), **kwargs) as resp:
            if resp.status == 204:
                return

            await self.maybe_raise_for_status(resp, raise_for_status)
            return await resp.json()
