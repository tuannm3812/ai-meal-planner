import logging
from typing import List, Dict, Any
from pydantic import BaseModel

# ---------------------------------------------------------
# Pydantic Models for Shopping List Enforcement
# ---------------------------------------------------------
class StoreDetails(BaseModel):
    store_name: str
    address: str

class ShoppingListItem(BaseModel):
    original_item_name: str
    store_product_name: str
    category_or_aisle: str
    estimated_price: float

class SupermarketPayload(BaseModel):
    store_details: StoreDetails
    shopping_list: List[ShoppingListItem]
    total_estimated_cost: float

# ---------------------------------------------------------
# Supermarket Sub-Agent Class
# ---------------------------------------------------------
class SupermarketAgent:
    def __init__(self, maps_api_key: str, inventory_api_key: str = None):
        """
        Initializes the agent with necessary API credentials to locate stores
        and query inventory via the Model Context Protocol.
        """
        self.maps_api_key = maps_api_key
        self.inventory_api_key = inventory_api_key
        logging.basicConfig(level=logging.INFO)

    def _locate_nearest_store(self, user_location: str) -> StoreDetails:
        """
        Simulated MCP tool call to a Mapping API.
        Finds the nearest optimal grocery store based on location.
        """
        logging.info(f"Locating supermarkets near: {user_location}")
        
        # Mock geographic response
        return StoreDetails(
            store_name="Coles Supermarket",
            address="Earlwood, NSW 2206"
        )

    def _map_inventory_and_price(self, item_name: str) -> Dict[str, Any]:
        """
        Simulated MCP tool call to a Grocery Inventory API.
        Semantically matches the generic recipe item to a store SKU.
        """
        # Mock inventory database
        mock_inventory = {
            "ground turkey (93% lean)": {
                "sku": "Coles Turkey Mince 500g",
                "aisle": "Meat & Poultry",
                "price": 6.50
            },
            "whole wheat hamburger bun": {
                "sku": "Tip Top Wholemeal Burger Buns 6pk",
                "aisle": "Bakery",
                "price": 4.00
            },
            "mixed salad greens": {
                "sku": "Fresh Salad Mix 150g",
                "aisle": "Produce",
                "price": 3.00
            }
        }
        
        # Default fallback for unmapped items
        return mock_inventory.get(item_name.lower(), {
            "sku": f"Generic {item_name}",
            "aisle": "Pantry",
            "price": 2.50
        })

    def generate_shopping_list(self, ingredients: List[Any], user_location: str) -> SupermarketPayload:
        """
        Takes the ingredients from the orchestrator and the user's location,
        finds the store, maps the products, and tallies the cost.
        """
        store = self._locate_nearest_store(user_location)
        shopping_list_items = []
        total_cost = 0.0

        for ingredient in ingredients:
            name = ingredient.item_name
            
            # Map generic ingredient to specific store product
            inventory_data = self._map_inventory_and_price(name)
            
            list_item = ShoppingListItem(
                original_item_name=name,
                store_product_name=inventory_data["sku"],
                category_or_aisle=inventory_data["aisle"],
                estimated_price=inventory_data["price"]
            )
            
            shopping_list_items.append(list_item)
            total_cost += inventory_data["price"]

        return SupermarketPayload(
            store_details=store,
            shopping_list=shopping_list_items,
            total_estimated_cost=round(total_cost, 2)
        )