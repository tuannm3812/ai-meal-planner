import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1])
OUT.mkdir(exist_ok=True)


def plan(pg, craving):
    pg.goto("http://localhost:5199/")
    pg.locator("#craving-input").fill(craving)
    pg.locator("#craving-input").press("Enter")
    pg.wait_for_url("**/plan**", timeout=60000)
    pg.get_by_text("Shopping list").first.wait_for(timeout=60000)
    pg.wait_for_timeout(1500)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--lang=en-US"])
    pg = b.new_context(
        locale="en-US", viewport={"width": 1280, "height": 900}, device_scale_factor=1.5
    ).new_page()
    pg.goto("http://localhost:5199/")
    pg.get_by_label("Age").fill("34")
    pg.get_by_label("Sex").select_option("male")
    pg.get_by_label("Height (cm)").fill("165")
    pg.get_by_label("Weight (kg)").fill("65")
    pg.get_by_label("Where you shop").fill("Earlwood, NSW")
    pg.get_by_role("button", name="Save and start planning").click()
    pg.wait_for_timeout(800)
    for c in ("salmon quinoa", "chickpea curry"):
        plan(pg, c)
        pg.get_by_role("button", name="Save meal").click()
        pg.wait_for_timeout(800)
    plan(pg, "chicken fried rice")
    pg.get_by_role("button", name="Save meal").click()
    pg.wait_for_timeout(800)
    boxes = pg.locator("section[aria-labelledby=shopping-heading] input[type=checkbox]")
    for i in (0, 1, 3):
        boxes.nth(i).check()
    pg.get_by_label("4 stars").check(force=True)
    pg.get_by_label("A note (optional)").fill("Quick weeknight dinner, would make again")
    pg.get_by_role("button", name="Save rating").click()
    pg.wait_for_timeout(1000)
    pg.evaluate("document.activeElement && document.activeElement.blur()")
    pg.mouse.move(0, 0)
    pg.screenshot(path=OUT / "w3-plan.png", full_page=True)
    pg.goto("http://localhost:5199/")
    pg.wait_for_timeout(2500)
    pg.screenshot(path=OUT / "w2-home.png", full_page=True)
    b.close()
