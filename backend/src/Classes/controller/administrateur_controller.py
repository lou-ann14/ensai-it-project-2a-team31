import requests
from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service.gare_service import GareService
from src.Classes.classes_service.train_service import TrainService
from src.Classes.classes_service.utilisateurs_service.administrateur_service import (
    gradeS_VALIDES,
    AdministrateurService,
)
from src.schema.administrateur_schema import (
    UtilisateurCreationModel,
    UtilisateurReponseModel,
)
from src.schema.gare_schema import GareReponseModel
from src.schema.train_schema import TrainBaseModel
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_administrateur_service():
    """Dependency Injection provider for AdministrateurService."""
    return AdministrateurService()


def get_gare_service():
    """Dependency Injection provider for GareService."""
    return GareService()


def get_train_service():
    """Dependency Injection provider for TrainService."""
    return TrainService()


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


# ------------------------------------------------------------------ gares


@router.post("/gares/importer", response_model=list[GareReponseModel], tags=["Administrateur"])
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


# ----------------------------------------------------------------- trains


@router.post(
    "/trains",
    response_model=TrainBaseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Administrateur"],
)
def creer_train(train: TrainBaseModel, train_service=Depends(get_train_service)):
    """Crée un nouveau train
    Param:
        train: le type, les places initiales [1re classe, 2de classe] et le numéro du train
    Returns:
        TrainBaseModel : le train créé
    Raises:
        HTTPException: erreur 500 si la création du train rencontre un problème
    """
    logger.info("Création d'un train")

    nouveau_train = train_service.creer(train.type_train, train.places_initiales, train.num_train)
    if not nouveau_train:
        raise HTTPException(status_code=500, detail="Erreur pendant la création du train.")

    return nouveau_train


@router.put("/trains/{num_train}", response_model=TrainBaseModel, tags=["Administrateur"])
def modifier_capacite(num_train: int, t: TrainBaseModel, train_service=Depends(get_train_service)):
    """Modifie la capacité d'un train
    Param:
        num_train (int) : le numéro du train à modifier
        t: le train avec ses nouvelles places [1re classe, 2de classe]
    Returns:
        TrainBaseModel : le train modifié
    Raises:
        HTTPException: erreur 400 si la capacité est incorrecte
        HTTPException: erreur 404 si le train n'existe pas
        HTTPException: erreur 500 si la modification ne s'exécute pas
    """
    logger.info("Modification de la capacité d'un train")

    train = train_service.trouver_par_num(num_train)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train (numéro={num_train}) non trouvé.")

    try:
        modifie = train_service.modifier_capacite(num_train, t.places_initiales)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not modifie:
        raise HTTPException(status_code=500, detail="Erreur pendant la modification du train.")

    train.places_initiales = t.places_initiales
    return train
