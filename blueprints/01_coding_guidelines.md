# Coding Guidelines & Architecture Rules

## Python Backend
* **Standard**: Strict adherence to PEP 8.
* **Typing**: All functions and classes must use comprehensive Python type hints.
* **Variable Naming Conventions**: 
  * Always use `train_df` (never `df_train`).
  * Always use `log_reg_clf` (never `clf_log_reg`).
  * Apply this naming logic universally across all data models and variables.
* **Architecture**: The system is a multi-agent AI data product integrating Model Context Protocol (MCP) tools for external queries and leveraging robust database storage.

## React Frontend
* Component-based architecture using functional components and hooks.
* Clean separation of state management and UI rendering.