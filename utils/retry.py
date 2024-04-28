import functools
import time

from ytm_grabber.core.custom_exceptions import TooManyRetryError


def retry(attempts_number: int, retry_sleep_sec: int):
    """Retry attempts run of function.

    Args:
    ----
        attempts_number (int): number of attempts
        retry_sleep_sec (int): sleep between attempts

    Returns:
    -------
        none: this is decorator

    """

    def decarator(func):
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
            raise TooManyRetryError(
                msg,
            )

        return wrapper

    return decarator
