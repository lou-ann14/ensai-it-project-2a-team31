import requests
from fastapi import APIRouter, Depends, HTTPException
from src.Classes.classes_service.gare_service import GareService
from src.schema.gare_schema import GareReponseModel
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_gare_service():
    """Dependency Injection provider for GareService."""
    return GareService()


@router.get("/", response_model=list[GareReponseModel], tags=["Gares"])
def rechercher_gares(
    nom: str | None = None,
    ville: str | None = None,
    gare_service=Depends(get_gare_service),
):
    """Recherche des gares dans notre base (autocomplétion)
    Param:
        nom (str, optionnel) : début du nom de la gare
        ville (str, optionnel) : début du nom de la ville
    Returns:
        list[GareReponseModel] : les gares correspondantes (liste vide si aucune)
    """
    logger.info("Recherche de gares")
    return gare_service.rechercher(nom, ville)


@router.post("/importer", response_model=list[GareReponseModel], tags=["Gares"])
def importer_gares(q: str, gare_service=Depends(get_gare_service)):
    """Importe dans notre base les gares trouvées sur l'API SNCF
    Param:
        q (str) : texte à rechercher (au moins 2 caractères)
    Returns:
        list[GareReponseModel] : les gares importées
    Raises:
        HTTPException: erreur 400 si le texte est trop court
        HTTPException: erreur 502 si l'API SNCF est indisponible
    """
    logger.info("Import de gares depuis l'API SNCF")
    try:
        return gare_service.importer(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException:
        logger.exception("Erreur lors de l'appel à l'API SNCF")
        raise HTTPException(status_code=502, detail="L'API SNCF est indisponible ou a refusé la requête.")