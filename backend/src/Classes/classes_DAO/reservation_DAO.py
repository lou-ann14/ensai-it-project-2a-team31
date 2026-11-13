from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.utilisateurs.client import Client
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log

logger = get_logger(__name__)


class ReservationDAO:
    """
    Classe qui interagit avec la base de données pour les objets de type Reservation
    """

    @log
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
            la même réservation, avec son id_reservation renseigné

        Raises:
        ------
        psycopg2.errors.ForeignKeyViolation
            si le client ou le trajet n'existe pas
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
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
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.creer : {e}")
            raise

        return reservation

    @log
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
            True si l'annulation a réussi, False si la réservation n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM reservations                          "
                    " WHERE id_reservation = %(id_reservation)s        ",
                    {"id_reservation": id_reservation},
                )
                nb_lignes_supprimees = cursor.rowcount
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.annuler : {e}")
            raise

        return nb_lignes_supprimees > 0

    @log
    def trouver_par_client(self, id_client: int) -> list[Reservation]:
        """
        Récupère toutes les réservations d'un client, triées par identifiant.
        Les réservations dont le client ou le trajet n'existe plus sont ignorées.

        Param:
        ------
        id_client: int
            l'identifiant du client

        Return:
        ------
        list[Reservation]
            la liste des réservations du client (vide si aucune)

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
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
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.trouver_par_client : {e}")
            raise

        reservations = []
        if reservations_bdd:
            for reservation_bdd in reservations_bdd:
                reservation = self._construire_reservation(reservation_bdd)
                if reservation is not None:
                    reservations.append(reservation)
        return reservations

    @log
    def trouver_par_id(self, id_reservation: int) -> Reservation | None:
        """
        Récupère une réservation par son identifiant.

        Param:
        ------
        id_reservation: int
            l'identifiant de la réservation

        Return:
        ------
        Reservation | None
            la réservation trouvée, ou None si elle n'existe pas
            (ou si son client ou son trajet n'existe plus)

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
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
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.trouver_par_id : {e}")
            raise

        if reservation_bdd is None:
            return None
        else:
            return self._construire_reservation(reservation_bdd)

    @log
    def compter_par_trajets(self, ids_trajets: list[int]) -> dict[int, dict[int, int]]:
        """
        Compte les places réservées sur plusieurs trajets, classe par classe,
        en une seule requête (utile pour afficher les places restantes d'une recherche).

        Param:
        ------
        ids_trajets: list[int]
            les identifiants des trajets

        Return:
        ------
        dict[int, dict[int, int]]
            {id_trajet: {classe: nombre de places réservées}}
            (un trajet ou une classe sans réservation est absent du dictionnaire)

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        if not ids_trajets:
            return {}
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_trajet, classe, COUNT(*) AS nb_reservees "
                    "  FROM reservations                                "
                    " WHERE id_trajet = ANY(%(ids_trajets)s)            "
                    " GROUP BY id_trajet, classe                        ",
                    {"ids_trajets": list(ids_trajets)},
                )
                lignes_bdd = cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.compter_par_trajets : {e}")
            raise

        comptes: dict[int, dict[int, int]] = {}
        for ligne_bdd in lignes_bdd:
            comptes.setdefault(ligne_bdd["id_trajet"], {})[ligne_bdd["classe"]] = ligne_bdd["nb_reservees"]
        return comptes

    @log
    def capacite_minimale_par_train(self, id_train: int) -> dict[int, int]:
        """
        Calcule, pour chaque classe, le nombre de places minimum que doit garder un train
        pour ne pas invalider les réservations de ses trajets à venir.
        Ce minimum est le plus grand des deux nombres suivants :
        - le nombre de réservations dans la classe ;
        - le plus grand numéro de place réservé dans la classe (les places étant numérotées
          de 1 à la capacité, réduire la capacité sous ce numéro rendrait la place inexistante).
        Les places non numériques (ancien format, ex. « 12A ») ne comptent que dans le nombre.

        Param:
        ------
        id_train: int
            l'identifiant du train

        Return:
        ------
        dict[int, int]
            {classe: capacité minimale} (une classe sans réservation à venir est absente)

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT r.classe,                                                       "
                    "       COUNT(*) AS nb_reservees,                                       "
                    "       MAX(CASE WHEN r.place ~ '^[0-9]+$' THEN r.place::int END)        "
                    "           AS place_max                                                "
                    "  FROM reservations r                                                  "
                    "  JOIN trajets t ON t.id_trajet = r.id_trajet                          "
                    " WHERE t.id_train = %(id_train)s                                       "
                    "   AND t.heure_depart > NOW()                                          "
                    " GROUP BY r.classe                                                     ",
                    {"id_train": id_train},
                )
                lignes_bdd = cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur base de données dans ReservationDAO.capacite_minimale_par_train : {e}")
            raise

        return {
            ligne_bdd["classe"]: max(ligne_bdd["nb_reservees"], ligne_bdd["place_max"] or 0)
            for ligne_bdd in lignes_bdd
        }

    def _construire_reservation(self, reservation_bdd: dict) -> Reservation | None:
        """
        Transforme une ligne de la table reservations en objet Reservation complet,
        en récupérant le client et le trajet grâce à UtilisateurDAO et TrajetDAO.

        Param:
        ------
        reservation_bdd: dict
            une ligne renvoyée par le curseur
            (id_reservation, id_client, id_trajet, place, classe, prix)

        Return:
        ------
        Reservation | None
            la réservation avec ses objets Client et Trajet,
            ou None si le client ou le trajet n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
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
