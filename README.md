# Concurrent SNCF — Projet informatique 2A ENSAI

API d'une compagnie ferroviaire qui exploite le réseau SNCF : gestion des comptes, des lignes,
des trajets et des réservations. Les gares et les temps de trajet viennent de
l'[API SNCF](https://numerique.sncf.com/startup/api/).

**Équipe** : Adam BENAMER, Satya KREMER, Nathan TIATIA, Laurine LEROY, Lou-Ann CLEMENT, Nour NSIRI
— **Encadrant** : Kévin LEROY

---

## Fonctionnalités

| | Fonctionnalité | Qui |
|---|---|---|
| **F1** | Création de compte, connexion, changement de mot de passe ; l'admin change le grade des comptes (sauf ceux des autres admins) | Tous / ADMIN |
| **F2** | Créer, modifier, supprimer une ligne entre deux gares (gares importées depuis l'API SNCF, autocomplétion) | COLLABORATEUR |
| **F3** | Planifier, modifier, supprimer un trajet (date, train, tarif) ; **durée calculée par l'API SNCF** | COLLABORATEUR |
| **F4** | Rechercher les trajets entre deux gares pour un jour donné | Tous |
| **F5** | **Places restantes** par classe affichées dans la recherche | Tous |
| **FO1** | Réserver une place, voir ses réservations passées et à venir, annuler | CLIENT |
| **FO2** | Deux classes de voyage : 2de classe (tarif de base) et 1re classe (tarif × 1,5) | CLIENT |

---

## Installation

Prérequis : Python 3.13, [uv](https://docs.astral.sh/uv/), une base PostgreSQL et un token de l'API SNCF.

Créer un fichier `backend/.env` :

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DATABASE=projet2a
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_SCHEMA=projet
SNCF_API_TOKEN=...
```

Installer les dépendances (depuis la racine du dépôt) :

```bash
uv sync --project backend
uv sync --project frontend   # seulement pour l'interface web
```

Initialiser la base (crée les tables et les comptes de test, **efface le schéma s'il existe**) :

```bash
cd backend
uv run python -m src.utils.reset_bdd
cd ..
```

---

## Lancement

```bash
# Backend : API sur http://127.0.0.1:5000, documentation Swagger sur /docs
uv run --project backend python backend/main.py

# Frontend (optionnel, dans un second terminal) : interface sur http://localhost:8501
uv run --project frontend streamlit run frontend/app.py
```

Sur Onyxia, ouvrir les ports 5000 / 8501 depuis l'onglet **Ports** de VS Code.

### Comptes de test

| Nom | Mot de passe | Grade |
|---|---|---|
| `admin` | `123` | ADMIN |
| `collaborateur` | `456` | COLLABORATEUR |
| `client` | `789` | CLIENT |

### Utiliser l'API (Swagger)

1. `POST /login/` avec un compte de test → copier le `token_acces` renvoyé.
2. Sur les autres routes, coller ce token dans le champ **`x-auth-token`**.
3. Parcours type :
   - **collaborateur** : `POST /collaborateur/gares/importer?q=Rennes` (puis `Nantes`) → `POST /collaborateur/trains`
     → `POST /collaborateur/lignes` → `POST /collaborateur/trajets`
   - **client** : `GET /utilisateur/trajets` (avec les places restantes) → `POST /utilisateur/reservations`
     → `GET /utilisateur/reservations` → `DELETE /utilisateur/reservations/{id}`

### Règles à connaître

- **Identité** : l'utilisateur est toujours déduit de son token, jamais d'un id passé dans la requête.
- **Places** : une place est un numéro entre 1 et la capacité de la classe dans le train
  (ex. 1 à 300 en 2de). Une place ne peut être réservée qu'une fois par trajet et par classe.
- **Codes d'erreur** : `401` non connecté ou token invalide, `403` grade insuffisant,
  `400` donnée invalide ou règle métier non respectée, `404` introuvable,
  `502` API SNCF indisponible.

---

## Tests

```bash
cd backend
uv run --with pytest --with httpx python -m pytest -q
```

348 tests, **84 % de couverture** du code. La base de données et l'API SNCF y sont simulées
(aucune connexion nécessaire). Le parcours complet a aussi été vérifié à la main sur PostgreSQL
avec la vraie API SNCF.

| Dossier | Ce qui est testé |
|---|---|
| `tests/test_objets` | classes métier, client de l'API SNCF |
| `tests/tests_DAO` | requêtes SQL (curseur simulé) |
| `tests/tests_service` | règles métier |
| `tests/test_controller_optionel` | routes HTTP (codes de retour, sécurité) |

---

## Architecture

```
backend/
├── main.py                      # application FastAPI
├── data/                        # init_bdd.sql (tables), admin.sql (comptes de test)
└── src/
    ├── Classes/
    │   ├── controller/          # routes HTTP : vérifient le grade, traduisent les erreurs en codes HTTP
    │   ├── classes_service/     # règles métier
    │   ├── classes_DAO/         # requêtes SQL
    │   └── classes_objets/      # Utilisateur, Gare, Ligne, Train, Trajet, Reservation
    ├── schema/                  # modèles Pydantic des requêtes et réponses
    └── utils/                   # connexion BDD, sécurité (hash, token), client API SNCF, logs
frontend/                        # interface Streamlit (voir frontend/README.md)
Dossier_analyse/                 # diagrammes du dossier d'analyse
```

Les gares sont importées une fois depuis l'API SNCF puis stockées en base : l'autocomplétion
interroge notre base (rapide) et non l'API à chaque lettre tapée.

---

## Limites connues

- Le token de connexion n'expire pas ; une nouvelle connexion remplace le token précédent.
- Un collaborateur peut modifier l'horaire d'un trajet déjà réservé : les passagers ne sont pas
  prévenus (pas de canal de communication client / collaborateur).
- L'API SNCF ne connaît les horaires que sur quelques semaines : pour un trajet plus lointain,
  la durée retenue est celle des horaires actuels.
