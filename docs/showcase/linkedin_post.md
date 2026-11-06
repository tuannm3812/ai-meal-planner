# LinkedIn post draft

Attach `ai-meal-planner-linkedin.png` (1080 × 1350, LinkedIn's 4:5 feed size).

---

"What should I eat?" sounds simple until you try to answer it properly.

I've been building AI Meal Planner, a multi-agent app that turns a craving into one meal sized to your body and goal, plus the shopping list for it.

How a plan is made:
1️⃣ A gradient-boosted model trained on 750,000 rows predicts exercise calories (R² 0.996), which feed a daily budget and the meal's target
2️⃣ Diet, allergy and health filters run first, then vector RAG picks from 34 curated recipes and resizes the portions
3️⃣ Each ingredient is looked up in USDA FoodData Central or local tables, and anything estimated is labelled
4️⃣ A supermarket agent maps the ingredients to a priced shopping list

The part I'm proudest of is measuring quality instead of eyeballing it. I wrote my own fixed, deterministic benchmark of 72 requests across different bodies, goals and dietary limits. A plan passes only if its calories land within 10% of target and protein, carbs and fat all sit inside the adult AMDR ranges.

The first run passed 10 of 72. Balancing portions per ingredient took it to 41. Making the planner admit when nothing on the menu matches (instead of quietly serving something unrelated) took it to 47. Adding a cooking fat to six recipes that had none, plus a rounding retry, took it to 72 of 72, with a median calorie deviation of 0.3%.

Under the hood: FastAPI with a CI-checked OpenAPI contract, 590+ Python tests, API keys and rate limits, OpenTelemetry tracing that keeps health data out of the traces, and two clients (React and Streamlit). It runs without an LLM key, so the core path still works when an AI API is down.

Try the demo: https://tuannm3812-ai-meal-planner.streamlit.app/
Code: https://github.com/tuannm3812/ai-meal-planner

It's a study project, not medical advice. I'd love feedback, especially from anyone working on nutrition or recommender systems.

#Python #FastAPI #MachineLearning #RAG #AIAgents #Nutrition #BuildInPublic
