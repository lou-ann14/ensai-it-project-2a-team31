from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.utils.env_var import display_values, load_environment_variables
from src.utils.reset_bdd import Reset_bdd

load_environment_variables()
display_values()


app = FastAPI(title="My Webservice")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirige vers la documentation de l'API"""
    return RedirectResponse(url="/docs")


@app.get("/reset_database", tags=["Misc"])
async def reset_database():
    """Réinitialise la base de données"""
    succes = Reset_bdd().Demarrer()

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
