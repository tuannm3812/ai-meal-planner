# Nutrition Agent Specification

## Role
A specialized Sub-Agent responsible for data grounding. It takes the structured ingredient list from the Primary Agent and maps it to verified nutritional data.

## MCP Tool Integration
*   **Tool**: USDA FoodData Central API via Model Context Protocol (MCP).
*   **Action**: Iterates through the `ingredients` array provided by the `MealPlanPayload`. For each `item_name`, it executes a vector search or direct query against the USDA database.

## Inputs
*   `MealPlanPayload.meal_definition.ingredients` (Array of items and gram quantities).

## Outputs
Must output a JSON object appending the exact macro breakdown to each ingredient:
*   `calories_kcal`
*   `protein_g`
*   `carbs_g`
*   `fat_g`
*   `total_meal_macros` (aggregated sum)