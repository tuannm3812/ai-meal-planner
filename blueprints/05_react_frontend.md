# React Frontend Specification

## Role
The user-facing dashboard for the Multi-Agent Meal Planner. It captures user input, communicates with the FastAPI backend, and dynamically renders the orchestrator's results.

## Technology Stack
*   **Framework**: React (using Vite).
*   **Styling**: Tailwind CSS for rapid, modern UI development.
*   **HTTP Client**: Axios or native `fetch` to handle asynchronous POST requests to `http://localhost:8000/generate-meal-plan`.

## UI Layout
The dashboard should be clean and scannable, divided into two main sections:

1.  **The Input Sidebar/Top Bar**:
    *   `Craving Input`: Text field for the desired meal.
    *   `User ID`: Text field (default to "user_123" for prototyping).
    *   `Location`: Text field (default to "Earlwood, NSW").
    *   `Submit Button`: Triggers the API call and displays a loading state.

2.  **The Results Dashboard (Grid Layout)**:
    *   **Meal Overview Card**: Displays the `structured_meal_name` and the list of raw ingredients.
    *   **Nutrition Card**: Highlights the calculated `total_calories`, `total_protein`, `total_carbs`, and `total_fat`.
    *   **Supermarket Card**: Displays the `store_details` and a formatted list of the mapped grocery items with their `estimated_price`, culminating in the `total_estimated_cost`.

## State Management
*   Use `useState` to handle form inputs.
*   Use `useState` to store the aggregated API response (`meal_plan`, `nutrition`, `shopping_list`).
*   Use `useState` for a boolean `isLoading` flag to show a spinner while the agents are generating the response.