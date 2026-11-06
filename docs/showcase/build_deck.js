// Builds the 16-slide seed to docs/showcase/slides/BRIEF.md and DESIGN.md.
// Slides stay plain shapes, text and tables so they are editable in Google Slides.
// Run from this folder with pptxgenjs installed and PPTX_SKILL set to the pptx
// skill folder (its apply_theme.js writes the Kitchen green theme into the file).
// This is a seed: once converted, the live deck is the source of truth.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const THEME = {
  name: "Kitchen green",
  headFontFace: "Google Sans",
  bodyFontFace: "Google Sans",
  colors: {
    dk1: "15291F", lt1: "FFFFFF", dk2: "4B5B52", lt2: "EEF4EF",
    accent1: "C8431F", accent2: "1B5E3F", accent3: "2F6FAB",
    accent4: "9A6A12", accent5: "7A4E9C", accent6: "DDE3DA",
    hlink: "B23A17", folHlink: "4B5B52",
  },
};
const HEAD = THEME.headFontFace;
const TINT_OK = "E3EFE6", TINT_WARN = "FBEBD6", WARN = "7A4A0C", NEUTRAL = "ECEFE8", ON_INK = "C9D3CC";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 960 x 540 pt
pres.title = "AI Meal Planner showcase";
pres.author = "Mike";
pres.theme = { headFontFace: HEAD, bodyFontFace: HEAD };
const C = pres.SchemeColor;
const INK = C.text1, MUTED = C.text2, WHITE = C.background1, PANEL = C.background2;
const TOMATO = C.accent1, GREEN = C.accent2, LINE = C.accent6;
const MONO = "Google Sans Code", BASELINE = "9AA5A0";

const pt = (n) => n / 72; // positions in DESIGN.md are points
const box = (x, y, w, h) => ({ x: pt(x), y: pt(y), w: pt(w), h: pt(h) });
const X0 = 43.5, W = 873, TOP = 130;

pres.defineSlideMaster({
  title: "DARK",
  background: { color: INK },
  objects: [{ placeholder: { options: { name: "title", type: "title", ...box(X0, 158, 590, 72), fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } }],
});
pres.defineSlideMaster({
  title: "COVER",
  background: { color: INK },
  objects: [{ placeholder: { options: { name: "title", type: "title", ...box(X0, 92, 300, 112), fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } }],
});
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: WHITE },
  objects: [
    { image: { path: "slides/assets/bg-corner.png", ...box(0, 0, 960, 540) } },
    { placeholder: { options: { name: "label", type: "body", ...box(X0, 21.7, W, 18), fontSize: 10, bold: true, color: INK, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", ...box(X0, 48.4, W, 36), fontFace: HEAD, fontSize: 24, bold: true, color: GREEN, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", ...box(X0, 90.9, W, 22), fontSize: 12, color: MUTED, align: "left", valign: "top", margin: 0 }, text: "" } },
    { image: { path: "slides/assets/mark.png", ...box(X0, 501, 18, 18) } },
    { text: { text: "AI Meal Planner", options: { ...box(68, 500, 200, 20), fontSize: 10, color: MUTED, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { ...box(856.5, 500, 60, 20), fontSize: 10, color: MUTED, align: "right" },
});

const text = (s, t, x, y, w, h, o = {}) =>
  s.addText(t, { isTextBox: true, margin: 0, color: INK, fontSize: 12, valign: "top", ...box(x, y, w, h), ...o });
// A card holds its own text, as DESIGN.md requires.
// Empty cards frame a figure, so they stay white with a border; text cards use the panel fill.
const card = (s, runs, x, y, w, h, o = {}) =>
  s.addText(runs, {
    shape: pres.ShapeType.roundRect, rectRadius: pt(12), ...box(x, y, w, h),
    fill: { color: o.fill || (runs === "" ? WHITE : PANEL) }, line: { color: o.fill || (runs === "" ? LINE : PANEL), width: 1 },
    margin: o.margin ?? 8, valign: o.valign || "top", color: o.color || INK, fontSize: 12,
  });
const hb = (h, b, o = {}) => [
  { text: h, options: { fontFace: HEAD, fontSize: 16, bold: true, color: o.hc || INK, breakLine: true, paraSpaceAfter: 4 } },
  { text: b, options: { fontSize: 12, color: o.bc || MUTED } },
];
const chip = (s, n, x, y) =>
  s.addText(String(n), { shape: pres.ShapeType.ellipse, ...box(x, y, 22, 22), fill: { color: INK }, color: WHITE, fontSize: 10, bold: true, align: "center", valign: "middle", margin: 0 });
const marker = (s, n, x, y) =>
  s.addText(String(n), { shape: pres.ShapeType.ellipse, ...box(x, y, 12, 12), fill: { color: TOMATO }, color: WHITE, fontSize: 8, bold: true, align: "center", valign: "middle", margin: 0 });
const arrow = (s, x1, y1, x2, y2) =>
  s.addShape(pres.ShapeType.line, { ...box(Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1)), line: { color: MUTED, width: 1, endArrowType: "triangle" } });
const limit = (s, t, x, y, w, h, prefix = "Limit:") =>
  s.addText([{ text: `${prefix} `, options: { bold: true, color: WARN } }, { text: t, options: { color: INK } }], {
    shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x, y, w, h), fill: { color: TINT_WARN }, line: { color: TINT_WARN, width: 1 }, fontSize: 8, margin: 8, valign: "middle",
  });
const caption = (s, n, t, x, y, w) =>
  text(s, [{ text: `Figure ${n}. `, options: { bold: true } }, { text: t }], x, y, w, 14, { fontSize: 9, color: MUTED });
// items: [[heading, body], ...]; offsets place each marker on its heading's first line.
const takeaways = (s, items, offsets) => {
  const runs = [];
  items.forEach(([h, b], i) => {
    runs.push({ text: h, options: { bold: true, breakLine: true, paraSpaceBefore: i ? 14 : 0, paraSpaceAfter: 6 } });
    runs.push({ text: b, options: { color: MUTED, breakLine: i < items.length - 1, paraSpaceAfter: 6 } });
  });
  text(s, runs, 684, TOP, 232.5, 356, { lineSpacingMultiple: 1.1, objectName: "Takeaways" });
  offsets.forEach((o, i) => marker(s, i + 1, 666, TOP + o));
};
// A coloured circle holding a white glyph, the icon style from slide 2.
const iconDot = (s, name, colour, x, y, d = 30) => {
  s.addShape(pres.ShapeType.ellipse, { ...box(x, y, d, d), fill: { color: colour }, line: { color: colour, width: 0.5 } });
  s.addImage({ path: `slides/assets/glyph-${name}.png`, ...box(x + d * 0.17, y + d * 0.17, d * 0.66, d * 0.66), altText: "" });
};
const slide = (label, title, subtitle, notes, section) => {
  const s = pres.addSlide({ masterName: "LIGHT", sectionTitle: section });
  const [main, sub] = label.split(" > ");
  s.addText(sub ? [{ text: main }, { text: ` > ${sub}`, options: { color: MUTED } }] : main, { placeholder: "label" });
  s.addText(title, { placeholder: "title" });
  s.addText(subtitle, { placeholder: "subtitle" });
  s.addNotes(notes);
  return s;
};
const dark = (title, notes, section) => {
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addNotes(notes);
  card(s, "", 656, 126, 250, 288);
  s.addImage({ path: "slides/assets/qr.png", ...box(681, 142, 200, 200), altText: "QR code to the live demo" });
  text(s, "Scan to try the live demo", 666, 354, 230, 24, { fontSize: 12, bold: true, align: "center" });
  return s;
};

const OPEN = "Opening", PROBLEM = "01 Problem", SOLUTION = "02 Solution", EVIDENCE = "03 Evidence", BUILD = "04 Build and limits", CLOSE = "Close";
[OPEN, PROBLEM, SOLUTION, EVIDENCE, BUILD, CLOSE].forEach((title) => pres.addSection({ title }));

// The four feature colours from DESIGN.md: tint, deep.
const G = ["E3EFE6", GREEN], T = ["FBE4DC", TOMATO], A = [TINT_WARN, WARN], K = ["DDE3DA", INK];
// Like takeaways, but placed anywhere; bodies stay one text box.
const notes = (s, items, offsets, x, y, w, h) => {
  const runs = [];
  items.forEach(([hd, b], i) => {
    runs.push({ text: hd, options: { bold: true, breakLine: true, paraSpaceBefore: i ? 12 : 0, paraSpaceAfter: 4 } });
    runs.push({ text: b, options: { color: MUTED, breakLine: i < items.length - 1 } });
  });
  text(s, runs, x, y, w, h, { lineSpacingMultiple: 1.1, objectName: "Takeaways" });
  offsets.forEach((o, i) => marker(s, i + 1, x - 18, y + o));
};
const bar = (s, x, y, w, h, fill, label, colour = WHITE) => s.addText(label || "", {
  shape: pres.ShapeType.rect, ...box(x, y, w, h), fill: { color: fill }, line: { color: fill, width: 0.5 }, color: colour, fontSize: 12, bold: true, margin: 8, valign: "middle",
});

// A paper tag marks pending work; ids match docs/showcase/pending-tasks.md.
// Delete every object named "Pending" before release.
const pend = (s, id, x, y) => {
  s.addShape(pres.ShapeType.roundRect, { ...box(x, y, 66, 16), rectRadius: pt(4), fill: { color: WARN }, line: { color: WHITE, width: 0.75 }, objectName: `Pending ${id}` });
  s.addImage({ path: "slides/assets/glyph-description.png", ...box(x + 3, y + 2, 12, 12), altText: `Pending task ${id}`, objectName: `Pending ${id} icon` });
  text(s, `${id} pending`, x + 17, y, 48, 16, { fontSize: 8, bold: true, color: WHITE, valign: "middle", objectName: `Pending ${id} label` });
};

// 1 — cover
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: OPEN });
  s.addText("What should I eat tonight?", { placeholder: "title" });
  s.addNotes("Everyone asks this question, so that's where this project starts.\n\n[Point: search bar]\nYou type a craving.\n\n[Point: plate labels]\nYou get one meal sized to you, and each ingredient says where its number came from.\n\n[Point: shopping list]\nThe shopping list is already written.\n\nThe rest of this deck shows how it works and how I measured it.\n\nReference — not read aloud\nValues are the real local run of 6 November 2026: slides/captures/2026-11-06-plan.json. The plate is an illustration, slides/build_cover_art.py.");
  s.addImage({ path: "slides/assets/cover-art.png", ...box(0, 0, 960, 540), altText: "Illustration of chicken fried rice on a plate, seen from above" });
  s.addImage({ path: "slides/assets/mark-dark.png", ...box(X0, 34, 28, 28), altText: "AI Meal Planner logo" });
  text(s, "AI Meal Planner", 80, 36, 240, 24, { fontSize: 16, bold: true, color: WHITE, valign: "middle" });
  s.addText([{ text: "chicken fried rice", options: { color: INK } }, { text: "|", options: { color: TOMATO } }], {
    shape: pres.ShapeType.roundRect, rectRadius: pt(25), ...box(X0, 262, 300, 50), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, fontSize: 18, margin: 14, valign: "middle",
  });
  text(s, "One meal sized to you, each ingredient's source shown, the shopping list ready.", X0, 328, 280, 44, { fontSize: 14, color: ON_INK });
  const callout = (x1, y1, x2, y2, flipV) => {
    const geo = { ...box(Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1)), flipV };
    s.addShape(pres.ShapeType.line, { ...geo, line: { color: INK, width: 3 } });
    s.addShape(pres.ShapeType.line, { ...geo, line: { color: WHITE, width: 1.25 } });
    s.addShape(pres.ShapeType.ellipse, { ...box(x1 - 5.5, y1 - 5.5, 11, 11), fill: { color: WHITE }, line: { color: INK, width: 1.5 } });
  };
  callout(560, 215, 508, 118, false);
  callout(530, 400, 420, 476, true);
  callout(690, 420, 800, 470, false);
  const tag = (a, b, x, y, align) =>
    text(s, [{ text: a, options: { fontSize: 12, bold: true, color: WHITE, breakLine: true } }, { text: b, options: { fontSize: 10, color: ON_INK } }], x, y, 160, 34, { align });
  tag("Chicken breast, 100 g", "Estimated", 342, 86, "right");
  tag("Cooked rice, 220 g", "Estimated", 256, 464, "right");
  tag("Vegetables, 115 g", "Reference", 806, 456, "left");
  s.addText("694 kcal, target 691", { shape: pres.ShapeType.roundRect, rectRadius: pt(14), ...box(540, 84, 150, 28), fill: { color: GREEN }, line: { color: GREEN, width: 1 }, color: WHITE, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
  const row = (a, b) => a + " ".repeat(23 - a.length - b.length) + b;
  const items = [["CHICKEN BREAST", "$7.80"], ["COOKED RICE", "$3.20"], ["WHOLE EGG", "$3.50"], ["VEGETABLES", "$3.50"], ["SESAME OIL", "$3.50"], ["SOY SAUCE", "$3.00"]];
  s.addText([
    { text: "SHOPPING LIST", options: { bold: true, fontSize: 12, breakLine: true, paraSpaceAfter: 8 } },
    ...items.map(([a, b]) => ({ text: row(a, b), options: { breakLine: true, paraSpaceAfter: 5 } })),
    { text: "-".repeat(23), options: { breakLine: true, paraSpaceAfter: 5 } },
    { text: row("ESTIMATED", "$24.50"), options: { bold: true } },
  ], { shape: pres.ShapeType.rect, ...box(748, 60, 182, 218), rotate: 3, fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: INK, fontFace: MONO, fontSize: 10, margin: 14, valign: "top", objectName: "Shopping list" });
  s.addShape(pres.ShapeType.roundRect, { ...box(X0, 404, 84, 84), rectRadius: pt(8), fill: { color: WHITE }, line: { color: WHITE, width: 1 } });
  s.addImage({ path: "slides/assets/qr.png", ...box(X0 + 6, 410, 72, 72), altText: "QR code to the live demo" });
  text(s, [{ text: "Try the live demo", options: { fontSize: 12, bold: true, color: WHITE, breakLine: true } }, { text: "Scan with your phone", options: { fontSize: 10, color: ON_INK } }], 139, 428, 110, 36);
  pend(s, "P1", 139, 466);
}

// 2 — executive summary
{
  const s = slide("EXECUTIVE SUMMARY", "One craving, sized to four different people", "Four agents and 34 curated recipes size the same chicken fried rice for each person, with no LLM key needed.",
    "If you read one slide, read this one.\n\n[Point: four plates]\nThis is the same craving for four people. It runs from 363 kcal for an older woman losing weight to 850 for a large athlete gaining, so the meal fits the person. Meal targets stay within 350 to 850 kcal, so the first and last plates sit at those limits.\n\n[Point: 72 of 72]\nThat quality is measured: all 72 plans in the project's own benchmark meet the targets, up from 10.\n\n[Point: Balanced and checked]\nFour features do that work, and it stays honest: estimates are labelled, and it says so when nothing matches.\n\nThe rest of the deck shows how it works and how that number was reached.\n\nReference — not read aloud\ndocs/meal_quality/baseline.json, chicken fried rice rows; fact sheet, docs/showcase/README.md; docs/7_meal_quality.md §2. These are a measure of plans, not of real users.", OPEN);
  // Row 1: the proof of "sized to you". Plate area is to scale with calories.
  card(s, "", X0, TOP, W, 140, { fill: INK });
  s.addImage({ path: "slides/assets/bg-band.png", ...box(X0, TOP, W, 140), altText: "" });
  const scale = 112 / Math.sqrt(850), art = (2 * 232 + 32) / (2 * 232); // plate.png has a small margin around the plate
  [[363, 26, "Older woman,", "losing weight"], [694, 48, "Active woman,", "maintaining"], [809, 60, "Average man,", "maintaining"], [850, 63, "Large athlete,", "gaining"]].forEach(([kcal, protein, a, b], i) => {
    const x = X0 + 10 + i * 218, cy = TOP + 70, cx = x + 62, d = Math.sqrt(kcal) * scale * art;
    s.addImage({ path: `slides/assets/plate-${kcal}.png`, ...box(cx - d / 2, cy - d / 2, d, d), altText: `Plate of chicken fried rice, ${kcal} kcal` });
    text(s, [
      { text: `${kcal} kcal`, options: { fontSize: 16, bold: true, color: WHITE, breakLine: true, paraSpaceAfter: 2 } },
      { text: `${protein} g protein`, options: { fontSize: 10, bold: true, color: WHITE, breakLine: true, paraSpaceAfter: 2 } },
      { text: a, options: { fontSize: 10, color: ON_INK, breakLine: true } },
      { text: b, options: { fontSize: 10, color: ON_INK } },
    ], x + 126, TOP + 30, 90, 80, { valign: "middle" });
  });
  // Row 2: the key features, in Garden green colours. Row 3: the number that proves each one.
  [
    ["person", "E3EFE6", GREEN, "Sized to you", [["Your body, a trained exercise model and your goal set a "], ["daily budget", 1], [", then this "], ["meal's target", 1], ["."]], "0.4%", "median gap to the meal target, worst 9.9%"],
    ["health_and_safety", "FBE4DC", TOMATO, "Fits your limits", [["Allergies, diets and health conditions "], ["rule out recipes or swap ingredients", 1], [" before a meal is picked."]], "5 of 5", "guardrail cases hold, including refusals"],
    ["balance", TINT_WARN, WARN, "Balanced and checked", [["Portions are resized toward "], ["target macro ranges", 1], [", and each ingredient "], ["shows its source", 1], ["."]], "72 of 72", "benchmark plans on target, up from 10"],
    ["shopping_basket", "DDE3DA", INK, "Ready to shop", [["Ingredients map to store items or category prices, with an "], ["estimated total", 1], ["."]], "$24.50", "estimated basket, not a cost per meal"],
  ].forEach(([icon, tint, deep, h, body, v, l], i) => {
    const x = X0 + i * 223, y = 282;
    card(s, "", x, y, 204, 142, { fill: tint });
    text(s, [
      { text: h, options: { fontFace: HEAD, fontSize: 16, bold: true, color: deep, breakLine: true, paraSpaceAfter: 4 } },
      ...body.map(([t, key]) => ({ text: t, options: { fontSize: 12, color: key ? deep : INK, bold: !!key } })),
    ], x + 12, y + 48, 184, 90);
    s.addShape(pres.ShapeType.ellipse, { ...box(x + 12, y + 12, 30, 30), fill: { color: deep }, line: { color: deep, width: 0.5 } });
    s.addImage({ path: `slides/assets/glyph-${icon}.png`, ...box(x + 17, y + 17, 20, 20), altText: "" });
    text(s, [{ text: v, options: { fontSize: 24, bold: true, color: deep, breakLine: true } }, { text: l, options: { fontSize: 10, color: MUTED } }], x + 12, 432, 192, 46);
  });
  pend(s, "P8", X0 + 3 * 223 + 134, 436);
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "the project's own offline test, not real users. 11 of the 72 are fallback meals; guardrails use a controlled recipe set. Meal targets stay within 350–850 kcal. Plate area shows calories." }], X0, 482, W, 14, { fontSize: 8, color: MUTED });
}

// 3 — agenda
{
  const s = slide("AGENDA", "Today's menu: four courses, from the problem to the limits", "Each course lists its pages by label. Select one to jump to it.",
    "This deck is served as a four-course menu.\n\n[Point: Starter]\nFirst, why this is worth solving.\n\n[Point: Main]\nThen what it does and how it works.\n\n[Point: Taste test]\nThen what a good meal means, and whether it got there.\n\n[Point: The bill]\nLast, how it's built, what isn't proven yet and what's still pending.\n\nEach page is a link, so you can jump straight to it.", OPEN);
  s.addImage({ path: "slides/assets/plate-salmon.png", ...box(668, 196, 248, 248), altText: "Plate of salmon and quinoa" });
  let y = TOP;
  [
    ["soup_kitchen", "E3EFE6", GREEN, "STARTER", "Problem", "Why is this worth solving?", [["Why it matters", 4]], 56],
    ["lunch_dining", "FBE4DC", TOMATO, "MAIN", "Solution", "What does it do, and how?", [["The flow", 5], ["Four agents", 6], ["Calorie target", 7], ["Choosing the meal", 8], ["Nutrition", 9]], 104],
    ["restaurant", TINT_WARN, WARN, "TASTE TEST", "Evidence", "Did we get there?", [["What good means", 10], ["Results", 11]], 62],
    ["receipt_long", "DDE3DA", INK, "THE BILL", "Build and limits", "What is unproven?", [["Architecture", 12], ["Engineering", 13], ["Limits", 14], ["Pending tasks", 15]], 104],
  ].forEach(([icon, tint, deep, course, h, q, pages, ch]) => {
    card(s, "", X0, y, 608, ch, { fill: tint });
    s.addShape(pres.ShapeType.ellipse, { ...box(X0 + 14, y + ch / 2 - 17, 34, 34), fill: { color: deep }, line: { color: deep, width: 0.5 } });
    s.addImage({ path: `slides/assets/glyph-${icon}.png`, ...box(X0 + 20, y + ch / 2 - 11, 22, 22), altText: "" });
    text(s, [
      { text: course, options: { fontSize: 10, bold: true, color: deep, breakLine: true } },
      { text: h, options: { fontSize: 16, bold: true, color: deep, breakLine: true } },
      { text: q, options: { fontSize: 10, color: deep } },
    ], X0 + 60, y + 4, 200, ch - 8, { valign: "middle" });
    const rowH = 19, y0 = y + (ch - pages.length * rowH) / 2;
    pages.forEach(([label, page], k) => {
      const ry = y0 + k * rowH;
      text(s, [{ text: label, options: { hyperlink: { slide: page }, color: deep } }], X0 + 268, ry, 130, rowH, { valign: "middle" });
      s.addShape(pres.ShapeType.line, { ...box(X0 + 400, ry + 13, 160, 0), line: { color: deep, width: 1, dashType: "sysDot" } });
      text(s, [{ text: String(page), options: { hyperlink: { slide: page }, color: deep, bold: true } }], X0 + 564, ry, 30, rowH, { align: "right", valign: "middle" });
    });
    y += ch + 8;
  });
}

// 4 — problem
{
  const s = slide("PROBLEM > WHY IT MATTERS", "Picking a meal is easy; sizing it to you is not", "Three questions sit between a craving and a meal you can trust.",
    "Most of us know what we feel like eating. The hard part comes after that.\n\n[Point: How much?]\nThe right amount depends on the person. Across the four benchmark profiles, daily budgets run from 1,200 to 4,521 kcal.\n\n[Point: Is it right for me?]\nThe same request changes with your limits. A vegan gets a different recipe, and a coeliac keeps the recipe with gluten-free pasta.\n\n[Point: What do I buy?]\nThis one pasta means five ingredients to find and price.\n\n[Point: Today, With the app]\nEach question has a manual habit today, and each card shows what the app does in its place.\n\nThe next section shows how one request answers all three.\n\nReference — not read aloud\nThe three questions and the Today lines are the project's framing, from docs/1_brief.md, not research findings. Budgets: docs/meal_quality/baseline.json. Pasta examples: a local run of the craving \"pasta\" for the average man, 7 November 2026, no provider keys.", PROBLEM);
  card(s, "", X0, TOP, 608, 78, { fill: INK });
  s.addImage({ path: "slides/assets/plate-pasta.png", ...box(X0 + 12, TOP + 6, 66, 66), altText: "Plate of tomato turkey pasta" });
  s.addText("I feel like pasta tonight.", { shape: pres.ShapeType.wedgeRoundRectCallout, ...box(X0 + 90, TOP + 16, 226, 42), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: INK, fontSize: 14, bold: true, align: "center", valign: "middle", margin: 4 });
  text(s, "One request answers all three.", X0 + 336, TOP, 260, 78, { fontSize: 14, bold: true, color: WHITE, valign: "middle" });
  [
    ["monitor_weight", G, "How much?", "Daily budgets in our benchmark run from 1,200 to 4,521 kcal.", "Guess from \"serves 4\"", "A budget, then a meal target"],
    ["no_food", T, "Is it right for me?", "Asked for pasta, a vegan gets lentil bolognese and a coeliac gets gluten-free pasta.", "Read every label", "Conflicts ruled out or swapped first"],
    ["shopping_cart", A, "What do I buy?", "This one pasta means five ingredients to find and price.", "Write a list, guess the cost", "A list with an estimated total"],
  ].forEach(([icon, [tint, deep], h, b, before, after], i) => {
    const y = 216 + i * 90;
    card(s, "", X0, y, 608, 84, { fill: tint });
    iconDot(s, icon, deep, X0 + 10, y + 27, 30);
    text(s, [{ text: h, options: { fontSize: 14, bold: true, color: deep, breakLine: true, paraSpaceAfter: 2 } }, { text: b, options: { color: deep } }], X0 + 50, y + 4, 240, 76, { valign: "middle" });
    const chip2 = (x, w, label, v, fill, colour) => s.addText([
      { text: label, options: { fontSize: 8, bold: true, color: colour, breakLine: true, paraSpaceAfter: 2 } },
      { text: v, options: { fontSize: 11, bold: true, color: colour } },
    ], { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x, y + 8, w, 68), fill: { color: fill }, line: { color: fill === WHITE ? deep : fill, width: 1 }, margin: 6, valign: "middle" });
    chip2(X0 + 298, 136, "TODAY", before, WHITE, deep);
    arrow(s, X0 + 435, y + 42, X0 + 450, y + 42);
    chip2(X0 + 451, 150, "WITH THE APP", after, deep, WHITE);
  });
  marker(s, 1, X0 + 590, 220);
  marker(s, 2, X0 + 590, 310);
  takeaways(s, [["The range is almost fourfold", "The largest daily budget is 3.8 times the smallest, so one recipe size can't fit everyone."], ["Limits change the meal itself", "Portions aren't enough. A limit can change the recipe or swap an ingredient."], ["Today is our framing", "The Today chips describe the problem as this project sees it. They aren't survey results."]], [2, 90, 164]);
}

// 5 — flow
{
  const s = slide("SOLUTION > THE FLOW", "One craving in, one meal and a shopping list out", "Three steps in the React app.",
    "This is the real React app, in three steps.\n\n[Point: You]\nYou enter your body, goal and anything to avoid.\n\n[Point: Craving]\nYou say what you feel like eating and where you shop.\n\n[Point: Your plan]\nYou get one meal, its balance, each ingredient's source and a shopping list. The badges say how it matched and what is estimated.\n\nNext, what happens behind these screens.\n\nReference — not read aloud\nCaptured 6 November 2026 from a local run with no provider keys: slides/captures/2026-11-06-plan.json. frontend/src/features/flow/MealFlow.jsx.", SOLUTION);
  [
    ["1-profile", "person", G, "1. You", "Goal, body details, activity and anything to avoid.", "34, male, 165 cm, 65 kg"],
    ["2-craving", "search", T, "2. Craving", "Say what you feel like eating and where you shop.", "chicken fried rice"],
    ["3-plan", "rice_bowl", A, "3. Your plan", "One meal, its balance, each ingredient's source and a shopping list.", "694 kcal, target 691"],
  ].forEach(([f, icon, [tint, deep], h, b, ex], i) => {
    const x = X0 + i * 209;
    card(s, "", x, TOP, 190, 336, { fill: tint });
    s.addImage({ path: `slides/captures/2026-11-06-${f}.jpg`, ...box(x + 10, TOP + 10, 170, 119), altText: `${h} screen of the React app` });
    s.addShape(pres.ShapeType.rect, { ...box(x + 10, TOP + 10, 170, 119), fill: { color: WHITE, transparency: 100 }, line: { color: LINE, width: 1 } });
    iconDot(s, icon, deep, x + 12, TOP + 142, 30);
    text(s, hb(h, b, { hc: deep, bc: deep }), x + 12, TOP + 180, 168, 104);
    s.addText(ex, { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x + 10, TOP + 294, 170, 30), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: deep, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
    if (i < 2) arrow(s, x + 191, TOP + 70, x + 208, TOP + 70);
  });
  marker(s, 1, X0 + 170, TOP + 146);
  marker(s, 2, X0 + 418 + 170, TOP + 146);
  caption(s, 1, "Real captures of the React app, run locally with no provider keys, 6 November 2026.", X0, 472, 608);
  takeaways(s, [["Two screens, then a result", "Everything the planner needs fits on the first two steps, then the result is one page."], ["The plan shows its working", "Balance, ingredient sources and estimates sit on the result page, not behind a menu."]], [2, 74]);
}

// 6 — agents
{
  const s = slide("SOLUTION > FOUR AGENTS", "Four agents work like one kitchen", "An order comes in, each station does one job, and a planning service runs them in order.",
    "Behind the screens is a FastAPI service, and it works like a kitchen.\n\n[Point: The portion planner]\nThe calorie agent sets a daily budget.\n\n[Point: The chef]\nThe recommendation agent sets the meal target, excludes conflicting meals and picks a relevant recipe.\n\n[Point: The taster]\nThe nutrition agent looks up each ingredient and labels estimates.\n\n[Point: The shopper]\nThe supermarket agent matches ingredients to store items or category prices, with an estimated total.\n\n[Point: white labels]\nThe white labels follow one real order: a 2,469 kcal budget, a 691 kcal target, 694 kcal served and a $24.50 estimated basket.\n\nThe meal comes from retrieval, not generation, so the core path needs no LLM key.\n\nReference — not read aloud\ndocs/2_architecture.md; docs/agents/; MealPlanningService. The kitchen roles are a metaphor for the agents.", SOLUTION);
  s.addText([{ text: "ORDER  ", options: { bold: true } }, { text: "chicken fried rice, active woman, maintaining" }], { shape: pres.ShapeType.rect, ...box(X0, TOP, 608, 30), fill: { color: WHITE }, line: { color: INK, width: 1, dashType: "dash" }, color: INK, fontFace: MONO, fontSize: 12, margin: 10, valign: "middle" });
  [
    [1, "scale", G, "THE PORTION PLANNER", "Calorie expenditure", "Estimates what you burn in a day and sets your budget.", "2,469 kcal budget", X0, 168],
    [2, "pan", T, "THE CHEF", "Meal recommendation", "Sets the meal target, rules out conflicts, picks a recipe and sizes it.", "691 kcal target", X0 + 313, 168],
    [3, "taster", A, "THE TASTER", "Nutrition verification", "Looks up each ingredient and labels what is estimated.", "694 kcal, 3 of 6 estimated", X0 + 313, 298],
    [4, "basket", K, "THE SHOPPER", "Supermarket", "Matches ingredients to store items or category prices.", "$24.50 estimated", X0, 298],
  ].forEach(([n, art, [tint, deep], role, h, b, out, x, y]) => {
    card(s, "", x, y, 295, 120, { fill: tint });
    s.addImage({ path: `slides/assets/station-${art}.png`, ...box(x + 8, y + 12, 104, 52), altText: `Illustration for ${role.toLowerCase()}` });
    s.addText(out, { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x + 8, y + 72, 104, 38), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: deep, fontSize: 10, bold: true, align: "center", valign: "middle", margin: 2 });
    text(s, [
      { text: role, options: { fontSize: 10, bold: true, color: deep, breakLine: true } },
      { text: h, options: { fontSize: 14, bold: true, color: deep, breakLine: true, paraSpaceAfter: 2 } },
      { text: b, options: { color: deep } },
    ], x + 120, y + 8, 168, 106);
    chip(s, n, x + 266, y + 6);
  });
  arrow(s, X0 + 296, 228, X0 + 312, 228);
  arrow(s, X0 + 460, 289, X0 + 460, 297);
  s.addShape(pres.ShapeType.line, { ...box(X0 + 296, 358, 16, 0), line: { color: MUTED, width: 1, beginArrowType: "triangle" } });
  arrow(s, X0 + 146, 419, X0 + 146, 427);
  card(s, [{ text: "One typed JSON response: meal, nutrition, shopping list and warnings", options: { fontFace: HEAD, fontSize: 12, bold: true, color: WHITE } }], X0, 428, 608, 32, { fill: INK, margin: 12, valign: "middle" });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "white labels show the active woman's real plan. The service balances portions after verification." }], X0, 468, 608, 14, { fontSize: 8, color: MUTED });
  marker(s, 1, X0 + 250, 172);
  marker(s, 2, X0 + 563, 172);
  takeaways(s, [["One job per station", "Each agent does a single task, so it can be tested and changed on its own."], ["Retrieval, not generation", "Meals come from 34 curated recipes, so the core path needs no LLM key, and offline the same request gives the same plan."]], [2, 74]);
}

// 7 — calorie target
{
  const s = slide("SOLUTION > CALORIE TARGET", "From your body to a meal target", "Worked example: an active woman who is keeping her weight gets a 691 kcal target for this meal.",
    "How does it decide how much? It's a short calculation, and this follows one real person through it.\n\n[Point: Body and activity]\nBody size and activity give about 2,344 kcal a day.\n\n[Point: Exercise]\nThe trained model adds 125 kcal of exercise.\n\n[Point: Goal]\nHer goal is to maintain, so nothing changes, and her budget is 2,469 kcal.\n\n[Point: This meal]\nOne meal gets 28% of that, which is 691 kcal.\n\n[Point: Bars]\nThe bars show how small the model's share is. Its high score is for exercise calories only, and in these plans it adds about 110 to 140 kcal.\n\nThe exercise inputs are defaults, and the activity multiplier may already count that exercise.\n\nReference — not read aloud\nLocal run, 7 November 2026: expenditure less BMR × activity is 142, 115, 125 and 108 kcal across the four profiles, 3–10% of expenditure. metrics.json; calorie_expenditure_agent.py; meal_recommendation_agent.py; DEC-24; docs/8_design.md §3.1. The 28% share is a design choice.", SOLUTION);
  [
    ["person", G, "Body and activity", "Size and activity give a daily estimate.", "2,344 kcal"],
    ["fitness_center", T, "Exercise", "A trained model adds exercise calories.", "+125 kcal"],
    ["flag", A, "Goal", "Gain +250, lose −400, with a floor.", "2,469 kcal"],
    ["rice_bowl", K, "This meal", "28% of the budget, within 350–850 kcal.", "691 kcal"],
  ].forEach(([icon, [tint, deep], h, b, out], i) => {
    const x = X0 + i * 156;
    card(s, "", x, TOP, 140, 136, { fill: tint });
    iconDot(s, icon, deep, x + 8, TOP + 8, 26);
    text(s, h, x + 40, TOP + 6, 96, 30, { bold: true, color: deep, valign: "middle" });
    text(s, b, x + 10, TOP + 40, 124, 52, { color: deep });
    s.addText(out, { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x + 10, TOP + 102, 120, 26), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: deep, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
    if (i < 3) arrow(s, x + 141, TOP + 68, x + 155, TOP + 68);
  });
  marker(s, 2, X0 + 312 + 124, TOP + 4);
  marker(s, 3, X0 + 468 + 124, TOP + 4);
  pend(s, "P5", X0 + 156 + 68, TOP + 84);
  card(s, "", X0, 276, 608, 186);
  text(s, "Her day and this meal, on one scale", X0 + 16, 286, 400, 18, { bold: true });
  const x0 = X0 + 16, k = 576 / 2469.2, w1 = 2344.3 * k, w2 = 124.9 * k;
  text(s, "Daily budget: 2,469 kcal", x0, 310, 300, 16, { color: MUTED });
  text(s, "+125 kcal from the model", x0 + 300, 310, 276, 16, { color: TOMATO, bold: true, align: "right" });
  bar(s, x0, 328, w1, 30, GREEN, "2,344 kcal from body and activity");
  bar(s, x0 + w1, 328, w2, 30, TOMATO);
  marker(s, 1, x0 + 562, 363);
  text(s, "This meal: 28% of the day", x0, 380, 300, 16, { color: MUTED });
  bar(s, x0, 398, 691.3 * k, 30, INK, "691 kcal");
  text(s, "Scale: full width is 2,469 kcal.", x0, 438, 400, 14, { fontSize: 9, color: MUTED });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "in the meal flow, exercise inputs use defaults (30 minutes, 100 bpm), and the activity multiplier may already count that exercise." }], X0, 468, 608, 14, { fontSize: 8, color: MUTED });
  takeaways(s, [["The model is a small part", "It adds about 110–140 kcal in these plans, 3–10% of the day. Its R² of 0.996 and 2.2 kcal error describe exercise calories only."], ["A floor protects low budgets", "Weight-loss budgets stop at 1,200 kcal for women and 1,500 for men. One test profile would otherwise get 986 kcal."], ["28% is a design choice", "It keeps meals in proportion, but the cap holds a large athlete's meal to 19% of the day."]], [2, 91, 180]);
}

// 8 — choosing the meal
{
  const s = slide("SOLUTION > CHOOSING THE MEAL", "Hard limits first, then a relevant recipe", "A vegan asks for chicken fried rice: the recipes narrow down to one, and the app ends in one of three ways.",
    "This is how it picks the meal, using one real request.\n\n[Point: Funnel]\nA vegan asks for chicken fried rice. Of 34 recipes, 13 are safe, 5 are relevant to the craving, and one is served: Tofu Fried Rice.\n\nSafety comes first, so a recipe can't win on relevance alone. Limits can also swap an ingredient rather than drop the recipe.\n\n[Point: Outcomes]\nThere are three possible endings: a close match, a standard meal with a note, or a refusal.\n\nReference — not read aloud\nLocal run, 7 November 2026: backend/app/rag/retriever.py, TF-IDF at 34 recipes, relevance threshold 0.16. DEC-27. Counts: docs/meal_quality/baseline.json. Refusals come from the guardrail cases, on a controlled recipe set; none of the 72 plans was refused.", SOLUTION);
  card(s, "", X0, TOP, 608, 170);
  text(s, "Recipes left at each step", X0 + 16, TOP + 10, 400, 18, { bold: true });
  const k = 11;
  [["All recipes", 34, BASELINE, "34"], ["Safe for a vegan", 13, TOMATO, "13"], ["Relevant to the craving", 5, WARN, "5"], ["Served", 1, GREEN, "1: Tofu Fried Rice"]].forEach(([l, n, c, v], i) => {
    const y = TOP + 36 + i * 32;
    text(s, l, X0 + 16, y, 148, 24, { valign: "middle" });
    bar(s, X0 + 168, y, n * k, 24, c);
    text(s, v, X0 + 168 + n * k + 8, y, 150, 24, { fontSize: 12, bold: true, color: c === BASELINE ? MUTED : c, valign: "middle" });
  });
  marker(s, 1, X0 + 168 + 13 * k + 34, TOP + 74);
  [
    ["check_circle", G, "Close match", "“chicken fried rice” gets that recipe, sized to you.", "61 of 72", "benchmark plans"],
    ["flag", A, "No close match", "“pizza” gets a standard meal and a note saying so.", "11 of 72", "benchmark plans"],
    ["block", K, "Nothing safe", "Too many limits: the plan is refused, not guessed.", "2 of 5", "guardrail cases"],
  ].forEach(([icon, [tint, deep], h, b, v, l], i) => {
    const x = X0 + i * 208, y = 310;
    card(s, "", x, y, 192, 154, { fill: tint });
    iconDot(s, icon, deep, x + 12, y + 10, 28);
    text(s, h, x + 48, y + 10, 140, 28, { fontSize: 14, bold: true, color: deep, valign: "middle" });
    text(s, b, x + 12, y + 44, 170, 52, { color: deep });
    text(s, [{ text: v, options: { fontSize: 16, bold: true, color: deep, breakLine: true } }, { text: l, options: { fontSize: 10, color: deep } }], x + 12, y + 104, 170, 42);
  });
  marker(s, 2, X0 + 208 + 174, 316);
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "refusals were tested on a controlled recipe set. None of the 72 benchmark plans was refused." }], X0, 470, 608, 14, { fontSize: 8, color: MUTED });
  notes(s, [["Safety comes before taste", "A recipe that breaks a limit is out, or adapted with a safe swap, before relevance counts."], ["Relevance decides what qualifies", "An off-menu craving falls back with a warning. Your profile only changes the order."]], [2, 80], 684, TOP, 232.5, 170);
  card(s, "", 684, 310, 232.5, 154, { fill: "FBE4DC" });
  iconDot(s, "health_and_safety", TOMATO, 696, 320, 28);
  text(s, "Or a safe swap", 732, 320, 180, 28, { fontSize: 14, bold: true, color: TOMATO, valign: "middle" });
  text(s, "A coeliac who asks for pasta keeps the recipe, made with gluten-free pasta. A limit doesn't always cost you the meal.", 696, 354, 208, 100, { color: TOMATO });
  pend(s, "P6", 696, 440);
}

// 9 — nutrition
{
  const s = slide("SOLUTION > NUTRITION", "Each ingredient is looked up, and estimates are labelled", "Example: chicken fried rice from a real local run, with no USDA or FatSecret keys.",
    "Can you trust the numbers? Each one shows where it came from.\n\n[Point: Source column]\nThis is a real plan. Three of its six ingredients are estimates, and the app says so.\n\n[Point: Stacked bar]\nThose three carry about two thirds of the calories, because chicken and rice are the biggest items.\n\n[Point: Lookup order]\nA trusted local reference comes first. Otherwise it tries USDA and then FatSecret, if keys are set, and last a local or category estimate.\n\nA reference value isn't an external verification either, so the plan's totals are approximate.\n\nReference — not read aloud\nbackend/app/agents/nutrition_verification_agent.py. Local run, 7 November 2026: 459 kcal estimated, 235 kcal reference, 694 kcal in all, against a 691 kcal target.", SOLUTION);
  const cell = (t, o) => ({ text: t, options: o || {} });
  const badge = (ok) => cell(ok ? "Reference" : "Estimated", { color: ok ? GREEN : WARN, bold: true, fill: { color: ok ? "E3EFE6" : TINT_WARN } });
  const right = { align: "right" };
  const rows = [
    [cell("Ingredient", { bold: true }), cell("Amount", { bold: true, ...right }), cell("kcal", { bold: true, ...right }), cell("Source", { bold: true })],
    ...[["Chicken breast", "100 g", "165", 0], ["Cooked rice", "220 g", "286", 0], ["Whole egg", "50 g", "72", 1], ["Vegetables", "115 g", "75", 1], ["Soy sauce", "15 g", "8", 0], ["Sesame oil", "10 g", "88", 1]].map(([n, a, c, ok]) => [cell(n), cell(a, right), cell(c, right), badge(ok)]),
  ];
  card(s, "", X0, TOP, 322, 276);
  s.addTable(rows, { ...box(X0 + 8, TOP + 12, 306, 252), colW: [pt(106), pt(66), pt(44), pt(90)], rowH: pt(36), fontSize: 12, color: INK, fontFace: HEAD, valign: "middle", border: { type: "none" } });
  caption(s, 1, "A real plan: 694 kcal against a 691 kcal meal target.", X0, 414, 322);
  const rx = 382, rw = 269.5, kk = rw / 693.6;
  text(s, "Where the 694 kcal come from", rx, TOP, rw, 18, { bold: true });
  bar(s, rx, TOP + 22, 458.9 * kk, 32, WARN, "459 estimated");
  bar(s, rx + 458.9 * kk, TOP + 22, 234.7 * kk, 32, GREEN, "235");
  text(s, "66% estimated, 34% reference", rx, TOP + 58, rw, 14, { fontSize: 10, color: MUTED });
  marker(s, 1, rx + rw - 12, TOP + 2);
  text(s, "Lookup order", rx, 212, rw, 18, { bold: true });
  [["verified", G, "1. Trusted local reference"], ["search", T, "2. USDA, then FatSecret, if keys are set"], ["calculate", A, "3. Local or category estimate"]].forEach(([icon, [tint, deep], t], i) => {
    const y = 234 + i * 62;
    card(s, "", rx, y, rw, 50, { fill: tint });
    iconDot(s, icon, deep, rx + 10, y + 12, 26);
    text(s, t, rx + 44, y, rw - 52, 50, { color: deep, valign: "middle" });
    if (i < 2) arrow(s, rx + 134, y + 51, rx + 134, y + 61);
  });
  marker(s, 2, rx + rw - 16, 300);
  pend(s, "P4", rx + rw - 72, 340);
  takeaways(s, [["Estimates carry 66% of the calories", "Only 3 of 6 ingredients are estimates, but they include chicken and rice, the biggest items."], ["Reference still means local", "With no provider keys, a plan's target check isn't an independent verification."]], [2, 90]);
}

// 10 — what good means
{
  const s = slide("EVIDENCE > WHAT GOOD MEANS", "We defined a good meal before improving one", "A plan passes only if it clears both tests, on a fixed set of 72 requests run offline.",
    "Before changing anything, I fixed what good means. A plan has to clear two tests.\n\n[Point: Within 10%]\nFirst, calories have to land within 10% of the meal's target.\n\n[Point: Macro bands]\nSecond, each macro has to sit inside the adult AMDR range, as a share of the meal's energy. The dots show one real plan.\n\n[Point: 72 requests]\nIt runs on the same 72 requests every time, so results can be compared.\n\nOne limit: AMDR is a daily reference, applied here to one meal.\n\nReference — not read aloud\ndocs/7_meal_quality.md §1; DEC-25. Example plan: docs/meal_quality/baseline.json, 28/46/26%.", EVIDENCE);
  card(s, "", X0, TOP, 352, 300);
  text(s, [{ text: "Test 2  ", options: { bold: true, color: TOMATO } }, { text: "Share of the meal's energy" }], X0 + 14, TOP + 14, 330, 22, { fontFace: HEAD, fontSize: 14, bold: true });
  const bx = X0 + 14, bw = 324;
  [["Protein", 10, 35, C.accent3, 28], ["Carbs", 45, 65, C.accent4, 46], ["Fat", 20, 35, C.accent5, 26]].forEach(([n, a, b, col, v], i) => {
    const y = 176 + i * 76;
    text(s, n, bx, y, 120, 18, { bold: true });
    text(s, `Allowed ${a}–${b}%`, bx + bw - 160, y, 160, 18, { bold: true, align: "right" });
    s.addShape(pres.ShapeType.roundRect, { ...box(bx, y + 26, bw, 14), rectRadius: pt(7), fill: { color: NEUTRAL }, line: { color: NEUTRAL, width: 0.5 } });
    s.addShape(pres.ShapeType.roundRect, { ...box(bx + (bw * a) / 100, y + 26, (bw * (b - a)) / 100, 14), rectRadius: pt(7), fill: { color: col }, line: { color: col, width: 0.5 } });
    s.addShape(pres.ShapeType.ellipse, { ...box(bx + (bw * v) / 100 - 9, y + 24, 18, 18), fill: { color: WHITE }, line: { color: INK, width: 2 } });
    text(s, `${v}%`, bx + (bw * v) / 100 - 30, y + 44, 60, 14, { fontSize: 10, bold: true, align: "center" });
  });
  text(s, "White dots: chicken fried rice for the active woman.", bx, 408, bw, 14, { fontSize: 9, color: MUTED });
  const x = X0 + 368, w = 240;
  card(s, [{ text: "Test 1", options: { fontSize: 12, bold: true, color: ON_INK, breakLine: true } }, { text: "Within 10%", options: { fontFace: HEAD, fontSize: 32, bold: true, color: WHITE, breakLine: true } }, { text: "of the meal's calorie target", options: { fontSize: 12, color: ON_INK } }], x, TOP, w, 124, { fill: INK, margin: 14, valign: "middle" });
  card(s, "", x, 266, w, 164);
  text(s, "72 fixed requests", x + 12, 276, 210, 20, { fontFace: HEAD, fontSize: 14, bold: true });
  const dots = (cols, x0, colour) => {
    for (let c = 0; c < cols; c++) for (let r = 0; r < 4; r++) s.addShape(pres.ShapeType.ellipse, { ...box(x0 + c * 11.5, 304 + r * 12.5, 9, 9), fill: { color: colour }, line: { color: colour, width: 0.5 } });
  };
  dots(12, x + 12, GREEN);
  dots(6, x + 160, TOMATO);
  text(s, "12 cravings × 4 body profiles", x + 12, 362, 136, 30, { fontSize: 10, color: GREEN, bold: true });
  text(s, "6 cravings × 4 limits", x + 160, 362, 72, 44, { fontSize: 10, color: TOMATO, bold: true });
  marker(s, 1, x + w - 18, TOP + 6);
  marker(s, 2, x + w - 18, 272);
  limit(s, "AMDR is a daily reference, applied here to one meal.", X0, 442, 608, 30);
  takeaways(s, [["Calories weren't the hard part", "At the first run 68 of 72 plans were within 10%, but only 10 cleared both tests."], ["Fixed requests make runs fair", "The same 72 requests run every time, offline, so each change can be measured."]], [2, 90]);
}

// 11 — results
{
  const s = slide("EVIDENCE > RESULTS", "Three fixes took the planner from 10 to 72 of 72", "Plans meeting both targets on the project's own benchmark, and what each fix changed.",
    "The first run passed only 10 of 72.\n\n[Point: Portion balancing]\nResizing each ingredient toward the ranges took it to 41, with the same meals.\n\n[Point: Honest fallback]\nThe relevance gate moved 11 off-menu requests to fallback meals, which took it to 47. That rise comes from moving requests, not from better meals.\n\n[Point: Cooking fat and rounding retry]\nAdding a fat to six recipes, and a retry after rounding, took it to all 72.\n\n[Point: 68 of 68]\nThe fixes were tuned on these 72, so I also asked for every recipe by name. Only 49 of 68 passed, so a further recipe fix took it to 68 of 68.\n\nThis shows plans meet the targets. It doesn't show that people prefer them.\n\nReference — not read aloud\ndocs/7_meal_quality.md §2; docs/meal_quality/baseline.md; DEC-26 to DEC-30; scripts/meal_quality_baseline.py --wider, 7 November 2026.", EVIDENCE);
  card(s, "", X0, TOP, 608, 262);
  text(s, "Plans meeting the targets, out of 72", X0 + 16, TOP + 10, 500, 18, { color: MUTED });
  // Drawn from shapes: Google Slides turns a native chart into a picture and loses its labels.
  const base = 326, unit = 148 / 72;
  [["First run", "Before any fix", 10, BASELINE, MUTED], ["Portion balancing", "Each ingredient resized", 41, GREEN, GREEN], ["Honest fallback", "Off-menu cravings moved", 47, WARN, WARN], ["Cooking fat, rounding retry", "Oil added to 6 recipes", 72, GREEN, GREEN]].forEach(([n, d, v, c, tc], i) => {
    const x = X0 + 20 + i * 144, bh = v * unit;
    s.addShape(pres.ShapeType.rect, { ...box(x + 22, base - bh, 92, bh), fill: { color: c }, line: { color: c, width: 0.5 }, objectName: `Bar ${n}` });
    text(s, String(v), x, base - bh - 24, 136, 22, { fontFace: HEAD, fontSize: 16, bold: true, color: tc, align: "center", valign: "bottom" });
    text(s, [{ text: n, options: { bold: true, breakLine: true } }, { text: d, options: { color: MUTED } }], x, base + 6, 136, 52, { align: "center", fontSize: 10 });
  });
  s.addShape(pres.ShapeType.line, { ...box(X0 + 20, base, 568, 0), line: { color: LINE, width: 1 } });
  marker(s, 1, X0 + 20 + 2 * 144 + 116, base - 47 * unit - 18);
  marker(s, 2, X0 + 20 + 3 * 144 + 116, base - 72 * unit - 18);
  [["balance", G, "0.4%", "median calorie gap, worst 9.9%"], ["health_and_safety", T, "5 of 5", "guardrail cases hold"], ["search", A, "68 of 68", "wider check: every recipe by name"]].forEach(([icon, [tint, deep], v, l], i) => {
    const x = X0 + i * 205;
    card(s, "", x, 402, 197, 78, { fill: tint });
    iconDot(s, icon, deep, x + 10, 412, 26);
    text(s, v, x + 44, 410, 148, 28, { fontFace: HEAD, fontSize: 16, bold: true, color: deep, valign: "middle" });
    text(s, l, x + 12, 442, 180, 32, { color: deep, fontSize: 10 });
  });
  marker(s, 3, 643, 396);
  takeaways(s, [["61 plans match; 11 are fallbacks", "Both pass, but the 41 to 47 step came from those 11 moving to fallback meals, not better meals. 8 of them are pizza and dessert."], ["68 of 72 include an estimate", "The benchmark runs without provider keys, so these plans aren't USDA-verified."], ["Tuned on these 72", "Asked for by name, recipes passed only 49 of 68 until a further fix made it 68 of 68. Neither shows that users prefer the plans."]], [2, 106, 180]);
}

// 12 — architecture
{
  const s = slide("BUILD AND LIMITS > ARCHITECTURE", "One service, two clients, four agents", "A request flows left to right. Each box names the model, data or tool behind it.",
    "This is the whole system on one page.\n\n[Point: Clients]\nThere are two clients: the live Streamlit demo and a React app.\n\n[Point: FastAPI]\nThey share one typed FastAPI contract, with API keys and rate limits.\n\n[Point: Planning service]\nA planning service runs the four agents in order.\n\n[Point: Models and data]\nEach agent has its own source: the trained model, the recipe corpus, the nutrition tables and the store reference.\n\n[Point: Built with]\nThe bottom row is the delivery stack.\n\nThe hosted demo runs the agents inside Streamlit, and Cloud Run is ready but not deployed.\n\nReference — not read aloud\ndocs/2_architecture.md; pyproject.toml; frontend/package.json; backend/app/services/meal_planning_service.py; DEC-2. Logos: slides/assets/logos/NOTICE.txt.", BUILD);
  const logo = (n, x, y, d = 20) => s.addImage({ path: `slides/assets/logos/${n}.png`, ...box(x, y, d, d), altText: `${n} logo` });
  [["CLIENTS", X0], ["API", 153], ["PLANNING SERVICE", 263]].forEach(([t, x]) => text(s, t, x, TOP, 220, 14, { fontSize: 10, bold: true, color: MUTED }));
  const top = 148;
  [
    ["Streamlit demo", "Live and public", ["streamlit"], G, top],
    ["React app", "Guided flow, run locally", ["react", "vite", "tailwindcss"], T, top + 134],
  ].forEach(([h, b, logos, [tint, deep], y]) => {
    card(s, "", X0, y, 96, 124, { fill: tint });
    s.addShape(pres.ShapeType.roundRect, { ...box(X0 + 6, y + 8, 84, 32), rectRadius: pt(8), fill: { color: WHITE }, line: { color: WHITE, width: 1 } });
    logos.forEach((n, i) => logo(n, X0 + 12 + i * 25, y + 14));
    text(s, [{ text: h, options: { bold: true, color: deep, breakLine: true } }, { text: b, options: { fontSize: 10, color: deep } }], X0 + 8, y + 46, 84, 74);
    arrow(s, X0 + 97, y + 62, 152, y + 62);
  });
  card(s, "", 153, top, 96, 258);
  logo("fastapi", 161, top + 10); logo("pydantic", 187, top + 10);
  text(s, [{ text: "FastAPI", options: { bold: true, breakLine: true } }, { text: "Typed JSON, API keys, rate limits", options: { fontSize: 10, color: MUTED } }], 161, top + 36, 82, 76);
  card(s, "", 159, top + 136, 84, 114, { fill: "DDE3DA" });
  logo("sqlite", 166, top + 142);
  text(s, [{ text: "SQLite", options: { bold: true, breakLine: true } }, { text: "Local history, via SQLModel", options: { fontSize: 10 } }], 166, top + 166, 74, 60);
  pend(s, "P2", 168, top + 230);
  arrow(s, 201, top + 116, 201, top + 135);
  arrow(s, 250, top + 129, 262, top + 129);
  card(s, "", 263, top, 388.5, 258, { fill: PANEL });
  logo("python", 271, top + 5, 16);
  text(s, "MealPlanningService", 292, top + 5, 280, 16, { fontFace: MONO, fontSize: 10, bold: true, valign: "middle" });
  [
    ["monitor_weight", G, "Calorie expenditure", "Trained HistGradientBoosting model", ["scikitlearn"]],
    ["skillet", T, "Meal recommendation", "TF-IDF search of 34 recipes, diet rules", ["scikitlearn"]],
    ["fact_check", A, "Nutrition verification", "Local tables; USDA, FatSecret with keys", []],
    ["balance", ["FFFFFF", INK], "Balance and reconcile", "A service step: linear programme for portions", ["scipy"]],
    ["shopping_basket", K, "Supermarket", "Local store items and category prices", []],
  ].forEach(([icon, [tint, deep], h, b, logos], i) => {
    const y = top + 26 + i * 46;
    card(s, "", 271, y, 372.5, 41, { fill: tint });
    iconDot(s, icon, deep, 278, y + 8, 25);
    text(s, [{ text: h, options: { bold: true, color: deep, breakLine: true } }, { text: b, options: { fontSize: 10, color: deep } }], 312, y + 2, 296, 37, { valign: "middle" });
    logos.forEach((n) => logo(n, 615, y + 10));
    if (i < 4) arrow(s, 290, y + 41, 290, y + 46);
  });
  card(s, "", X0, 414, 608, 54, { fill: INK });
  text(s, "BUILT WITH", X0 + 10, 417, 200, 12, { fontSize: 8, bold: true, color: ON_INK });
  let cx = X0 + 6;
  [["python", "Python", 78], ["docker", "Docker", 78], ["githubactions", "GitHub Actions", 116], ["googlecloud", "Cloud Run", 94], ["opentelemetry", "OpenTelemetry", 116], ["googlegemini", "Gemini", 78]].forEach(([n, t, w]) => {
    s.addShape(pres.ShapeType.roundRect, { ...box(cx, 431, w, 30), rectRadius: pt(6), fill: { color: WHITE }, line: { color: WHITE, width: 1 } });
    logo(n, cx + 5, 437, 18);
    text(s, t, cx + 27, 431, w - 28, 30, { fontSize: 10, bold: true, valign: "middle" });
    if (n === "googlecloud") pend(s, "P3", cx + 14, 410);
    cx += w + 4;
  });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "the hosted demo runs the same service inside Streamlit. Gemini is optional and off by default. Logos belong to their owners." }], X0, 472, 608, 14, { fontSize: 8, color: MUTED });
  marker(s, 1, 234, top + 6);
  marker(s, 2, 628, top + 5);
  marker(s, 3, 628, top + 26 + 3 * 46 + 2);
  takeaways(s, [["One contract, two clients", "Streamlit and React use the same planning service, so the logic lives in one place."], ["Small models, no GPU", "The one trained model is 0.64 MB, and TF-IDF is enough for 34 recipes."], ["Balancing comes after lookup", "Portions are solved on looked-up numbers, then the shopping list is written from the final amounts."]], [2, 74, 149]);
}

// 13 — engineering
{
  const s = slide("BUILD AND LIMITS > ENGINEERING", "Built like a product, not a notebook", "Six production habits, in the order a change travels through them, each with a file behind it.",
    "Although this is a portfolio project, I held it to production habits. Follow a change from left to right.\n\n[Point: Contract]\nThe API contract is committed, and CI fails if it drifts.\n\n[Point: Tests]\nThe last full run passed 630 Python tests at 95% coverage, and CI won't pass below 89%.\n\n[Point: Cloud Run]\nFrom here the line turns amber: the deployment workflow and tracing are built, but they wait for a GCP project.\n\n[Point: CI checks]\nFive checks run on every pull request, and all five passed on the latest one.\n\nReference — not read aloud\ndocs/openapi.json; .github/workflows/ci.yml and deploy.yml; docs/6_deployment.md; backend/tests/test_telemetry_redaction.py; local full run, 7 November 2026: 538 backend and 92 Streamlit tests.", BUILD);
  card(s, "", X0, TOP, 608, 190);
  text(s, "From a change to production", X0 + 16, TOP + 8, 300, 18, { bold: true });
  [[GREEN, "Runs today", 382], [WARN, "Built, waiting for a GCP project", 462]].forEach(([c, t, x]) => {
    s.addShape(pres.ShapeType.ellipse, { ...box(x, TOP + 13, 8, 8), fill: { color: c }, line: { color: c, width: 0.5 } });
    text(s, t, x + 12, TOP + 9, 170, 16, { fontSize: 9, color: MUTED, valign: "middle" });
  });
  const ly = 193, sx = X0 + 54, step = 100;
  s.addShape(pres.ShapeType.line, { ...box(sx, ly, step * 3, 0), line: { color: GREEN, width: 4 } });
  s.addShape(pres.ShapeType.line, { ...box(sx + step * 3, ly, step * 2, 0), line: { color: WARN, width: 4, dashType: "dash" } });
  [
    ["fact_check", GREEN, "Contract", "CI fails on any drift", "docs/openapi.json"],
    ["science", GREEN, "Tests", "630 Python tests", "backend/tests/"],
    ["lock", GREEN, "Security", "API keys, rate limits", "api/auth.py"],
    ["inventory_2", GREEN, "Container", "One Docker image", "Dockerfile"],
    ["cloud_upload", WARN, "Cloud Run", "Ready, not live", "deploy.yml"],
    ["visibility", WARN, "Tracing", "Health data kept out", "core/telemetry.py"],
  ].forEach(([icon, c, h, b, f], i) => {
    const x = sx + i * step;
    iconDot(s, icon, c, x - 20, ly - 20, 40);
    text(s, [{ text: h, options: { bold: true, color: c, breakLine: true } }, { text: b, options: { fontSize: 10, color: MUTED } }], x - 49, ly + 24, 98, 34, { align: "center" });
    text(s, f, x - 49, ly + 60, 98, 12, { fontFace: MONO, fontSize: 8, color: c, align: "center" });
    if (i > 3) pend(s, "P3", x - 33, ly + 76 - 2);
  });
  marker(s, 2, sx + 4 * step + 16, ly - 30);
  marker(s, 3, sx + 5 * step + 16, ly - 30);
  const y = 330, h = 146;
  // Tests: one bar, to scale.
  card(s, "", X0, y, 192, h, { fill: "E3EFE6" });
  text(s, "630", X0 + 14, y + 8, 164, 44, { fontSize: 32, bold: true, color: GREEN, valign: "middle" });
  text(s, "Python tests, all passing", X0 + 14, y + 52, 168, 18, { color: GREEN });
  const tw = 164;
  bar(s, X0 + 14, y + 78, tw * 538 / 630, 16, GREEN);
  bar(s, X0 + 14 + tw * 538 / 630, y + 78, tw * 92 / 630, 16, TOMATO);
  text(s, [{ text: "538 backend", options: { bold: true, color: GREEN, breakLine: true } }, { text: "92 Streamlit", options: { bold: true, color: TOMATO } }], X0 + 14, y + 100, 164, 34, { fontSize: 10 });
  // Coverage: the track runs 0 to 100%, with the CI floor marked.
  const cx = X0 + 208;
  card(s, "", cx, y, 192, h, { fill: "FBE4DC" });
  text(s, "95%", cx + 14, y + 8, 164, 44, { fontSize: 32, bold: true, color: TOMATO, valign: "middle" });
  text(s, "test coverage", cx + 14, y + 52, 168, 18, { color: TOMATO });
  s.addShape(pres.ShapeType.rect, { ...box(cx + 14, y + 78, tw, 16), fill: { color: WHITE }, line: { color: WHITE, width: 0.5 } });
  bar(s, cx + 14, y + 78, tw * 0.95, 16, TOMATO);
  s.addShape(pres.ShapeType.line, { ...box(cx + 14 + tw * 0.89, y + 72, 0, 28), line: { color: INK, width: 1.5 } });
  text(s, "CI fails below the 89% floor", cx + 14, y + 104, 168, 28, { fontSize: 10, bold: true, color: TOMATO });
  // CI: the five real checks.
  const kx = X0 + 416;
  card(s, "", kx, y, 192, h, { fill: TINT_WARN });
  text(s, "5 CI checks on every pull request", kx + 14, y + 8, 168, 32, { bold: true, color: WARN });
  ["backend (Python 3.11)", "backend (Python 3.12)", "requirements drift", "frontend", "container"].forEach((t, i) => {
    const ry = y + 44 + i * 19;
    s.addShape(pres.ShapeType.ellipse, { ...box(kx + 14, ry + 1, 14, 14), fill: { color: WARN }, line: { color: WARN, width: 0.5 } });
    s.addImage({ path: "slides/assets/glyph-check_circle.png", ...box(kx + 15, ry + 2, 12, 12), altText: "" });
    text(s, t, kx + 34, ry, 150, 16, { fontSize: 10, color: WARN, valign: "middle" });
  });
  marker(s, 1, kx + 174, y + 6);
  takeaways(s, [["CI stops drift", "Tests, the API contract and the dependency file are checked on every pull request, so they can't quietly fall out of step."], ["Built is not the same as live", "Cloud Run is ready, but no GCP project exists yet, so it hasn't run for real."], ["Privacy is tested, not promised", "A test proves health data stays out of traces. A real trace still has to arrive in Cloud Trace."]], [2, 106, 180]);
}

// 14 — limits
{
  const s = slide("BUILD AND LIMITS > LIMITS", "What this project does not prove yet", "The further right, the less has been shown.",
    "These are the limits, arranged by how far the evidence goes. Each step up is less proven.\n\n[Point: Measured]\nThe plans hit their targets on fixed requests. That's solid, but the checks also guided the fixes.\n\n[Point: Estimated]\nA lot of what's inside those plans is estimated or assumed.\n\n[Point: Not tested]\nNobody has used it, it isn't deployed, and no clinician has reviewed it.\n\nIt's a planning aid, not medical advice.\n\nReference — not read aloud\ndocs/4_next_steps.md §7; docs/7_meal_quality.md; DEC-31; AGENTS.md, Open risks.", BUILD);
  [
    ["check_circle", G, "Measured", ["72 of 72 and 68 of 68, offline", "But the checks guided the fixes", "11 of 72 fall back"], 178],
    ["calculate", A, "Estimated", ["68 of 72 plans include an estimate", "AMDR is a daily range on one meal", "Default exercise inputs", "Diet rules match ingredient names"], 258],
    ["group", T, "Not tested", ["No user testing", "No clinical review", "Not deployed", "No database migrations", "Taste and health outcomes unknown"], 336],
  ].forEach(([icon, [tint, deep], h, items, ht], i) => {
    const x = X0 + i * 208, y = 468 - ht;
    card(s, "", x, y, 192, ht, { fill: tint });
    iconDot(s, icon, deep, x + 12, y + 10, 30);
    text(s, h, x + 50, y + 10, 136, 30, { fontSize: 16, bold: true, color: deep, valign: "middle" });
    text(s, items.map((t, k) => ({ text: t, options: { color: deep, bullet: { indent: 10 }, breakLine: k < items.length - 1, paraSpaceAfter: 6 } })), x + 12, y + 50, 172, ht - 58);
  });
  pend(s, "P9", X0 + 416 + 12, 442);
  text(s, [{ text: "How far the evidence goes", options: { fontSize: 14, bold: true, breakLine: true } }, { text: "Each step up is less proven.", options: { color: MUTED } }], X0, TOP + 4, 340, 44);
  text(s, "A planning aid, not medical advice.", X0, 472, 608, 14, { fontSize: 9, bold: true, color: WARN });
  marker(s, 1, X0 + 172, 468 - 178 + 6);
  marker(s, 2, X0 + 208 + 172, 468 - 258 + 6);
  marker(s, 3, X0 + 416 + 172, 468 - 336 + 6);
  takeaways(s, [["What is solid", "Plans hit their targets on fixed requests, and the run can be repeated."], ["What is soft", "Most plans lean on estimates. Name matching missed soy sauce until this review."], ["What is unknown", "Nobody has used it, so targets say nothing yet about taste or health."]], [2, 74, 164]);
}

// 15 — pending tasks
{
  const s = slide("BUILD AND LIMITS > PENDING TASKS", "Pending tasks, in priority order", "Each paper tag in this deck points to one of these notes.",
    "This board is the work still open, in the order I'd do it.\n\n[Point: Now]\nFirst, make the demo work on first use, add migrations and deploy.\n\n[Point: Next]\nThen better inputs: real nutrition data, real exercise details and proper allergen tags.\n\n[Point: Later]\nThen scale: more recipes, live prices, and testing with people.\n\nReference — not read aloud\ndocs/showcase/pending-tasks.md; docs/4_next_steps.md §6 and §7.", BUILD);
  [
    ["NOW", T, [["P1", "Turn on demo mode"], ["P2", "Add database migrations"], ["P3", "Deploy to Cloud Run"]]],
    ["NEXT", A, [["P4", "Run the benchmark with USDA keys"], ["P5", "Ask for real exercise details"], ["P6", "Tag allergens on ingredients"]]],
    ["LATER", G, [["P7", "Grow to 75–100 recipes"], ["P8", "Connect live store prices"], ["P9", "Use feedback, test with people"]]],
  ].forEach(([h, [tint, deep], notes], i) => {
    const x = X0 + i * 208;
    card(s, "", x, TOP, 192, 340, { fill: PANEL });
    s.addText(h, { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x + 10, TOP + 10, 172, 26), fill: { color: deep }, line: { color: deep, width: 1 }, color: WHITE, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
    notes.forEach(([id, t], k) => {
      const y = TOP + 46 + k * 96;
      s.addShape(pres.ShapeType.rect, { ...box(x + 12, y, 168, 86), fill: { color: tint }, line: { color: tint, width: 1 }, rotate: [-1, 1, 0][(i + k) % 3], shadow: { type: "outer", color: "15291F", opacity: 0.18, blur: 4, offset: 2, angle: 90 } });
      pend(s, id, x + 20, y + 8);
      text(s, t, x + 20, y + 28, 152, 52, { bold: true, color: deep });
    });
  });
  marker(s, 1, X0 + 162, TOP + 54);
  marker(s, 2, X0 + 208 + 162, TOP + 54);
  marker(s, 3, X0 + 416 + 162, TOP + 54);
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "the full checklist is in " }, { text: "docs/showcase/pending-tasks.md", options: { fontFace: MONO } }, { text: "." }], X0, 474, 608, 12, { fontSize: 8, color: MUTED });
  takeaways(s, [["Fix what visitors see first", "A demo that fails on first use undoes everything else, so it leads the board."], ["Accuracy before scale", "Better inputs and allergen tags come before more recipes."], ["People matter most", "Only testing with people can show that the plans help."]], [2, 74, 149]);
}

// 16 — close
{
  const s = dark("Try it and read the code",
    "That's AI Meal Planner: one craving in, one meal sized to you, with each ingredient's source shown.\n\n[Point: QR code]\nThe demo and code are here.\n\nReference — not read aloud\nREADME.md.", CLOSE);
  text(s, "tuannm3812-ai-meal-planner.streamlit.app", X0, 248, 590, 22, { fontSize: 16, bold: true, color: WHITE, hyperlink: { url: "https://tuannm3812-ai-meal-planner.streamlit.app/" } });
  text(s, "github.com/tuannm3812/ai-meal-planner", X0, 282, 590, 22, { fontSize: 16, color: ON_INK, hyperlink: { url: "https://github.com/tuannm3812/ai-meal-planner" } });
  text(s, "A multi-agent meal planner, a portfolio project by Mike", X0, 330, 590, 18, { color: WHITE });
  text(s, "A study project. Not medical advice.", X0, 352, 590, 18, { color: ON_INK });
  text(s, "The demo is the Streamlit client and may take a minute to wake.", X0, 374, 590, 18, { color: ON_INK });
  pend(s, "P1", X0, 400);
  s.addImage({ path: "slides/assets/mark-dark.png", ...box(X0, 92, 52, 52), altText: "AI Meal Planner logo" });
}

(async () => {
  const out = process.argv[2] || "ai-meal-planner-deck.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
