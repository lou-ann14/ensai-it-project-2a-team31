from fastapi import APIRouter, Depends, HTTPException
from src.Classes.classes_service.utilisateurs_service.administrateur_service import (
    AdministrateurService,
)
from src.schema.administrateur_schema import UtilisateurReponseModel
from src.utils.log_utils import get_logger
from src.utils.securite import verif_token

router = APIRouter()

logger = get_logger(__name__)


def get_administrateur_service():
    """Dependency Injection provider for AdministrateurService."""
    return AdministrateurService()


@router.get("/utilisateurs", response_model=UtilisateurReponseModel, tags=["Administrateur"])
def rechercher_compte(
    id_utilisateur: int | None = None,
    nom_utilisateur: str | None = None,
    administrateur_service=Depends(get_administrateur_service),
    admin=Depends(verif_token)
):
    """Recherche un compte par identifiant ou par nom d'utilisateur
    Param:
        id_utilisateur (int, optionnel)
        nom_utilisateur (str, optionnel)
    Returns:
        UtilisateurReponseModel : l'utilisateur trouvé
    Raises:
        HTTPException: erreur 400 si aucun critère n'est renseigné
        HTTPException: erreur 404 si l'utilisateur n'est pas trouvé
    """
    logger.info("Recherche d'un compte")

    if admin.grade != "ADMIN":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        utilisateur = administrateur_service.recherche_compte(nom_utilisateur, id_utilisateur)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")


    return utilisateur


@router.put(
    "/utilisateurs/{id_utilisateur}/grade",
    response_model=UtilisateurReponseModel,
    tags=["Administrateur"],
)
def modifier_grade(
    id_utilisateur: int,
    nouveau_grade: str,
    administrateur_service=Depends(get_administrateur_service),
    admin=Depends(verif_token),
):
    """Modifie le niveau d'habilitation d'un utilisateur (CLIENT, COLLABORATEUR ou ADMIN)
    Param:
        id_utilisateur (int)
        nouveau_grade (str)
    Returns:
        UtilisateurReponseModel : l'utilisateur avec son nouveau rôle
    Raises:
        HTTPException: erreur 400 si le rôle est invalide, si l'utilisateur n'existe pas
                       ou si c'est un administrateur
    """
    logger.info("Modification du rôle d'un utilisateur")
    if admin.grade != "ADMIN":
        raise HTTPException(status_code=401, detail="Vous n'avez pas le niveau d'habilitation requis.")
    try:
        utilisateur = administrateur_service.gerer_habilitation(id_utilisateur, nouveau_grade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return utilisateur
