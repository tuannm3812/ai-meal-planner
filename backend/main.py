import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our agents
from meal_definition_agent import MealDefinitionAgent
from nutrition_agent import NutritionAgent
from supermarket_agent import SupermarketAgent

# ---------------------------------------------------------
# API Request & Response Schemas
# ---------------------------------------------------------
class MealRequest(BaseModel):
    user_id: str
    craving: str
    location: str

# ---------------------------------------------------------
# Mock Database for Prototyping
# ---------------------------------------------------------
class MockDatabase:
    def fetch_user_profile(self, user_id: str):
        # Simulating a database fetch for a user profile
        return {
            "age": 28,
            "gender": "m",
            "weight": 80.0,  # kg
            "height": 180.0, # cm
            "workout_level": 1.55, # Moderate activity
            "dietary_restrictions": ["dairy-free", "high-protein"]
        }

# ---------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------
app = FastAPI(title="Multi-Agent Meal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change "*" to your frontend URL (e.g., "http://localhost:5173")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents with our Mock DB
mock_db = MockDatabase()
meal_agent = MealDefinitionAgent(db_connection=mock_db) 
nutrition_agent = NutritionAgent(usda_api_key="mock_key")
supermarket_agent = SupermarketAgent(maps_api_key="mock_key", inventory_api_key="mock_key")

@app.post("/generate-meal-plan")
async def generate_meal_plan(request: MealRequest):
    """
    Master endpoint that triggers the full multi-agent chain.
    """
    try:
        # Step 1: Meal Definition
        meal_payload = meal_agent.generate_meal_payload(
            craving=request.craving,
            user_id=request.user_id
        )
        
        # Step 2: Nutrition Calculation
        nutrition_payload = nutrition_agent.calculate_meal_macros(
            ingredients=meal_payload.meal_definition.ingredients
        )
        
        # Step 3: Supermarket Mapping
        supermarket_payload = supermarket_agent.generate_shopping_list(
            ingredients=meal_payload.meal_definition.ingredients,
            user_location=request.location
        )
        
        # Aggregate the final response
        return {
            "status": "success",
            "meal_plan": meal_payload.dict(),
            "nutrition": nutrition_payload.dict(),
            "shopping_list": supermarket_payload.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)