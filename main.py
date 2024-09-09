"""Main core file. You can redefine dafault parametrs in app_config, endpoints."""

from ytm_browser import start_endpoints
from ytm_browser.textual_ui.app import YtMusicApp

if __name__ == "__main__":
    app = YtMusicApp(start_endpoints.endpoints)
    app.run()
