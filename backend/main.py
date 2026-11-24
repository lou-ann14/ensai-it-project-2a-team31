from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from src.Classes.controller import (
    administrateur_controller,
    collaborateur_controller,
    login_controller,
    utilisateur_controller,
)
from src.utils.env_var import display_values, load_environment_variables
from src.utils.log_utils import LogMiddleware, get_logger, initialize_logs
from src.utils.reset_bdd import Reset_bdd
from src.utils.securite import verif_token, verifier_grade

logger = get_logger(__name__)

initialize_logs("Webservice")

load_environment_variables()
display_values()


app = FastAPI(
    title="API Concurrent SNCF",
    version="1.0.0",
    description=(
        "API d'une compagnie ferroviaire concurrente de la SNCF (projet informatique 2A ENSAI).\n\n"
        "**Authentification** : `POST /login/` renvoie un `token_acces`, à envoyer ensuite "
        "dans l'en-tête `X-Auth-Token` de chaque requête.\n\n"
        "**Comptes de test** : `admin` / `123`, `collaborateur` / `456`, `client` / `789`."
    ),
)

app.add_middleware(LogMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepte les erreurs Pydantic 422 pour les ajouter aux logs.

    Param:
    ------
    request: Request
        la requête reçue
    exc: RequestValidationError
        l'erreur de validation

    Return:
    ------
    JSONResponse
        la réponse 422, avec le détail des erreurs
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )

app.include_router(administrateur_controller.router, prefix="/admin", tags=["Administrateur"])
app.include_router(collaborateur_controller.router, prefix="/collaborateur", tags=["Collaborateur"])
app.include_router(utilisateur_controller.router, prefix="/utilisateur", tags=["Utilisateur"])
app.include_router(login_controller.router, prefix="/login", tags=["Login"])

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redirige vers la documentation de l'API.

    Return:
    ------
    RedirectResponse
        la redirection vers la page /docs
    """
    return RedirectResponse(url="/docs")


@app.get("/reset_database", tags=["BDD"])
def reset_database(token=Depends(verif_token)):
    """
    Réinitialise la base de données (ADMIN uniquement).

    Param:
    ------
    token: Utilisateur
        l'utilisateur connecté, retrouvé grâce à son token

    Return:
    ------
    dict
        un message qui indique le résultat

    Raises:
    ------
    HTTPException
        erreur 401 si le token est manquant ou invalide
    HTTPException
        erreur 403 si l'utilisateur n'est pas administrateur
    """
    # Le grade est vérifié AVANT la réinitialisation : sinon n'importe quel compte connecté
    # pouvait effacer la base (l'erreur n'était levée qu'après coup).
    verifier_grade(token, "ADMIN")
    logger.info("Database reset")
    succes = Reset_bdd().demarrer()
    return {
        "message": f"Database re-initialization - {'SUCCES' if succes else 'ECHEC'}"
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

    logger.info("Arrêt du Webservice")
