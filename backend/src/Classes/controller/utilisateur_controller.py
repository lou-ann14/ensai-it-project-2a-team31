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
from src.Classes.classes_service.utilisateurs_service.client_service import (
    ClientService,
)
from src.schema.administrateur_schema import UtilisateurReponseModel
from src.schema.collaborateur_schema import MessageModel
from src.schema.gare_schema import GareReponseModel
from src.schema.train_schema import TrainReponseModel
from src.schema.utilisateur_schema import (
    CompteCreationModel,
    ReservationCreationModel,
    ReservationReponseModel,
    TrajetReponseModel,
)
from src.utils.log_utils import get_logger
from src.utils.securite import verif_token

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


def get_client_service():
    """Dependency Injection provider for ClientService."""
    return ClientService()


def trouver_client(id_client: int, utilisateur=Depends(verif_token)) -> Client:
    """Récupère le client à partir de son id
    Raises:
        HTTPException: erreur 400 si le compte n'est pas un compte client
        HTTPException: erreur 404 si le client n'existe pas
    """
    utilisateur = UtilisateurDAO().trouver_par_id(id_client)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail=f"Le client #{id_client} n'existe pas.")
    if utilisateur.grade != "CLIENT":
        raise HTTPException(status_code=400, detail="Cette action est réservée aux comptes clients.")
    return Client(mdp=utilisateur.mdp, nom_utilisateur=utilisateur.nom_utilisateur, id=utilisateur.id)


def trouver_gare(nom: str, gare_service: GareService) -> Gare:
    """Retrouve une gare à partir de son nom (insensible à la casse)
    Le nom exact est prioritaire : « Rennes » désigne Rennes, et non Rennes Beaulieu Chimie.
    Sinon, un début de nom suffit s'il ne correspond qu'à une seule gare.
    Param:
        nom (str) : le nom de la gare, ou son début
        gare_service (GareService)
    Returns:
        Gare : la gare trouvée
    Raises:
        HTTPException: erreur 400 si le nom est vide ou correspond à plusieurs gares
        HTTPException: erreur 404 si aucune gare ne correspond
    """
    nom = nom.strip()
    if not nom:
        raise HTTPException(status_code=400, detail="Le nom de la gare est obligatoire.")

    gares = gare_service.rechercher(nom, None)
    exactes = [gare for gare in gares if gare.nom.casefold() == nom.casefold()]
    candidates = exactes or gares

    if not candidates:
        raise HTTPException(status_code=404, detail=f"Aucune gare ne correspond à « {nom} ».")
    if len(candidates) > 1:
        exemples = ", ".join(f"{gare.nom} ({gare.ville})" for gare in candidates[:5])
        raise HTTPException(
            status_code=400,
            detail=f"Plusieurs gares correspondent à « {nom} », précisez le nom : {exemples}.",
        )
    return candidates[0]


@router.get("/trajets", response_model=list[TrajetReponseModel], tags=["Utilisateur"])
def rechercher_trajets(
    gare_depart: str,
    gare_arrivee: str,
    date_voyage: date,
    trajet_service=Depends(get_trajet_service),
    gare_service=Depends(get_gare_service),
    utilisateur=Depends(verif_token)
):
    """Recherche les trajets entre deux gares pour un jour donné
    Param:
        gare_depart (str) : le nom de la gare de départ
        gare_arrivee (str) : le nom de la gare d'arrivée
        date_voyage (date) : le jour du voyage (format AAAA-MM-JJ)
    Returns:
        list[TrajetReponseModel] : les trajets triés par heure de départ (liste vide si aucun)
    Raises:
        HTTPException: erreur 400 si les deux gares sont identiques ou si un nom est vide
                       ou correspond à plusieurs gares
        HTTPException: erreur 404 si aucune gare ne correspond à un nom
    """
    logger.info("Recherche de trajets par un utilisateur")

    depart = trouver_gare(gare_depart, gare_service)
    arrivee = trouver_gare(gare_arrivee, gare_service)

    try:
        return trajet_service.rechercher(depart, arrivee, date_voyage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gares", response_model=list[GareReponseModel], tags=["Utilisateur"])
def rechercher_gares(
    nom: str | None = None,
    ville: str | None = None,
    gare_service=Depends(get_gare_service),
    utilisateur=Depends(verif_token)
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
    utilisateur=Depends(verif_token)
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
    client = trouver_client(reservation.id_client)

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


@router.get("/reservations", response_model=list[ReservationReponseModel], tags=["Utilisateur"])
def voir_historique_reservations(id_client: int, client_service=Depends(get_client_service), utilisateur=Depends(verif_token)):
    """Affiche toutes les réservations d'un client (passées et à venir)
    Param:
        id_client (int) : l'id du client
    Returns:
        list[ReservationReponseModel] : les réservations du client (liste vide si aucune)
    Raises:
        HTTPException: erreur 400 si le compte n'est pas un compte client
        HTTPException: erreur 404 si le client n'existe pas
    """
    logger.info("Consultation de l'historique des réservations")

    return client_service.voir_historique_reservations(trouver_client(id_client))


@router.delete("/reservations/{id_reservation}", response_model=MessageModel, tags=["Utilisateur"])
def annuler_reservation(id_reservation: int, id_client: int, client_service=Depends(get_client_service), utilisateur=Depends(verif_token)):
    """Annule une réservation d'un client
    Param:
        id_reservation (int) : l'id de la réservation à annuler
        id_client (int) : l'id du client qui annule
    Returns:
        MessageModel : un message de confirmation
    Raises:
        HTTPException: erreur 400 si le compte n'est pas un compte client, si la réservation
                       appartient à un autre client ou si le trajet est déjà parti
        HTTPException: erreur 404 si le client ou la réservation n'existe pas
    """
    logger.info("Annulation d'une réservation")

    client = trouver_client(id_client)

    try:
        annulee = client_service.annuler_reservation(client, id_reservation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not annulee:
        raise HTTPException(status_code=404, detail=f"La réservation #{id_reservation} n'existe pas.")

    return {"message": "Annulation de la réservation réussie"}


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


@router.get("/trains/{num_train}", response_model=TrainReponseModel, tags=["Utilisateur"])
def trouver_train(num_train: int, train_service=Depends(get_train_service), utilisateur=Depends(verif_token)):
    """Trouve un train à l'aide de son numéro
    Param:
        num_train (int)
    Returns:
        TrainReponseModel : le train trouvé
    Raises:
        HTTPException: erreur 404 si le train n'est pas trouvé
    """
    logger.info("Recherche d'un train par un utilisateur")

    return train_service.trouver_train_par_num(num_train)
