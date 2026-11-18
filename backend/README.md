# Backend — API Concurrent SNCF

API [FastAPI](https://fastapi.tiangolo.com/) du projet. L'installation, le lancement, les comptes de
test et l'architecture sont décrits dans le [README principal](../README.md).

Résumé (depuis la racine du dépôt) :

```bash
uv sync --project backend                          # dépendances
uv run --project backend python backend/main.py    # API sur le port 5000, Swagger sur /docs
```

Tests (depuis ce dossier) :

```bash
uv run --with pytest --with httpx python -m pytest -q
```
