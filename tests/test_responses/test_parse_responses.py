from pathlib import Path

import pytest

from utils import json_utils
from ytm_browser.core import responses

RESPONSES_DIR = "tests/raw_responses"


playlists = tuple(Path(f"{RESPONSES_DIR}/playlists").glob("*.json"))
playlists_ids = [str(playlist) for playlist in playlists]

tracks = tuple(Path(f"{RESPONSES_DIR}/tracks").glob("*.json"))
tracks_ids = [str(track) for track in tracks]


@pytest.mark.parametrize("playlist_response", playlists, ids=playlists_ids)
def test_common_parse_playlist(playlist_response: str | Path) -> None:
    raw_response = json_utils.read_json(playlist_response)
    assert isinstance(
        responses.parse_response(raw_response),
        responses.PlaylistResponse,
    )


@pytest.mark.parametrize("track_response", tracks, ids=tracks_ids)
def test_common_parse_track(track_response: str | Path) -> None:
    raw_response = json_utils.read_json(track_response)
    assert isinstance(
        responses.parse_response(raw_response),
        responses.TrackResponse,
    )
