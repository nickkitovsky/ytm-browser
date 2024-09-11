"""Playlist download module."""

from pathlib import Path

import yt_dlp

from ytm_browser.core import responses

DEFAULT_SAVE_DIR = "files/music"
# FILE_TEMPLATE = '%(artist)s - %(title)s.%(ext)s'
# FILE_TEMPLATE = '%(title)s.%(ext)s'
FILE_TEMPLATE = "%(uploader)s - %(title)s.%(ext)s"


def download_playlist(
    playlist: responses.PlaylistResponse,
    target_dir: Path | str | None = None,
) -> None:
    """Download tracks from playlist.

    Args:
    ----
        playlist (Playlist): Playlist object
        target_dir (Path | str | None, optional): Dir to download music(USE '/' in path).\
            Defaults DEFAULT_SAVE_DIR(`files/music`).

    Raises:
    ------
        ValueError: _description_
        ValueError: _description_

    """
    ydl_opts = {
        "format": "251",
        "outtmpl": f"{DEFAULT_SAVE_DIR}/{FILE_TEMPLATE}",
        "add-metadata": True,
        "embed-metadata": True,
        "extract-audio": True,
        "audio-quality": 0,
        "retries": 35,
        "quality": "0",
        "cover_format": "jpg",
        "writethumbnail": True,
        "embedthumbnail": True,
        "windowsfilenames": True,
        "restrict-filenames": True,
        # TODO: add archive file support: 'download_archive': 'archive.txt',
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": 0,
            },
            {"key": "EmbedThumbnail"},
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
    }
    match target_dir:
        case str() | Path():
            target_dir = Path(target_dir)
        case None:
            target_dir = DEFAULT_SAVE_DIR
        case _:
            msg = "wrong `target_dir` value"
            raise ValueError(msg)
    if isinstance(playlist, responses.PlaylistResponse):
        target_dir_with_playlist = Path(target_dir, playlist.title)
        target_dir_with_playlist.mkdir(parents=True, exist_ok=True)
        # TODO: Normalize playlist title for well dirname
        ydl_opts["outtmpl"] = f"{target_dir_with_playlist}/{FILE_TEMPLATE}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(
                [
                    f"https://www.youtube.com/watch?v={track.video_id}"
                    for track in playlist.children
                ],
            )
    else:
        msg = "bad format for `playlist` object"
        raise ValueError(msg)
