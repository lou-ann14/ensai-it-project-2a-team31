from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.utilisateurs.client import Client
from src.utils.db_connexion import DBConnexion


class ReservationDAO:
    """Classe qui interagit avec la base de données pour les objets de type Reservation"""

    def creer(self, reservation: Reservation) -> Reservation:
        """
        Enregistre une nouvelle réservation dans la base de données.

        Param:
        ------
        reservation: Reservation
            la réservation à créer (son id_reservation est None avant l'insertion)

        Return:
        ------
        Reservation
            l'objet Reservation créé, avec son id_reservation renseigné
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO reservations(id_client, id_trajet, place, classe, prix)      "
                    "VALUES (%(id_client)s, %(id_trajet)s, %(place)s, %(classe)s, %(prix)s)   "
                    "RETURNING id_reservation                                                 ",
                    {
                        "id_client": reservation.client.id,
                        "id_trajet": reservation.trajet.id_trajet,
                        "place": reservation.place,
                        "classe": reservation.classe,
                        "prix": reservation.prix,
                    },
                )
                reservation.id_reservation = cursor.fetchone()["id_reservation"]

        return reservation

    def annuler(self, id_reservation: int) -> bool:
        """
        Supprime une réservation de la base de données.

        Param:
        ------
        id_reservation: int
            l'identifiant de la réservation à annuler

        Return:
        ------
        bool
            True si l'annulation a réussi, False sinon
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM reservations                          "
                    " WHERE id_reservation = %(id_reservation)s        ",
                    {"id_reservation": id_reservation},
                )
                nb_lignes_supprimees = cursor.rowcount

        return nb_lignes_supprimees > 0

    def trouver_par_client(self, id_client: int) -> list[Reservation]:
        """
        Récupère toutes les réservations d'un client spécifique.

        Param:
        ------
        id_client: int
            l'identifiant du client

        Return:
        ------
        list[Reservation]
            la liste des réservations du client (vide si aucune)
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_reservation,                            "
                    "       id_client,                                 "
                    "       id_trajet,                                 "
                    "       place,                                     "
                    "       classe,                                    "
                    "       prix                                       "
                    "  FROM reservations                               "
                    " WHERE id_client = %(id_client)s                  "
                    " ORDER BY id_reservation                          ",
                    {"id_client": id_client},
                )
                reservations_bdd = cursor.fetchall()

        reservations = []
        if reservations_bdd:
            for reservation_bdd in reservations_bdd:
                reservation = self._construire_reservation(reservation_bdd)
                if reservation is not None:
                    reservations.append(reservation)
        return reservations

    def trouver_par_id(self, id_reservation: int) -> Reservation | None:
        """
        Récupère une réservation par son identifiant.

        Param:
        ------
        id_reservation: int
            l'identifiant de la réservation

        Return:
        ------
        Reservation
            l'objet Reservation trouvé, ou None s'il n'existe pas
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_reservation,                            "
                    "       id_client,                                 "
                    "       id_trajet,                                 "
                    "       place,                                     "
                    "       classe,                                    "
                    "       prix                                       "
                    "  FROM reservations                               "
                    " WHERE id_reservation = %(id_reservation)s        ",
                    {"id_reservation": id_reservation},
                )
                reservation_bdd = cursor.fetchone()

        if reservation_bdd is None:
            return None
        else:
            return self._construire_reservation(reservation_bdd)

    def _construire_reservation(self, reservation_bdd: dict) -> Reservation | None:
        """
        Transforme une ligne de la table reservations en objet Reservation complet,
        en récupérant le client et le trajet grâce aux autres DAO.

        Param:
        ------
        reservation_bdd: dict
            une ligne renvoyée par le curseur (id_reservation, id_client, id_trajet,
            place, classe, prix)

        Return:
        ------
        Reservation | None
            la réservation avec ses objets Client et Trajet,
            ou None si le client ou le trajet n'existe pas
        """
        utilisateur = UtilisateurDAO().trouver_par_id(reservation_bdd["id_client"])
        trajet = TrajetDAO().trouver_par_id(reservation_bdd["id_trajet"])

        if utilisateur is None or trajet is None:
            return None

        client = Client(
            id=utilisateur.id,
            mdp=utilisateur.mdp,
            nom_utilisateur=utilisateur.nom_utilisateur,
        )

        return Reservation(
            id_reservation=reservation_bdd["id_reservation"],
            client=client,
            trajet=trajet,
            place=reservation_bdd["place"],
            classe=reservation_bdd["classe"],
            prix=reservation_bdd["prix"],
        )
