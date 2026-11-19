# Generated slide brief

Edit brief-content.json, then rebuild.

## 1. What should I eat tonight?

Layout: mp_cover

Reader question: What is this project, and why should a reader care?

Message: Introduce the app through the question everyone asks.

Exact face text:

- PERSONAL PROJECT | MULTI-AGENT MEAL PLANNER
- What should I eat tonight?
- One meal sized to your body and goal, each ingredient's source shown, and the shopping / list ready.
- Manh Tuan (Mike) Nguyen
- TD School, University of Technology Sydney
- November 2026
- Chicken breast, 100 g
- Estimated
- Cooked rice, 220 g
- Estimated
- Vegetables, 115 g
- Reference
- 694 kcal, target 691
- SHOPPING LIST
- CHICKEN BREAST
- $7.80
- COOKED RICE
- $3.20
- WHOLE EGG
- $3.50
- VEGETABLES
- $3.50
- SESAME OIL
- $3.50
- SOY SAUCE
- $3.00
- ESTIMATED
- $24.50

## 2. Agenda

Layout: mp_agenda

Reader question: Which sections are in this deck, and where do they begin?

Message: Locate each section by its page number.

Exact face text:

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
- AI Meal Planner
- 2

## 3. One craving, sized to four different people

Layout: mp_summary

Reader question: What does the planner do, and how well does it work?

Message: Plate area shows calories. All figures come from the project's own offline benchmark, not a user study.

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
- TAKEAWAY
- Plate area shows calories. All figures come from the project's own offline benchmark, not a user study.
- 363 kcal
- 26 g protein
- Older woman, losing / weight
- 694 kcal
- 48 g protein
- Active woman, / maintaining
- 809 kcal
- 60 g protein
- Average man, / maintaining
- 850 kcal
- 63 g protein
- Large athlete, gaining
- Sized to you
- 0.4%
- Median gap between each meal and its / target, worst 9.9%.
- worst
- median
- -10%
- target
- +10%
- On target
- 72 of 72
- Benchmark plans meet the calorie and / macro targets, up from 10.
- Dark: the 10 that passed at the first run
- Fits your limits
- 5 of 5
- Guardrail cases hold: limits rule out / recipes or swap ingredients.
- Honest about gaps
- 68 of 72
- Plans include an estimated ingredient, / and the app labels each one.
- Dark: plans with an estimated ingredient

## 4. Picking a meal is easy; sizing it to you is not

Layout: mp_problem

Reader question: Why is this worth solving?

Message: The Today lines are this project's framing of the problem, not survey results.

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
- TAKEAWAY
- The Today lines are this project's framing of the problem, not survey results.
- I feel like pasta tonight.
- 1
- 2
- 3
- One request answers all three.
- 1
- How much?
- Daily budgets in the benchmark run from 1,200 / to 4,521 kcal.
- TODAY
- Guess from "serves 4"
- WITH THE APP
- A budget, then a meal / target
- 2
- Is it right for me?
- Asked for pasta, a vegan gets lentil bolognese / and a coeliac gets gluten-free pasta.
- TODAY
- Read every label
- WITH THE APP
- Conflicts ruled out or / swapped first
- 3
- What do I buy?
- This one pasta means five ingredients to find / and price.
- TODAY
- Write a list, guess the / cost
- WITH THE APP
- A list with an estimated / total

## 5. One craving in, one meal and a shopping list out

Layout: mp_flow

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
- TAKEAWAY
- Two short screens lead to one plan page that shows how it was made.
- 1. You
- Goal, body details, activity and anything to avoid.
- 34, male, 165 cm, 65 kg
- 2. Craving
- Say what you feel like eating and where you shop.
- chicken fried rice
- 3. Your plan
- One meal, its balance, sources and a shopping list.
- 694 kcal, target 691

## 6. Four agents work like one kitchen

Layout: mp_agents

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
- An order comes in, each station does one job, and a planning service runs them in order.
- AI Meal Planner
- 6
- TAKEAWAY
- Meals come from 34 curated recipes, not generation, so the core path needs no LLM key.
- ORDER   chicken fried rice, active woman, maintaining
- THE PORTION PLANNER
- Calorie expenditure
- Estimates a day's burn and sets the / daily budget.
- 2,469 kcal budget
- THE CHEF
- Meal recommendation
- Sets the meal target, rules out / conflicts, picks a recipe and sizes it.
- 691 kcal target
- THE TASTER
- Nutrition verification
- Looks up each ingredient and labels / estimates.
- 694 kcal, 3 of 6 estimated
- THE SHOPPER
- Supermarket
- Matches ingredients to store items or / category prices.
- $24.50 estimated

## 7. From your body to a meal target

Layout: mp_calories

Reader question: How does it decide how much?

Message: The model's R² of 0.996 is for exercise calories only, which add just 3–10% of the day in these plans.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Calorie target
- From your body to a meal target
- Worked example: an active woman keeping her weight. Her meal target is 28% of the daily budget.
- AI Meal Planner
- 7
- TAKEAWAY
- The model's R² of 0.996 is for exercise calories only, which add just 3–10% of the day in these plans.
- Body and activity
- Size and activity give a daily estimate.
- 2,344 kcal
- Exercise
- A trained model adds exercise / calories.
- +125 kcal
- Goal
- Gain +250, lose −400, with a safety / floor.
- 2,469 kcal budget
- This meal
- 28% of the budget, within 350–850 / kcal.
- 691 kcal target
- Her day and this meal, on one scale
- Daily budget: 2,469 kcal
- 2,344 kcal from body and activity
- +125 kcal from the trained model
- This meal: 28% of the day
- 691 kcal
- Scale: full width is 2,469 kcal. Exercise inputs use defaults (30 minutes, 100 bpm).

## 8. Hard limits come first, then a relevant recipe

Layout: mp_choosing

Reader question: How does it choose the meal?

Message: Safety comes before relevance, and the profile only changes the order of safe, relevant recipes.

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
- TAKEAWAY
- Safety comes before relevance, and the profile only changes the order of safe, relevant recipes.
- Recipes left at each step
- All recipes
- 34
- Safe for a vegan
- 13
- Relevant to the craving
- 5
- Served
- 1: Tofu Fried Rice
- Close match
- "chicken fried rice" gets that recipe, / sized to you.
- 61 of 72 benchmark plans
- No close match
- "pizza" gets a standard meal and a / note saying so.
- 11 of 72 benchmark plans
- Nothing safe
- Too many limits: the plan is refused, / not guessed.
- 2 of 5 guardrail cases
- Or a safe swap
- A coeliac who asks for pasta keeps the / recipe with gluten-free pasta.
- Each swap checked against all / limits

## 9. Each ingredient is looked up, and estimates are labelled

Layout: mp_nutrition

Reader question: Can you trust the numbers?

Message: Only 3 of 6 ingredients are estimates, but they carry 66% of the calories; with no keys, nothing here is externally verified.

Exact face text:

- 1
- 2
- 3
- 4
- HOW IT WORKS
- Nutrition
- Each ingredient is looked up, and estimates are labelled
- Chicken fried rice from a local run with no USDA or FatSecret keys: 694 kcal against a 691 kcal target.
- AI Meal Planner
- 9
- TAKEAWAY
- Only 3 of 6 ingredients are estimates, but they carry 66% of the calories; with no keys, nothing here is externally verified.
- Ingredient
- Amount
- kcal
- Source
- Chicken breast
- 100 g
- 165
- Estimated
- Cooked rice
- 220 g
- 286
- Estimated
- Whole egg
- 50 g
- 72
- Reference
- Mixed vegetables
- 115 g
- 75
- Reference
- Soy sauce
- 15 g
- 8
- Estimated
- Sesame oil
- 10 g
- 88
- Reference
- Where the 694 kcal come from
- 459 kcal estimated, 66%
- 235 reference
- Lookup order
- 1. Trusted local reference
- Checked local values come first.
- 2. USDA, then FatSecret
- Used only when provider keys are set.
- 3. Local or category estimate
- The last resort, always labelled.

## 10. We defined a good meal before improving one

Layout: mp_good

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
- TAKEAWAY
- At the first run 68 of 72 plans hit calories, but only 10 cleared both tests.
- Test 2: share of the meal's energy
- Protein
- Allowed 10–35%
- 28%
- Carbs
- Allowed 45–65%
- 46%
- Fat
- Allowed 20–35%
- 26%
- Dots: chicken fried rice for the active woman. AMDR is a daily reference, applied here to one meal.
- TEST 1
- Within 10%
- of the meal's calorie target
- 72 fixed requests
- 12 cravings × 4 body profiles
- 6 cravings × 4 diet or / health limits

## 11. Three fixes took the planner from 10 to 72 of 72

Layout: mp_results

Reader question: Did it get better, and why?

Message: The 41 to 47 step moved 11 off-menu requests to fallback meals; the fixes were tuned on these 72, so the wider check matters.

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
- TAKEAWAY
- The 41 to 47 step moved 11 off-menu requests to fallback meals; the fixes were tuned on these 72, so the wider check matters.
- Plans meeting both targets, out of 72
- 10
- First run
- Before any fix
- 41
- Portion balancing
- Ingredients resized
- 47
- Honest fallback
- Off-menu cravings moved
- 72
- Cooking fat, retry
- Oil added to 6 recipes
- 0.4%
- median calorie gap, worst 9.9%
- 5 of 5
- guardrail cases hold
- 68 of 68
- wider check, every recipe by name

## 12. One service, two clients, four agents

Layout: mp_architecture

Reader question: What is it made of?

Message: Both clients use the same planning service, and the one trained model is 0.64 MB, so the core path needs no GPU.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Architecture
- One service, two clients, four agents
- A request flows left to right. Each box names the model, data or tool behind it.
- AI Meal Planner
- 12
- TAKEAWAY
- Both clients use the same planning service, and the one trained model is 0.64 MB, so the core path needs no GPU.
- CLIENTS
- API
- PLANNING SERVICE
- Streamlit
- Live, public demo
- React
- Guided flow, run / locally
- FastAPI
- Typed JSON, API / keys, rate limits
- SQLite
- Local history, via / SQLModel
- MealPlanningService
- Calorie expenditure
- Trained HistGradientBoosting model
- Meal recommendation
- TF-IDF search of 34 recipes, diet rules
- Nutrition verification
- Local tables; USDA, FatSecret with keys
- Balance and reconcile
- A service step: linear programme for portions
- Supermarket
- Local store items and category prices
- BUILT WITH
- Python
- Docker
- GitHub Actions
- Cloud Run, not yet live
- OpenTelemetry
- Gemini, optional

## 13. Built like a product, not a notebook

Layout: mp_engineering

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
- Six production habits, in the order a change travels through them.
- AI Meal Planner
- 13
- TAKEAWAY
- Health data is kept out of traces by a test, but no trace has reached Cloud Trace yet.
- From a change to production
- Teal: runs today. Grey: built, waiting for a GCP project.
- Contract
- CI fails on any drift
- docs/openapi.json
- Tests
- 630 Python tests
- backend/tests/
- Security
- API keys, rate limits
- api/auth.py
- Container
- One Docker image
- Dockerfile
- Cloud Run
- Ready, not live
- deploy.yml
- Tracing
- Health data kept out
- core/telemetry.py
- 630
- Python tests, all passing: 538 backend, 92 Streamlit
- 95%
- coverage, and CI fails below an 89% floor
- 5
- CI checks on every pull request

## 14. What this project does not prove yet

Layout: mp_limits

Reader question: What is unproven?

Message: A planning aid, not medical advice: plans hit their targets, but nobody has used it yet.

Exact face text:

- 1
- 2
- 3
- 4
- LIMITS AND NEXT STEPS
- Limits
- What this project does not prove yet
- The further right, the less has been shown.
- AI Meal Planner
- 14
- TAKEAWAY
- A planning aid, not medical advice: plans hit their targets, but nobody has used it yet.
- How far the evidence goes
- Each step up is less proven.
- Measured
- •  72 of 72 and 68 of 68, offline
- •  But the checks guided the fixes
- •  11 of 72 fall back
- Estimated
- •  68 of 72 plans include an estimate
- •  AMDR is a daily range on one meal
- •  Default exercise inputs
- •  Diet rules match ingredient names
- Not tested
- •  No user testing
- •  No clinical review
- •  Not deployed
- •  No database migrations
- •  Taste and health outcomes unknown

## 15. What comes next, in priority order

Layout: mp_next

Reader question: What comes next?

Message: Foundations first, then better inputs, then scale and people; each step answers a limit on the previous page.

Exact face text:

- 1
- 2
- 3
- 4
- LIMITS AND NEXT STEPS
- Next steps
- What comes next, in priority order
- How the project got here, and the work still ahead.
- AI Meal Planner
- 15
- TAKEAWAY
- Foundations first, then better inputs, then scale and people; each step answers a limit on the previous page.
- 8 Oct
- Refactor on main
- 11 Oct
- API keys, deploy workflow, tracing
- 18 Oct
- 72 of 72 plans on target
- 21 Oct
- React design approved
- 7 Nov
- 68 of 68, gluten fix
- Now
- Next steps
- NOW
- Add database migrations
- Deploy to Cloud Run
- Add user accounts
- NEXT
- Run the benchmark with USDA keys
- Ask for real exercise details
- Tag allergens on ingredients
- LATER
- Grow to 75–100 recipes
- Connect live store prices
- Use feedback, then test with people

## 16. Thank you

Layout: mp_close

Reader question: Where do I try it?

Message: Thank the audience and point to the demo and code.

Exact face text:

- Thank you
- Try the live demo, read the code, and send me your feedback.
- Manh Tuan (Mike) Nguyen
- TD School, University of Technology Sydney
- Demo tuannm3812-ai-meal-planner.streamlit.app
- Code github.com/tuannm3812/ai-meal-planner
- Scan for the live demo
- Salmon Quinoa Plate, one of the 34 curated recipes. A study project, not medical advice.
