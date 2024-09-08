"""Main core file. You can redefine dafault parametrs in app_config, endpoints."""

from ytm_browser import start_endpoints
from ytm_browser.textual_ui.browse_app import DevApp

if __name__ == "__main__":
    app = DevApp()
    app.run()
