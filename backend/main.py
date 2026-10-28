from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from src.utils.env_var import display_values, load_environment_variables
from src.utils.log_utils import LogMiddleware, get_logger, initialize_logs
from src.utils.reset_bdd import Reset_bdd
from fastapi import HTTPException   
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service.utilisateurs_service.administrateur_service import AdministrateurService


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

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige vers la documentation de l'API"""
    return RedirectResponse(url="/docs")


@app.get("/reset_database", tags=["Misc"])
async def reset_database():
    """Réinitialise la base de données"""
    logger.info("Database reset")
    succes = Reset_bdd().demarrer()

    return {
        "message": f"Database re-initialization - {'SUCCES' if succes else 'ECHEC'}"
    }

def utilisateur_en_json(utilisateur: Utilisateur) -> dict:
    """Transforme un Utilisateur en dictionnaire, sans le mot de passe"""
    return {"id": utilisateur.id, "nom_utilisateur": utilisateur.nom_utilisateur, "role": utilisateur.role}


@app.get("/admin/utilisateurs", tags=["Administrateur"])
def rechercher_compte(id_utilisateur: int | None = None, nom_utilisateur: str | None = None):
    """Recherche un compte par identifiant ou par nom d'utilisateur"""
    try:
        utilisateur = AdministrateurService().recherche_compte(nom_utilisateur, id_utilisateur)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return utilisateur_en_json(utilisateur)


@app.put("/admin/utilisateurs/{id_utilisateur}/role", tags=["Administrateur"])
def modifier_role(id_utilisateur: int, nouveau_role: str):
    """Modifie le niveau d'habilitation d'un utilisateur (CLIENT, COLLABORATEUR ou ADMIN)"""
    try:
        utilisateur = AdministrateurService().gerer_habilitation(id_utilisateur, nouveau_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return utilisateur_en_json(utilisateur)


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
