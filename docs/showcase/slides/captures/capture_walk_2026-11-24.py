"""Deck captures of the Market Receipt React app (2026-11-24): slide 5 and appendix A1-A4.

Start the local stack first (see scripts/capture_screenshots.py), then:

    uv run --no-project --with "playwright==1.60.0" python capture_walk_2026-11-24.py OUT

Writes the PNG crops and pins.json: for each crop, a point just left of every pinned element in
per-mille of the crop's width and height, the units mp_walk's "pins" use.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:5199"
pins = {}


def box(loc):
    loc.scroll_into_view_if_needed()
    b = loc.bounding_box()
    sy = loc.page.evaluate("window.scrollY")
    return {"x": b["x"], "y": b["y"] + sy, "width": b["width"], "height": b["height"]}


def shot(pg, name, clip, targets):
    pg.evaluate("window.scrollTo(0, 0)")
    pg.wait_for_timeout(300)
    pg.screenshot(path=OUT / f"{name}.png", full_page=True, clip=clip)
    found = []
    for t in targets:
        b = box(t) if not isinstance(t, dict) else t
        # The pin sits just left of the element, so it never covers what it names.
        cx = max(b["x"] - 16, clip["x"] + 14) if not isinstance(t, dict) else t["x"]
        cy = b["y"] + b["height"] / 2 if not isinstance(t, dict) else t["y"]
        found.append([round((cx - clip["x"]) / clip["width"] * 1000), round((cy - clip["y"]) / clip["height"] * 1000)])
    pg.evaluate("window.scrollTo(0, 0)")
    pins[name] = {"pins": found, "aspect": clip["width"] / clip["height"]}


def plan(pg, craving):
    pg.goto(BASE + "/")
    field = pg.get_by_placeholder("Something warm with chicken and rice")
    field.fill(craving)
    field.press("Enter")
    pg.wait_for_url("**/plan", timeout=60000)
    pg.get_by_text("Shopping list").first.wait_for(timeout=60000)
    pg.wait_for_timeout(1200)


with sync_playwright() as p:
    b = p.chromium.launch(args=["--lang=en-US"])
    pg = b.new_context(locale="en-US", viewport={"width": int(sys.argv[2]) if len(sys.argv) > 2 else 1280, "height": 900}, device_scale_factor=1.5).new_page()

    # A1 and the flow's step 1: the first visit's details form.
    pg.goto(BASE + "/")
    pg.get_by_label("Age").fill("34")
    pg.get_by_label("Sex").select_option("male")
    pg.get_by_label("Height (cm)").fill("165")
    pg.get_by_label("Weight (kg)").fill("65")
    pg.get_by_label("Where you shop").fill("Earlwood, NSW")
    pg.wait_for_timeout(500)
    form = pg.locator("section[aria-labelledby=profile-heading]").first
    f = box(form)
    clip = {"x": f["x"], "y": f["y"], "width": f["width"], "height": f["height"]}
    shot(pg, "walk-1-first-visit", clip, [
        pg.get_by_text("Your goal", exact=True).first,
        pg.get_by_text("Your body", exact=True).first,
        pg.get_by_text("Your activity", exact=True).first,
        pg.get_by_text("Anything to avoid?").first,
        pg.get_by_text("Your store", exact=True).first,
        pg.get_by_role("button", name="Save and start planning"),
    ])
    shot(pg, "app-1-profile-zoom", {"x": f["x"], "y": f["y"], "width": f["width"], "height": f["width"] / 1.42}, [])

    pg.get_by_role("button", name="Save and start planning").click()
    pg.wait_for_timeout(800)
    for c in ("salmon quinoa", "chickpea curry"):
        plan(pg, c)
        pg.get_by_role("button", name="Save meal").click()
        pg.wait_for_timeout(700)

    # A3, A4 and the flow's step 3: the plan page.
    plan(pg, "chicken fried rice")
    pg.get_by_role("button", name="Save meal").click()
    pg.wait_for_timeout(700)
    boxes = pg.locator("section[aria-labelledby=shopping-heading] input[type=checkbox]")
    for i in (0, 1, 3):
        boxes.nth(i).check()
    pg.get_by_label("4 stars").check(force=True)
    pg.get_by_label("A note (optional)").fill("Quick weeknight dinner, would make again")
    pg.get_by_role("button", name="Save rating").click()
    pg.wait_for_timeout(1000)
    pg.evaluate("document.activeElement && document.activeElement.blur()")
    pg.mouse.move(0, 0)
    width = pg.evaluate("document.documentElement.clientWidth")
    rail = 256
    shop = box(pg.locator("section[aria-labelledby=shopping-heading]"))
    top = {"x": rail, "y": 0, "width": width - rail, "height": min(shop["y"] + shop["height"] + 24, (width - rail) * 0.92)}
    shot(pg, "walk-3-plan", top, [
        pg.locator("section[aria-labelledby=plan-heading]").get_by_text("Portions rebalanced").first,
        pg.get_by_role("button", name="Saved to My meals"),
        pg.get_by_text("use estimated nutrition").first,
        pg.locator("section[aria-labelledby=nutrition-heading] svg").first,
        pg.locator("section[aria-labelledby=balance-heading]").first,
        pg.locator("section[aria-labelledby=shopping-heading] input[type=checkbox]").first,
    ])
    shot(pg, "app-3-plan-zoom", {"x": rail, "y": 0, "width": width - rail, "height": (width - rail) / 1.42}, [])

    pg.get_by_role("tab", name="Ingredients").click()
    pg.wait_for_timeout(600)
    pg.evaluate("document.activeElement && document.activeElement.blur()")
    tabs = box(pg.get_by_role("tablist"))
    rating = box(pg.locator("section[aria-labelledby=rating-heading]"))
    lower = {"x": rail, "y": tabs["y"] - 24, "width": width - rail, "height": rating["y"] + rating["height"] + 24 - (tabs["y"] - 24)}
    shot(pg, "walk-4-after", lower, [
        pg.get_by_role("tablist"),
        pg.locator("section[aria-labelledby=sources-heading] h2").first,
        pg.locator("section[aria-labelledby=sources-heading]").get_by_text("Reference", exact=True).first,
        pg.get_by_text("Estimated total", exact=False).first,
        pg.get_by_role("button", name="Copy list"),
        pg.locator("section[aria-labelledby=rating-heading] h2").first,
    ])

    # A2 and the flow's step 2: home, with three saved meals.
    pg.goto(BASE + "/")
    pg.wait_for_timeout(2500)
    pg.mouse.move(0, 0)
    page_h = pg.evaluate("document.documentElement.scrollHeight")
    home = {"x": 0, "y": 0, "width": width, "height": min(page_h, 1220)}
    shot(pg, "walk-2-home", home, [
        pg.get_by_placeholder("Something warm with chicken and rice"),
        pg.get_by_text("Today’s workout").first,
        pg.get_by_text("Or try one of these").first,
        pg.locator("section[aria-labelledby=home-meals] h2").first,
        pg.locator("section[aria-labelledby=latest-heading] h2").first,
        pg.get_by_text("Sized for you", exact=True).first,
    ])
    hero = box(pg.locator("section[aria-labelledby=home-heading]"))
    shot(pg, "app-2-craving-zoom", {"x": rail, "y": 0, "width": hero["width"], "height": hero["width"] / 1.42}, [])
    b.close()

(OUT / "pins.json").write_text(json.dumps(pins, indent=1))
print(json.dumps(pins))
