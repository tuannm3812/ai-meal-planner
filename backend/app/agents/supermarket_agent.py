import logging
from typing import Any

from pydantic import BaseModel, Field

from ..rag.reference_data import load_reference
from ..schemas.common import AgentMetadata, average_confidence
from ..schemas.requests import Ingredient

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


class SupermarketPayload(BaseModel):
    store_details: StoreDetails
    shopping_list: list[ShoppingListItem]
    total_estimated_cost: float
    metadata: AgentMetadata


class SupermarketAgent:
    def __init__(self, maps_api_key: str | None = None, inventory_api_key: str | None = None):
        self.maps_api_key = maps_api_key
        self.inventory_api_key = inventory_api_key

    def generate_shopping_list(
        self, ingredients: list[Ingredient], user_location: str
    ) -> SupermarketPayload:
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

        confidence = average_confidence(shopping_list_items)
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

    def _map_inventory_and_price(self, item_name: str) -> dict[str, Any]:
        inventory = load_reference("supermarket_prices")

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
