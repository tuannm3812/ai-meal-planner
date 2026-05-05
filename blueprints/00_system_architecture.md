# System Architecture & Data Flow

## 1. High-Level Overview
This project is a multi-agent, AI-powered meal planning application. It utilizes a React frontend for the user interface, a Python backend for agent orchestration, Model Context Protocol (MCP) for external tool integration, and a high-performance database for user state and vector-based meal retrieval.

## 2. Technology Stack
*   **Frontend**: React (Functional components, Hooks).
*   **Backend**: Python 3.10+ (FastAPI recommended for async agent handling).
*   **AI/LLM**: Google Gemini deployed via Vertex AI for agent reasoning.
*   **Infrastructure**: Containerized services deployed via Cloud Run.
*   **Database**: Relational or NoSQL database with vector search capabilities to store user biometric profiles, dietary preferences, and semantically search past meal plans.

## 3. The Multi-Agent Orchestration
The system follows a strict hierarchical agent pattern. The Primary Agent coordinates the workflow and delegates specific tasks to specialized Sub-Agents.

### A. Meal Definition Agent (Primary Orchestrator)
*   **Trigger**: Receives user request (e.g., "burger") and pulls the user's saved biometric profile from the database.
*   **Action**: Calculates caloric targets and structures the raw input into a definitive meal blueprint (JSON).
*   **Handoff**: Passes the structured ingredient list to the Sub-Agents.

### B. Nutrition Agent (Sub-Agent)
*   **Trigger**: Receives the exact ingredient array from the Primary Agent.
*   **Action**: Uses MCP tools to query the USDA FoodData Central API.
*   **Output**: Returns validated, scaled macronutrient data (Calories, Protein, Carbs, Fat) back to the orchestrator.

### C. Supermarket Agent (Sub-Agent)
*   **Trigger**: Receives the ingredient list and the user's location coordinates.
*   **Action**: Uses MCP tools to interface with mapping or grocery APIs to locate the nearest supermarket and map ingredients to standard grocery items.
*   **Output**: Generates a localized, scalable grocery list.

## 4. Data Flow Protocol
1.  **User Input**: User submits a craving via the React UI.
2.  **State Retrieval**: Backend fetches the user's biometric data from the database.
3.  **Agent Chain**: 
    *   Meal Definition Agent drafts the recipe.
    *   Nutrition Agent fetches macros via MCP.
    *   Supermarket Agent builds the grocery list via MCP.
4.  **Response**: Backend aggregates the JSON outputs and streams them to the React UI for dynamic rendering.
5.  **Storage**: The final generated meal and its vector embeddings are written to the database for future recommendations.