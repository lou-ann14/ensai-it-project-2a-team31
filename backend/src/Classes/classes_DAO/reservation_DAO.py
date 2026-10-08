from src.Classes.classes_objets.reservation import Reservation
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
                        "id_client": reservation.id_client,
                        "id_trajet": reservation.id_trajet,
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
            for reservation in reservations_bdd:
                reservations.append(
                    Reservation(
                        id_reservation=reservation["id_reservation"],
                        id_client=reservation["id_client"],
                        id_trajet=reservation["id_trajet"],
                        place=reservation["place"],
                        classe=reservation["classe"],
                        prix=reservation["prix"],
                    )
                )

        return reservations