// Builds the 12-slide showcase deck to DESIGN.md and docs/showcase/README.md §8.
// Slides stay plain shapes, text and tables so they are editable in Google Slides.
// Run from this folder with pptxgenjs installed and PPTX_SKILL set to the pptx
// skill folder (its apply_theme.js writes the Kitchen green theme into the file).
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const THEME = {
  name: "Kitchen green",
  headFontFace: "Bricolage Grotesque",
  bodyFontFace: "Inter",
  colors: {
    dk1: "15291F", lt1: "FFFFFF", dk2: "4B5B52", lt2: "F6F7F2",
    accent1: "C8431F", accent2: "1B5E3F", accent3: "2F6FAB",
    accent4: "9A6A12", accent5: "7A4E9C", accent6: "DDE3DA",
    hlink: "B23A17", folHlink: "4B5B52",
  },
};
const HEAD = THEME.headFontFace;
const TINT_OK = "E3EFE6", TINT_WARN = "FBEBD6", WARN = "7A4A0C", ON_INK = "C9D3CC";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "AI Meal Planner showcase";
pres.author = "Mike";
pres.theme = { headFontFace: HEAD, bodyFontFace: "Inter" };
const C = pres.SchemeColor;
const INK = C.text1, MUTED = C.text2, WHITE = C.background1, GROUND = C.background2;
const TOMATO = C.accent1, GREEN = C.accent2, LINE = C.accent6;
const L = 0.6, W = 12.13; // left margin, content width

pres.defineSlideMaster({
  title: "DARK",
  background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: L, y: 2.2, w: 8.2, h: 1.0, fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: GROUND },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: L, y: 0.45, w: W, h: 1.2, fontFace: HEAD, fontSize: 30, bold: true, color: INK, align: "left", valign: "top", margin: 0 }, text: "" } },
    { image: { path: "assets/mark.png", x: L, y: 6.92, w: 0.26, h: 0.26 } },
    { text: { text: "AI Meal Planner", options: { x: L + 0.34, y: 6.88, w: 3, h: 0.34, fontSize: 11, color: MUTED, margin: 0, valign: "middle" } } },
  ],
  slideNumber: { x: 12.13, y: 6.88, w: 0.6, h: 0.34, fontSize: 11, color: MUTED, align: "right" },
});

const text = (s, t, o) => s.addText(t, { isTextBox: true, margin: 0, color: INK, fontSize: 15, valign: "top", ...o });
const card = (s, x, y, w, h, fill) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.14, fill: { color: fill || WHITE }, line: { color: fill ? fill : LINE, width: 1 } });
const circle = (s, n, x, y, d = 0.46) =>
  s.addText(String(n), { shape: pres.ShapeType.ellipse, x, y, w: d, h: d, fill: { color: INK }, color: WHITE, fontSize: 14, bold: true, align: "center", valign: "middle", margin: 0 });
const arrow = (s, x1, y1, x2, y2) =>
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipV: y2 < y1, line: { color: MUTED, width: 1.5, endArrowType: "triangle" } });
const slide = (master, title, notes, section) => {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addNotes(notes);
  return s;
};

const STORY = "The product", HOW = "How it works", PROOF = "Quality", END = "Close";
[STORY, HOW, PROOF, END].forEach((title) => pres.addSection({ title }));

// 1 — title
{
  const s = slide("DARK", "AI Meal Planner",
    "Hi, I'm Mike. This is AI Meal Planner, a portfolio project I built end to end. In ten minutes I'll show what it does, how it works and how I measured whether its meals are any good. You can scan the code and try it while I talk.", STORY);
  s.addImage({ path: "assets/mark.png", x: L, y: 1.1, w: 0.8, h: 0.8, altText: "AI Meal Planner plate mark" });
  text(s, [{ text: "Say what you crave.", options: { breakLine: true } }, { text: "Get a meal that " }, { text: "fits you", options: { color: TOMATO, bold: true } }, { text: "." }],
    { x: L, y: 3.3, w: 7.2, h: 1.3, fontFace: HEAD, fontSize: 30, color: WHITE });
  text(s, "A multi-agent meal planner · a portfolio project by Mike", { x: L, y: 4.85, w: 7.2, h: 0.4, fontSize: 16, color: ON_INK });
  card(s, 9.1, 1.75, 3.45, 3.95, WHITE);
  s.addImage({ path: "assets/qr.png", x: 9.45, y: 2.0, w: 2.75, h: 2.75, altText: "QR code to the live demo" });
  text(s, "Scan to try the live demo", { x: 9.3, y: 4.92, w: 3.05, h: 0.4, fontSize: 14, bold: true, align: "center" });
}

// 2 — problem
{
  const s = slide("LIGHT", "Picking a meal is easy; sizing it to your body is not",
    "Most of us know what we feel like eating. The hard part is everything after that: how much suits my body and goal, does it fit my diet, and what do I need to buy. Those are three separate chores today, so this project joins them into one step.", STORY);
  [
    ["How much?", "Calorie needs change with your body, activity and goal."],
    ["Is it right for me?", "Diets, allergies and health conditions rule meals out."],
    ["What do I buy?", "Recipes, nutrition and shopping lists live in different places."],
  ].forEach(([h, b], i) => {
    const x = L + i * 4.16;
    card(s, x, 2.1, 3.81, 3.5);
    circle(s, i + 1, x + 0.35, 2.4);
    text(s, h, { x: x + 0.35, y: 3.05, w: 3.1, h: 0.5, fontFace: HEAD, fontSize: 22, bold: true });
    text(s, b, { x: x + 0.35, y: 3.65, w: 3.1, h: 1.7, fontSize: 18, color: MUTED });
  });
}

// 3 — flow
{
  const s = slide("LIGHT", "One craving in, one meal and a shopping list out",
    "The app is three steps. You say who you are and your goal. You say what you feel like eating. You get one meal sized to you, its macro balance and a shopping list. These are the approved design screens for the React app.", STORY);
  [["1-profile", "You", "Body, goal and what to avoid"], ["2-craving", "Craving", "What you feel like eating"], ["3-plan", "Your plan", "One meal, balance, shopping list"]].forEach(([f, h, b], i) => {
    const x = L + i * 4.16;
    s.addImage({ path: `assets/${f}.jpg`, x, y: 1.75, w: 3.81, h: 2.68, altText: `${h} screen of the app` });
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.75, w: 3.81, h: 2.68, rectRadius: 0.1, fill: { color: WHITE, transparency: 100 }, line: { color: LINE, width: 1 } });
    circle(s, i + 1, x, 4.7);
    text(s, h, { x: x + 0.6, y: 4.67, w: 3.2, h: 0.5, fontFace: HEAD, fontSize: 22, bold: true, valign: "middle" });
    text(s, b, { x: x + 0.6, y: 5.2, w: 3.2, h: 0.8, fontSize: 16, color: MUTED });
    if (i < 2) arrow(s, x + 3.86, 3.09, x + 4.11, 3.09);
  });
}

// 4 — pipeline
{
  const s = slide("LIGHT", "Four agents work in sequence and return one typed answer",
    "Behind the screens is a FastAPI service with four agents. Each does one job and hands on. Because the meal comes from retrieval rather than generation, the core path works with no LLM key at all. Gemini is optional, for a final explanation only.", HOW);
  text(s, "Your profile and craving", { x: L, y: 1.85, w: 4, h: 0.4, fontSize: 16, bold: true, color: MUTED });
  [
    ["Calorie expenditure", "A trained model predicts your daily burn and sets the meal's target"],
    ["Meal recommendation", "Filters unsafe meals, finds the closest recipe, resizes portions"],
    ["Nutrition verification", "Checks each ingredient and labels what is estimated"],
    ["Supermarket", "Maps ingredients to products with an estimated cost"],
  ].forEach(([h, b], i) => {
    const x = L + i * 3.1;
    card(s, x, 2.35, 2.75, 2.85);
    circle(s, i + 1, x + 0.25, 2.55);
    text(s, h, { x: x + 0.25, y: 3.1, w: 2.3, h: 0.75, fontFace: HEAD, fontSize: 18, bold: true });
    text(s, b, { x: x + 0.25, y: 3.85, w: 2.3, h: 1.25, fontSize: 14, color: MUTED });
    if (i < 3) arrow(s, x + 2.78, 3.77, x + 3.07, 3.77);
  });
  card(s, L, 5.5, W, 0.95, INK);
  text(s, "One typed JSON response: meal, nutrition, shopping list and warnings", { x: L + 0.35, y: 5.5, w: W - 0.7, h: 0.95, fontSize: 18, bold: true, color: WHITE, valign: "middle" });
}

// 5 — model
{
  const s = slide("LIGHT", "A model trained on 750,000 rows sets each meal's calorie target",
    "The first agent is a gradient-boosted model trained on a Kaggle dataset of 750,000 rows. On validation data it explains 99.6% of the variance, with a mean error of 2.2 kcal. Your goal then adjusts the target, and weight-loss plans have a hard floor so it never suggests too little.", HOW);
  [["750,000", "training rows"], ["0.996", "R² on validation data"], ["2.2 kcal", "mean error"]].forEach(([n, l], i) => {
    const x = L + i * 4.16, dark = i === 0;
    card(s, x, 1.95, 3.81, 2.5, dark ? INK : undefined);
    text(s, n, { x: x + 0.35, y: 2.3, w: 3.2, h: 1.1, fontFace: HEAD, fontSize: 54, bold: true, color: dark ? WHITE : INK, valign: "middle" });
    text(s, l, { x: x + 0.35, y: 3.5, w: 3.2, h: 0.5, fontSize: 16, color: dark ? ON_INK : MUTED });
  });
  card(s, L, 4.75, W, 1.45, TINT_OK);
  text(s, "Safety floor", { x: L + 0.35, y: 4.93, w: 4, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: GREEN });
  text(s, "Weight-loss plans never go below 1,200 kcal a day for women or 1,500 for men.", { x: L + 0.35, y: 5.38, w: W - 0.7, h: 0.5, fontSize: 18 });
}

// 6 — retrieval
{
  const s = slide("LIGHT", "Diet and allergy filters run first, then search finds the closest tested recipe",
    "Safety comes before relevance. Conflicting meals are removed first, then vector search looks through 34 tested recipes. If nothing is genuinely close, it doesn't pretend. You get a standard meal and a note saying so, and if nothing is safe it refuses.", HOW);
  const y = 2.45, h = 2.2;
  [["Your craving", "and profile"], ["Safety filters", "Diet, allergy and health conditions"], ["Recipe search", "Vector RAG over 34 tested recipes"]].forEach(([a, b], i) => {
    const x = L + i * 2.95, w = 2.55;
    card(s, x, y, w, h);
    text(s, a, { x: x + 0.22, y: y + 0.35, w: w - 0.44, h: 0.5, fontFace: HEAD, fontSize: 18, bold: true });
    text(s, b, { x: x + 0.22, y: y + 0.9, w: w - 0.44, h: 1.1, fontSize: 14, color: MUTED });
    arrow(s, x + w + 0.04, y + h / 2, x + 2.91, y + h / 2);
  });
  const ox = 9.45, ow = 3.28;
  card(s, ox, 1.95, ow, 1.45, TINT_OK);
  text(s, "Close match", { x: ox + 0.25, y: 2.1, w: ow - 0.5, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: GREEN });
  text(s, "That recipe, sized to you", { x: ox + 0.25, y: 2.55, w: ow - 0.5, h: 0.6, fontSize: 14 });
  card(s, ox, 3.55, ow, 1.45, TINT_WARN);
  text(s, "No close match", { x: ox + 0.25, y: 3.7, w: ow - 0.5, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: WARN });
  text(s, "A standard meal and a note saying so", { x: ox + 0.25, y: 4.15, w: ow - 0.5, h: 0.6, fontSize: 14 });
  card(s, ox, 5.15, ow, 1.25);
  text(s, "Nothing safe", { x: ox + 0.25, y: 5.27, w: ow - 0.5, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true });
  text(s, "The plan is refused, not guessed", { x: ox + 0.25, y: 5.72, w: ow - 0.5, h: 0.5, fontSize: 14 });
}

// 7 — verification
{
  const s = slide("LIGHT", "Every ingredient is checked against USDA, and estimates are labelled",
    "Nutrition is looked up per ingredient: USDA FoodData Central first, then FatSecret, then local tables. Whatever the source, the screen says so. In this example half the ingredients use estimates, and the app tells you. Being honest about that matters more to me than looking precise.", HOW);
  const badge = (t, ok) => ({ text: t, options: { color: ok ? MUTED : WARN, bold: !ok, fill: { color: ok ? "ECEFE8" : TINT_WARN } } });
  const cell = (t, o) => ({ text: t, options: o || {} });
  const rows = [
    [cell("Ingredient", { bold: true, color: MUTED }), cell("Amount", { bold: true, color: MUTED, align: "right" }), cell("Source", { bold: true, color: MUTED })],
    ...[["Cooked white rice", "200 g", 0], ["Mixed vegetables", "105 g", 1], ["Chicken breast", "85 g", 0], ["Whole egg", "45 g", 1], ["Soy sauce", "15 g", 0], ["Sesame oil", "10 g", 1]]
      .map(([n, a, ok]) => [cell(n), cell(a, { align: "right", bold: true }), badge(ok ? "Reference" : "Estimated", ok)]),
  ];
  card(s, L, 1.85, 7.3, 4.65);
  text(s, "Chicken Fried Rice", { x: L + 0.3, y: 2.0, w: 6.7, h: 0.45, fontFace: HEAD, fontSize: 20, bold: true });
  s.addTable(rows, { x: L + 0.3, y: 2.5, w: 6.7, colW: [3.5, 1.2, 2.0], rowH: 0.52, fontSize: 15, color: INK, fontFace: "Inter", valign: "middle", border: { type: "none" } });
  const x = 8.25, w = 4.48;
  text(s, "Where the numbers come from", { x, y: 1.9, w, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true });
  ["USDA FoodData Central", "FatSecret, if configured", "Local reference tables"].forEach((t, i) => {
    const y = 2.55 + i * 1.12;
    card(s, x, y, w, 0.82);
    circle(s, i + 1, x + 0.2, y + 0.18);
    text(s, t, { x: x + 0.82, y, w: w - 1, h: 0.82, fontSize: 16, valign: "middle" });
    if (i < 2) arrow(s, x + w / 2, y + 0.85, x + w / 2, y + 1.09);
  });
  card(s, x, 5.75, w, 0.75, TINT_WARN);
  text(s, "Here, 3 of 6 ingredients are estimates", { x: x + 0.25, y: 5.75, w: w - 0.4, h: 0.75, fontSize: 15, bold: true, color: WARN, valign: "middle" });
}

// 8 — targets
{
  const s = slide("LIGHT", "We defined a good meal before trying to improve one",
    "Before changing anything I fixed what good means. A plan passes only if its calories are within 10% of target and each macro sits inside the adult AMDR ranges. The test set is 72 fixed requests across four body profiles and four diet or health limits. It runs offline and gives identical results every time.", PROOF);
  card(s, L, 1.85, 7.9, 4.65);
  text(s, "Share of the meal's energy", { x: L + 0.35, y: 2.05, w: 7, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true });
  const bx = L + 0.35, bw = 7.2;
  [["Protein", 10, 35, C.accent3], ["Carbs", 45, 65, C.accent4], ["Fat", 20, 35, C.accent5]].forEach(([n, a, b, col], i) => {
    const y = 2.7 + i * 1.15;
    text(s, n, { x: bx, y, w: 3, h: 0.35, fontSize: 16, bold: true });
    text(s, `${a}–${b}%`, { x: bx + bw - 2, y, w: 2, h: 0.35, fontSize: 16, bold: true, align: "right", color: col });
    s.addShape(pres.ShapeType.roundRect, { x: bx, y: y + 0.45, w: bw, h: 0.24, rectRadius: 0.12, fill: { color: "ECEFE8" }, line: { color: "ECEFE8", width: 0.5 } });
    s.addShape(pres.ShapeType.roundRect, { x: bx + (bw * a) / 100, y: y + 0.45, w: (bw * (b - a)) / 100, h: 0.24, rectRadius: 0.12, fill: { color: col }, line: { color: col, width: 0.5 } });
  });
  const x = 8.85, w = 3.88;
  card(s, x, 1.85, w, 2.2, INK);
  text(s, "Within 10%", { x: x + 0.3, y: 2.1, w: w - 0.6, h: 0.95, fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, valign: "middle" });
  text(s, "of the calorie target", { x: x + 0.3, y: 3.1, w: w - 0.6, h: 0.5, fontSize: 16, color: ON_INK });
  card(s, x, 4.3, w, 2.2);
  text(s, "72 requests", { x: x + 0.3, y: 4.5, w: w - 0.6, h: 0.75, fontFace: HEAD, fontSize: 32, bold: true, valign: "middle" });
  text(s, "4 body profiles, 4 diet or health limits, offline and repeatable", { x: x + 0.3, y: 5.3, w: w - 0.6, h: 1.0, fontSize: 15, color: MUTED });
}

// 9 — results
{
  const s = slide("LIGHT", "Three fixes took the planner from 10 to 72 of 72",
    "The first run passed only 10 of 72. Balancing portions per ingredient took it to 41. Making the planner admit when nothing matches took it to 47. Adding a cooking fat to six recipes that had none took it to all 72, with a median calorie deviation of 0.3%. Five guardrail cases, including refusals, also behave as designed.", PROOF);
  card(s, L, 1.75, 7.3, 4.8);
  s.addChart(pres.charts.BAR, [{ name: "Plans meeting the targets", labels: ["First run", "Portion balancing", "Honest fallback", "Cooking fat"], values: [10, 41, 47, 72] }], {
    x: L + 0.2, y: 1.9, w: 6.9, h: 4.5, barDir: "col", chartColors: ["1B5E3F"], barGapWidthPct: 55,
    showTitle: true, title: "Plans meeting the targets, out of 72", titleFontSize: 14, titleColor: "4B5B52", titleFontFace: "Inter",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelColor: "15291F", dataLabelFontFace: "Inter",
    catAxisLabelColor: "4B5B52", catAxisLabelFontSize: 12, catAxisLabelFontFace: "Inter",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 80, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
  });
  const x = 8.25, w = 4.48;
  [["Portion balancing", "Resize each ingredient toward the ranges"], ["Honest fallback", "Say so when nothing on the menu matches"], ["Cooking fat", "Add oil to six recipes that had no fat source"]].forEach(([h, b], i) => {
    const y = 1.75 + i * 1.27;
    circle(s, i + 1, x, y + 0.03);
    text(s, h, { x: x + 0.62, y, w: w - 0.62, h: 0.42, fontFace: HEAD, fontSize: 18, bold: true });
    text(s, b, { x: x + 0.62, y: y + 0.44, w: w - 0.62, h: 0.7, fontSize: 14, color: MUTED });
  });
  card(s, x, 5.55, w, 1.0, INK);
  text(s, [{ text: "0.3%", options: { fontFace: HEAD, fontSize: 26, bold: true, color: WHITE } }, { text: "  median calorie deviation", options: { fontSize: 14, color: ON_INK } }], { x: x + 0.3, y: 5.55, w: w - 0.5, h: 1.0, valign: "middle" });
}

// 10 — engineering
{
  const s = slide("LIGHT", "It is built like a product, not a notebook",
    "Although it's a portfolio project, I held it to production habits. The API contract is committed and CI fails if it drifts. There are 596 Python tests at 95% coverage. It has API keys and rate limits, tracing that keeps health data out of traces, and a Cloud Run deployment workflow that is ready for a GCP project.", HOW);
  [
    ["Typed API contract", "FastAPI and Pydantic; OpenAPI checked in CI"],
    ["Tested", "596 Python tests at 95% coverage"],
    ["Secured", "API keys, rate limits, no history in hosted mode"],
    ["Deployable", "Containers and a Cloud Run workflow"],
    ["Observable", "OpenTelemetry tracing, health data kept out"],
    ["Two clients", "A live Streamlit demo and a React app"],
  ].forEach(([h, b], i) => {
    const x = L + (i % 3) * 4.16, y = 1.75 + Math.floor(i / 3) * 2.45;
    card(s, x, y, 3.81, 2.2);
    text(s, h, { x: x + 0.32, y: y + 0.32, w: 3.2, h: 0.5, fontFace: HEAD, fontSize: 20, bold: true });
    text(s, b, { x: x + 0.32, y: y + 0.92, w: 3.2, h: 1.1, fontSize: 16, color: MUTED });
  });
}

// 11 — next
{
  const s = slide("LIGHT", "What comes next, and what it is not yet",
    "The next steps are a larger recipe library, using feedback to learn preferences, and a real cloud deployment. And to be clear about limits: prices are estimates from a local list, some nutrition comes from local tables, and this is a study project, not medical advice.", END);
  const col = (x, h, items, fill, hc) => {
    card(s, x, 1.75, 5.9, 4.75, fill);
    text(s, h, { x: x + 0.4, y: 2.0, w: 5.1, h: 0.5, fontFace: HEAD, fontSize: 22, bold: true, color: hc || INK });
    items.forEach((t, i) => {
      const y = 2.75 + i * 1.15;
      circle(s, i + 1, x + 0.4, y + 0.02);
      text(s, t, { x: x + 1.02, y, w: 4.5, h: 0.95, fontSize: 18 });
    });
  };
  col(L, "Next", ["A larger recipe library", "Learn from user feedback", "A live deployment on Cloud Run"]);
  col(L + 6.23, "Not yet", ["Prices are estimates, not live store data", "Some nutrition uses labelled estimates", "A study project, not medical advice"], TINT_WARN, WARN);
}

// 12 — close
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: END });
  s.addText("Try it and read the code", { placeholder: "title" });
  s.addNotes("That's AI Meal Planner: one craving in, one meal that fits you, and all 72 test plans on target. The demo and code are here. Thanks, and I'm happy to take questions.");
  text(s, "tuannm3812-ai-meal-planner.streamlit.app", { x: L, y: 3.75, w: 7.6, h: 0.4, fontSize: 18, bold: true, color: WHITE, hyperlink: { url: "https://tuannm3812-ai-meal-planner.streamlit.app/" } });
  text(s, "github.com/tuannm3812/ai-meal-planner", { x: L, y: 4.25, w: 7.6, h: 0.4, fontSize: 18, color: ON_INK, hyperlink: { url: "https://github.com/tuannm3812/ai-meal-planner" } });
  text(s, "A study project. Not medical advice.", { x: L, y: 5.0, w: 7.6, h: 0.4, fontSize: 14, color: ON_INK });
  card(s, 9.1, 1.75, 3.45, 3.95, WHITE);
  s.addImage({ path: "assets/qr.png", x: 9.45, y: 2.0, w: 2.75, h: 2.75, altText: "QR code to the live demo" });
  text(s, "Scan to try the live demo", { x: 9.3, y: 4.92, w: 3.05, h: 0.4, fontSize: 14, bold: true, align: "center" });
}

(async () => {
  const out = process.argv[2] || "ai-meal-planner-deck.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
