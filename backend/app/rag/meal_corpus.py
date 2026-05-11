import json
from pathlib import Path

from pydantic import BaseModel, Field


class CorpusIngredient(BaseModel):
    item_name: str = Field(min_length=2)
    base_quantity_grams: int = Field(gt=0, le=2000)


class MealCorpusItem(BaseModel):
    meal_id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    dietary_flags: list[str] = Field(default_factory=list)
    avoid_conditions: list[str] = Field(default_factory=list)
    ingredients: list[CorpusIngredient]

    def retrieval_text(self) -> str:
        parts = [
            self.name,
            self.description,
            " ".join(self.tags),
            " ".join(self.dietary_flags),
            " ".join(ingredient.item_name for ingredient in self.ingredients),
        ]
        return " ".join(parts).lower()


def load_meal_corpus(corpus_path: Path) -> list[MealCorpusItem]:
    with corpus_path.open("r", encoding="utf-8") as corpus_file:
        raw_items = json.load(corpus_file)
    return [MealCorpusItem.model_validate(item) for item in raw_items]
