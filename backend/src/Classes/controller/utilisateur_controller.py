from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service.gare_service import GareService
from src.Classes.classes_service.reservations_service import ReservationService
from src.Classes.classes_service.train_service import TrainService
from src.Classes.classes_service.trajet_service import TrajetService
from src.schema.administrateur_schema import UtilisateurReponseModel
from src.schema.gare_schema import GareReponseModel
from src.schema.train_schema import TrainBaseModel
from src.schema.utilisateur_schema import (
    CompteCreationModel,
    ReservationCreationModel,
    ReservationReponseModel,
    TrajetReponseModel,
)
from src.utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_gare_service():
    """Dependency Injection provider for GareService."""
    return GareService()


def get_reservation_service():
    """Dependency Injection provider for ReservationService."""
    return ReservationService()


def get_train_service():
    """Dependency Injection provider for TrainService."""
    return TrainService()


def get_trajet_service():
    """Dependency Injection provider for TrajetService."""
    return TrajetService()


@router.get("/trajets", response_model=list[TrajetReponseModel], tags=["Utilisateur"])
def rechercher_trajets(
    id_gare_depart: int,
    id_gare_arrivee: int,
    date_voyage: date,
    trajet_service=Depends(get_trajet_service),
):
    """Recherche les trajets entre deux gares pour un jour donné
    Param:
        id_gare_depart (int) : l'id de la gare de départ
        id_gare_arrivee (int) : l'id de la gare d'arrivée
        date_voyage (date) : le jour du voyage (format AAAA-MM-JJ)
    Returns:
        list[TrajetReponseModel] : les trajets triés par heure de départ (liste vide si aucun)
    Raises:
        HTTPException: erreur 400 si les deux gares sont identiques
    """
    logger.info("Recherche de trajets par un utilisateur")

    # La recherche n'utilise que l'id des gares
    gare_depart = Gare(nom=None, ville=None, id_sncf=None, id_gare=id_gare_depart)
    gare_arrivee = Gare(nom=None, ville=None, id_sncf=None, id_gare=id_gare_arrivee)

    try:
        return trajet_service.rechercher(gare_depart, gare_arrivee, date_voyage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gares", response_model=list[GareReponseModel], tags=["Utilisateur"])
def rechercher_gares(
    nom: str | None = None,
    ville: str | None = None,
    gare_service=Depends(get_gare_service),
):
    """Recherche des gares par nom et/ou par ville (autocomplétion)
    Param:
        nom (str, optionnel) : début du nom de la gare
        ville (str, optionnel) : début du nom de la ville
    Returns:
        list[GareReponseModel] : les gares correspondantes (liste vide si aucune)
    """
    logger.info("Recherche de gares par un utilisateur")
    return gare_service.rechercher(nom, ville)


@router.post(
    "/reservations",
    response_model=ReservationReponseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Utilisateur"],
)
def reserver(
    reservation: ReservationCreationModel,
    reservation_service=Depends(get_reservation_service),
    trajet_service=Depends(get_trajet_service),
):
    """Réserve une place sur un trajet
    Param:
        reservation: l'id du client, l'id du trajet, la place et la classe (1 ou 2)
    Returns:
        ReservationReponseModel : la réservation créée, avec son client, son trajet et son prix
    Raises:
        HTTPException: erreur 400 si une donnée est invalide, si le trajet est déjà parti,
                       si le compte n'est pas un compte client ou si la place est déjà prise
        HTTPException: erreur 404 si le client ou le trajet n'existe pas
    """
    logger.info("Création d'une réservation")

    # Les id servent seulement à désigner le client et le trajet : le service reçoit des objets
    utilisateur = UtilisateurDAO().trouver_par_id(reservation.id_client)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail=f"Le client #{reservation.id_client} n'existe pas.")
    if utilisateur.grade != "CLIENT":
        raise HTTPException(status_code=400, detail="Seul un compte client peut réserver un trajet.")
    client = Client(mdp=utilisateur.mdp, nom_utilisateur=utilisateur.nom_utilisateur, id=utilisateur.id)

    trajet = trajet_service.trouver_par_id(reservation.id_trajet)
    if trajet is None:
        raise HTTPException(status_code=404, detail=f"Le trajet #{reservation.id_trajet} n'existe pas.")

    try:
        return reservation_service.creer(
            client,
            trajet,
            reservation.place,
            reservation.classe,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/comptes",
    response_model=UtilisateurReponseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Utilisateur"],
)
def creer_compte(compte: CompteCreationModel):
    """Crée un compte client
    Param:
        compte: le nom d'utilisateur et le mot de passe
    Returns:
        UtilisateurReponseModel : le compte créé, avec l'id généré par la base (sans le mot de passe)
    Raises:
        HTTPException: erreur 400 si une donnée est invalide ou si le nom est déjà pris
    """
    logger.info("Création d'un compte")

    nom_utilisateur = compte.nom_utilisateur.strip()

    if not nom_utilisateur or not compte.mdp:
        raise HTTPException(status_code=400, detail="Le nom d'utilisateur et le mot de passe sont obligatoires.")
    if UtilisateurDAO().trouver_par_nom_utilisateur(nom_utilisateur) is not None:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")

    # Le grade est imposé : on ne laisse pas quelqu'un se créer un compte ADMIN
    try:
        nouvel_utilisateur = Utilisateur(id=None, mdp=compte.mdp, nom_utilisateur=nom_utilisateur, grade="CLIENT")
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UtilisateurDAO().creer(nouvel_utilisateur)


@router.get("/trains/{num_train}", response_model=TrainBaseModel, tags=["Utilisateur"])
def trouver_train(num_train: int, train_service=Depends(get_train_service)):
    """Trouve un train à l'aide de son numéro
    Param:
        num_train (int)
    Returns:
        TrainBaseModel : le train trouvé
    Raises:
        HTTPException: erreur 404 si le train n'est pas trouvé
    """
    logger.info("Recherche d'un train par un utilisateur")

    train = train_service.trouver_par_num(num_train)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train (numéro={num_train}) non trouvé.")
    return train
