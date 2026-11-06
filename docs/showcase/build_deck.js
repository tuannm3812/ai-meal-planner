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
  text(s, "One meal sized to you, every number explained, the shopping list ready.", X0, 328, 280, 44, { fontSize: 14, color: ON_INK });
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
  const s = slide("EXECUTIVE SUMMARY", "One craving, sized to four different people", "The same chicken fried rice from the benchmark, and every plan met its targets.",
    "If you read one slide, read this one.\n\n[Point: four plates]\nThis is the same craving for four people. It runs from 363 kcal for an older woman losing weight to 850 for a large athlete gaining, so the meal fits the person.\n\n[Point: 72 of 72]\nThat quality is measured: all 72 plans in the project's own benchmark meet the targets, up from 10.\n\n[Point: Balanced and checked]\nFour features do that work, and it stays honest: estimates are labelled, and it says so when nothing matches.\n\nThe rest of the deck shows how it works and how that number was reached.\n\nReference — not read aloud\ndocs/meal_quality/baseline.json, chicken fried rice rows; fact sheet, docs/showcase/README.md; docs/7_meal_quality.md §2. These are a measure of plans, not of real users.", OPEN);
  // Row 1: the proof of "sized to you". Plate area is to scale with calories.
  card(s, "", X0, TOP, W, 140, { fill: INK });
  s.addImage({ path: "slides/assets/bg-band.png", ...box(X0, TOP, W, 140), altText: "" });
  const scale = 112 / Math.sqrt(850), art = (2 * 232 + 32) / (2 * 232); // plate.png has a small margin around the plate
  [[363, "Older woman,", "losing weight"], [694, "Active woman,", "maintaining"], [809, "Average man,", "maintaining"], [850, "Large athlete,", "gaining"]].forEach(([kcal, a, b], i) => {
    const x = X0 + 10 + i * 218, cy = TOP + 70, cx = x + 62, d = Math.sqrt(kcal) * scale * art;
    s.addImage({ path: "slides/assets/plate.png", ...box(cx - d / 2, cy - d / 2, d, d), altText: `Plate of chicken fried rice, ${kcal} kcal` });
    text(s, [
      { text: `${kcal} kcal`, options: { fontSize: 16, bold: true, color: WHITE, breakLine: true, paraSpaceAfter: 2 } },
      { text: a, options: { fontSize: 10, color: ON_INK, breakLine: true } },
      { text: b, options: { fontSize: 10, color: ON_INK } },
    ], x + 126, TOP + 36, 90, 70, { valign: "middle" });
  });
  // Row 2: the key features, each with its own food colour and icon.
  [
    ["person", "E3EFE6", "1B5E3F", "Sized to you", "A trained model and your goal set a daily budget, then this meal's target."],
    ["health_and_safety", "FBE4DC", "C8431F", "Safe for your diet", "Allergies, diets and health conditions rule out conflicting recipes first."],
    ["balance", "FFF3C9", "A67C00", "Balanced and checked", "Portions are resized toward healthy ranges, and each ingredient shows its source."],
    ["shopping_basket", "EEF2D6", "66791C", "Ready to shop", "Ingredients map to products, with an estimated total for your list."],
  ].forEach(([icon, tint, deep, h, b], i) => {
    const x = X0 + i * 223, y = 282;
    card(s, hb(h, b, { bc: INK }), x, y, 204, 142, { fill: tint, margin: 12, valign: "bottom" });
    s.addShape(pres.ShapeType.ellipse, { ...box(x + 12, y + 12, 30, 30), fill: { color: deep }, line: { color: deep, width: 0.5 } });
    s.addImage({ path: `slides/assets/glyph-${icon}.png`, ...box(x + 17, y + 17, 20, 20), altText: "" });
  });
  // Row 3: the key numbers.
  [["72 of 72", "benchmark plans on target, up from 10"], ["0.3%", "median calorie deviation"], ["34", "curated recipes"], ["4 agents", "and no LLM key needed"]].forEach(([v, l], i) => {
    const x = X0 + i * 223;
    text(s, [{ text: v, options: { fontSize: 24, bold: true, color: GREEN, breakLine: true } }, { text: l, options: { fontSize: 10, color: MUTED } }], x + 12, 432, 192, 46);
  });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "benchmark figures come from the project's own offline test. Plate area is to scale with calories." }], X0, 482, W, 14, { fontSize: 8, color: MUTED });
}

// 3 — agenda
{
  const s = slide("AGENDA", "From the problem to what is still unproven", "Four sections, each answering one question.",
    "The deck has four sections.\n\nFirst why this is worth solving, then how it works, then what was measured, and last how it's built and what isn't proven yet.\n\nEach range is a link, so you can jump straight to a section.", OPEN);
  [["01", "Problem", "Why is this worth solving?", "Page 4", 4], ["02", "Solution", "What does it do, and how?", "Pages 5–9", 5], ["03", "Evidence", "What is a good meal, and did we get there?", "Pages 10–11", 10], ["04", "Build and limits", "How is it built, and what is unproven?", "Pages 12–13", 12]].forEach(([n, h, q, r, p], i) => {
    const x = X0 + i * 224;
    text(s, n, x, 150, 200, 60, { fontFace: HEAD, fontSize: 46, bold: true, color: GREEN });
    text(s, h, x, 224, 200, 24, { fontFace: HEAD, fontSize: 16, bold: true });
    text(s, q, x, 254, 190, 54, { color: MUTED });
    text(s, [{ text: r, options: { hyperlink: { slide: p }, color: INK, bold: true } }], x, 318, 200, 18);
  });
}

// 4 — problem
{
  const s = slide("PROBLEM > WHY IT MATTERS", "Picking a meal is easy; sizing it to you is not", "Three questions sit between a craving and a meal you can trust.",
    "Most of us know what we feel like eating. The hard part comes after that.\n\n[Point: How much?]\nThe right amount depends on your body, activity and goal.\n\n[Point: Is it right for me?]\nDiets, allergies and health conditions rule meals out.\n\n[Point: What do I buy?]\nThe recipe, the nutrition and the shopping list usually live in different places.\n\nThe next section shows how one request answers all three.\n\nReference — not read aloud\nThese three are the project's framing, from docs/1_brief.md, not research findings.", PROBLEM);
  [["How much?", "Calorie needs change with your body, activity and goal."], ["Is it right for me?", "Diets, allergies and health conditions rule meals out."], ["What do I buy?", "Recipes, nutrition and shopping lists live in different places."]].forEach(([h, b], i) => {
    const x = X0 + i * 297;
    card(s, hb(h, b), x, TOP + 14, 279, 196, { margin: 18, valign: "bottom" });
    chip(s, i + 1, x + 18, TOP + 32);
  });
  card(s, [{ text: "One request answers all three.", options: { fontFace: HEAD, fontSize: 16, bold: true, color: WHITE } }], X0, 366, W, 56, { fill: INK, margin: 16, valign: "middle" });
}

// 5 — flow
{
  const s = slide("SOLUTION > THE FLOW", "One craving in, one meal and a shopping list out", "Three steps in the React app.",
    "This is the real React app, in three steps.\n\n[Point: You]\nYou enter your body, goal and anything to avoid.\n\n[Point: Craving]\nYou say what you feel like eating.\n\n[Point: Your plan]\nYou get one meal, its balance and a shopping list. The badges say how it matched and what is estimated.\n\nNext, what happens behind these screens.\n\nReference — not read aloud\nCaptured 6 November 2026 from a local run with no provider keys. frontend/src/features/flow/MealFlow.jsx.", SOLUTION);
  [["1-profile", "You", "Body, goal and what to avoid"], ["2-craving", "Craving", "What you feel like eating"], ["3-plan", "Your plan", "One meal, balance and shopping list"]].forEach(([f, h, b], i) => {
    const x = X0 + i * 297;
    s.addImage({ path: `slides/captures/2026-11-06-${f}.jpg`, ...box(x, TOP, 279, 196), altText: `${h} screen of the React app` });
    s.addShape(pres.ShapeType.rect, { ...box(x, TOP, 279, 196), fill: { color: WHITE, transparency: 100 }, line: { color: LINE, width: 1 } });
    chip(s, i + 1, x, 342);
    text(s, h, x + 30, 342, 245, 22, { fontFace: HEAD, fontSize: 16, bold: true, valign: "middle" });
    text(s, b, x + 30, 368, 245, 18, { color: MUTED });
    if (i < 2) arrow(s, x + 281, TOP + 98, x + 295, TOP + 98);
  });
  caption(s, 1, "Real captures of the React app, run locally with no provider keys, 6 November 2026.", X0, 400, W);
}

// 6 — agents
{
  const s = slide("SOLUTION > FOUR AGENTS", "Four agents, one typed answer", "Each agent does one job, and a planning service runs them in order.",
    "Behind the screens is a FastAPI service with four agents.\n\n[Point: Calorie expenditure]\nThis agent sets a daily budget.\n\n[Point: Meal recommendation]\nThis one sets the meal target, excludes conflicting meals and picks a relevant recipe.\n\n[Point: Nutrition verification]\nThis one looks up each ingredient and labels estimates.\n\n[Point: Supermarket]\nThis one maps ingredients to products with an estimated cost.\n\nThe meal comes from retrieval, not generation, so the core path needs no LLM key.\n\nReference — not read aloud\ndocs/2_architecture.md; docs/agents/; MealPlanningService.", SOLUTION);
  [["Calorie expenditure", "Estimates daily expenditure and sets the daily budget."], ["Meal recommendation", "Sets the meal target, excludes conflicting meals, picks a relevant recipe and sizes portions."], ["Nutrition verification", "Looks up each ingredient and labels estimates."], ["Supermarket", "Maps ingredients to products with an estimated cost."]].forEach(([h, b], i) => {
    const x = X0 + i * 223;
    card(s, hb(h, b), x, TOP, 204, 212, { margin: 12, valign: "bottom" });
    chip(s, i + 1, x + 12, TOP + 12);
    if (i < 3) arrow(s, x + 206, TOP + 106, x + 221, TOP + 106);
  });
  card(s, [{ text: "One typed JSON response: meal, nutrition, shopping list and warnings", options: { fontFace: HEAD, fontSize: 16, bold: true, color: WHITE } }], X0, 358, W, 56, { fill: INK, margin: 16, valign: "middle" });
  text(s, [{ text: "Note: ", options: { bold: true } }, { text: "the service balances portions after verification. The core path needs no LLM key." }], X0, 424, W, 14, { fontSize: 8, color: MUTED });
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
