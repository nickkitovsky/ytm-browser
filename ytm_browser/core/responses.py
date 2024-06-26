import contextlib
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

from utils import parse_util
from ytm_browser.core import api_client, custom_exceptions


@dataclass(frozen=True, slots=True)
class ParseRules:
    chain: tuple
    return_keys: set | None = None


class AbstractResponse(ABC):
    def __init__(self, raw_response: dict | list) -> None:
        self.validate_response(raw_response=raw_response)
        self.title = self.parse_title(raw_response)
        self.payload = self.parse_payload(raw_response)
        self._children = None

    def __hash__(self) -> int:
        return hash((self.title, self.payload))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.title == other.title and self.payload == other.payload

    def __str__(self) -> str:
        return str(self.title)

    @abstractmethod
    def parse_title(self, raw_response: dict | list) -> str:
        """Parse title function."""

    @abstractmethod
    def parse_payload(self, raw_response: dict | list) -> dict[str, dict]:
        """Parse children payload function."""

    @abstractmethod
    def set_chain_children(self) -> tuple[ParseRules, ...]:
        """Set tuple of children payload chains."""

    @abstractmethod
    def _get_validate_key(self) -> str:
        """Return string unique key for response type (if key wont found raise WrongResponseTypeError exception)."""  # noqa: E501

    def validate_response(
        self,
        raw_response: dict | list,
    ) -> None:
        if isinstance(raw_response, dict) and not raw_response.get(
            self._get_validate_key(),
        ):
            msg = f"Response is not valid {self.__class__.__name__} type."
            raise custom_exceptions.WrongResponseTypeError(msg)

    @property
    def children(self) -> list:
        if not self._children:
            response = api_client.SyncClient().send_request(self.payload)
            for current_chain in self.set_chain_children():
                with contextlib.suppress(TypeError, KeyError):
                    raw_children = parse_util.extract_chain(
                        json_obj=response,
                        chain=current_chain.chain,
                    )
                    if isinstance(raw_children, list):
                        self._children = [
                            parse_response(parse_util.extract_chain(raw_child))
                            for raw_child in raw_children
                        ]
                        return self._children
            msg = "Any valid children chain not found."
            raise custom_exceptions.ParsingError(msg)

        return self._children


# Responses list need to import all response types class using `@register`
# if you create custom response type, you should add @register to your response class.  # noqa: E501
#
# @register
# class MyCustomResponse:
#    pass
registered_responses_types: set[type[AbstractResponse]] = set()


def register(decorated: type[AbstractResponse]) -> type[AbstractResponse]:
    registered_responses_types.add(decorated)
    return decorated


@register
class EndpointResponse(AbstractResponse):
    def parse_title(self, raw_response: dict | list) -> str:
        return raw_response.get("title")

    def parse_payload(self, raw_response: dict | list) -> dict[str, dict]:
        return raw_response.get("payload")

    def set_chain_children(self) -> tuple[ParseRules, ...]:
        return (
            # common_case
            ParseRules(
                chain=("contents", "content", "contents", "items"),
            ),
        )

    def _get_validate_key(self) -> str:
        return "payload"


@register
class PlaylistResponse(AbstractResponse):
    def parse_title(self, raw_response: dict | list) -> str:
        title = parse_util.extract_chain(
            json_obj=raw_response,
            chain=("title", "runs"),
        )
        subtitle = ""
        try:
            subtitle = str(
                parse_util.extract_chain(
                    raw_response,
                    ("subtitle", "runs"),
                ),
            )
        except KeyError:
            title = f"{title}".strip()
        else:
            title = f"{title} ({subtitle})".strip()
        return title

    def parse_payload(self, raw_response: dict | list) -> dict[str, dict]:
        for current_chain in self.set_chain_payload():
            with contextlib.suppress(KeyError):
                payload = parse_util.extract_chain(
                    json_obj=raw_response,
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

    def set_chain_payload(self) -> tuple[ParseRules, ...]:
        return (
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

    def set_chain_children(self) -> tuple[ParseRules, ...]:
        return (
            # common_cases
            ParseRules(
                chain=("queueDatas",),
            ),
        )

    def _get_validate_key(self) -> str:
        return "aspectRatio"


@register
class TrackResponse:
    def __init__(self, raw_response: dict | list) -> None:
        self.validate_response(raw_response)
        raw_response = parse_util.extract_chain(json_obj=raw_response)

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

    def __hash__(self) -> int:
        return hash(self.video_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.video_id == other.video_id

    def __str__(self) -> str:
        return (
            f"{self.artist} - {self.title} ({self.lenght} [{self.video_id}])"
        )

    def validate_response(
        self,
        raw_response: dict | list,
    ) -> None:
        if isinstance(raw_response, dict) and not raw_response.get("videoId"):
            msg = f"Response is not valid {self.__class__.__name__} type."
            raise custom_exceptions.WrongResponseTypeError(msg)

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


def make_parse_response() -> (
    typing.Callable[..., AbstractResponse | TrackResponse]
):
    previous_response_type = None
    response_types = list(registered_responses_types)

    def parse_response(
        raw_response: list | dict,
    ) -> AbstractResponse | TrackResponse:
        nonlocal previous_response_type
        nonlocal response_types
        if previous_response_type:
            start_index = response_types.index(previous_response_type)
            response_types = (
                response_types[start_index:] + response_types[:start_index]
            )

        for response_type in response_types:
            with contextlib.suppress(custom_exceptions.WrongResponseTypeError):
                response = response_type(raw_response)
                previous_response_type = response_type
                return response
        msg = "Not found any appropriate response type"
        raise custom_exceptions.ParserError(msg)

    return parse_response


parse_response = make_parse_response()
