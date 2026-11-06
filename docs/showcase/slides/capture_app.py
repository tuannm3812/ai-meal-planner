"""Capture the three React screens used on slides 5 and 9.

Start the API and client first, from a scratch clone so plans never touch your database:

    STORAGE_BACKEND=json SKIP_DOTENV=1 API_KEYS= ALLOWED_ORIGINS=http://localhost:5199 \\
      uv run uvicorn backend.app.main:app --port 8011
    (cd frontend && VITE_API_URL=http://localhost:8011 npx vite --port 5199)

then:

    uv run --no-project --with "playwright==1.60.0" \\
      python docs/showcase/slides/capture_app.py <output folder>

Replaces scripts/capture_screenshots.py for the showcase; that one drives the old dashboard.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

out = Path(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(
        viewport={"width": 1280, "height": 900}, device_scale_factor=1.5, locale="en-AU"
    )
    pg.goto("http://localhost:5199")
    pg.wait_for_selector("#profile-heading", timeout=20000)
    pg.wait_for_timeout(800)
    for label, val in [("Age", "34"), ("Height (cm)", "165"), ("Weight (kg)", "65")]:
        pg.get_by_label(label).fill(val)
    pg.get_by_label("Sex").select_option(index=1)
    pg.wait_for_timeout(300)
    pg.screenshot(path=out / "1-profile.png")
    print(pg.inner_text("body")[:600])
    pg.get_by_role("button", name="Next: what are you craving?").click()
    pg.wait_for_selector("#craving-heading")
    pg.get_by_label("Your craving").fill("chicken fried rice")
    pg.wait_for_timeout(300)
    pg.screenshot(path=out / "2-craving.png")
    pg.get_by_role("button", name="Plan my meal").click()
    pg.wait_for_function(
        "document.body.innerText.includes('kcal') && document.body.innerText.includes('Shopping')",
        timeout=90000,
    )
    pg.wait_for_timeout(1200)
    pg.screenshot(path=out / "3-plan.png")
    pg.screenshot(path=out / "3-plan-full.png", full_page=True)
    print(pg.inner_text("body")[:1400])
    b.close()
