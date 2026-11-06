# Speaker notes — AI Meal Planner deck

Generated from the seed on 7 November 2026; keep aligned with the live deck's notes.
Pattern: slides/DESIGN.md, Speaker notes.

## Slide 1 — p1

Everyone asks this question, so that's where this project starts.
[Point: search bar]
You type a craving.
[Point: plate labels]
You get one meal sized to you, and each ingredient says where its number came from.
[Point: shopping list]
The shopping list is already written.
The rest of this deck shows how it works and how I measured it.
Reference — not read aloud
Values are the real local run of 6 November 2026: slides/captures/2026-11-06-plan.json. The plate is an illustration, slides/build_cover_art.py.

## Slide 2 — p2

If you read one slide, read this one.
[Point: four plates]
This is the same craving for four people. It runs from 363 kcal for an older woman losing weight to 850 for a large athlete gaining, so the meal fits the person. Meal targets stay within 350 to 850 kcal, so the first and last plates sit at those limits.
[Point: 72 of 72]
That quality is measured: all 72 plans in the project's own benchmark meet the targets, up from 10.
[Point: Balanced and checked]
Four features do that work, and it stays honest: estimates are labelled, and it says so when nothing matches.
The rest of the deck shows how it works and how that number was reached.
Reference — not read aloud
docs/meal_quality/baseline.json, chicken fried rice rows; fact sheet, docs/showcase/README.md; docs/7_meal_quality.md §2. These are a measure of plans, not of real users.

## Slide 3 — p3

This deck is served as a four-course menu.
[Point: Starter]
First, why this is worth solving.
[Point: Main]
Then what it does and how it works.
[Point: Taste test]
Then what a good meal means, and whether it got there.
[Point: The bill]
Last, how it's built and what isn't proven yet.
Each page is a link, so you can jump straight to it.

## Slide 4 — p4

Most of us know what we feel like eating. The hard part comes after that.
[Point: How much?]
The right amount depends on the person. Across the four benchmark profiles, daily budgets run from 1,200 to 4,521 kcal.
[Point: Is it right for me?]
The same request changes with your limits. A vegan gets a different recipe, and a coeliac keeps the recipe with gluten-free pasta.
[Point: What do I buy?]
This one pasta means five ingredients to find and price.
[Point: Today, With the app]
Each question has a manual habit today, and each card shows what the app does in its place.
The next section shows how one request answers all three.
Reference — not read aloud
The three questions and the Today lines are the project's framing, from docs/1_brief.md, not research findings. Budgets: docs/meal_quality/baseline.json. Pasta examples: a local run of the craving "pasta" for the average man, 7 November 2026, no provider keys.

## Slide 5 — p5

This is the real React app, in three steps.
[Point: You]
You enter your body, goal and anything to avoid.
[Point: Craving]
You say what you feel like eating and where you shop.
[Point: Your plan]
You get one meal, its balance, each ingredient's source and a shopping list. The badges say how it matched and what is estimated.
Next, what happens behind these screens.
Reference — not read aloud
Captured 6 November 2026 from a local run with no provider keys: slides/captures/2026-11-06-plan.json. frontend/src/features/flow/MealFlow.jsx.

## Slide 6 — p6

Behind the screens is a FastAPI service, and it works like a kitchen.
[Point: The portion planner]
The calorie agent sets a daily budget.
[Point: The chef]
The recommendation agent sets the meal target, excludes conflicting meals and picks a relevant recipe.
[Point: The taster]
The nutrition agent looks up each ingredient and labels estimates.
[Point: The shopper]
The supermarket agent matches ingredients to store items or category prices, with an estimated total.
[Point: white labels]
The white labels follow one real order: a 2,469 kcal budget, a 691 kcal target, 694 kcal served and a $24.50 estimated basket.
The meal comes from retrieval, not generation, so the core path needs no LLM key.
Reference — not read aloud
docs/2_architecture.md; docs/agents/; MealPlanningService. The kitchen roles are a metaphor for the agents.

## Slide 7 — p7

How does it decide how much? It's a short calculation, not one model.
[Point: Exercise calories]
The trained model predicts exercise calories.
[Point: Daily estimate]
Those are added to a BMR-based daily estimate.
[Point: Goal]
Your goal then adjusts it.
[Point: Meal target]
The meal target is 28% of the daily budget, kept between 350 and 850 kcal.
The model's scores describe exercise calories only, not daily needs.
Reference — not read aloud
metrics.json; docs/agents/calorie_expenditure_agent.md; calorie_expenditure_agent.py; meal_recommendation_agent.py; DEC-24; docs/8_design.md §3.1. In the meal flow, exercise inputs use defaults: 30 minutes, 100 bpm.

## Slide 8 — p8

This is how it picks the meal.
[Point: Relevance and limits]
The craving is compared with each recipe, and anything that conflicts with your diet, allergies or conditions is excluded.
[Point: Ranking]
Relevance decides what qualifies. Your profile only influences the order.
Then there are three honest outcomes.
[Point: No close match]
If nothing is close, you get a standard meal and a note saying so.
[Point: Nothing safe]
If nothing is safe, it refuses.
Reference — not read aloud
docs/agents/meal_recommendation_agent.md; backend/app/rag/retriever.py; DEC-27.

## Slide 9 — p9

Can you trust the numbers? Each one shows where it came from.
[Point: Source column]
This is a real plan. Three of its six ingredients are estimates, and the app says so.
[Point: Lookup order]
A trusted local reference comes first. Otherwise it tries cached or provider lookups, USDA and then FatSecret if configured, and last a local or category estimate.
A reference value isn't an external verification either, so the plan's totals are approximate.
Reference — not read aloud
backend/app/agents/nutrition_verification_agent.py. Run of 6 November 2026: 694 kcal against a 691 kcal target, 28/46/26% split; profile 34, male, 165 cm, 65 kg, moderately active, maintain.

## Slide 10 — p10

Before changing anything, I fixed what good means.
[Point: Macro bands]
Each macro has to sit inside the adult AMDR range, as a share of the meal's energy.
[Point: Within 10%]
Calories have to land within 10% of the target.
[Point: 72 requests]
A plan passes only if all of that holds, on a fixed set of 72 requests.
One limit: AMDR is a daily reference, applied here to one meal.
Reference — not read aloud
docs/7_meal_quality.md §1; DEC-25.

## Slide 11 — p11

The first run passed only 10 of 72.
[Point: Portion balancing]
Resizing each ingredient toward the ranges took it to 41, with the same meals.
[Point: Honest fallback]
The relevance gate moved 11 off-menu scenarios to fallback meals, which took it to 47.
[Point: Cooking fat and rounding retry]
Adding a fat to six recipes, and a retry after rounding, took it to all 72.
This shows plans meet the targets. It doesn't show that people prefer them.
Reference — not read aloud
docs/7_meal_quality.md §2; docs/meal_quality/baseline.md; DEC-26 to DEC-28.

## Slide 12 — p12

Although this is a portfolio project, I held it to production habits.
[Point: Typed API contract]
The API contract is committed, and CI fails if it drifts.
[Point: Tested]
The last full run logged 598 Python tests at 95% coverage.
[Point: Deployable]
The Cloud Run workflow is ready, but it isn't deployed to a GCP project yet.
Each of these has a file behind it in the repo.
Reference — not read aloud
docs/openapi.json; .github/workflows/; docs/6_deployment.md; docs/5_agent_log.md, 2026-11-02.

## Slide 13 — p13

Here are the next steps and the limits, side by side.
[Point: Next]
A larger recipe library, learning from feedback, and a live deployment.
[Point: Not yet]
Prices are local estimates, nutrition isn't fully verified, and it hasn't been tested with users or clinicians.
It's a planning aid, not medical advice.
Reference — not read aloud
docs/4_next_steps.md §6 and §7.

## Slide 14 — p14

That's AI Meal Planner: one craving in, one meal sized to you, and every number showing how it was produced.
[Point: QR code]
The demo and code are here.
Reference — not read aloud
README.md.
