# Generated slide brief

Edit brief-content.json, then rebuild.

## 1. What should I eat tonight?

Layout: cover

Reader question: What is this project, and why should a reader care?

Message: Introduce the app through the question everyone asks.

Exact face text:

- PERSONAL PROJECT | MULTI-AGENT MEAL PLANNER
- What should I eat tonight?
- One meal sized to your body and goal, each ingredient's source shown, and the shopping / list ready.
- Mike
- Personal portfolio project
- November 2026

## 2. Agenda

Layout: agenda

Reader question: Which sections are in this deck, and where do they begin?

Message: Locate each section by its page number.

Exact face text:

- AI Meal Planner
- 2
- Agenda
- 1
- Overview
- 3
- One-page summary
- 4
- Why it matters
- 2
- How it works
- 5
- The flow
- 6
- Four agents
- 7
- Calorie target
- 8
- Choosing the meal
- 9
- Nutrition
- 3
- Evidence
- 10
- What good means
- 11
- Results
- 12
- Architecture
- 13
- Engineering
- 4
- Limits and next steps
- 14
- Limits
- 15
- Next steps

## 3. One craving, sized to four different people

Layout: research_summary

Reader question: What does the planner do, and how well does it work?

Message: The meal fits the person, and every number says where it came from; the benchmark is the project's own, not a user study.

Exact face text:

- 1
- 2
- 3
- 4
- OVERVIEW
- One-page summary
- One craving, sized to four different people
- Four agents and 34 curated recipes size the same chicken fried rice for each person, with no LLM key needed.
- AI Meal Planner
- 3
- The problem
- A recipe gives one size for everyone. Daily needs differ, diets rule meals out, and the shopping / is left to you.
- The approach
- Four agents turn one craving into one meal: a calorie budget, a safe recipe, a nutrition lookup / and a priced shopping list.
- Sized to you: 363 to 850 kcal
- The same chicken fried rice runs from 363 kcal for an older woman losing weight to 850 / kcal for a large athlete gaining.
- On target: 72 of 72 plans
- Every plan in the project's own offline benchmark meets the calorie and macro targets, / up from 10. Median calorie gap 0.4%.
- Fits your limits: 5 of 5
- Diets, allergies and conditions rule out recipes or swap ingredients first. All five / guardrail cases behave as designed.
- Honest about gaps: 68 of 72
- 68 of 72 plans include an estimated ingredient, and 11 of 72 are fallback meals. The app / labels both.
- TAKEAWAY
- The meal fits the person, and every number says where it came from; the benchmark is the project's own, not a user study.

## 4. Picking a meal is easy; sizing it to you is not

Layout: panels

Reader question: Why is this worth solving?

Message: One request answers all three; the Today lines are this project's framing, not survey results.

Exact face text:

- 1
- 2
- 3
- 4
- OVERVIEW
- Why it matters
- Picking a meal is easy; sizing it to you is not
- Three questions sit between a craving and a meal you can trust.
- AI Meal Planner
- 4
- How much?
- Daily budgets in the benchmark run from 1,200 to / 4,521 kcal.
- Today: guess from "serves 4".
- With the app: a budget, then a meal target.
- Is it right for me?
- Asked for pasta, a vegan gets lentil bolognese and a / coeliac gets gluten-free pasta.
- Today: read every label.
- With the app: conflicts ruled out or swapped first.
- What do I buy?
- This one pasta means five ingredients to find and / price.
- Today: write a list, guess the cost.
- With the app: a list with an estimated total.
- TAKEAWAY
- One request answers all three; the Today lines are this project's framing, not survey results.

## 5. One craving in, one meal and a shopping list out

Layout: figure_evidence

Reader question: What does a person actually do?

Message: Two short screens lead to one plan page that shows how it was made.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- The flow
- One craving in, one meal and a shopping list out
- Three steps in the React app, captured from a local run with no provider keys.
- AI Meal Planner
- 5
- 1. You
- 2. Craving
- 3. Your plan
- Real captures of the React app, 6 November 2026.
- Source: AI Meal Planner React app, local run with no provider keys, 6 November 2026
- TAKEAWAY
- Two short screens lead to one plan page / that shows how it was made.
- 1
- 1
- Body, goal and limits first
- The planner asks only what it needs to size a meal.
- 2
- 2
- Then the craving and the store
- One free-text craving, such as chicken fried rice.
- 3
- 3
- The plan shows its working
- 694 kcal against a 691 kcal target, the macro / balance and each ingredient's source.

## 6. Four agents work like one kitchen

Layout: process

Reader question: How does one request become one plan?

Message: Meals come from 34 curated recipes, not generation, so the core path needs no LLM key.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Four agents
- Four agents work like one kitchen
- A planning service runs them in order for one request: chicken fried rice, active woman, maintaining.
- AI Meal Planner
- 6
- Calorie expenditure
- Estimates a day's burn and sets the / budget: 2,469 kcal.
- Meal recommendation
- Sets the meal target, rules out conflicts, / picks a recipe and sizes it: 691 kcal.
- Nutrition verification
- Looks up each ingredient and labels / estimates: 694 kcal, 3 of 6 estimated.
- Supermarket
- Matches ingredients to store items or / category prices: $24.50 estimated.
- TAKEAWAY
- Meals come from 34 curated recipes, not generation, so the core path needs no LLM key.

## 7. The trained model adds only 125 kcal to her day

Layout: chart

Reader question: How does it decide how much?

Message: The model's R² of 0.996 is for exercise calories, which add 3–10% of the day in these plans.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Calorie target
- The trained model adds only 125 kcal to her day
- Worked example: an active woman keeping her weight. Her meal target is 28% of the daily budget.
- AI Meal Planner
- 7
- kcal
- Body and activity (BMR)
- 2344
- Exercise (trained model)¹
- 125
- Daily budget
- 2469
- This meal (28%)
- 691
- 0
- 2500
- Note: ¹ Exercise inputs use defaults (30 minutes, 100 bpm), and the activity multiplier may already count that exercise.
- TAKEAWAY
- The model's R² of 0.996 is for exercise calories, which add 3–10% of the day in these plans.

## 8. Hard limits come first, then a relevant recipe

Layout: chart

Reader question: How does it choose the meal?

Message: Safety comes before relevance; across the benchmark, 61 of 72 plans match the craving and 11 fall back with a note.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Choosing the meal
- Hard limits come first, then a relevant recipe
- A vegan asks for chicken fried rice: the recipes narrow down to one.
- AI Meal Planner
- 8
- recipes
- All recipes
- 34
- Safe for a vegan
- 13
- Relevant to the craving
- 5
- Served: Tofu Fried Rice
- 1
- 0
- 34
- TAKEAWAY
- Safety comes before relevance; across the benchmark, 61 of 72 plans match the craving and 11 fall back with a note.

## 9. Three of six ingredients are estimates, carrying 66% of the calories

Layout: comparison

Reader question: Can you trust the numbers?

Message: Lookup order is trusted local values, then USDA and FatSecret with keys, then estimates; here nothing is externally verified.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Nutrition
- Three of six ingredients are estimates, carrying 66% of the calories
- Chicken fried rice from a local run with no USDA or FatSecret keys: 694 kcal against a 691 kcal target.
- AI Meal Planner
- 9
- Source
- Ingredients, amount and kcal
- Share of 694 kcal
- Estimated
- Chicken breast, 100 g: 165 kcal
- Cooked rice, 220 g: 286 kcal
- Soy sauce, 15 g: 8 kcal
- 459 kcal, 66%
- Reference
- Whole egg, 50 g: 72 kcal
- Mixed vegetables, 115 g: 75 kcal
- Sesame oil, 10 g: 88 kcal
- 235 kcal, 34%
- TAKEAWAY
- Lookup order is trusted local values, then USDA and FatSecret with keys, then estimates; here nothing is externally verified.

## 10. We defined a good meal before improving one

Layout: panels

Reader question: What counts as good?

Message: At the first run 68 of 72 plans hit calories, but only 10 cleared both tests.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- What good means
- We defined a good meal before improving one
- A plan passes only if it clears both tests, on a fixed set of 72 requests run offline.
- AI Meal Planner
- 10
- Test 1: calories
- Within 10% of the meal's calorie target.
- Test 2: macros
- Protein 10–35% of energy
- Carbs 45–65%
- Fat 20–35%
- 72 fixed requests
- 12 cravings × 4 body profiles
- 6 cravings × 4 diet or health limits
- Note: AMDR is a daily reference, applied here to one meal.
- TAKEAWAY
- At the first run 68 of 72 plans hit calories, but only 10 cleared both tests.

## 11. Three fixes took the planner from 10 to 72 of 72

Layout: chart

Reader question: Did it get better, and why?

Message: The 41 to 47 step moved 11 off-menu requests to fallback meals; a wider check of every recipe by name passes 68 of 68.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Results
- Three fixes took the planner from 10 to 72 of 72
- Plans meeting both targets on the project's own offline benchmark of 72 requests.
- AI Meal Planner
- 11
- plans meeting both targets¹
- First run
- 10
- Portion balancing
- 41
- Honest fallback
- 47
- Cooking fat, rounding retry
- 72
- 0
- 72
- Note: ¹ Out of 72 benchmark requests. Median calorie gap 0.4%, worst 9.9%; 5 of 5 guardrail cases hold. This shows plans meet targets, not that users prefer them.
- TAKEAWAY
- The 41 to 47 step moved 11 off-menu requests to fallback meals; a wider check of every recipe by name passes 68 of 68.

## 12. One service, two clients, four agents

Layout: process

Reader question: What is it made of?

Message: The one trained model is 0.64 MB and TF-IDF suits 34 recipes, so the core path needs no GPU.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Architecture
- One service, two clients, four agents
- Streamlit and React share one FastAPI contract and one planning service.
- AI Meal Planner
- 12
- Clients
- A live Streamlit demo and a React app / (Vite, Tailwind).
- FastAPI
- Typed JSON with Pydantic, API keys / and rate limits; local history in SQLite.
- Planning service
- Four agents plus a balance step: / scikit-learn model, TF-IDF search, / SciPy portions.
- Delivery
- Python, Docker, GitHub Actions; Cloud / Run ready but not yet deployed.
- TAKEAWAY
- The one trained model is 0.64 MB and TF-IDF suits 34 recipes, so the core path needs no GPU.

## 13. Built like a product, not a notebook

Layout: panels

Reader question: Is the engineering real?

Message: Health data is kept out of traces by a test, but no trace has reached Cloud Trace yet.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Engineering
- Built like a product, not a notebook
- Production habits on a portfolio project, each with a file behind it.
- AI Meal Planner
- 13
- Tested
- 630 Python tests, all passing
- 95% coverage, 89% floor in CI
- Checked on every change
- 5 CI checks per pull request
- API contract fails CI on drift
- Ready to ship
- One Docker image
- Cloud Run workflow, not yet live
- TAKEAWAY
- Health data is kept out of traces by a test, but no trace has reached Cloud Trace yet.

## 14. What this project does not prove yet

Layout: evidence

Reader question: What is unproven?

Message: A planning aid, not medical advice.

Exact face text:

- 1
- 2
- 3
- 4
- LIMITS AND NEXT STEPS
- Limits
- What this project does not prove yet
- Results measured offline, with estimated inputs and no users.
- AI Meal Planner
- 14
- TAKEAWAY
- A planning aid, not medical advice.
- 1
- Measured: targets met offline
- 72 of 72 and 68 of 68, but the same checks guided the fixes; 11 of 72 fall back.
- 1
- Solid, within its scope
- The run is repeatable, but it measures plans against / targets, not taste or health.
- 2
- Estimated: inputs
- 68 of 72 plans include an estimate; exercise inputs are defaults; diet rules match ingredient names.
- 2
- Soft where inputs are guessed
- Name matching missed soy sauce until this review; / it is now fixed.
- 3
- Not tested: people
- No users, no clinical review, not deployed, no database migrations.
- 3
- Unknown until people use it
- Only testing with people can show that the plans / help.

## 15. What comes next, in priority order

Layout: comparison

Reader question: What comes next?

Message: Each step answers a limit on the previous page.

Exact face text:

- 1
- 2
- 3
- 4
- LIMITS AND NEXT STEPS
- Next steps
- What comes next, in priority order
- Foundations first, then better inputs, then scale and people.
- AI Meal Planner
- 15
- Now
- Next
- Later
- Add database migrations
- Run the benchmark with USDA keys
- Grow to 75–100 recipes
- Deploy to Cloud Run
- Ask for real exercise details
- Connect live store prices
- Add user accounts
- Tag allergens on ingredients
- Use feedback, then test with people
- TAKEAWAY
- Each step answers a limit on the previous page.

## 16. Try it and read the code

Layout: close

Reader question: Where do I try it?

Message: Point to the demo and code.

Exact face text:

- THANK YOU
- Try it and read the code
- tuannm3812-ai-meal-planner.streamlit.app · github.com/tuannm3812/ai-meal-planner
- A multi-agent meal planner, a personal project by Mike
- A study project. Not medical advice.
