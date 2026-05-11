from dataclasses import dataclass

from .meal_corpus import MealCorpusItem


@dataclass(frozen=True)
class IngredientSubstitutionRule:
    original_name: str
    replacement_name: str
    replacement_grams: int | None
    blocked_groups: set[str]
    reason: str


@dataclass(frozen=True)
class PlannedSubstitution:
    original_name: str
    replacement_name: str
    replacement_grams: int
    reason: str


ALLERGEN_KEYWORDS = {
    "dairy": {"milk", "cheese", "yogurt", "cottage cheese", "whey", "butter"},
    "egg": {"egg"},
    "fish": {"salmon", "tuna", "fish"},
    "gluten": {"wheat", "wholemeal", "bread", "bun", "pasta", "tortilla"},
    "peanut": {"peanut"},
    "sesame": {"sesame"},
    "shellfish": {"shrimp", "prawn", "crab", "lobster"},
    "soy": {"soy", "tofu", "tempeh"},
}

ANIMAL_PROTEIN_KEYWORDS = {
    "meat": {"chicken", "turkey", "beef", "lean beef", "steak"},
    "fish": {"salmon", "tuna", "fish"},
    "shellfish": {"shrimp", "prawn", "crab", "lobster"},
}

CONSTRAINT_ALIASES = {
    "celiac": "gluten",
    "coeliac": "gluten",
    "dairy free": "dairy",
    "dairy-free": "dairy",
    "egg allergy": "egg",
    "fish allergy": "fish",
    "gluten free": "gluten",
    "gluten-free": "gluten",
    "gluten intolerance": "gluten",
    "lactose intolerance": "dairy",
    "kidney disease": "kidney_disease",
    "milk allergy": "dairy",
    "peanut allergy": "peanut",
    "sesame allergy": "sesame",
    "shellfish allergy": "shellfish",
    "soy allergy": "soy",
    "soy free": "soy",
    "soy-free": "soy",
    "tree nut allergy": "tree_nut",
}

SUBSTITUTION_RULES = [
    IngredientSubstitutionRule(
        "whole egg",
        "firm tofu",
        80,
        {"egg", "vegan"},
        "replaced egg for egg-free or vegan constraint",
    ),
    IngredientSubstitutionRule(
        "greek yogurt",
        "soy yogurt",
        None,
        {"dairy", "vegan"},
        "replaced dairy yogurt",
    ),
    IngredientSubstitutionRule(
        "cottage cheese",
        "soy yogurt",
        None,
        {"dairy", "vegan"},
        "replaced dairy cheese",
    ),
    IngredientSubstitutionRule(
        "whole wheat hamburger bun",
        "gluten-free bun",
        None,
        {"gluten"},
        "replaced wheat bun for gluten constraint",
    ),
    IngredientSubstitutionRule(
        "whole wheat bread",
        "gluten-free bread",
        None,
        {"gluten"},
        "replaced wheat bread for gluten constraint",
    ),
    IngredientSubstitutionRule(
        "whole wheat tortilla",
        "corn tortilla",
        None,
        {"gluten"},
        "replaced wheat tortilla for gluten constraint",
    ),
    IngredientSubstitutionRule(
        "wholemeal pasta",
        "gluten-free pasta",
        None,
        {"gluten"},
        "replaced wheat pasta for gluten constraint",
    ),
    IngredientSubstitutionRule(
        "soy sauce",
        "coconut aminos",
        None,
        {"soy", "sodium_sensitive"},
        "replaced soy sauce for soy or sodium constraint",
    ),
    IngredientSubstitutionRule(
        "low sodium soy sauce",
        "coconut aminos",
        None,
        {"soy"},
        "replaced soy sauce for soy constraint",
    ),
    IngredientSubstitutionRule(
        "firm tofu",
        "chickpeas",
        None,
        {"soy"},
        "replaced tofu for soy constraint",
    ),
    IngredientSubstitutionRule(
        "soy milk",
        "oat milk",
        None,
        {"soy"},
        "replaced soy milk for soy constraint",
    ),
    IngredientSubstitutionRule(
        "peanut butter",
        "sunflower seed butter",
        None,
        {"peanut"},
        "replaced peanut butter",
    ),
    IngredientSubstitutionRule(
        "sesame oil",
        "olive oil",
        None,
        {"sesame"},
        "replaced sesame oil",
    ),
    IngredientSubstitutionRule(
        "shrimp",
        "chicken breast",
        None,
        {"shellfish"},
        "replaced shellfish protein",
    ),
    IngredientSubstitutionRule(
        "salmon fillet",
        "chicken breast",
        None,
        {"fish"},
        "replaced fish protein",
    ),
    IngredientSubstitutionRule(
        "tuna",
        "chicken breast",
        None,
        {"fish"},
        "replaced fish protein",
    ),
]


def normalize_label(value: str) -> str:
    return value.strip().lower().replace("_", " ").replace("-", " ")


def constraint_groups(labels: list[str]) -> set[str]:
    normalized_labels = {normalize_label(label) for label in labels if label.strip()}
    groups = {
        group
        for label in normalized_labels
        for alias, group in CONSTRAINT_ALIASES.items()
        if alias in label
    }

    if any(label in {"vegan", "plant based", "plant-based"} for label in normalized_labels):
        groups.add("vegan")
        groups.update({"dairy", "egg"})
    if "vegetarian" in normalized_labels:
        groups.add("vegetarian")
    if any(label in {"hypertension", "high blood pressure", "low sodium"} for label in normalized_labels):
        groups.add("sodium_sensitive")

    return groups


def blocked_groups_for_ingredient(item_name: str, groups: set[str]) -> set[str]:
    normalized_name = normalize_label(item_name)
    blocked = {
        group
        for group, keywords in ALLERGEN_KEYWORDS.items()
        if group in groups and any(keyword in normalized_name for keyword in keywords)
    }

    if "vegan" in groups:
        blocked.update(
            group
            for group, keywords in ANIMAL_PROTEIN_KEYWORDS.items()
            if any(keyword in normalized_name for keyword in keywords)
        )
    if "vegetarian" in groups:
        blocked.update(
            group
            for group in {"meat", "fish", "shellfish"}
            if any(keyword in normalized_name for keyword in ANIMAL_PROTEIN_KEYWORDS[group])
        )
    if "sodium_sensitive" in groups and "soy sauce" in normalized_name:
        blocked.add("sodium_sensitive")
    if "kidney_disease" in groups and any(
        keyword in normalized_name
        for keyword in {"kidney beans", "lentils", "chickpeas", "tofu", "soy sauce"}
    ):
        blocked.add("kidney_disease")

    return blocked


def planned_substitution(
    item_name: str,
    quantity_grams: int,
    groups: set[str],
) -> PlannedSubstitution | None:
    normalized_name = normalize_label(item_name)
    for rule in SUBSTITUTION_RULES:
        if rule.original_name == normalized_name and rule.blocked_groups & groups:
            return PlannedSubstitution(
                original_name=item_name,
                replacement_name=rule.replacement_name,
                replacement_grams=rule.replacement_grams or quantity_grams,
                reason=rule.reason,
            )
    return None


def meal_conflicts_with_health_conditions(
    meal: MealCorpusItem,
    health_conditions: list[str],
) -> bool:
    avoid_conditions = {normalize_label(condition) for condition in meal.avoid_conditions}
    requested_conditions = {normalize_label(condition) for condition in health_conditions}
    return bool(avoid_conditions & requested_conditions)


def substitution_plan_for_meal(
    meal: MealCorpusItem,
    groups: set[str],
) -> list[PlannedSubstitution]:
    substitutions = []
    for ingredient in meal.ingredients:
        substitution = planned_substitution(
            ingredient.item_name,
            ingredient.base_quantity_grams,
            groups,
        )
        if substitution:
            substitutions.append(substitution)
    return substitutions


def meal_is_allowed(
    meal: MealCorpusItem,
    groups: set[str],
    health_conditions: list[str],
) -> bool:
    if meal_conflicts_with_health_conditions(meal, health_conditions):
        return False

    for ingredient in meal.ingredients:
        blocked = blocked_groups_for_ingredient(ingredient.item_name, groups)
        if not blocked:
            continue
        if not planned_substitution(ingredient.item_name, ingredient.base_quantity_grams, blocked):
            return False
    return True
