# Supermarket Agent Specification

## Role
A localized Sub-Agent that acts as the real-world connector. It takes the structured ingredient list and maps it to available items at a nearby grocery store based on the user's location.

## MCP Tool Integration
*   **Tool**: Mapping API (e.g., Google Places) to locate the nearest supermarket, and Grocery/Inventory APIs to map generic ingredients to specific store SKUs and estimated prices.
*   **Action**: Performs geographic radius searches and semantic matching between the Meal Definition Agent's `item_name` and the store's inventory database.

## Inputs
*   `MealPlanPayload.meal_definition.ingredients` (Array of items and quantities).
*   User location data (Coordinates or localized string, e.g., "Earlwood, NSW").

## Outputs
Must strictly output a JSON object containing:
1.  `store_details`: Name and address of the selected supermarket.
2.  `shopping_list`: Array of mapped items including:
    *   Original `item_name`
    *   Matched `store_product_name`
    *   `category_or_aisle`
    *   `estimated_price`
3.  `total_estimated_cost`: Sum of the shopping list items.