# Backend — API Concurrent SNCF

This is a layered REST API built with [FastAPI](https://fastapi.tiangolo.com/). It is used to manage users, travels, and their respective data.
For more information please refer to [main README](../README.md).

## Run the application
Command to run from the repository's root directory:


Install dependencies: `uv sync --project backend`
Run the application: `uv run --project backend python backend/main.py`

First lauch: click on **Reset Database** to initialize it.

## Architecture

The backend follows a **Layered Architecture**:

- **Business Object** (`classes_objets/`) : Represents the pure domain entities
- **Controller** (`controller/`) : Handles HTTP requests and routing via FastAPI
- **Service** (`classes_service/`) : Contains the core business logic
- **DAO** (`slasses_DAO/`) : Manages database interactions
- **Schema** (`schema/`) : Data contract via [Pydantic](https://pydantic.dev/docs/validation/latest/get-started/) to ensure API requests and responses follow a strict structure


### Config files

In both the backend and frontend folders, you will find:

| Item                  | Description                                         | 
| --------------------- | --------------------------------------------------- | 
| logging_config.yml    | Configuration for the structured logging system.    | 
| pyproject.toml        | Project metadata and dependency definitions.        | 
| uv.lock               | Lockfile that ensures reproducible environments by pinning exact dependency versions. |
| \_\_init\_\_.py       | Marks a directory as a Python package, enabling module imports. |


## ⚒️ Development toolkit

### Debugging & Logs

The application uses a structured logging system. Logs are written to the `backend/logs/` directory and follow the format defined in `logging_config.yml`.

A custom `@log` decorator is available to automatically log method inputs and outputs, making it much easier to trace the flow of data through the services.

### Unit tests

To run the tests from the repository's root directory:
`uv run --with pytest --with httpx python -m pytest -q`
