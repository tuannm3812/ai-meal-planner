import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class StoreDetails(BaseModel):
    store_name: str
    address: str
    location_source: str


class ShoppingListItem(BaseModel):
    original_item_name: str
    store_product_name: str
    category_or_aisle: str
    estimated_price: float
    data_source: str
    confidence: float = Field(ge=0, le=1)


class AgentMetadata(BaseModel):
    agent_name: str
    source: str
    confidence: float = Field(ge=0, le=1)
    warnings: List[str] = Field(default_factory=list)


class SupermarketPayload(BaseModel):
    store_details: StoreDetails
    shopping_list: List[ShoppingListItem]
    total_estimated_cost: float
    metadata: AgentMetadata


class SupermarketAgent:
    def __init__(self, maps_api_key: str | None = None, inventory_api_key: str | None = None):
        self.maps_api_key = maps_api_key
        self.inventory_api_key = inventory_api_key

    def generate_shopping_list(self, ingredients: List[Any], user_location: str) -> SupermarketPayload:
        store = self._locate_nearest_store(user_location)
        shopping_list_items = []
        warnings = []
        total_cost = 0.0

        for ingredient in ingredients:
            name = ingredient.item_name
            inventory_data = self._map_inventory_and_price(name)

            if inventory_data["source"] != "local_inventory_reference":
                warnings.append(f"Estimated grocery mapping for {name}")

            list_item = ShoppingListItem(
                original_item_name=name,
                store_product_name=inventory_data["sku"],
                category_or_aisle=inventory_data["aisle"],
                estimated_price=inventory_data["price"],
                data_source=inventory_data["source"],
                confidence=inventory_data["confidence"],
            )

            shopping_list_items.append(list_item)
            total_cost += inventory_data["price"]

        confidence = self._average_confidence(shopping_list_items)
        return SupermarketPayload(
            store_details=store,
            shopping_list=shopping_list_items,
            total_estimated_cost=round(total_cost, 2),
            metadata=AgentMetadata(
                agent_name="SupermarketAgent",
                source="local_store_inventory",
                confidence=confidence,
                warnings=warnings,
            ),
        )

    def _locate_nearest_store(self, user_location: str) -> StoreDetails:
        logger.info("Locating supermarkets near: %s", user_location)
        normalized_location = user_location.lower()

        if "earlwood" in normalized_location:
            return StoreDetails(
                store_name="Coles Supermarket",
                address="Earlwood, NSW 2206",
                location_source="local_reference",
            )

        if "sydney" in normalized_location or "nsw" in normalized_location:
            return StoreDetails(
                store_name="Woolworths Metro",
                address=f"Near {user_location}",
                location_source="regional_estimate",
            )

        return StoreDetails(
            store_name="Local Supermarket",
            address=f"Near {user_location}",
            location_source="generic_estimate",
        )

    def _map_inventory_and_price(self, item_name: str) -> Dict[str, Any]:
        inventory = {
            "lean turkey mince": {
                "sku": "Coles Turkey Mince 500g",
                "aisle": "Meat & Poultry",
                "price": 6.50,
            },
            "ground turkey (93% lean)": {
                "sku": "Coles Turkey Mince 500g",
                "aisle": "Meat & Poultry",
                "price": 6.50,
            },
            "chicken breast": {
                "sku": "Chicken Breast Fillets 500g",
                "aisle": "Meat & Poultry",
                "price": 7.80,
            },
            "firm tofu": {
                "sku": "Firm Tofu 450g",
                "aisle": "Plant-Based Protein",
                "price": 4.20,
            },
            "whole wheat hamburger bun": {
                "sku": "Wholemeal Burger Buns 6pk",
                "aisle": "Bakery",
                "price": 4.00,
            },
            "wholemeal pasta": {
                "sku": "Wholemeal Pasta 500g",
                "aisle": "Pantry",
                "price": 2.80,
            },
            "brown rice": {
                "sku": "Brown Rice 1kg",
                "aisle": "Pantry",
                "price": 3.20,
            },
            "mixed salad greens": {
                "sku": "Fresh Salad Mix 150g",
                "aisle": "Produce",
                "price": 3.00,
            },
            "baby spinach": {
                "sku": "Baby Spinach 120g",
                "aisle": "Produce",
                "price": 3.50,
            },
            "broccoli": {
                "sku": "Fresh Broccoli",
                "aisle": "Produce",
                "price": 2.20,
            },
            "tomato": {
                "sku": "Fresh Tomatoes",
                "aisle": "Produce",
                "price": 1.40,
            },
            "tomato passata": {
                "sku": "Tomato Passata 700g",
                "aisle": "Pantry",
                "price": 2.30,
            },
            "avocado": {
                "sku": "Fresh Avocado",
                "aisle": "Produce",
                "price": 2.00,
            },
            "soy sauce": {
                "sku": "Soy Sauce 250ml",
                "aisle": "Asian Foods",
                "price": 3.00,
            },
        }

        matched_item = inventory.get(item_name.lower())
        if matched_item:
            return {
                **matched_item,
                "source": "local_inventory_reference",
                "confidence": 0.82,
            }

        aisle, price = self._estimate_category_and_price(item_name)
        return {
            "sku": f"Generic {item_name}",
            "aisle": aisle,
            "price": price,
            "source": "category_price_estimate",
            "confidence": 0.46,
        }

    @staticmethod
    def _estimate_category_and_price(item_name: str) -> tuple[str, float]:
        name = item_name.lower()
        if any(token in name for token in ["chicken", "turkey", "beef", "fish", "tofu"]):
            return "Protein", 6.50
        if any(token in name for token in ["rice", "pasta", "bread", "bun", "noodle"]):
            return "Pantry", 3.20
        if any(token in name for token in ["spinach", "greens", "lettuce", "tomato", "broccoli"]):
            return "Produce", 2.80
        return "Grocery", 3.50

    @staticmethod
    def _average_confidence(items: List[ShoppingListItem]) -> float:
        if not items:
            return 0.0
        return round(sum(item.confidence for item in items) / len(items), 2)
