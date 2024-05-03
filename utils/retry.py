import functools
import time
from typing import Callable, TypeVar

from ytm_browser.core import custom_exceptions

RT = TypeVar("RT")  # return type


def retry(
    attempts_number: int,
    retry_sleep_sec: int,
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Retry attempts run of function.

    Args:
    ----
        attempts_number (int): number of attempts
        retry_sleep_sec (int): sleep between attempts

    Returns:
    -------
        none: this is decorator

    """

    def decarator(func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            # TODO: For logging change '_' to attempt
            for _ in range(attempts_number):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    time.sleep(retry_sleep_sec)
                # TODO: Add logging 'Trying attempt {attempt+1} of {attempts_number}'

            # TODO: Add logging 'func {func.__name__} retry failed'
            msg = f"Exceed max retry num: {attempts_number} failed."
            raise custom_exceptions.TooManyRetryError(msg)

        return wrapper

    return decarator
