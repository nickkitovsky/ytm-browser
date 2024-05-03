import contextlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Never, Self

from utils import parse_util
from ytm_browser.core import api_client, custom_exceptions


@dataclass(frozen=True, slots=True)
class ParseRules:
    chain: tuple
    return_keys: set | None = None


class AbstractResponse(ABC):
    def __init__(self, raw_response: dict | list) -> None:
        self._raw_response = raw_response
        self._title = None
        self._payload = None
        self._children = None

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def payload(self) -> str:
        pass

    @property
    @abstractmethod
    def _chain_children(self) -> ParseRules:
        pass

    @property
    def children(self) -> list:
        response = api_client.SyncClient().send_request(self._payload)
        for current_chain in self._chain_children:
            with contextlib.suppress(TypeError, KeyError):
                return parse_util.extract_chain(
                    json_obj=response,
                    chain=current_chain.chain,
                )
        msg = "Any valid children chain not found."
        raise custom_exceptions.ParsingError(msg)


# Responses list need to import all response types class using `register` decorator
# if you create custom response type, you should add @register to begining our response class.
#
# @register
# class MyCustomResponse:
#    pass
registered_responses: list[type[AbstractResponse]] = []


def register(decorated: type[AbstractResponse]) -> type[AbstractResponse]:
    registered_responses.append(decorated)
    return decorated


@register
class EndpointResponse(AbstractResponse):
    @property
    def title(self) -> str:
        if not self._title:
            self._title = self._raw_response.get("title")
        return self._title

    @property
    def payload(self) -> str:
        if not self._payload:
            self._payload = self._raw_response.get("payload")
        return self._payload

    @property
    def _chain_children(self) -> tuple[ParseRules, ...]:
        return (
            # common_case
            ParseRules(
                chain=("contents", "content", "contents", "items"),
            ),
        )


@register
class PlaylistResponse(AbstractResponse):
    @property
    def title(self) -> str:
        if not self._title:
            self._title = self._parse_title()
        return self._title

    @property
    def payload(self) -> str:
        if not self._payload:
            self._payload = self._raw_response.get("payload")
        return self._payload

    @property
    def _chain_children(self) -> tuple[ParseRules, ...]:
        return (
            # common_cases
            ParseRules(
                chain=("contents", 0, "content", "content", "contents"),
            ),
        )

    def _parse_title(self) -> str:
        title = parse_util.extract_chain(
            json_obj=self._raw_response,
            chain=("title", "runs"),
        )
        subtitle = ""
        try:
            subtitle = str(
                parse_util.extract_chain(
                    self._raw_response,
                    ("subtitle", "runs"),
                ),
            )
        except KeyError:
            title = f"{title}".strip()
        else:
            title = f"{title} ({subtitle})".strip()
        return title

    def _parse_payload(self) -> dict[str, str]:
        chains_payload = (
            # listen_again
            ParseRules(
                chain=(
                    "menu",
                    "items",
                    0,
                    "navigationEndpoint",
                    "watchEndpoint",
                ),
                return_keys={"params", "videoId"},
            ),
            # common_cases
            ParseRules(
                chain=(
                    "menu",
                    "items",
                    0,
                    "navigationEndpoint",
                    "watchPlaylistEndpoint",
                ),
                return_keys={"params", "playlistId"},
            ),
        )

        for current_chain in chains_payload:
            with contextlib.suppress(KeyError):
                payload = parse_util.extract_chain(
                    json_obj=self._raw_response,
                    chain=current_chain.chain,
                )
                if isinstance(payload, dict) and current_chain.return_keys:
                    return {
                        key: value
                        for key, value in payload.items()
                        if key in current_chain.return_keys
                    }
        msg = "Problem of parsing Playlist's response payload"
        raise custom_exceptions.ParsingError(msg)


@register
class Track:
    def __init__(self, raw_response: dict | list) -> None:
        self.artist = self._parse_artist(raw_track_data=raw_response)
        self.title = self._parse_trackdata_field(
            raw_track_data=raw_response,
            chain=("title", "runs"),
        )
        self.lenght = self._parse_trackdata_field(
            raw_track_data=raw_response,
            chain=("lengthText", "runs"),
        )
        self.video_id = raw_response.get("videoId", "")

    def _parse_trackdata_field(
        self,
        raw_track_data: dict,
        chain: tuple[str, ...],
    ) -> str:
        field = parse_util.extract_chain(json_obj=raw_track_data, chain=chain)
        if isinstance(field, str):
            return field.strip()
        msg = f"error of parsing {chain[0]} track field"
        raise custom_exceptions.ParsingError(msg)

    def _parse_artist(self, raw_track_data: dict) -> str:
        track_data = raw_track_data["longBylineText"]["runs"]
        artist = [
            field["text"]
            for field in track_data
            if field.get("navigationEndpoint") and self._is_artist_field(field)
        ]
        return ", ".join(artist) if artist else track_data[0]["text"]

    def _is_artist_field(self, field: dict) -> bool:
        field_type = parse_util.extract_chain(
            json_obj=field,
            chain=(
                "navigationEndpoint",
                "browseEndpoint",
                "browseEndpointContextSupportedConfigs",
                "pageType",
            ),
        )
        return field_type == "MUSIC_PAGE_TYPE_ARTIST"
