from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import (
    CollaborateurService,
)
from src.utils.db_connexion import DBConnexion
from src.Classes.controller import train_controller
from src.utils.env_var import display_values, load_environment_variables
from src.utils.log_utils import LogMiddleware, get_logger, initialize_logs
from src.utils.reset_bdd import Reset_bdd

logger = get_logger(__name__)

initialize_logs("Webservice")

load_environment_variables()
display_values()


app = FastAPI(title="My Webservice")

app.add_middleware(LogMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic 422 errors to log them.
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )

app.include_router(train_controller.router, prefix = "/trains", tags = ["Trains"])


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige vers la documentation de l'API"""
    return RedirectResponse(url="/docs")


@app.get("/reset_database", tags=["BDD"])
async def reset_database():
    """Réinitialise la base de données"""
    logger.info("Database reset")
    succes = Reset_bdd().demarrer()

    return {
        "message": f"Database re-initialization - {'SUCCES' if succes else 'ECHEC'}"
    }


@app.post("/creer_ligne")
async def creer_ligne(gare_depart_id: int, gare_arrivee_id: int, id_collaborateur: int):
    """Permet à un collaborateur de créer une ligne"""

    logger.info("Création d'une ligne")

    service = CollaborateurService(DBConnexion().connexion)
    id_ligne = service.creer_ligne(gare_depart_id, gare_arrivee_id, id_collaborateur)

    return {
        "message": "Création de la ligne réussie",
        "id_ligne": id_ligne
    }


@app.post("/creer_trajet")
async def creer_trajet(id_ligne: int, heure_depart: datetime, heure_arrivee: datetime, temps_trajet: int):
    """Permet à un collaborateur de créer un trajet"""

    logger.info("Création d'un trajet")

    service = CollaborateurService(DBConnexion().connexion)
    id_trajet = service.creer_trajet(id_ligne, heure_depart, heure_arrivee, temps_trajet)

    return {
        "message": "Création du trajet réussie",
        "id_trajet": id_trajet
    }

# Lance l'application FastAPI
if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
