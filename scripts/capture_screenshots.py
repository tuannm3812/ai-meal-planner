"""Regenerate the README screenshots in docs/assets/screenshots/.

Not part of the app or its tests, so Playwright is not a project dependency.
Start the three apps first, ideally from a scratch worktree so the generated
meal plans never touch your real database/ files:

    STORAGE_BACKEND=json SKIP_DOTENV=1 API_KEYS= \\
      ALLOWED_ORIGINS=http://localhost:5199 \\
      uv run uvicorn backend.app.main:app --port 8011
    (cd frontend && VITE_API_URL=http://localhost:8011 npx vite --port 5199)
    STREAMLIT_DEMO_MODE=1 uv run streamlit run streamlit_app/app.py \\
      --server.headless true --server.port 8599

then:

    uv run --no-project --with "playwright==1.60.0" \\
      python scripts/capture_screenshots.py docs/assets/screenshots

Playwright 1.60.0 uses Chromium build 1223; install it once with
`playwright install chromium` if it is not cached. On macOS, number fields
follow the OS region setting (for example "1,55"), which no browser flag
overrides.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1])
REACT = "http://localhost:5199/"
STREAMLIT = "http://localhost:8599/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--lang=en-US"])
    page = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 1000}).new_page()

    page.goto(REACT)
    page.get_by_label("Craving Input").fill("high-protein chicken rice bowl")
    page.get_by_role("button", name="Generate Meal Plan").click()
    page.get_by_text("Meal Overview").wait_for(timeout=60000)
    page.wait_for_timeout(800)
    page.screenshot(path=OUT / "react-meal-plan.png", full_page=True)

    page.get_by_role("button", name="Calories").click()
    page.get_by_role("button", name="Predict Expenditure").click()
    page.get_by_text("Daily expenditure").wait_for(timeout=30000)
    page.screenshot(path=OUT / "react-calories.png", full_page=True)

    page.get_by_role("button", name="History").click()
    page.get_by_role("button", name="Load meal history").click()
    page.wait_for_timeout(2000)
    page.screenshot(path=OUT / "react-history.png", full_page=True)

    demo = browser.new_context(locale="en-US", viewport={"width": 1440, "height": 1400}).new_page()
    demo.goto(STREAMLIT)
    demo.get_by_role("button", name="Generate meal").wait_for(timeout=60000)
    demo.get_by_role("button", name="Generate meal").click()
    demo.get_by_text("Estimated total").wait_for(timeout=90000)
    demo.wait_for_timeout(1500)
    demo.screenshot(path=OUT / "streamlit-demo.png")

    browser.close()
print("captured", sorted(f.name for f in OUT.glob("*.png")))
