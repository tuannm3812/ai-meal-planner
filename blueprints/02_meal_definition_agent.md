# Meal Definition Agent Specification

## Role
The primary orchestrator. It receives user biometric data and food cravings, calculates daily caloric targets, and translates concepts into structured meals.

## Inputs
* User biometrics (gender, weight, height, workout level)
* Dietary restrictions
* Craving/Target Food

## Outputs
Must strictly output JSON containing:
1. `user_context` (caloric target, restrictions)
2. `meal_definition` (craving, structured meal name, and an array of ingredients with base quantities in grams).