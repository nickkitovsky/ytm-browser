from ytm_browser.core import responses

new_releases = {
    "title": "New releases albums",
    "payload": {"browse_id": "FEmusic_new_releases_albums"},
}
mixed_for_you = {
    "title": "Mixed for you",
    "payload": {"browse_id": "FEmusic_mixed_for_you"},
}
listen_again = {
    "title": "Listen again",
    "payload": {"browse_id": "FEmusic_listen_again"},
}
library = {
    "title": "Library",
    "payload": {"browse_id": "FEmusic_library_landing"},
}

raw_endpoints = [new_releases, mixed_for_you, listen_again, library]
endpoints = [
    responses.parse_response(raw_endpoint) for raw_endpoint in raw_endpoints
]
