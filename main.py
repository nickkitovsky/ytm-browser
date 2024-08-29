"""Main core file. You can redefine dafault parametrs in app_config, endpoints."""

from ytm_browser.textual_ui.app import YtMusicApp

if __name__ == "__main__":
    app = YtMusicApp()
    app.run()
