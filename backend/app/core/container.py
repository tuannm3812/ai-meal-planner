"""Builds the application's agents and repositories once, for injection."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from ..agents.calorie_expenditure_agent import CalorieExpenditureAgent
from ..agents.meal_recommendation_agent import MealRecommendationAgent
from ..agents.nutrition_verification_agent import NutritionVerificationAgent
from ..agents.supermarket_agent import SupermarketAgent
from ..repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)
from ..services.meal_planning_service import MealPlanningService
from .config import AppSettings


@dataclass(frozen=True)
class Container:
    """The application's constructed collaborators."""

    settings: AppSettings
    user_profiles: UserProfileRepository
    meal_history: MealPlanRepository
    meal_feedback: MealFeedbackRepository
    meal_agent: MealRecommendationAgent
    nutrition_agent: NutritionVerificationAgent
    supermarket_agent: SupermarketAgent
    calorie_agent: CalorieExpenditureAgent
    meal_planning_service: MealPlanningService


def build_container(settings: AppSettings) -> Container:
    """Construct every collaborator once.

    Args:
        settings: Resolved application settings.

    Returns:
        A Container holding the built agents, repositories and service.
    """
    user_profiles = UserProfileRepository(settings.data_dir)
    meal_agent = MealRecommendationAgent(
        db_connection=user_profiles,
        gemini_api_key=settings.gemini_api_key,
        meal_corpus_path=settings.meal_corpus_path,
        enable_llm_adaptation=settings.enable_gemini_adaptation,
        rag_backend=settings.rag_backend,
        rag_embedding_cache_dir=settings.rag_embedding_cache_dir,
        rag_embedding_activation_size=settings.rag_embedding_activation_size,
    )
    nutrition_agent = NutritionVerificationAgent(
        usda_api_key=settings.usda_api_key,
        fatsecret_client_id=settings.fatsecret_client_id,
        fatsecret_client_secret=settings.fatsecret_client_secret,
    )
    supermarket_agent = SupermarketAgent(
        maps_api_key=settings.maps_api_key,
        inventory_api_key=settings.inventory_api_key,
    )
    calorie_agent = CalorieExpenditureAgent(
        model_path=settings.calorie_model_path,
        model_version=settings.calorie_model_version,
    )
    return Container(
        settings=settings,
        user_profiles=user_profiles,
        meal_history=MealPlanRepository(settings.data_dir),
        meal_feedback=MealFeedbackRepository(settings.data_dir),
        meal_agent=meal_agent,
        nutrition_agent=nutrition_agent,
        supermarket_agent=supermarket_agent,
        calorie_agent=calorie_agent,
        meal_planning_service=MealPlanningService(
            meal_agent=meal_agent,
            nutrition_agent=nutrition_agent,
            supermarket_agent=supermarket_agent,
            calorie_agent=calorie_agent,
            profile_repo=user_profiles,
        ),
    )


def get_container(request: Request) -> Container:
    """Return the container built during application startup.

    Args:
        request: The incoming request, whose app state holds the container.

    Returns:
        The application's Container.
    """
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]
"""Injects the request-scoped view of the application's built container."""
