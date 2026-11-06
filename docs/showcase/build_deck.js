// Builds the 14-slide seed to docs/showcase/slides/BRIEF.md and DESIGN.md.
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
    ["person", "E3EFE6", GREEN, "Sized to you", [["Your body, a trained exercise model and your goal set a "], ["daily budget", 1], [", then this "], ["meal's target", 1], ["."]], "0.3%", "median gap to the meal target, worst 9.9%"],
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
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "the project's own offline test, not real users. 11 of the 72 are fallback meals; guardrails use a controlled recipe set. Meal targets stay within 350–850 kcal. Plate area shows calories." }], X0, 482, W, 14, { fontSize: 8, color: MUTED });
}

// 3 — agenda
{
  const s = slide("AGENDA", "Today's menu: four courses, from the problem to the limits", "Each course lists its pages by label. Select one to jump to it.",
    "This deck is served as a four-course menu.\n\n[Point: Starter]\nFirst, why this is worth solving.\n\n[Point: Main]\nThen what it does and how it works.\n\n[Point: Taste test]\nThen what a good meal means, and whether it got there.\n\n[Point: The bill]\nLast, how it's built and what isn't proven yet.\n\nEach page is a link, so you can jump straight to it.", OPEN);
  s.addImage({ path: "slides/assets/plate-salmon.png", ...box(668, 196, 248, 248), altText: "Plate of salmon and quinoa" });
  let y = TOP;
  [
    ["soup_kitchen", "E3EFE6", GREEN, "STARTER", "Problem", "Why is this worth solving?", [["Why it matters", 4]], 62],
    ["lunch_dining", "FBE4DC", TOMATO, "MAIN", "Solution", "What does it do, and how?", [["The flow", 5], ["Four agents", 6], ["Calorie target", 7], ["Choosing the meal", 8], ["Nutrition", 9]], 112],
    ["restaurant", TINT_WARN, WARN, "TASTE TEST", "Evidence", "Did we get there?", [["What good means", 10], ["Results", 11]], 78],
    ["receipt_long", "DDE3DA", INK, "THE BILL", "Build and limits", "What is unproven?", [["Engineering", 12], ["Next steps", 13]], 78],
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
  card(s, "", X0, TOP, 270, 356, { fill: INK });
  s.addImage({ path: "slides/assets/plate-pasta.png", ...box(X0 + 35, TOP + 92, 200, 200), altText: "Plate of tomato turkey pasta" });
  s.addText("I feel like pasta tonight.", { shape: pres.ShapeType.wedgeRoundRectCallout, ...box(X0 + 20, TOP + 18, 230, 56), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: INK, fontSize: 16, bold: true, align: "center", valign: "middle", margin: 6 });
  text(s, "One request answers all three.", X0 + 20, TOP + 306, 230, 30, { fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
  [
    ["monitor_weight", "E3EFE6", GREEN, "How much?", "Daily budgets in our benchmark run from 1,200 to 4,521 kcal.", "Guess from \"serves 4\"", "A budget, then a meal target"],
    ["no_food", "FBE4DC", TOMATO, "Is it right for me?", "Asked for pasta, a vegan gets lentil bolognese and a coeliac gets gluten-free pasta.", "Read every label", "Conflicts ruled out or swapped first"],
    ["shopping_cart", TINT_WARN, WARN, "What do I buy?", "This one pasta means five ingredients to find and price.", "Write a list, guess the cost", "A list with an estimated total"],
  ].forEach(([icon, tint, deep, h, b, before, after], i) => {
    const y = TOP + i * 123;
    card(s, "", 331.5, y, 585, 110, { fill: tint });
    iconDot(s, icon, deep, 345, y + 37, 36);
    text(s, hb(h, b, { hc: deep, bc: deep }), 392, y + 8, 212, 94, { valign: "middle" });
    const chip = (x, w, label, t, fill, colour) => s.addText([
      { text: label, options: { fontSize: 8, bold: true, color: colour, breakLine: true, paraSpaceAfter: 2 } },
      { text: t, options: { fontSize: 11, bold: true, color: colour } },
    ], { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x, y + 18, w, 74), fill: { color: fill }, line: { color: fill === WHITE ? deep : fill, width: 1 }, margin: 8, valign: "middle" });
    chip(614, 128, "TODAY", before, WHITE, deep);
    arrow(s, 743, y + 55, 758, y + 55);
    chip(760, 144, "WITH THE APP", after, deep, WHITE);
  });
}

// 5 — flow
{
  const s = slide("SOLUTION > THE FLOW", "One craving in, one meal and a shopping list out", "Three steps in the React app.",
    "This is the real React app, in three steps.\n\n[Point: You]\nYou enter your body, goal and anything to avoid.\n\n[Point: Craving]\nYou say what you feel like eating and where you shop.\n\n[Point: Your plan]\nYou get one meal, its balance, each ingredient's source and a shopping list. The badges say how it matched and what is estimated.\n\nNext, what happens behind these screens.\n\nReference — not read aloud\nCaptured 6 November 2026 from a local run with no provider keys: slides/captures/2026-11-06-plan.json. frontend/src/features/flow/MealFlow.jsx.", SOLUTION);
  [
    ["1-profile", "person", "E3EFE6", GREEN, "1. You", "Goal, body details, activity and anything to avoid."],
    ["2-craving", "search", "FBE4DC", TOMATO, "2. Craving", "Say what you feel like eating and where you shop."],
    ["3-plan", "rice_bowl", TINT_WARN, WARN, "3. Your plan", "One meal, its balance, each ingredient's source and a shopping list."],
  ].forEach(([f, icon, tint, deep, h, b], i) => {
    const x = X0 + i * 297;
    card(s, hb(h, b, { hc: deep, bc: deep }), x, TOP, 279, 336, { fill: tint, margin: 14, valign: "bottom" });
    s.addImage({ path: `slides/captures/2026-11-06-${f}.jpg`, ...box(x + 12, TOP + 12, 255, 179), altText: `${h} screen of the React app` });
    s.addShape(pres.ShapeType.rect, { ...box(x + 12, TOP + 12, 255, 179), fill: { color: WHITE, transparency: 100 }, line: { color: LINE, width: 1 } });
    iconDot(s, icon, deep, x + 14, TOP + 203, 30);
    if (i < 2) arrow(s, x + 281, TOP + 168, x + 295, TOP + 168);
  });
  caption(s, 1, "Real captures of the React app, run locally with no provider keys, 6 November 2026.", X0, 474, W);
}

// 6 — agents
{
  const s = slide("SOLUTION > FOUR AGENTS", "Four agents work like one kitchen", "An order comes in, each station does one job, and a planning service runs them in order.",
    "Behind the screens is a FastAPI service, and it works like a kitchen.\n\n[Point: The portion planner]\nThe calorie agent sets a daily budget.\n\n[Point: The chef]\nThe recommendation agent sets the meal target, excludes conflicting meals and picks a relevant recipe.\n\n[Point: The taster]\nThe nutrition agent looks up each ingredient and labels estimates.\n\n[Point: The shopper]\nThe supermarket agent matches ingredients to store items or category prices, with an estimated total.\n\n[Point: white labels]\nThe white labels follow one real order: a 2,469 kcal budget, a 691 kcal target, 694 kcal served and a $24.50 estimated basket.\n\nThe meal comes from retrieval, not generation, so the core path needs no LLM key.\n\nReference — not read aloud\ndocs/2_architecture.md; docs/agents/; MealPlanningService. The kitchen roles are a metaphor for the agents.", SOLUTION);
  s.addText([{ text: "ORDER  ", options: { bold: true } }, { text: "chicken fried rice, active woman, maintaining" }], { shape: pres.ShapeType.rect, ...box(X0, TOP, W, 34), fill: { color: WHITE }, line: { color: INK, width: 1, dashType: "dash" }, color: INK, fontFace: MONO, fontSize: 12, margin: 10, valign: "middle" });
  [
    ["scale", "E3EFE6", GREEN, "THE PORTION PLANNER", "Calorie expenditure", "Estimates what you burn in a day and sets your daily budget.", "2,469 kcal budget"],
    ["pan", "FBE4DC", TOMATO, "THE CHEF", "Meal recommendation", "Sets the meal target, rules out conflicts, picks a relevant recipe and sizes it.", "691 kcal target"],
    ["taster", TINT_WARN, WARN, "THE TASTER", "Nutrition verification", "Looks up each ingredient and labels what is estimated.", "694 kcal, 3 of 6 estimated"],
    ["basket", "DDE3DA", INK, "THE SHOPPER", "Supermarket", "Matches ingredients to store items or category prices.", "$24.50 estimated"],
  ].forEach(([art, tint, deep, role, h, b, out], i) => {
    const x = X0 + i * 223, y = 174;
    card(s, "", x, y, 204, 226, { fill: tint });
    s.addImage({ path: `slides/assets/station-${art}.png`, ...box(x + 32, y + 10, 140, 70), altText: `Illustration for ${role.toLowerCase()}` });
    text(s, [
      { text: role, options: { fontSize: 10, bold: true, color: deep, breakLine: true, paraSpaceAfter: 2 } },
      { text: h, options: { fontSize: 14, bold: true, color: deep, breakLine: true, paraSpaceAfter: 4 } },
      { text: b, options: { fontSize: 12, color: deep } },
    ], x + 12, y + 84, 182, 104);
    s.addText(out, { shape: pres.ShapeType.roundRect, rectRadius: pt(8), ...box(x + 12, y + 192, 180, 26), fill: { color: WHITE }, line: { color: WHITE, width: 1 }, color: deep, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0 });
    if (i < 3) arrow(s, x + 206, y + 113, x + 221, y + 113);
  });
  card(s, [{ text: "One typed JSON response: meal, nutrition, shopping list and warnings", options: { fontFace: HEAD, fontSize: 16, bold: true, color: WHITE } }], X0, 408, W, 42, { fill: INK, margin: 16, valign: "middle" });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "white labels show the active woman's real plan. The service balances portions after verification. The core path needs no LLM key." }], X0, 458, W, 14, { fontSize: 8, color: MUTED });
}

// 7 — calorie target
{
  const s = slide("SOLUTION > CALORIE TARGET", "From your body to a meal target", "A trained exercise-calorie model feeds a daily budget, then one meal's target.",
    "How does it decide how much? It's a short calculation, not one model.\n\n[Point: Exercise calories]\nThe trained model predicts exercise calories.\n\n[Point: Daily estimate]\nThose are added to a BMR-based daily estimate.\n\n[Point: Goal]\nYour goal then adjusts it.\n\n[Point: Meal target]\nThe meal target is 28% of the daily budget, kept between 350 and 850 kcal.\n\nThe model's scores describe exercise calories only, not daily needs.\n\nReference — not read aloud\nmetrics.json; docs/agents/calorie_expenditure_agent.md; calorie_expenditure_agent.py; meal_recommendation_agent.py; DEC-24; docs/8_design.md §3.1. In the meal flow, exercise inputs use defaults: 30 minutes, 100 bpm.", SOLUTION);
  [["Exercise calories", "Predicted by the trained model"], ["Daily estimate", "Added to a BMR-based estimate"], ["Goal", "+250 kcal to gain, −400 to lose, subject to the floor"], ["Meal target", "28% of the budget, kept to 350–850 kcal"]].forEach(([h, b], i) => {
    const x = X0 + i * 154;
    card(s, hb(h, b), x, TOP, 138, 146, { margin: 10 });
    if (i < 3) arrow(s, x + 139, TOP + 73, x + 153, TOP + 73);
  });
  marker(s, 2, 43.5 + 2 * 154 + 122, TOP + 4);
  [["0.996", "validation R²"], ["2.2 kcal", "MAE"], ["750,000", "dataset rows"]].forEach(([v, l], i) => {
    card(s, [{ text: v, options: { fontFace: HEAD, fontSize: 16, bold: true, breakLine: true, paraSpaceAfter: 3 } }, { text: l, options: { fontSize: 12, color: MUTED } }], X0 + i * 205, 292, 197, 72, { margin: 12, valign: "middle" });
  });
  marker(s, 1, 643, 286);
  caption(s, 1, "Exercise-calorie model, Kaggle Playground Series S5E5.", X0, 372, 600);
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "in the meal flow, exercise inputs use defaults (30 minutes, 100 bpm)." }], X0, 390, 600, 14, { fontSize: 8, color: MUTED });
  takeaways(s, [["These scores are for exercise calories", "They describe the model's task, not daily needs or a meal target."], ["Weight-loss budgets have a floor", "1,200 kcal for women or 1,500 for men, capped at estimated expenditure. A warning explains when it applies."]], [2, 74]);
}

// 8 — choosing the meal
{
  const s = slide("SOLUTION > CHOOSING THE MEAL", "Hard limits first, then a relevant recipe", "Incompatible recipes are excluded before selection, across 34 curated recipes.",
    "This is how it picks the meal.\n\n[Point: Relevance and limits]\nThe craving is compared with each recipe, and anything that conflicts with your diet, allergies or conditions is excluded.\n\n[Point: Ranking]\nRelevance decides what qualifies. Your profile only influences the order.\n\nThen there are three honest outcomes.\n\n[Point: No close match]\nIf nothing is close, you get a standard meal and a note saying so.\n\n[Point: Nothing safe]\nIf nothing is safe, it refuses.\n\nReference — not read aloud\ndocs/agents/meal_recommendation_agent.md; backend/app/rag/retriever.py; DEC-27.", SOLUTION);
  [["Craving and profile", "What you want and what to avoid"], ["Relevance and limits", "Vector similarity; conflicts excluded"], ["Ranking", "Your profile influences the order"]].forEach(([h, b], i) => {
    const x = X0 + i * 208;
    card(s, hb(h, b), x, TOP, 192, 104, { margin: 10 });
    if (i < 2) arrow(s, x + 193, TOP + 52, x + 207, TOP + 52);
  });
  text(s, "Three honest outcomes", X0, 252, 400, 18, { bold: true });
  card(s, hb("Close match", "That recipe, sized to you", { hc: GREEN, bc: INK }), X0, 276, 192, 112, { fill: TINT_OK, margin: 10 });
  card(s, hb("No close match", "A standard meal and a note saying so", { hc: WARN, bc: INK }), X0 + 208, 276, 192, 112, { fill: TINT_WARN, margin: 10 });
  card(s, hb("Nothing safe", "The plan is refused, not guessed", { bc: INK }), X0 + 416, 276, 192, 112, { margin: 10 });
  marker(s, 1, X0 + 208 + 176, 280);
  marker(s, 2, X0 + 416 + 176, 280);
  takeaways(s, [["Relevance decides what qualifies", "An off-menu craving falls back with a warning. The profile only influences ranking."], ["If nothing is safe, it refuses", "It would rather return no plan than guess."]], [2, 92]);
}

// 9 — nutrition
{
  const s = slide("SOLUTION > NUTRITION", "Each ingredient is looked up, and estimates are labelled", "Example: Chicken Fried Rice from a real local run with no provider keys.",
    "Can you trust the numbers? Each one shows where it came from.\n\n[Point: Source column]\nThis is a real plan. Three of its six ingredients are estimates, and the app says so.\n\n[Point: Lookup order]\nA trusted local reference comes first. Otherwise it tries cached or provider lookups, USDA and then FatSecret if configured, and last a local or category estimate.\n\nA reference value isn't an external verification either, so the plan's totals are approximate.\n\nReference — not read aloud\nbackend/app/agents/nutrition_verification_agent.py. Run of 6 November 2026: 694 kcal against a 691 kcal target, 28/46/26% split; profile 34, male, 165 cm, 65 kg, moderately active, maintain.", SOLUTION);
  const cell = (t, o) => ({ text: t, options: o || {} });
  const badge = (ok) => cell(ok ? "Reference" : "Estimated", { color: ok ? MUTED : WARN, bold: !ok, fill: { color: ok ? NEUTRAL : TINT_WARN } });
  const rows = [
    [cell("Ingredient", { bold: true }), cell("Amount", { bold: true, align: "right" }), cell("Source", { bold: true })],
    ...[["Chicken breast", "100 g", 0], ["Cooked white rice", "220 g", 0], ["Whole egg", "50 g", 1], ["Mixed vegetables", "115 g", 1], ["Soy sauce", "15 g", 0], ["Sesame oil", "10 g", 1]].map(([n, a, ok]) => [cell(n), cell(a, { align: "right" }), badge(ok)]),
  ];
  card(s, "", X0, TOP, 372, 276);
  s.addTable(rows, { ...box(X0 + 12, TOP + 12, 348, 252), colW: [pt(170), pt(78), pt(100)], rowH: pt(36), fontSize: 12, color: INK, fontFace: HEAD, valign: "middle", border: { type: "none" } });
  marker(s, 1, 410, 134);
  text(s, "Lookup order", 432, TOP, 220, 22, { fontFace: HEAD, fontSize: 16, bold: true });
  ["Trusted local reference", "Cached or provider lookup: USDA, then FatSecret if configured", "Local or category estimate"].forEach((t, i) => {
    const y = 160 + i * 84;
    card(s, t, 432, y, 220, 66, { margin: 10, valign: "middle" });
    if (i < 2) arrow(s, 542, y + 67, 542, y + 83);
  });
  marker(s, 2, 640, 332);
  caption(s, 1, "A real plan: 694 kcal against a 691 kcal meal target.", X0, 414, 600);
  takeaways(s, [["3 of 6 ingredients are estimates", "The app says so on screen, so the totals read as approximate."], ["With no provider keys", "Values come from local tables, so a plan's target check isn't an independent verification."]], [2, 74]);
}

// 10 — what good means
{
  const s = slide("EVIDENCE > WHAT GOOD MEANS", "We defined a good meal before improving one", "Fixed targets on 72 requests, run offline and repeatably.",
    "Before changing anything, I fixed what good means.\n\n[Point: Macro bands]\nEach macro has to sit inside the adult AMDR range, as a share of the meal's energy.\n\n[Point: Within 10%]\nCalories have to land within 10% of the target.\n\n[Point: 72 requests]\nA plan passes only if all of that holds, on a fixed set of 72 requests.\n\nOne limit: AMDR is a daily reference, applied here to one meal.\n\nReference — not read aloud\ndocs/7_meal_quality.md §1; DEC-25.", EVIDENCE);
  card(s, "", X0, TOP, 560, 300);
  text(s, "Share of the meal's energy", X0 + 18, TOP + 16, 500, 22, { fontFace: HEAD, fontSize: 16, bold: true });
  const bx = X0 + 18, bw = 524;
  [["Protein", 10, 35, C.accent3], ["Carbs", 45, 65, C.accent4], ["Fat", 20, 35, C.accent5]].forEach(([n, a, b, col], i) => {
    const y = 186 + i * 78;
    text(s, n, bx, y, 200, 18, { bold: true });
    text(s, `${a}–${b}%`, bx + bw - 120, y, 120, 18, { bold: true, align: "right" });
    s.addShape(pres.ShapeType.roundRect, { ...box(bx, y + 26, bw, 14), rectRadius: pt(7), fill: { color: NEUTRAL }, line: { color: NEUTRAL, width: 0.5 } });
    s.addShape(pres.ShapeType.roundRect, { ...box(bx + (bw * a) / 100, y + 26, (bw * (b - a)) / 100, 14), rectRadius: pt(7), fill: { color: col }, line: { color: col, width: 0.5 } });
  });
  const x = 621.5, w = 295;
  card(s, [{ text: "Within 10%", options: { fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, breakLine: true } }, { text: "of the calorie target", options: { fontSize: 12, color: ON_INK } }], x, TOP, w, 142, { fill: INK, margin: 16, valign: "middle" });
  card(s, hb("72 requests", "12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits"), x, 288, w, 142, { margin: 16, valign: "middle" });
  limit(s, "AMDR is a daily reference, applied here to one meal.", X0, 444, W, 30);
}

// 11 — results
{
  const s = slide("EVIDENCE > RESULTS", "Three fixes took the planner from 10 to 72 of 72", "Plans meeting the targets on the project's own benchmark.",
    "The first run passed only 10 of 72.\n\n[Point: Portion balancing]\nResizing each ingredient toward the ranges took it to 41, with the same meals.\n\n[Point: Honest fallback]\nThe relevance gate moved 11 off-menu scenarios to fallback meals, which took it to 47.\n\n[Point: Cooking fat and rounding retry]\nAdding a fat to six recipes, and a retry after rounding, took it to all 72.\n\nThis shows plans meet the targets. It doesn't show that people prefer them.\n\nReference — not read aloud\ndocs/7_meal_quality.md §2; docs/meal_quality/baseline.md; DEC-26 to DEC-28.", EVIDENCE);
  card(s, "", X0, TOP, 608, 256);
  text(s, "Plans meeting the targets, out of 72", X0 + 16, TOP + 12, 500, 18, { color: MUTED });
  // Drawn from shapes: Google Slides turns a native chart into a picture and loses its labels.
  const base = 342, unit = 158 / 72;
  [["First run", 10], ["Portion balancing", 41], ["Honest fallback", 47], ["Cooking fat and rounding retry", 72]].forEach(([n, v], i) => {
    const x = X0 + 20 + i * 144, bh = v * unit;
    s.addShape(pres.ShapeType.rect, { ...box(x + 22, base - bh, 92, bh), fill: { color: i ? GREEN : BASELINE }, line: { color: i ? GREEN : BASELINE, width: 0.5 }, objectName: `Bar ${n}` });
    text(s, String(v), x, base - bh - 24, 136, 22, { fontFace: HEAD, fontSize: 16, bold: true, align: "center", valign: "bottom" });
    text(s, n, x, base + 6, 136, 32, { align: "center", color: MUTED, fontSize: 10 });
  });
  s.addShape(pres.ShapeType.line, { ...box(X0 + 20, base, 568, 0), line: { color: LINE, width: 1 } });
  marker(s, 1, X0 + 20 + 2 * 144 + 116, base - 47 * unit - 18);
  marker(s, 2, X0 + 20 + 3 * 144 + 116, base - 72 * unit - 18);
  [["0.3%", "median calorie deviation"], ["9.9%", "worst calorie deviation"], ["5 of 5", "guardrail cases hold"]].forEach(([v, l], i) => {
    card(s, [{ text: v, options: { fontFace: HEAD, fontSize: 16, bold: true, breakLine: true, paraSpaceAfter: 3 } }, { text: l, options: { fontSize: 12, color: MUTED } }], X0 + i * 205, 398, 197, 72, { margin: 12, valign: "middle" });
  });
  marker(s, 3, 643, 392);
  takeaways(s, [["61 plans match; 11 are fallbacks", "Both pass. A fallback meets the targets but isn't what was asked for."], ["68 of 72 include an estimate", "The benchmark runs without provider keys, so these plans aren't USDA-verified."], ["Targets, not preference", "This shows plans meet targets, not that users prefer them."]], [2, 74, 164]);
}

// 12 — engineering
{
  const s = slide("BUILD AND LIMITS > ENGINEERING", "Built like a product, not a notebook", "Production habits on a portfolio project.",
    "Although this is a portfolio project, I held it to production habits.\n\n[Point: Typed API contract]\nThe API contract is committed, and CI fails if it drifts.\n\n[Point: Tested]\nThe last full run logged 598 Python tests at 95% coverage.\n\n[Point: Deployable]\nThe Cloud Run workflow is ready, but it isn't deployed to a GCP project yet.\n\nEach of these has a file behind it in the repo.\n\nReference — not read aloud\ndocs/openapi.json; .github/workflows/; docs/6_deployment.md; docs/5_agent_log.md, 2026-11-02.", BUILD);
  [["Typed API contract", "FastAPI and Pydantic; OpenAPI checked in CI"], ["Tested", "598 Python tests at 95% coverage"], ["Secured", "API keys and rate limits; no history in hosted mode"], ["Deployable", "Containers and a Cloud Run workflow"], ["Observable", "Tracing that keeps health data out"], ["Two clients", "A live Streamlit demo and a React app"]].forEach(([h, b], i) => {
    card(s, hb(h, b), X0 + (i % 3) * 297, TOP + Math.floor(i / 3) * 150, 279, 134, { margin: 14, valign: "middle" });
  });
  limit(s, "the Cloud Run workflow is ready but not yet deployed to a GCP project.", X0, 434, W, 30);
}

// 13 — next
{
  const s = slide("BUILD AND LIMITS > NEXT STEPS", "What comes next, and what it is not yet", "The next steps follow from the limits.",
    "Here are the next steps and the limits, side by side.\n\n[Point: Next]\nA larger recipe library, learning from feedback, and a live deployment.\n\n[Point: Not yet]\nPrices are local estimates, nutrition isn't fully verified, and it hasn't been tested with users or clinicians.\n\nIt's a planning aid, not medical advice.\n\nReference — not read aloud\ndocs/4_next_steps.md §6 and §7.", BUILD);
  const col = (x, h, items, fill, hc) => {
    card(s, [{ text: h, options: { fontFace: HEAD, fontSize: 16, bold: true, color: hc || INK } }], x, TOP, 427.5, 300, { fill, margin: 18 });
    items.forEach((t, i) => {
      const y = 186 + i * 72;
      chip(s, i + 1, x + 18, y);
      text(s, t, x + 52, y, 360, 22, { valign: "middle" });
    });
  };
  col(X0, "Next", ["A larger recipe library", "Learning from user feedback", "A live Cloud Run deployment"]);
  col(X0 + 445.5, "Not yet", ["Live store prices", "Full verified nutrition", "Any user or clinical testing"], TINT_WARN, WARN);
  limit(s, "a planning aid, not medical advice.", X0, 444, W, 30, "Note:");
}

// 14 — close
{
  const s = dark("Try it and read the code",
    "That's AI Meal Planner: one craving in, one meal sized to you, and every number showing how it was produced.\n\n[Point: QR code]\nThe demo and code are here.\n\nReference — not read aloud\nREADME.md.", CLOSE);
  text(s, "tuannm3812-ai-meal-planner.streamlit.app", X0, 248, 590, 22, { fontSize: 16, bold: true, color: WHITE, hyperlink: { url: "https://tuannm3812-ai-meal-planner.streamlit.app/" } });
  text(s, "github.com/tuannm3812/ai-meal-planner", X0, 282, 590, 22, { fontSize: 16, color: ON_INK, hyperlink: { url: "https://github.com/tuannm3812/ai-meal-planner" } });
  text(s, "A multi-agent meal planner, a portfolio project by Mike", X0, 330, 590, 18, { color: WHITE });
  text(s, "A study project. Not medical advice.", X0, 352, 590, 18, { color: ON_INK });
  s.addImage({ path: "slides/assets/mark-dark.png", ...box(X0, 92, 52, 52), altText: "AI Meal Planner logo" });
}

(async () => {
  const out = process.argv[2] || "ai-meal-planner-deck.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
