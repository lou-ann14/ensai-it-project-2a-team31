# Frontend (Streamlit)

Web interface for the Concurrent SNCF API. It only talks to the backend API, so the backend
must be running first.

## Run the application

From the repository root:

```bash
# 1. Backend (first terminal)
uv sync --project backend
uv run --project backend python backend/main.py

# 2. Frontend (second terminal)
uv sync --project frontend
uv run --project frontend streamlit run frontend/app.py
```

The interface runs on port **8501** (`http://localhost:8501`). On Onyxia, open it with the
VS Code proxy URL (`VSCODE_PROXY_URI`) by replacing `{{port}}` with `8501`, or from the
**Ports** tab of VS Code.

The API address is read from the `.env` file (`BACKEND_URL`, default `http://localhost:5000`),
as well as the request timeout (`BACKEND_TIMEOUT`, in seconds, default 10). Requests that call
the SNCF API (station import, journey creation) get at least 30 seconds.

## Test accounts

Created when the database is initialized (file `backend/data/admin.sql`):

| Username        | Password | Role          |
|-----------------|----------|---------------|
| `admin`         | `123`    | ADMIN         |
| `collaborateur` | `456`    | COLLABORATEUR |
| `client`        | `789`    | CLIENT        |

## Pages by role

Roles follow a hierarchy: each role also gets the pages of the roles below it.

| Role          | Pages                                                                     |
|---------------|---------------------------------------------------------------------------|
| Not logged in | Login, account creation                                                   |
| CLIENT        | Search journeys, book a seat, My bookings (with cancellation)            |
| COLLABORATEUR | Everything above, plus Stations (SNCF import), Lines, Trains, Journeys    |
| ADMIN         | Everything above, plus Accounts (search, change a role)                   |

### Search and booking

- The departures board shows, for each journey: times, duration, train, price in both classes
  and the **remaining seats** in each class (`COMPLET` when a class is full).
- The "Tarification transparente" box shows how the price is split: operating cost,
  network fee, margin and VAT.
- When booking, the seat is given automatically by default. The user can also pick one in the
  list of free seats.

## Code organization

```
frontend/
├── app.py        # entry point: login and navigation by role
├── api.py        # HTTP calls to the API (one function per route)
├── commun.py     # session, error handling, formatting helpers
├── style.py      # look of the app (departures board, tickets)
└── vues/         # one page per file
```
