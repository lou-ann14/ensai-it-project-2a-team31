# Backend - Concurrent SNCF API

This is a layered REST API built with [FastAPI](https://fastapi.tiangolo.com/). It manages user
accounts, railway lines, trains, journeys and bookings. Stations and travel times come from the
[SNCF API](https://numerique.sncf.com/startup/api/).

For more information, see the [main README](../README.md).

## Setup

1. Create a `backend/.env` file:

   ```env
   POSTGRES_HOST=127.0.0.1
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=projet2a
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=...
   POSTGRES_SCHEMA=projet
   SNCF_API_TOKEN=...
   ```

   This file contains passwords: it is ignored by Git and must never be committed.

2. Install the dependencies (from the repository root):

   ```bash
   uv sync --project backend
   ```

3. First launch only: initialize the database (creates the tables and the test accounts).
   **Warning: this deletes everything in the schema.**

   ```bash
   cd backend
   uv run python -m src.utils.reset_bdd
   cd ..
   ```

   After that, the database can also be reset from the Swagger with `GET /reset_database`
   (admin account only).

## Run the application

From the repository root:

```bash
uv run --project backend python backend/main.py
```

The API runs on port **5000**. The Swagger documentation is at `http://127.0.0.1:5000/docs`.

### Test accounts

| Username        | Password | Role          |
|-----------------|----------|---------------|
| `admin`         | `123`    | ADMIN         |
| `collaborateur` | `456`    | COLLABORATEUR |
| `client`        | `789`    | CLIENT        |

### Using the Swagger

1. Call `POST /login/` with one of the accounts above and copy the `token_acces` you get back.
2. Paste this token in the `x-auth-token` field of the other routes.

Roles follow a hierarchy: **CLIENT < COLLABORATEUR < ADMIN**. A collaborator can do everything a
client can, and an admin can do everything a collaborator can. The only exception: an admin
cannot change the role of another admin.

| Routes                                 | Who can use them         | Examples                                                    |
|----------------------------------------|--------------------------|-------------------------------------------------------------|
| `/login`, `POST /utilisateur/comptes`  | anyone                   | log in, create an account                                   |
| `/utilisateur/...`                     | any logged-in user       | search stations and journeys, book, cancel, change password |
| `/collaborateur/...`                   | COLLABORATEUR and ADMIN  | import stations, manage trains, lines and journeys          |
| `/admin/...`, `/reset_database`        | ADMIN only               | find an account, change a role, reset the database          |

## Architecture

The backend follows a **layered architecture**. Each layer only calls the layer below it.

- **Business objects** (`classes_objets/`): the domain entities (user, station, line, train, journey, booking)
- **Controllers** (`controller/`): FastAPI routes. They check the token and the role, and turn
  business errors into HTTP status codes
- **Services** (`classes_service/`): the business rules (seats, prices, travel times...)
- **DAO** (`classes_DAO/`): the SQL queries to the PostgreSQL database
- **Schemas** (`schema/`): request and response models with
  [Pydantic](https://docs.pydantic.dev/latest/), so requests and responses follow a strict structure
- **Utils** (`utils/`): database connection, security (password hashing, token, roles),
  SNCF API client, logs

Error codes: `400` invalid data or business rule not respected, `401` not logged in,
`403` role too low, `404` not found, `502` SNCF API unavailable.

### Config files

| File                  | Description                                                     |
|-----------------------|-----------------------------------------------------------------|
| `logging_config.yml`  | Configuration of the logging system                             |
| `pyproject.toml`      | Project metadata and dependencies (the frontend has its own)    |
| `uv.lock`             | Pins the exact version of each dependency (the frontend has its own) |
| `data/init_bdd.sql`   | Creates the tables                                              |
| `data/admin.sql`      | Creates the three test accounts                                 |
| `__init__.py`         | Marks a folder as a Python package                              |

## ⚒️ Development toolkit

### Debugging & logs

Logs are written to the `backend/logs/` folder, with the format defined in `logging_config.yml`.
Every HTTP request is logged. The `@log` decorator also logs the inputs and outputs of a method,
which makes it easier to follow the data through the services.

### Unit tests

From the `backend/` folder:

```bash
uv run --with pytest --with httpx python -m pytest -q
```

With the code coverage:

```bash
uv run --with pytest --with httpx --with pytest-cov python -m pytest -q --cov=src
```

The database and the SNCF API are mocked, so the tests do not need any connection.
There are 416 tests (85 % coverage), split by layer:

| Folder                           | What is tested                           |
|----------------------------------|------------------------------------------|
| `tests/test_objets`              | business objects, SNCF client, roles     |
| `tests/tests_DAO`                | SQL queries                              |
| `tests/tests_service`            | business rules                           |
| `tests/test_controller_optionel` | HTTP routes (status codes, security)     |
