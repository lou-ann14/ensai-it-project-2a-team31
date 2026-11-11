# Frontend (Streamlit)

Interface web de l'API Concurrent SNCF. Elle appelle l'API du backend : celle-ci doit donc être lancée avant.

## Lancer l'application

Depuis la racine du dépôt :

```bash
# 1. Backend (dans un premier terminal)
uv sync --project backend
uv run --project backend python backend/main.py

# 2. Frontend (dans un second terminal)
uv sync --project frontend
uv run --project frontend streamlit run frontend/app.py
```

L'interface est servie sur le port **8501**. Sur Onyxia, ouvrez-la avec l'URL du proxy VS Code
(`VSCODE_PROXY_URI`) en remplaçant `{{port}}` par `8501`, ou depuis l'onglet **Ports** de VS Code.

L'URL de l'API est lue dans le `.env` (`BACKEND_URL`, par défaut `http://localhost:5000`),
tout comme le délai d'attente (`BACKEND_TIMEOUT`, en secondes).

## Comptes de test

Créés par `GET /reset_database` (fichier `backend/data/admin.sql`) :

| Nom             | Mot de passe | Grade         |
|-----------------|--------------|---------------|
| `admin`         | `123`        | ADMIN         |
| `collaborateur` | `456`        | COLLABORATEUR |
| `client`        | `789`        | CLIENT        |

## Pages selon le grade

| Grade         | Pages                                                        |
|---------------|--------------------------------------------------------------|
| Tous          | Connexion, création de compte, recherche de trajets          |
| CLIENT        | Réservation depuis la recherche, Mes réservations (annulation) |
| COLLABORATEUR | Gares (import SNCF), Lignes, Trains, Trajets                 |
| ADMIN         | Comptes (recherche, changement de grade)                     |

## Organisation du code

```
frontend/
├── app.py        # point d'entrée : connexion et navigation selon le grade
├── api.py        # appels HTTP à l'API (une fonction par route)
├── commun.py     # session, gestion des erreurs, formatage
└── vues/         # une page par fichier
```
