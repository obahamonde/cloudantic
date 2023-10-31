"""
Logging and error handling utilities for the Swagchain API.
"""
import asyncio
import functools
import logging
from time import perf_counter
from typing import Awaitable, Callable, Generator, Sequence, TypeVar, Union, cast

from aiohttp.web_exceptions import HTTPException
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import install
from rich.traceback import install as ins
from tenacity import retry as retry_
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential
from typing_extensions import ParamSpec

EXCEPTIONS = (
    asyncio.TimeoutError,
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    TimeoutError,
    UnicodeDecodeError,
    UnicodeEncodeError,
    UnicodeError,
    TypeError,
    ValueError,
    ZeroDivisionError,
    IndexError,
    AttributeError,
    ImportError,
    ModuleNotFoundError,
    NotImplementedError,
    RecursionError,
    OverflowError,
    KeyError,
    Exception,
    HTTPException,
)

T = TypeVar("T")
P = ParamSpec("P")


def setup_logging(name: str) -> logging.Logger:
    """
    Set's up logging using the Rich library for pretty and informative terminal logs.

    Arguments:
    name -- Name for the logger instance. It's best practice to use the name of the module where logger is defined.
    """
    install()
    ins()
    console = Console(record=True, force_terminal=True)
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        tracebacks_extra_lines=2,
        tracebacks_theme="monokai",
        show_level=False,
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])
    logger_ = logging.getLogger(name)
    logger_.setLevel(logging.INFO)
    return logger_


logger = setup_logging(__name__)


def process_time(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """
    A decorator to measure the execution time of a coroutine.

    Arguments:
    func -- The coroutine whose execution time is to be measured.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """
        Wrapper function to time the function call.
        """
        start = perf_counter()
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end = perf_counter()
        logger.info(
            "Time taken to execute %s: %s seconds", wrapper.__name__, end - start
        )
        return result  # type: ignore

    return wrapper


def handle_errors(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """
    A decorator to handle errors in a coroutine.

    Arguments:
    func -- The coroutine whose errors are to be handled.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """
        Wrapper function to handle errors in the function call.
        """
        try:
            if asyncio.iscoroutinefunction(func):
                response = await func(*args, **kwargs)
                logger.info(response)
                return response  # type: ignore
            response = func(*args, **kwargs)
            logger.info(response)
            return response  # type: ignore
        except EXCEPTIONS as exc:
            detail = getattr(exc, "detail", str(exc))
            if detail:
                detail = str(detail).strip()
                logger.error(detail)
            else:
                detail = exc.__class__.__name__  # type: ignore
                logger.error(detail)
            logger.error(str(exc))
            raise HTTPException(detail=detail, status_code=500) from exc

    return wrapper


def chunker(seq: Sequence[T], size: int) -> Generator[Sequence[T], None, None]:
    """
    A generator function that chunks a sequence into smaller sequences of the given size.

    Arguments:
    seq -- The sequence to be chunked.
    size -- The size of the chunks.
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def gen_emptystr() -> str:
    """
    A generator function that returns an empty string.
    """
    return cast(str, None)


def handle(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """
    A decorator to apply all decorators to a coroutine.

    Arguments:

    func -- The coroutine to decorate.
    """
    return functools.reduce(
        lambda f, g: g(f),  # type: ignore
        [retry(), handle_errors, process_time],
        func,
    )


def async_io(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """
    Decorator to convert an IO bound function to a coroutine by running it in a thread pool.
    """

    @handle
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def async_cpu(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """
    Decorator to convert a CPU bound function to a coroutine by running it in a process pool.
    """

    @handle
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.get_running_loop().run_in_executor(
            None, func, *args, **kwargs
        )

    return wrapper


def retry(
    retries: int = 10, wait: int = 1, max_wait: int = 60
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Wrap an async function with exponential backoff."""

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        @retry_(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=wait, max=max_wait),
            retry=retry_if_exception_type(EXCEPTIONS),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await func(*args, **kwargs)  # type: ignore

        return wrapper

    return cast(Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]], decorator)  # type: ignore    # noqa: E501
