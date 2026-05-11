from backend.app.repositories.storage import MealFeedbackRepository


def test_feedback_repository_lists_saved_meals(tmp_path) -> None:
    repository = MealFeedbackRepository(tmp_path)

    repository.save(
        {
            "user_id": "user_123",
            "request_id": "request-liked",
            "meal_id": "chicken_fried_rice",
            "meal_name": "Chicken Fried Rice",
            "liked": True,
            "rating": 5,
            "saved": True,
            "notes": "Good lunch",
        }
    )
    repository.save(
        {
            "user_id": "user_123",
            "request_id": "request-disliked",
            "meal_id": "turkey_burger_bowl",
            "meal_name": "Turkey Burger Bowl",
            "liked": False,
            "rating": 2,
            "saved": False,
            "notes": None,
        }
    )

    all_feedback = repository.list_for_user("user_123")
    saved_meals = repository.list_for_user("user_123", saved_only=True)

    assert len(all_feedback) == 2
    assert len(saved_meals) == 1
    assert saved_meals[0]["meal_id"] == "chicken_fried_rice"
