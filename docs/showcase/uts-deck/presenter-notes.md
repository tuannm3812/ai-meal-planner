# Presenter notes

## 1. What should I eat tonight?

Introduce the app through the question everyone asks.

Everyone asks this question, so that's where this project starts. You type a craving, and you get one meal sized to you, with each ingredient's source shown and the shopping list already written.
The rest of this deck shows how it works and how I measured it.

References:
- sources.md

## 2. Agenda

Locate each section by its page number.

The deck runs from the problem, through how the planner works, to what was measured and what is still open.

References:

## 3. One craving, sized to four different people

If you read one slide, read this one.

This is the same craving for four people, so the meal fits the person.
That quality is measured: all 72 plans in the project's own benchmark meet the targets, up from 10.
It stays honest: estimates are labelled, and it says so when nothing matches.

References:
- sources.md
- claims-register.md

## 4. Picking a meal is easy; sizing it to you is not

Show the work that sits between a craving and a meal.

Most of us know what we feel like eating. The hard part comes after that.
The right amount depends on the person. Diets and conditions change the meal. And even one meal means several ingredients to find and price.
The next section shows how one request answers all three.
Sources: Benchmark budgets: docs/meal_quality/baseline.json; pasta examples: local run, 7 November 2026, no provider keys.

References:
- sources.md
- claims-register.md

## 5. One craving in, one meal and a shopping list out

Walk through the real app in three steps.

You enter your body, goal and anything to avoid. Then you say what you feel like eating and where you shop.
You get one meal, its balance, each ingredient's source and a shopping list.
Sources: Captures: docs/showcase/slides/captures/2026-11-06-plan.json; React app, local run, 6 November 2026.

References:
- sources.md
- claims-register.md

## 6. Four agents work like one kitchen

Show the four agents and their real outputs.

The calorie agent sets a daily budget, the recommendation agent picks and sizes the meal, the nutrition agent labels estimates, and the supermarket agent prices the list.
The service balances portions after verification.
Sources: backend/app/services/meal_planning_service.py; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 7. From your body to a meal target

Follow one person from body to meal target.

Body size and activity give about 2,344 kcal a day. The trained model adds 125. Her goal is to maintain, so her budget is 2,469, and one meal gets 28%: 691 kcal.
Exercise adds only 5% here because the run uses default exercise inputs: 30 minutes at 100 bpm.
A weight-loss floor of 1,200 kcal for women and 1,500 for men protects low budgets.
Sources: calorie_expenditure_agent.py; models/calorie_expenditure/metrics.json; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 8. Hard limits come first, then a relevant recipe

Show the funnel from one real request.

Of 34 recipes, 13 are safe for a vegan, 5 are relevant to the craving, and one is served.
If nothing is close, you get a standard meal and a note. If nothing is safe, it refuses.
Sources: backend/app/rag/retriever.py; local run, 7 November 2026; docs/meal_quality/baseline.json.

References:
- sources.md
- claims-register.md

## 9. Each ingredient is looked up, and estimates are labelled

Show where each number came from.

Three of the six ingredients are estimates, but they include chicken and rice, the biggest items, so they carry 459 of the 694 kcal.
Sources: nutrition_verification_agent.py; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 10. We defined a good meal before improving one

Fix what good means before changing anything.

Calories had to land within 10% of the target, and each macro inside the adult AMDR range. The same 72 requests run every time.
Sources: docs/7_meal_quality.md §1; DEC-25.

References:
- sources.md
- claims-register.md

## 11. Three fixes took the planner from 10 to 72 of 72

Show what each fix changed.

Resizing each ingredient took it to 41. The relevance gate moved 11 off-menu requests to fallback meals, giving 47. Adding a fat to six recipes and a rounding retry took it to 72.
The fixes were tuned on these 72, so I also asked for every recipe by name: 49 of 68 passed before a further fix, 68 of 68 after.
Sources: docs/7_meal_quality.md §2; docs/meal_quality/baseline.md; DEC-26 to DEC-30.

References:
- sources.md
- claims-register.md

## 12. One service, two clients, four agents

Show the whole system on one page.

Both clients use the same planning service, so the logic lives in one place.
The hosted demo runs the same service inside Streamlit.
Sources: docs/2_architecture.md; pyproject.toml; frontend/package.json.

References:
- sources.md
- claims-register.md

## 13. Built like a product, not a notebook

Show the production habits.

On the line, teal steps run today; the grey ones are built and wait for a GCP project.
The last full run passed 630 Python tests at 95% coverage. Five checks run on every pull request.
The deployment workflow and tracing are built, but they wait for a GCP project.
Sources: ci.yml; docs/openapi.json; test_telemetry_redaction.py; local full run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 14. What this project does not prove yet

Put the limits in one place.

Plans hit their targets on fixed requests. Most lean on estimates. Nobody has used it yet.
Sources: docs/4_next_steps.md §7; docs/7_meal_quality.md; DEC-31.

References:
- sources.md
- claims-register.md

## 15. What comes next, in priority order

Pair the limits with the work that answers them.

Foundations first: migrations, a real deployment and accounts. Then better inputs. Then scale and testing with people.
Sources: docs/4_next_steps.md §6 and §7.

References:
- sources.md
- claims-register.md

## 16. Thank you

Thank the audience and point to the demo and code.

Thank you. That's AI Meal Planner: one craving in, one meal sized to you, with each ingredient's source shown.
The demo and the code are linked here.

References:
- sources.md
