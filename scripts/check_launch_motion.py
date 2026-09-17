#!/usr/bin/env python3
"""Runtime motion gate for the launch page.

Normal motion must still scrub the hero film. When the operating system asks
for reduced motion, the particle canvas and hero film must become identical
still pixels after scrolling, with no horizontal overflow on desktop or mobile.
"""
from __future__ import annotations

import sys
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: object) -> None:
        return


@contextmanager
def launch_server() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/site/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def snapshot(page: Page) -> dict[str, object]:
    return page.evaluate(
        """() => {
          const hero = document.getElementById('heroFilm');
          const poster = document.querySelector('.film img.first');
          return {
            reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
            frame: hero.dataset.frame || '0',
            sky: document.getElementById('atmosphere').toDataURL(),
            hero: hero.toDataURL(),
            overflowX: document.documentElement.scrollWidth - window.innerWidth,
            posterOpacity: Number(getComputedStyle(poster).opacity),
          };
        }"""
    )


def check_normal_motion(browser: Browser, url: str) -> list[str]:
    errors: list[str] = []
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=1,
        reduced_motion="no-preference",
    )
    page = context.new_page()
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))

    page.goto(url)
    page.locator(".film.ready").wait_for(timeout=5000)
    page.wait_for_timeout(300)
    page.mouse.wheel(0, 900)
    page.wait_for_timeout(800)

    frame = int(page.locator("#heroFilm").get_attribute("data-frame") or "0")
    if frame < 2:
        errors.append(f"normal scroll only reached hero frame {frame}, expected scrubbing")

    context.close()
    return errors


def check_reduced_motion(
    browser: Browser, url: str, width: int, height: int
) -> list[str]:
    errors: list[str] = []
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    page = context.new_page()
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))

    page.goto(url)
    page.locator(".film.ready").wait_for(timeout=5000)
    page.wait_for_timeout(500)
    before = snapshot(page)

    page.mouse.wheel(0, min(900, height - 20))
    page.wait_for_timeout(750)
    after = snapshot(page)

    if not before["reduced"] or not after["reduced"]:
        errors.append(f"{width}px viewport did not emulate reduced motion")
    if before["overflowX"] > 0 or after["overflowX"] > 0:
        errors.append(
            f"{width}px viewport has horizontal overflow "
            f"(before={before['overflowX']}, after={after['overflowX']})"
        )
    if before["frame"] != "0" or after["frame"] != "0":
        errors.append(
            f"{width}px hero frame changed from {before['frame']} to {after['frame']}, expected 0"
        )
    if float(before["posterOpacity"]) < 0.99 or float(after["posterOpacity"]) < 0.99:
        errors.append(
            f"{width}px poster opacity was not fully visible "
            f"(before={before['posterOpacity']}, after={after['posterOpacity']})"
        )
    if before["sky"] != after["sky"]:
        errors.append(f"{width}px particle canvas changed pixels in reduced motion")
    if before["hero"] != after["hero"]:
        errors.append(f"{width}px hero film changed pixels in reduced motion")

    context.close()
    return errors


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is required: python -m pip install playwright", file=sys.stderr)
        return 1

    with launch_server() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            failures = [
                *check_normal_motion(browser, url),
                *check_reduced_motion(browser, url, 1440, 900),
                *check_reduced_motion(browser, url, 390, 844),
                *check_reduced_motion(browser, url, 320, 844),
            ]
        finally:
            browser.close()

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 2

    print("Launch motion contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
