# Concurrent SNCF - ENSAI 2nd year IT project

API for a railway company that runs trains on the SNCF network: user accounts, lines, journeys
and bookings. Stations and travel times come from the
[SNCF API](https://numerique.sncf.com/startup/api/).

**Team**: Adam BENAMER, Satya KREMER, Nathan TIATIA, Laurine LEROY, Lou-Ann CLEMENT, Nour NSIRI
- **Supervisor**: Kévin LEROY

More details in [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).

---

## Features

| | Feature | Who |
|---|---|---|
| **F1** | Create an account, log in, change password; the admin changes the role of an account (except other admins) | Everyone / ADMIN |
| **F2** | Create, edit and delete a line between two stations (stations imported from the SNCF API, autocompletion) | COLLABORATEUR |
| **F3** | Plan, edit and delete a journey (date, train, price); **travel time computed with the SNCF API** | COLLABORATEUR |
| **F4** | Search the journeys between two stations on a given day | Everyone |
| **F5** | **Remaining seats** in each class and **transparent pricing** (price split: operating cost, network fee, margin, VAT) in the search results | Everyone |
| **FO1** | Book a seat (given automatically, or picked from the free seats), see past and upcoming bookings, cancel | CLIENT |
| **FO2** | Two travel classes: 2nd class (base price) and 1st class (base price × 1.5) | CLIENT |

Roles follow a hierarchy: **CLIENT < COLLABORATEUR < ADMIN**. A collaborator can do everything a
client can (including booking), and an admin can do everything a collaborator can.

---

## Setup

Requirements: Python 3.13, [uv](https://docs.astral.sh/uv/), a PostgreSQL database and an SNCF API token.

Create a `backend/.env` file (it is ignored by Git, never commit it):

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DATABASE=projet2a
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_SCHEMA=projet
SNCF_API_TOKEN=...
```

Install the dependencies (from the repository root):

```bash
uv sync --project backend
uv sync --project frontend   # only for the web interface
```

Initialize the database (creates the tables and the test accounts, **deletes the schema if it exists**):

```bash
cd backend
uv run python -m src.utils.reset_bdd
cd ..
```

---

## Run

```bash
# Backend: API on http://127.0.0.1:5000, Swagger documentation on /docs
uv run --project backend python backend/main.py

# Frontend (optional, in a second terminal): interface on http://localhost:8501
uv run --project frontend streamlit run frontend/app.py
```

On Onyxia, open ports 5000 / 8501 from the **Ports** tab of VS Code.

### Test accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `123` | ADMIN |
| `collaborateur` | `456` | COLLABORATEUR |
| `client` | `789` | CLIENT |

### Using the API (Swagger)

1. `POST /login/` with a test account, then copy the `token_acces` you get back.
2. On the other routes, paste this token in the **`x-auth-token`** field.
3. Typical flow:
   - **collaborator**: `POST /collaborateur/gares/importer?q=Rennes` (then `Nantes`) → `POST /collaborateur/trains`
     → `POST /collaborateur/lignes` → `POST /collaborateur/trajets`
   - **client**: `GET /utilisateur/trajets` (remaining seats, price details) → `GET /utilisateur/trajets/{id}/places`
     (free seats) → `POST /utilisateur/reservations`
     → `GET /utilisateur/reservations` → `DELETE /utilisateur/reservations/{id}`

### Business rules

- **Identity**: the user always comes from the token, never from an id sent in the request.
  Nobody can book, see or cancel a booking for someone else.
- **Seats**: a seat is a number between 1 and the capacity of the class in the train
  (e.g. 1 to 300 in 2nd class). A seat can only be booked once per journey and class.
  If no seat is given, the first free seat is assigned.
- **Capacity**: the capacity of a train cannot go below the seats already booked on its upcoming
  journeys.
- **Journeys**: a journey cannot be planned in the past. Once a journey has bookings, its line
  cannot change and its train cannot be replaced by a train that is too small (changing the time
  is still allowed).
- **Prices**: 2nd class = base price, 1st class = base price × 1.5. The price details assume 10 %
  VAT, then 35 % network fee, 50 % operating cost and 15 % margin on the price before tax
  (company assumptions, in `tarification.py`).
- **Error codes**: `401` not logged in or invalid token, `403` role too low,
  `400` invalid data or business rule not respected, `404` not found,
  `502` SNCF API unavailable.

---

## Tests

```bash
cd backend
uv run --with pytest --with httpx2 python -m pytest -q
```

416 tests, **85 % code coverage**. The database and the SNCF API are mocked (no connection
needed). The full flow was also checked by hand on PostgreSQL with the real SNCF API.

| Folder | What is tested |
|---|---|
| `tests/test_objets` | business classes, SNCF API client, roles |
| `tests/tests_DAO` | SQL queries (mocked cursor) |
| `tests/tests_service` | business rules |
| `tests/test_controller_optionel` | HTTP routes (status codes, security) |

---

## Architecture

```
backend/
├── main.py                      # FastAPI application
├── data/                        # init_bdd.sql (tables), admin.sql (test accounts)
└── src/
    ├── Classes/
    │   ├── controller/          # HTTP routes: check the role, turn errors into HTTP codes
    │   ├── classes_service/     # business rules
    │   ├── classes_DAO/         # SQL queries
    │   └── classes_objets/      # Utilisateur, Gare, Ligne, Train, Trajet, Reservation
    ├── schema/                  # Pydantic models for requests and responses
    └── utils/                   # database connection, security (hash, token, roles), SNCF API client, logs
frontend/                        # Streamlit interface (see frontend/README.md)
Dossier_analyse/                 # analysis report and diagrams
suivi-folder/                    # weekly progress reports
```

Stations are imported once from the SNCF API and then stored in our database: autocompletion
queries our database (fast) instead of calling the API for every letter typed.

---

## Known limitations

- The login token does not expire; logging in again replaces the previous token.
- A collaborator can change the time of a journey that already has bookings: passengers are not
  notified (there is no communication channel between clients and collaborators).
- The SNCF API only knows the timetables a few weeks ahead: for a later journey, the travel time
  used is the one from the current timetables.
