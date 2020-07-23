import collections
from collections.abc import Sequence
import logging
import typing as t

log = logging.getLogger(__name__)


class EmptyPaginatorLines(Exception):
    """Exception for empty paginator lines."""


class LinePaginator(Sequence):

    def __init__(
        self,
        lines: t.Iterable[str],
        max_chars: t.Optional[int] = None,
        max_lines: t.Optional[int] = None,
        truncation_msg: str = '...',
        page_header: str = '',
        page_prefix: str = '',
        page_suffix: str = ''
    ) -> None:
        if not lines:
            raise EmptyPaginatorLines('Cannot paginator empty lines.')

        min_chars = len(truncation_msg) + len(page_header) + \
            len(page_header) + len(page_prefix) + len(page_suffix) + 100

        if max_chars < min_chars:
            raise ValueError(
                f'A minimum of {min_chars} characters is needed for pagination. '
                'Please raise the `max_chars` limit.'
            )

        self.lines = collections.deque(lines)
        self.max_chars = max_chars
        self.max_lines = max_lines
        self.truncation_msg = truncation_msg
        self.page_header = page_header
        self.page_prefix = page_prefix
        self.page_suffix = page_suffix

        if self.page_header:
            self.max_chars -= len(self.page_header) + 1

        if self.page_prefix:
            self.max_chars -= len(self.page_prefix) + 1

        if self.page_suffix:
            self.max_chars -= len(self.page_suffix) + 1

        self.pages = list()
        self.current_page = None

        self._remaining_chars = None
        self._index = 0

        # Create the first page
        self.start_page()
        self.create_pages()

    def __len__(self) -> int:
        """Returns the number of pages in the paginator."""
        return len(self.pages)

    def __getitem__(self, page_number: int) -> str:
        """Get a page by its page number."""
        return self.pages[page_number]

    def truncate_line(self, line: str) -> str:
        """
        Truncate a long line and add the remainder back on the line queue.

        If a suitable breakpoint cannot be found (a space), it will break
        on characters instead.
        """
        log.trace('Truncating a long line for the paginator.')

        # Determine a good lower bound to truncate within using a space
        lower_bound = self.max_chars // 8
        upper_bound = self._remaining_chars - len(self.truncation_msg) - 2

        # Find the space to break on
        breakpoint_ = line.rfind(' ', lower_bound, upper_bound)

        if breakpoint_ == -1:
            # Cannot find a space
            # Truncate on characters instead
            log.trace('Cannot find a space to break on; truncating on characters instead.')
            breakpoint_ = self.max_chars - len(self.truncation_msg)

        # Add the remainder to the next page
        line, next_line = line[:breakpoint_] + self.truncation_msg, line[breakpoint_:]
        self.lines.appendleft(next_line)

        return line

    def create_pages(self) -> None:
        """Create pages using the constraints given."""
        while self.lines:
            # Get a line from the beginning of the queue
            line = self.lines.popleft()

            # This line is longer than one page
            if len(line) > self.max_chars:
                # Check if current page has enough space to add
                # a piece of the long line.
                if self._remaining_chars <= self.max_chars // 4:
                    self.start_page()

                # Truncate line and add the remainder back on the line queue
                line = self.truncate_line(line)

            # Close the current page if the line does not fit
            if self._remaining_chars < len(line) + 2:
                self.start_page()

            if self.max_lines and len(self.current_page) >= self.max_lines:
                self.start_page()

            line = line.rstrip()
            if not line:
                continue

            # Append this line and update remaining characters
            self.current_page.append(line)
            self._remaining_chars -= len(line) + 2

        # Close the final page once finished
        self.start_page()

    def start_page(self) -> None:
        """Close a page once it's been created and start a new one."""
        if self.create_page:
            self.current_page.append(self.page_suffix)
            self.pages.append('\n'.join(self.current_page))

        self.current_page = [self.page_prefix] if self.page_prefix else []

        if self.page_header:
            self.current_page.append(self.page_header)

        self._remaining_chars = self.max_chars
