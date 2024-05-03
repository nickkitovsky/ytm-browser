"""Common utils for parsing."""

from typing import Sequence
from unicodedata import normalize


def extract_chain(
    json_obj: dict | list,
    chain: Sequence | None = None,
) -> list | dict | str | None:
    """Extract chain keys from dict or list.

    Skipping signle nested element (len==1). If last argument 'runs', it will be automatically joined to str.

    Args:
    ----
        json_obj (dict | list): the object from witch the data will be extracted
        chain (Iterable | None, optional): chain of keys whitch will be extracted.\
            If chain is None, extract only single nested element. Defaults to None.

    Returns:
    -------
        list | dict | str | None: object after parsing

    """
    if chain:
        for element in chain:
            while len(json_obj) == 1:
                match json_obj:
                    case list(json_obj):
                        json_obj = json_obj[0]
                    case dict(json_obj) if element in json_obj:
                        break
                    case dict(json_obj):
                        json_obj = next(iter(json_obj.values()))

            json_obj = json_obj[element]
        if chain[-1] == "runs" and isinstance(json_obj, list):
            return extract_runs(runs_list=json_obj)
    else:
        while len(json_obj) == 1:
            match json_obj:
                case list(json_obj):
                    json_obj = json_obj[0]
                case dict(json_obj):
                    json_obj = next(iter(json_obj.values()))
    return json_obj


def _normalize_unicode(unicode_string: str) -> str:
    """Normalize unicode text.

    Args:
    ----
       unicode_string (str): string with unicode symbols problem

    Returns:
    -------
        str: normalized unicode string

    """
    if isinstance(unicode_string, str):
        return normalize("NFKD", unicode_string)
    msg = "unicode_string should be str"
    raise TypeError(msg)


def extract_runs(
    runs_list: list, separator: str | None = "", *, fix_unicode: bool = True
) -> str:
    """Join list's fields in 'runs' object to str.

    Args:
    ----
        runs_list (list): 'runs' elements contains list.
        separator (str, optional): separator in returnted string. Defaults to ' '.
        fix_unicode (bool): need normalize string. Defaults True.

    Returns:
    -------
        str: string which joined from 'runs' element.

    """
    joined_string = f"{separator}".join([field["text"] for field in runs_list])
    if fix_unicode:
        return _normalize_unicode(joined_string)
    return joined_string
