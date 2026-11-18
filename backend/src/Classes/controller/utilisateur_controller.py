from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_service.gare_service import GareService
from src.Classes.classes_service.reservations_service import ReservationService
from src.Classes.classes_service.train_service import TrainService
from src.Classes.classes_service.trajet_service import TrajetService
from src.Classes.classes_service.utilisateurs_service.utilisateur_service import (
    UtilisateurService,
)
from src.schema.administrateur_schema import UtilisateurReponseModel
from src.schema.collaborateur_schema import MessageModel
from src.schema.gare_schema import GareReponseModel
from src.schema.train_schema import TrainReponseModel
from src.schema.utilisateur_schema import (
    CompteCreationModel,
    MotDePasseModificationModel,
    ReservationCreationModel,
    ReservationReponseModel,
    TrajetReponseModel,
)
from src.utils.log_utils import get_logger
from src.utils.securite import verif_token

router = APIRouter()

logger = get_logger(__name__)


def get_utilisateur_service():
    """Dependency Injection provider for UtilisateurService."""
    return UtilisateurService()


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


def trouver_client(utilisateur=Depends(verif_token)) -> Client:
    """Dépendance FastAPI : renvoie le client connecté (identifié par son token).
    L'id du client vient toujours du token, jamais d'un paramètre de la requête :
    un client ne peut donc pas agir au nom d'un autre.
    Raises:
        HTTPException: erreur 401 si le token est manquant ou invalide (via verif_token)
        HTTPException: erreur 400 si le compte n'est pas un compte client
    """
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
    client: Client = Depends(trouver_client),
):
    """Réserve une place sur un trajet pour le client connecté
    Param:
        reservation: l'id du trajet, la place et la classe (1 ou 2)
    Returns:
        ReservationReponseModel : la réservation créée, avec son client, son trajet et son prix
    Raises:
        HTTPException: erreur 401 si le token est manquant ou invalide
        HTTPException: erreur 400 si une donnée est invalide, si le trajet est déjà parti,
                       si le compte n'est pas un compte client ou si la place est déjà prise
        HTTPException: erreur 404 si le trajet n'existe pas
    """
    logger.info("Création d'une réservation")

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
def voir_historique_reservations(
    reserv_service=Depends(get_reservation_service),
    client: Client = Depends(trouver_client),
):
    """Affiche toutes les réservations du client connecté (passées et à venir)
    Returns:
        list[ReservationReponseModel] : les réservations du client (liste vide si aucune)
    Raises:
        HTTPException: erreur 401 si le token est manquant ou invalide
        HTTPException: erreur 400 si le compte n'est pas un compte client
    """
    logger.info("Consultation de l'historique des réservations")

    return reserv_service.historique_par_client(client.id)


@router.delete("/reservations/{id_reservation}", response_model=MessageModel, tags=["Utilisateur"])
def annuler_reservation(
    id_reservation: int,
    reserv_service=Depends(get_reservation_service),
    client: Client = Depends(trouver_client),
):
    """Annule une réservation du client connecté
    Param:
        id_reservation (int) : l'id de la réservation à annuler
    Returns:
        MessageModel : un message de confirmation
    Raises:
        HTTPException: erreur 401 si le token est manquant ou invalide
        HTTPException: erreur 400 si le compte n'est pas un compte client, si la réservation
                       appartient à un autre client ou si le trajet est déjà parti
        HTTPException: erreur 404 si la réservation n'existe pas
    """
    logger.info("Annulation d'une réservation")

    try:
        annulee = reserv_service.annuler(id_reservation, client.id)
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
def creer_compte(compte: CompteCreationModel, utilisateur_service=Depends(get_utilisateur_service)):
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

    # Le service impose le grade CLIENT et hache le mot de passe
    try:
        return utilisateur_service.creer_compte(nom_utilisateur, compte.mdp)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/mot-de-passe", response_model=MessageModel, tags=["Utilisateur"])
def changer_mot_de_passe(
    demande: MotDePasseModificationModel,
    utilisateur_service=Depends(get_utilisateur_service),
    utilisateur=Depends(verif_token),
):
    """Change le mot de passe de l'utilisateur connecté (quel que soit son grade)
    Param:
        demande: l'ancien mot de passe (pour confirmer l'identité) et le nouveau
    Returns:
        MessageModel : un message de confirmation
    Raises:
        HTTPException: erreur 401 si le token est manquant ou invalide
        HTTPException: erreur 400 si l'ancien mot de passe est incorrect
                       ou si le nouveau mot de passe est vide
    """
    logger.info("Changement de mot de passe")

    try:
        change = utilisateur_service.changer_mdp(utilisateur.id, demande.ancien_mdp, demande.nouveau_mdp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not change:
        raise HTTPException(status_code=400, detail="L'ancien mot de passe est incorrect.")

    return {"message": "Mot de passe modifié avec succès"}


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

    train = train_service.trouver_train_par_num(num_train)
    if train is None:
        raise HTTPException(status_code=404, detail=f"Le train numéro {num_train} n'existe pas.")
    return train
