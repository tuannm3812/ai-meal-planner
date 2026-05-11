# Meal Recommendation Agent

## Role

Recommend structured meal plans from a calorie budget, user preferences, restrictions, and retrieved meal candidates.

## Inputs

- Meal calorie budget from `CalorieExpenditureAgent`.
- Dietary restrictions and allergies.
- Food preferences, disliked foods, cuisine, budget, and prep-time constraints.
- Optional craving or meal goal.

## Process

1. Retrieve meal candidates from the curated meal corpus.
2. Filter unsafe or incompatible meals.
3. Use GenAI to adapt portions and ingredient choices when needed.
4. Return typed JSON with searchable ingredient names and gram quantities.

## Outputs

- `user_context`
- `meal_definition`
- `retrieved_sources`
- `metadata`

The agent should never return free-form recipe text as the primary contract.
