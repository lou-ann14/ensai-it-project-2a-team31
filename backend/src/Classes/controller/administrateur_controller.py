from fastapi import APIRouter, Depends, HTTPException
from src.Classes.classes_service.utilisateurs_service.administrateur_service import (
    AdministrateurService,
)
from src.schema.administrateur_schema import UtilisateurReponseModel
from src.utils.log_utils import get_logger
from src.utils.securite import verif_token, verifier_grade

router = APIRouter()

logger = get_logger(__name__)


def get_administrateur_service():
    """
    Fournit une instance de AdministrateurService (injection de dépendance FastAPI).

    Return:
    ------
    AdministrateurService
        une nouvelle instance de AdministrateurService
    """
    return AdministrateurService()


@router.get("/utilisateurs", response_model=UtilisateurReponseModel, tags=["Administrateur"])
def rechercher_compte(
    id_utilisateur: int | None = None,
    nom_utilisateur: str | None = None,
    administrateur_service=Depends(get_administrateur_service),
    admin=Depends(verif_token)
):
    """
    Recherche un compte par identifiant ou par nom d'utilisateur (réservé aux administrateurs).

    Param:
    ------
    id_utilisateur: int | None
        l'identifiant du compte recherché (optionnel)
    nom_utilisateur: str | None
        le nom d'utilisateur du compte recherché (optionnel)

    Return:
    ------
    UtilisateurReponseModel
        l'utilisateur trouvé

    Raises:
    ------
    HTTPException
        erreur 400 si aucun critère n'est renseigné
    HTTPException
        erreur 401 si le token est manquant ou invalide
    HTTPException
        erreur 403 si l'utilisateur n'a pas au moins le grade ADMIN
    HTTPException
        erreur 404 si l'utilisateur n'est pas trouvé
    """
    logger.info("Recherche d'un compte")

    verifier_grade(admin, "ADMIN")
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
    """
    Modifie le niveau d'habilitation d'un utilisateur (CLIENT, COLLABORATEUR ou ADMIN).
    Réservé aux administrateurs.

    Param:
    ------
    id_utilisateur: int
        l'identifiant de l'utilisateur à modifier
    nouveau_grade: str
        le nouveau grade : CLIENT, COLLABORATEUR ou ADMIN

    Return:
    ------
    UtilisateurReponseModel
        l'utilisateur avec son nouveau grade

    Raises:
    ------
    HTTPException
        erreur 400 si le grade est invalide, si l'utilisateur n'existe pas
        ou si c'est un administrateur
    HTTPException
        erreur 401 si le token est manquant ou invalide
    HTTPException
        erreur 403 si l'utilisateur n'a pas au moins le grade ADMIN
    """
    logger.info("Modification du rôle d'un utilisateur")
    verifier_grade(admin, "ADMIN")
    try:
        utilisateur = administrateur_service.gerer_habilitation(id_utilisateur, nouveau_grade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return utilisateur
