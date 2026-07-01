"""Capture MOCK screenshots of the running app for local preview only.

NOT for submission -- real screenshots (6b_deployment_test.png,
7c_error_handling_interface.png) must be taken inside the IBM Skills Network
Cloud IDE per SKILLS_NETWORK_STEPS.md, since they must reflect the real
Watson NLP service. These are saved with a MOCK_ prefix so they can never be
confused with the real required filenames.
"""
import sys
import threading
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "submission_assets"
sys.path.insert(0, str(ROOT))

REAL_URL_PREFIX = "https://sn-watson-emotion.labs.skillsnetwork.site"
MOCK_URL_PREFIX = "http://127.0.0.1:8000"

_original_post = requests.post


def _patched_post(url, *args, **kwargs):
    if url.startswith(REAL_URL_PREFIX):
        url = MOCK_URL_PREFIX + url[len(REAL_URL_PREFIX):]
    return _original_post(url, *args, **kwargs)


requests.post = _patched_post

import server  # noqa: E402  (picks up the patched requests.post)


def run_server():
    server.app.run(host="127.0.0.1", port=5000, use_reloader=False)


def main():
    ASSETS.mkdir(exist_ok=True)
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(1.5)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 500})

        page.goto("http://127.0.0.1:5000/")
        page.fill("#textToAnalyze", "I am so happy I am doing this")
        page.click("text=Run Sentiment Analysis")
        page.wait_for_function(
            "document.getElementById('system_response').innerText.length > 0"
        )
        page.screenshot(path=str(ASSETS / "MOCK_6b_deployment_test.png"))
        print("Saved MOCK_6b_deployment_test.png")

        page.fill("#textToAnalyze", "")
        page.evaluate("document.getElementById('system_response').innerText = ''")
        page.click("text=Run Sentiment Analysis")
        page.wait_for_function(
            "document.getElementById('system_response').innerText.includes('Invalid text')"
        )
        page.screenshot(path=str(ASSETS / "MOCK_7c_error_handling_interface.png"))
        print("Saved MOCK_7c_error_handling_interface.png")

        browser.close()


if __name__ == "__main__":
    main()
