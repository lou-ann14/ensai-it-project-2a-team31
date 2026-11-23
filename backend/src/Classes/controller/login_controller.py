from fastapi import APIRouter, Depends, HTTPException
from src.Classes.classes_service.utilisateurs_service.utilisateur_service import (
    UtilisateurService,
)
from src.schema.utilisateur_schema import CompteCreationModel
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_uti_service():
    """
    Fournit une instance de UtilisateurService (injection de dépendance FastAPI).

    Return:
    ------
    UtilisateurService
        une nouvelle instance de UtilisateurService
    """
    return UtilisateurService()


@router.post("/", tags=["Login"])
def login(utilisateur: CompteCreationModel, service=Depends(get_uti_service)):
    """
    Authentifie un utilisateur et lui attribue un nouveau token d'accès.

    Param:
    ------
    utilisateur: CompteCreationModel
        le nom d'utilisateur et le mot de passe

    Return:
    ------
    dict
        l'id de l'utilisateur, son nom, son grade et son token d'accès

    Raises:
    ------
    HTTPException
        erreur 401 si le nom ou le mot de passe est incorrect
    """
    logger.info("Login")
    uti = service.login(utilisateur.nom_utilisateur, utilisateur.mdp)
    if uti:
        return {
            "id": uti.id,
            "nom": uti.nom_utilisateur,
            "grade": uti.grade,
            "token_acces": uti.token,
        }
    raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect.")