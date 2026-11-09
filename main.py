from playwright.sync_api import sync_playwright
from threading import Event
from datetime import datetime
import keyboard
import re

stop_event = Event()

keyboard.add_hotkey("f8", stop_event.set)

print("RNGDLE Checker started!")
print("Press F8 to stop.")

try:
    with sync_playwright() as p:
        i = 0

        while not stop_event.is_set():
            i += 1
            print(f"\nAttempt {i}")

            browser = p.chromium.launch(
                headless=False,
                args=["--start-maximized"]
            )

            try:
                page = browser.new_page(no_viewport=True)

                page.goto("https://www.rngdle.com/")

                if stop_event.is_set():
                    break

                page.get_by_role("button", name="GENERATE").click()

                page.reload()

                if stop_event.wait(2):
                    break

                percentage_text = page.get_by_text(
                    re.compile(r"(TOP|BOTTOM)\s*[<>]?\d+%", re.I)
                ).inner_text(timeout=10000)

                print("Result:", percentage_text)

                match = re.search(
                    r"(TOP|BOTTOM)\s*([<>])?(\d+)%",
                    percentage_text,
                    re.I
                )

                if stop_event.is_set():
                    break

                if match and match.group(2) != ">" and int(match.group(3)) <= 10:

                    filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"

                    page.screenshot(path=filename)
                    print("SAVED:", filename)

                else:
                    print("SKIPPED:", percentage_text)

            finally:
                browser.close()

except KeyboardInterrupt:
    print("Stopped using Ctrl+C.")

finally:
    keyboard.unhook_all_hotkeys()
    print("Program stopped!")
