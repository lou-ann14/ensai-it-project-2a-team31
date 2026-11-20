from datetime import datetime

from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service import tarification
from src.Classes.classes_service.tarification import COEFFICIENT_PREMIERE_CLASSE  # noqa: F401 (réexporté)
from src.Classes.classes_service.trajet_service import TrajetService
from src.utils.log_utils import log

CLASSES_VALIDES = (1, 2)  # 1 = première classe, 2 = seconde classe
TENTATIVES_ATTRIBUTION = 3  # essais si une place attribuée automatiquement est prise entre-temps


class ReservationService:
    """Classe qui gère les opérations métier sur les réservations"""

    @log
    def creer(self, client: Utilisateur, trajet: Trajet, place: str | None, classe: int) -> Reservation:
        """
        Méthode servant à créer une réservation.

        Param:
        ------
        client: Utilisateur
            le client qui réserve
        trajet: Trajet
            le trajet réservé
        place: str | None
            le numéro de place choisi par le client, ou None / vide pour que
            la première place libre de la classe soit attribuée automatiquement
        classe: int
            la classe choisie lors de la réservation (1 ou 2)

        Return:
        ------
        Reservation
            la réservation créée, avec son id_reservation renseigné

        Raises:
        ------
        ValueError
            si une donnée est invalide, si le client ou le trajet est manquant,
            si le trajet est déjà parti, si le trajet n'a pas de train, s'il n'y a plus de place
            dans cette classe, si le numéro de place n'existe pas dans le train,
            si le client n'existe pas en base, ou si la place est déjà réservée pour ce trajet
            dans cette classe
        """
        if client is None:
            raise ValueError("Le client est obligatoire.")
        if classe not in CLASSES_VALIDES:
            raise ValueError("La classe doit être 1 (première) ou 2 (seconde).")
        place = place.strip() if place else ""

        if trajet is None:
            raise ValueError("Le trajet est obligatoire.")
        if trajet.heure_depart <= datetime.now():
            raise ValueError("Ce trajet est déjà parti : il n'est plus réservable.")

        # Place choisie par le client : on la vérifie. Sinon : on attribue la première place libre.
        attribution_auto = not place
        tentatives = TENTATIVES_ATTRIBUTION if attribution_auto else 1
        for tentative in range(1, tentatives + 1):
            if attribution_auto:
                place = self._attribuer_place(trajet, classe)
            else:
                place = self._verifier_place(trajet, place, classe)

            reservation = Reservation(
                client=client,
                trajet=trajet,
                place=place,
                classe=classe,
                prix=tarification.prix(trajet.tarif_base, classe),
                id_reservation=None
            )
            # La base garantit qu'une place n'est réservée qu'une fois par trajet et par classe
            # (contrainte UNIQUE sur id_trajet, classe, place) et que le client existe (clé étrangère)
            try:
                return ReservationDAO().creer(reservation)
            except UniqueViolation:
                # Place attribuée automatiquement mais prise entre-temps par un autre client :
                # on recommence avec la place libre suivante
                if attribution_auto and tentative < tentatives:
                    continue
                raise ValueError(f"La place {place} est déjà réservée pour ce trajet dans cette classe.")
            except ForeignKeyViolation:
                raise ValueError(f"Le client #{client.id} n'existe pas.")

    @staticmethod
    def _attribuer_place(trajet: Trajet, classe: int) -> str:
        """
        Attribue au client la première place libre de la classe choisie (place la plus petite).

        Return:
        ------
        str
            le numéro de la place attribuée

        Raises:
        ------
        ValueError
            si le trajet n'a pas de train ou si la classe est complète
        """
        libres = TrajetService().places_libres(trajet)[classe]
        if not libres:
            libelle = "première classe" if classe == 1 else "seconde classe"
            raise ValueError(f"Ce trajet est complet en {libelle}.")
        return str(libres[0])

    @staticmethod
    def _verifier_place(trajet: Trajet, place: str, classe: int) -> str:
        """
        Vérifie qu'il reste de la place dans la classe choisie et que le numéro de place existe.
        Une place est un numéro entre 1 et la capacité de la classe dans le train du trajet :
        avec la contrainte UNIQUE (id_trajet, classe, place) de la base, aucune surréservation
        n'est donc possible.

        Return:
        ------
        str
            le numéro de place normalisé (« 007 » devient « 7 », pour que la contrainte UNIQUE
            ne voie pas deux places différentes)

        Raises:
        ------
        ValueError
            si le trajet n'a pas de train, si la classe est complète
            ou si le numéro de place n'existe pas dans le train
        """
        if trajet.train is None:
            raise ValueError("Aucun train n'est associé à ce trajet : il n'est pas réservable.")

        libelle = "première classe" if classe == 1 else "seconde classe"
        capacite = trajet.train.places_premieres if classe == 1 else trajet.train.places_secondes

        TrajetService().ajouter_places_restantes([trajet])
        restantes = trajet.places_restantes_premiere if classe == 1 else trajet.places_restantes_seconde
        if not restantes:
            raise ValueError(f"Ce trajet est complet en {libelle}.")

        if not place.isdigit() or not 1 <= int(place) <= capacite:
            raise ValueError(f"La place doit être un numéro entre 1 et {capacite} en {libelle}.")
        return str(int(place))

    @log
    def annuler(self, id_reservation: int, id_client: int) -> bool:
        """
        Méthode servant à annuler une réservation existante.

        Param:
        ------
        id_reservation: int
            l'identifiant unique de la réservation à annuler
        id_client: int
            l'identifiant du client qui demande l'annulation

        Return:
        ------
        bool
            True si l'annulation a réussi, False sinon (réservation inexistante)

        Raises:
        ------
        ValueError
            si la réservation appartient à un autre client
            ou si le trajet de la réservation est déjà parti
        """
        reservation = ReservationDAO().trouver_par_id(id_reservation)
        if reservation is None:
            return False

        if reservation.client.id != id_client:
            raise ValueError("Cette réservation appartient à un autre client.")

        if reservation.trajet.heure_depart <= datetime.now():
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
