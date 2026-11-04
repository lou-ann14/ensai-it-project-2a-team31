from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client
from src.Classes.classes_service.reservations_service import ReservationService
from src.utils.log_utils import log


class ClientService:
    """Classe qui gère les actions réservées aux clients"""

    @log
    def reserver_trajet(self, client: Client, trajet: Trajet, place: str, classe: int) -> Reservation:
        """
        Méthode servant à réserver une place sur un trajet.

        Param:
        ------
        client: Client
            le client qui réserve
        trajet: Trajet
            le trajet réservé
        place: str
            le numéro de place
        classe: int
            la classe choisie (1 ou 2)

        Return:
        ------
        Reservation
            la réservation créée, avec son id_reservation et son prix renseignés

        Raises:
        ------
        ValueError
            si une donnée est invalide, si le trajet est déjà parti,
            si le client n'existe pas en base ou si la place est déjà réservée
        """
        return ReservationService().creer(client, trajet, place, classe)

    @log
    def voir_historique_reservations(self, client: Client) -> list[Reservation]:
        """
        Méthode servant à consulter toutes les réservations d'un client (passées et à venir).

        Param:
        ------
        client: Client
            le client dont on veut l'historique

        Return:
        ------
        list[Reservation]
            la liste des réservations du client (vide si aucune)
        """
        return ReservationService().historique_par_client(client.id)

    @log
    def annuler_reservation(self, client: Client, id_reservation: int) -> bool:
        """
        Méthode servant à annuler une réservation du client.

        Param:
        ------
        client: Client
            le client qui annule
        id_reservation: int
            l'identifiant de la réservation à annuler

        Return:
        ------
        bool
            True si l'annulation a réussi, False si la réservation n'existe pas

        Raises:
        ------
        ValueError
            si la réservation appartient à un autre client
            ou si le trajet est déjà parti
        """
        reservation = ReservationDAO().trouver_par_id(id_reservation)
        if reservation is None:
            return False
        if reservation.client.id != client.id:
            raise ValueError("Cette réservation appartient à un autre client.")

        return ReservationService().annuler(id_reservation)
