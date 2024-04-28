"""Helper functions for write/read json."""

import json
from pathlib import Path


def write_json(filename: str, filedata: dict | list) -> None:
    """Write dict or list object to file.

    Args:
    ----
        filename (str): File for dump data
        filedata (dict | list): Data for writing

    """
    with open(filename, mode="w") as fs:
        json.dump(filedata, fs)


def read_json(filemane: str | Path) -> dict:
    """Read json object from file.

    Args:
    ----
        filemane (str | Path): File for load data

    Returns:
    -------
        dict: Json object(dict)

    """
    with Path(filemane).open(encoding="utf-8") as fs:
        # with open(filemane, encoding="utf-8") as fs:
        return json.load(fs)
