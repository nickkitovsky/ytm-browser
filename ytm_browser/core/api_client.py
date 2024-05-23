"""Client for YoutubeMusic."""

import atexit
from enum import IntEnum
from pathlib import Path
from typing import Self

from curl_cffi import requests

from utils.retry import retry
from ytm_browser.core import credentials, custom_exceptions


class HttpCodes(IntEnum):
    UNAUTHORIZED = 401
    SUCCEED = 200


class SyncClient:
    """Client for YoutubeMusic API (class uses Singleton pattern)."""

    # store class instance for use singleton pattern
    _instance = None

    def __new__(cls) -> Self:
        """Overview __new__ method, for use singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._session = requests.Session(impersonate="chrome")
        atexit.register(self._session.close, self)

    @classmethod
    def create_with_credentials(
        cls,
        credentails_data: credentials.Credentials | str | Path | list[str],
    ) -> Self:
        _instance = cls()
        _instance.set_credentials(credentails_data=credentails_data)
        return _instance

    def set_credentials(
        self,
        credentails_data: credentials.Credentials | str | Path | list[str],
    ) -> None:
        match credentails_data:
            case credentials.Credentials():
                self.credentials = credentails_data
            case str() | Path():
                self.credentials = credentials.read_credentials_from_file(
                    credentails_data,
                )
            case list() if all(
                isinstance(line, str) for line in credentails_data
            ):
                self.credentials = (
                    credentials.read_credentials_from_clipboard()
                )
            case _:
                msg = "Wrong type of credentials_data"
                raise custom_exceptions.CredentialsDataError(msg)

    # TODO: add vebrose mod for retry decorator
    # @retry(attempts_number=5, retry_sleep_sec=1)
    def send_request(self, payload: dict, timeout: int = 10) -> dict:
        """Send request to API."""
        self._check_credentials()
        credentials_with_payload = self.credentials.json_data | payload
        response = self._session.post(
            url=self._set_url(payload=payload),
            timeout=timeout,
            headers=self.credentials.headers,
            params=self.credentials.params,
            json=credentials_with_payload,
        )
        match response:
            case requests.models.Response() if response.status_code == HttpCodes.SUCCEED.value:  # noqa: E501
                return response.json()
            case requests.models.Response() if response.status_code == HttpCodes.UNAUTHORIZED.value:  # noqa: E501
                msg = "Credentials data is not valid. Please update it."
                raise custom_exceptions.CredentialsDataError(msg)
            case _:
                msg = "Unknow response error"
                raise requests.models.RequestsError(msg)

    def _set_url(self, payload: dict[str, str]) -> str:
        match payload:
            case {"browse_id": _} | {"browseId": _}:
                return "https://music.youtube.com/youtubei/v1/browse"
            case {"playlistId": _} | {"videoId": _}:
                return "https://music.youtube.com/youtubei/v1/music/get_queue"
            case _:
                msg = "Unknow payload type."
                raise custom_exceptions.PayloadError(msg)

    def _check_credentials(self) -> None:
        if not self.credentials:
            msg = "Credentials is not set. Please call first set_credentials(credentails_data: credentials.Credentials | str | Path | list[str])."  # noqa: E501
            raise custom_exceptions.CredentialsDataError(msg)
