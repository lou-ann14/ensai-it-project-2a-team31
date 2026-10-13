from datetime import datetime

from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_service.trajet_service import TrajetService
from src.utils.log_utils import log

CLASSES_VALIDES = (1, 2)  # 1 = première classe, 2 = seconde classe
COEFFICIENT_PREMIERE_CLASSE = 1.5  # la première classe coûte 1,5 fois le tarif de base


class ReservationService:
    """Classe qui gère les opérations métier sur les réservations"""

    @log
    def creer(self, id_client: int, id_trajet: int, place: str, classe: int) -> Reservation:
        """
        Méthode servant à créer une réservation.

        Param:
        ------
        id_client: int
            l'id du client
        id_trajet: int
            l'id du trajet réservé
        place: str
            le numéro de place de la réservation
        classe: int
            la classe choisie lors de la réservation (1 ou 2)

        Return:
        ------
        Reservation
            la réservation créée, avec son id_reservation renseigné

        Raises:
        ------
        ValueError
            si une donnée est invalide, si le trajet n'existe pas ou est déjà parti,
            si le client n'existe pas, ou si la place est déjà réservée pour ce trajet
            dans cette classe
        """
        if id_client is None:
            raise ValueError("Le client est obligatoire.")
        if classe not in CLASSES_VALIDES:
            raise ValueError("La classe doit être 1 (première) ou 2 (seconde).")
        place = place.strip() if place else ""
        if not place:
            raise ValueError("Le numéro de place est obligatoire.")

        trajet = TrajetService().trouver_par_id(id_trajet)
        if trajet is None:
            raise ValueError(f"Le trajet #{id_trajet} n'existe pas.")
        if trajet.heure_depart <= datetime.now():
            raise ValueError("Ce trajet est déjà parti : il n'est plus réservable.")

        # TODO : vérifier qu'il reste des places dans cette classe (capacité du train,
        # TrainDAO.trouver_par_id) quand TrainDAO sera écrit.

        prix = trajet.tarif_base
        if classe == 1:
            prix = prix * COEFFICIENT_PREMIERE_CLASSE

        reservation = Reservation(
            id_reservation=None,
            id_client=id_client,
            id_trajet=id_trajet,
            place=place,
            classe=classe,
            prix=round(prix, 2),
        )
        # La base garantit qu'une place n'est réservée qu'une fois par trajet et par classe
        # (contrainte UNIQUE sur id_trajet, classe, place) et que le client existe (clé étrangère)
        try:
            return ReservationDAO().creer(reservation)
        except UniqueViolation:
            raise ValueError(f"La place {place} est déjà réservée pour ce trajet dans cette classe.")
        except ForeignKeyViolation:
            raise ValueError(f"Le client #{id_client} n'existe pas.")

    @log
    def annuler(self, id_reservation: int) -> bool:
        """
        Méthode servant à annuler une réservation existante.

        Param:
        ------
        id_reservation: int
            l'identifiant unique de la réservation à annuler

        Return:
        ------
        bool
            True si l'annulation a réussi, False sinon (réservation inexistante)

        Raises:
        ------
        ValueError
            si le trajet de la réservation est déjà parti
        """
        reservation = ReservationDAO().trouver_par_id(id_reservation)
        if reservation is None:
            return False

        trajet = TrajetService().trouver_par_id(reservation.id_trajet)
        if trajet is not None and trajet.heure_depart <= datetime.now():
            raise ValueError("Ce trajet est déjà parti : la réservation ne peut plus être annulée.")

        return ReservationDAO().annuler(id_reservation)

    @log
    def historique_par_client(self, id_client: int) -> list[Reservation]:
        """
        Méthode servant à récupérer l'historique des réservations d'un client
        (passées et à venir).

        Param:
        ------
        id_client: int
            l'id du client

        Return:
        ------
        list[Reservation]
            la liste des réservations du client (vide si aucune)

        Raises:
        ------
        ValueError
            si l'id du client est manquant
        """
        if id_client is None:
            raise ValueError("Le client est obligatoire.")
        return ReservationDAO().trouver_par_client(id_client)
        