from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service.utilisateurs_service.administrateur_service import (
    gradeS_VALIDES,
    AdministrateurService,
)
from src.schema.administrateur_schema import (
    UtilisateurCreationModel,
    UtilisateurReponseModel,
)
from src.utils.log_utils import get_logger

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

    try:
        utilisateur = administrateur_service.gerer_habilitation(id_utilisateur, nouveau_grade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return utilisateur


@router.post(
    "/utilisateurs",
    response_model=UtilisateurReponseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Administrateur"],
)
def ajouter_utilisateur(utilisateur: UtilisateurCreationModel):
    """Ajoute un nouvel utilisateur (CLIENT, COLLABORATEUR ou ADMIN)
    Param:
        utilisateur: le nom d'utilisateur, le mot de passe et le rôle
    Returns:
        UtilisateurReponseModel : l'utilisateur créé, avec l'id généré par la base
    Raises:
        HTTPException: erreur 400 si une donnée est invalide ou si le nom est déjà pris
    """
    logger.info("Ajout d'un utilisateur")

    nom_utilisateur = utilisateur.nom_utilisateur.strip()
    grade = utilisateur.grade.strip().upper()

    if not nom_utilisateur or not utilisateur.mdp:
        raise HTTPException(status_code=400, detail="Le nom d'utilisateur et le mot de passe sont obligatoires.")
    if grade not in gradeS_VALIDES:
        raise HTTPException(status_code=400, detail=f"Le rôle doit être parmi {', '.join(gradeS_VALIDES)}.")
    if UtilisateurDAO().trouver_par_nom_utilisateur(nom_utilisateur) is not None:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")

    try:
        nouvel_utilisateur = Utilisateur(id=None, mdp=utilisateur.mdp, nom_utilisateur=nom_utilisateur, grade=grade)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UtilisateurDAO().creer(nouvel_utilisateur)
