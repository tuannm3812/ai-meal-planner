// A real response from the local API (POST /generate-meal-plan for "chicken
// fried rice", a 34-year-old woman maintaining her weight), the one the
// docs/8_design.md prototype was drawn from. Test data only.
export const SAMPLE_PLAN = {
  "status": "success",
  "plan_status": "matched",
  "request_id": "sample-request",
  "generated_at": "2026-10-22T00:00:00+00:00",
  "request": {
    "user_id": "user_123",
    "craving": "chicken fried rice",
    "location": "Earlwood, NSW",
    "health_conditions": [],
    "dietary_preferences": [],
    "age": 34,
    "sex": "female",
    "height_cm": 168.0,
    "weight_kg": 64.0,
    "activity_multiplier": 1.55,
    "goal": "maintain"
  },
  "calorie_budget": {
    "estimated_daily_expenditure_kcal": 2231.4,
    "meal_calorie_budget_kcal": 2231.4,
    "model_version": "hist_gradient_boosting_deep_v0.1.0",
    "confidence": 0.82,
    "warnings": []
  },
  "meal_plan": {
    "user_context": {
      "caloric_target": 2231,
      "dietary_restrictions": [
        "dairy-free",
        "high-protein"
      ]
    },
    "meal_definition": {
      "craving_input": "chicken fried rice",
      "structured_meal_name": "Chicken Fried Rice",
      "ingredients": [
        {
          "item_name": "chicken breast",
          "base_quantity_grams": 85
        },
        {
          "item_name": "cooked white rice",
          "base_quantity_grams": 200
        },
        {
          "item_name": "whole egg",
          "base_quantity_grams": 45
        },
        {
          "item_name": "mixed vegetables",
          "base_quantity_grams": 105
        },
        {
          "item_name": "soy sauce",
          "base_quantity_grams": 15
        },
        {
          "item_name": "sesame oil",
          "base_quantity_grams": 10
        }
      ]
    },
    "metadata": {
      "agent_name": "MealRecommendationAgent",
      "source": "local_vector_rag_meal_corpus",
      "confidence": 0.95,
      "warnings": [
        "Retrieved meal template chicken_fried_rice using local vector RAG.",
        "Matched terms: chicken, fried, rice",
        "Scaled portions from 726 kcal toward 625 kcal.",
        "Rebalanced ingredient portions toward the recommended protein, carbohydrate and fat split."
      ],
      "explanation": null
    },
    "retrieval": {
      "query": "chicken fried rice",
      "retriever": "tfidf_vector_retriever_v0.1",
      "selected_meal_id": "chicken_fried_rice",
      "selected_score": 1.0013,
      "matched_terms": [
        "chicken",
        "fried",
        "rice"
      ],
      "candidates": [
        {
          "meal_id": "chicken_fried_rice",
          "name": "Chicken Fried Rice",
          "score": 1.0013,
          "rank": 1,
          "matched_terms": [
            "chicken",
            "fried",
            "rice"
          ]
        },
        {
          "meal_id": "tofu_fried_rice",
          "name": "Tofu Fried Rice",
          "score": 0.5727,
          "rank": 2,
          "matched_terms": [
            "fried",
            "rice"
          ]
        },
        {
          "meal_id": "chicken_soup_bowl",
          "name": "Chicken Vegetable Soup Bowl",
          "score": 0.5348,
          "rank": 3,
          "matched_terms": [
            "chicken",
            "rice"
          ]
        }
      ],
      "substitutions": []
    },
    "portion_scaling": {
      "target_meal_calories": 625,
      "estimated_template_calories": 725.9,
      "scale_factor": 0.86
    }
  },
  "nutrition": {
    "ingredients_macros": [
      {
        "item_name": "chicken breast",
        "base_quantity_grams": 85,
        "calories_kcal": 140.2,
        "protein_g": 26.3,
        "carbs_g": 0.0,
        "fat_g": 3.1,
        "data_source": "local_reference_table",
        "verification": "estimated",
        "confidence": 0.78
      },
      {
        "item_name": "cooked white rice",
        "base_quantity_grams": 200,
        "calories_kcal": 260.0,
        "protein_g": 5.4,
        "carbs_g": 56.4,
        "fat_g": 0.6,
        "data_source": "local_reference_table",
        "verification": "estimated",
        "confidence": 0.78
      },
      {
        "item_name": "whole egg",
        "base_quantity_grams": 45,
        "calories_kcal": 64.4,
        "protein_g": 5.7,
        "carbs_g": 0.3,
        "fat_g": 4.3,
        "data_source": "trusted_local_reference",
        "verification": "trusted_local",
        "confidence": 0.82
      },
      {
        "item_name": "mixed vegetables",
        "base_quantity_grams": 105,
        "calories_kcal": 68.2,
        "protein_g": 3.5,
        "carbs_g": 13.7,
        "fat_g": 0.2,
        "data_source": "trusted_local_reference",
        "verification": "trusted_local",
        "confidence": 0.82
      },
      {
        "item_name": "soy sauce",
        "base_quantity_grams": 15,
        "calories_kcal": 7.9,
        "protein_g": 1.2,
        "carbs_g": 0.7,
        "fat_g": 0.1,
        "data_source": "local_reference_table",
        "verification": "estimated",
        "confidence": 0.78
      },
      {
        "item_name": "sesame oil",
        "base_quantity_grams": 10,
        "calories_kcal": 88.4,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 10.0,
        "data_source": "trusted_local_reference",
        "verification": "trusted_local",
        "confidence": 0.82
      }
    ],
    "total_calories": 629.1,
    "total_protein": 42.1,
    "total_carbs": 71.1,
    "total_fat": 18.3,
    "nutrition_status": "mixed",
    "sources": [
      "local_reference_table",
      "trusted_local_reference"
    ],
    "metadata": {
      "agent_name": "NutritionVerificationAgent",
      "source": "local_reference_table+trusted_local_reference",
      "confidence": 0.8,
      "warnings": [
        "Estimated nutrition for chicken breast",
        "Estimated nutrition for cooked white rice",
        "Estimated nutrition for soy sauce"
      ]
    }
  },
  "shopping_list": {
    "store_details": {
      "store_name": "Coles Supermarket",
      "address": "Earlwood, NSW 2206",
      "location_source": "local_reference"
    },
    "shopping_list": [
      {
        "original_item_name": "chicken breast",
        "store_product_name": "Chicken Breast Fillets 500g",
        "category_or_aisle": "Meat & Poultry",
        "estimated_price": 7.8,
        "data_source": "local_inventory_reference",
        "confidence": 0.82
      },
      {
        "original_item_name": "cooked white rice",
        "store_product_name": "Generic cooked white rice",
        "category_or_aisle": "Pantry",
        "estimated_price": 3.2,
        "data_source": "category_price_estimate",
        "confidence": 0.46
      },
      {
        "original_item_name": "whole egg",
        "store_product_name": "Generic whole egg",
        "category_or_aisle": "Grocery",
        "estimated_price": 3.5,
        "data_source": "category_price_estimate",
        "confidence": 0.46
      },
      {
        "original_item_name": "mixed vegetables",
        "store_product_name": "Generic mixed vegetables",
        "category_or_aisle": "Grocery",
        "estimated_price": 3.5,
        "data_source": "category_price_estimate",
        "confidence": 0.46
      },
      {
        "original_item_name": "soy sauce",
        "store_product_name": "Soy Sauce 250ml",
        "category_or_aisle": "Asian Foods",
        "estimated_price": 3.0,
        "data_source": "local_inventory_reference",
        "confidence": 0.82
      },
      {
        "original_item_name": "sesame oil",
        "store_product_name": "Generic sesame oil",
        "category_or_aisle": "Grocery",
        "estimated_price": 3.5,
        "data_source": "category_price_estimate",
        "confidence": 0.46
      }
    ],
    "total_estimated_cost": 24.5,
    "metadata": {
      "agent_name": "SupermarketAgent",
      "source": "local_store_inventory",
      "confidence": 0.58,
      "warnings": [
        "Estimated grocery mapping for cooked white rice",
        "Estimated grocery mapping for whole egg",
        "Estimated grocery mapping for mixed vegetables",
        "Estimated grocery mapping for sesame oil"
      ]
    }
  },
  "reconciliation": {
    "target_meal_calories": 625,
    "verified_calories_before": 629.1,
    "deviation_before": 0.0066,
    "rescaled": false,
    "verified_calories_after": null,
    "deviation_after": null,
    "within_tolerance": true,
    "tolerance": 0.15
  },
  "macro_balance": {
    "outcome": "rebalanced",
    "target_meal_calories": 625,
    "macro_percent_before": {
      "protein": 35.9,
      "carbs": 36.1,
      "fat": 28.0
    },
    "macro_percent_after": {
      "protein": 27.3,
      "carbs": 46.1,
      "fat": 26.7
    },
    "macros_in_range_after": true
  },
  "infeasible_reason": null
}
