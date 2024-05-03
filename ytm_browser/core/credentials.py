"""Module for working with auth files."""

import json
import shlex
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pyperclip  # type: ignore  # noqa: PGH003 # missing stub files

from ytm_browser.core import custom_exceptions


@dataclass
class Credentials:
    headers: dict
    params: dict
    json_data: dict


def read_credentials_from_file(curl_request_file: str | Path) -> Credentials:
    """Read file with your session from Dev tools, and then 'copy as cURL'.

    Args:
    ----
        curl_request_file (str | Path): Path to file

    Raises:
    ------
        TypeError: Wrong type. You must pass str or Path object
        FileNotFoundError: Wrong file path

    Returns:
    -------
        Self(AuthData): AuthData instance.

    """
    if not isinstance(curl_request_file, (str, Path)):
        msg = "Incorrect type of `curl_file` (str or Path only)"
        raise TypeError(msg)
    try:
        with Path(curl_request_file).open(encoding="utf-8") as fs:
            return parse_curl_request(fs.readlines())
    except FileNotFoundError as exc:
        msg = "Incorrect file name or Path object"
        raise FileNotFoundError(msg) from exc


def read_credentials_from_clipboard() -> Credentials:
    clipboard_content = pyperclip.paste()
    return parse_curl_request(clipboard_content.split("\n"))


def search_credentials_in_dir(dir_path: str | Path) -> dict[str, Credentials]:
    """Scan dir to authdata files.

    Args:
    ----
        dir_path (str | Path): path to curl files

    Returns:
    -------
        dict[str, Credentials]: {filename: Credentials}

    """
    credentials_in_dir: dict = {}
    if isinstance(dir_path, str) and "\\" in dir_path:
        dir_path = dir_path.replace("\\", "/")
    dir_path = Path(dir_path)
    if Path(dir_path).is_dir():
        files = dir_path.glob("*")
        for file in files:
            with suppress(custom_exceptions.ParsingError):
                credentials_in_dir |= {
                    file.name: read_credentials_from_file(file),
                }
    return credentials_in_dir


def parse_curl_request(raw_curl_content: list[str]) -> Credentials:
    """Parse curl request for authentification on Youtube Music."""

    def _fix_cmd_breaklines(content_with_cr: list) -> list:
        """Fix cmd windows break line, remove CR character."""
        return [line.replace("^", "") for line in content_with_cr]

    if "^" in raw_curl_content[0]:
        raw_curl_content = _fix_cmd_breaklines(raw_curl_content)
    try:
        # Parsing 'params' section
        post_url = shlex.split(raw_curl_content[0])[1]
        query_post_url = urlsplit(post_url).query
        post_params = dict(parse_qsl(query_post_url))
        # Parsing 'data-raw' section for json_data
        data_raw = [
            shlex.split(raw_curl_content_line)[1]
            for raw_curl_content_line in raw_curl_content
            if raw_curl_content_line.startswith("  --data-raw")
        ]
        json_data = json.loads(s=data_raw[0])
        # delete default browseId
        json_data.pop("browseId", None)
        # Parsing 'headers' section
        raw_headers = [
            shlex.split(raw_curl_content_line)[1]
            for raw_curl_content_line in raw_curl_content
            if raw_curl_content_line.startswith("  -H")
        ]
        # Parse "key: value" to [key, value] and create headers dict
        headers = dict([line.split(": ") for line in raw_headers])
        return Credentials(
            headers=headers,
            params=post_params,
            json_data=json_data,
        )
    except (IndexError, json.JSONDecodeError, AttributeError) as exc:
        msg = "error of parse curl_data"
        raise custom_exceptions.ParsingError(msg) from exc
