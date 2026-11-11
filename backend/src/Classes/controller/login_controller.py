from fastapi import APIRouter, Depends, HTTPException
from src.schema.utilisateur_schema import CompteCreationModel
from src.Classes.classes_service.utilisateurs_service.utilisateur_service import (
    UtilisateurService,
)
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_uti_service():
    """Dependency provider."""
    return UtilisateurService()


@router.post("/", tags=["Login"])
def login(utilisateur: CompteCreationModel, service=Depends(get_uti_service)):
    """Authentifie un utilisateur.
    Param:
        utilisateur: nom et mot de passe
    Returns:
        dict: contient l'id de l'utilisateur, son nom, son grade et son token d'accès
    Raises:
        HTTPException: 401 error si les paramètres sont faux ou que l'utilisateur n'existe pas."""
    logger.info("Login")
    uti = service.login(utilisateur.nom_utilisateur, utilisateur.mdp)
    if uti:
        return {
            "id": uti.id,
            "nom": uti.nom_utilisateur,
            "grade": uti.grade,
            "token_acces": uti.token,
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")