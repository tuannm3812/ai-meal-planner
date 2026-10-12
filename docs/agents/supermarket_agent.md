# Supermarket Agent

## Role

Turn the meal's final ingredient list into a priced shopping list at a named
store. It runs last in `MealPlanningService`, after reconciliation (span
`supermarket.list`). It is deterministic and makes no network calls.

This document describes the agent as implemented in
`backend/app/agents/supermarket_agent.py`. An earlier version described
mapping and grocery-inventory APIs reached through MCP tools. None of those
exist in this repository, and the 2026-10-07 production-readiness direction
chose to describe the local implementation rather than build them.

## Inputs

- The final ingredients, after any reconciliation rescale. Only each
  `item_name` is used: prices are per item, not scaled by
  `base_quantity_grams`.
- The user's location, a free-text string such as `"Earlwood, NSW"`.

## Store selection

`_locate_nearest_store` matches the location string; it does not geocode or
look anything up:

| Location contains | Store | `location_source` |
| --- | --- | --- |
| `earlwood` | Coles Supermarket, Earlwood, NSW 2206 | `local_reference` |
| `sydney` or `nsw` | Woolworths Metro, "Near ‹location›" | `regional_estimate` |
| anything else | Local Supermarket, "Near ‹location›" | `generic_estimate` |

## Item mapping and prices

For each ingredient, `_map_inventory_and_price`:

1. **Looks up** the lowercased name in
   `data/reference/supermarket_prices.json`, a local table of 15 entries
   mapping a name to a store product, an aisle and a price. A match has
   `data_source: local_inventory_reference` and confidence 0.82.
2. **Otherwise estimates** by keyword category:

   | Category | Keywords | Price |
   | --- | --- | --- |
   | Protein | chicken, turkey, beef, fish, tofu | 6.50 |
   | Pantry | rice, pasta, bread, bun, noodle | 3.20 |
   | Produce | spinach, greens, lettuce, tomato, broccoli | 2.80 |
   | Grocery | anything else | 3.50 |

   An estimate has `data_source: category_price_estimate`, confidence 0.46,
   product name `Generic ‹item›`, and adds the warning
   `Estimated grocery mapping for ‹item›`.

Prices are illustrative reference values, not live store prices or stock.

## Output

`SupermarketPayload`:

- `store_details`: `store_name`, `address`, `location_source`.
- `shopping_list`: for each ingredient, `original_item_name`,
  `store_product_name`, `category_or_aisle`, `estimated_price`,
  `data_source` and `confidence`.
- `total_estimated_cost`: the sum of item prices, rounded to cents.
- `metadata`: `agent_name: SupermarketAgent`,
  `source: local_store_inventory`, the mean item confidence, and the
  estimate warnings.

## Not implemented

- **No places, mapping or inventory API, and no MCP tools.** The
  `MAPS_API_KEY` and `INVENTORY_API_KEY` settings are passed to the agent and
  stored, but nothing reads them.
- **No quantity-aware pricing.** One price per ingredient, whatever the grams.
- **Privacy.** The location is used only to choose a store. Since G10b it is
  neither logged nor exported in traces. The `supermarket.list` span carries
  no attributes (DEC-17).

## Tests

- `backend/tests/test_supermarket_agent.py`: the agent itself.
- `backend/tests/test_reference_data.py`: the reference tables.
- `backend/tests/test_meal_planning_service.py`: the full pipeline.
