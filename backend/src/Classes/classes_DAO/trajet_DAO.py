from datetime import datetime

from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.utils.db_connexion import DBConnexion

# Récupère un trajet avec sa ligne, ses deux gares et son train.
# LEFT JOIN sur trains : un trajet peut ne pas encore avoir de train (id_train vide).
SELECT_TRAJET = (
    "SELECT t.id_trajet, t.heure_depart, t.heure_arrivee, t.tarif_base,        "
    "       l.id_ligne,                                                        "
    "       gd.id_gare AS id_gare_depart, gd.nom AS nom_gare_depart,           "
    "       gd.ville AS ville_gare_depart, gd.id_sncf AS id_sncf_gare_depart,  "
    "       ga.id_gare AS id_gare_arrivee, ga.nom AS nom_gare_arrivee,         "
    "       ga.ville AS ville_gare_arrivee, ga.id_sncf AS id_sncf_gare_arrivee,"
    "       tr.id_train, tr.type_train, tr.places_premieres, tr.places_secondes, tr.num_train      "
    "  FROM trajets t                                                          "
    "  JOIN lignes l ON l.id_ligne = t.id_ligne                                "
    "  JOIN gares gd ON gd.id_gare = l.id_gare_depart                          "
    "  JOIN gares ga ON ga.id_gare = l.id_gare_arrivee                         "
    "  LEFT JOIN trains tr ON tr.id_train = t.id_train                         "
)


class TrajetDAO:
    """Classe qui interagit avec la base de données pour les objets de type Trajet"""

    @staticmethod
    def _construire_trajet(trajet_bdd: dict) -> Trajet:
        """Transforme une ligne renvoyée par SELECT_TRAJET en objet Trajet complet."""
        ligne = Ligne(
            gare_depart=Gare(
                nom=trajet_bdd["nom_gare_depart"],
                ville=trajet_bdd["ville_gare_depart"],
                id_sncf=trajet_bdd["id_sncf_gare_depart"],
                id_gare=trajet_bdd["id_gare_depart"],
            ),
            gare_arrivee=Gare(
                nom=trajet_bdd["nom_gare_arrivee"],
                ville=trajet_bdd["ville_gare_arrivee"],
                id_sncf=trajet_bdd["id_sncf_gare_arrivee"],
                id_gare=trajet_bdd["id_gare_arrivee"],
            ),
            id_ligne=trajet_bdd["id_ligne"],
        )

        train = None
        if trajet_bdd["id_train"] is not None:
            train = Train(
                type_train=trajet_bdd["type_train"],
                places_initiales=[trajet_bdd["places_premieres"], trajet_bdd["places_secondes"]],
                num_train=trajet_bdd["num_train"],
                id_train=trajet_bdd["id_train"],
            )

        return Trajet(
            heure_depart=trajet_bdd["heure_depart"],
            heure_arrivee=trajet_bdd["heure_arrivee"],
            ligne=ligne,
            train=train,
            tarif_base=trajet_bdd["tarif_base"],
            id_trajet=trajet_bdd["id_trajet"],
        )

    def creer(self, trajet: Trajet) -> Trajet:
        """
        Enregistre un nouveau trajet dans la base de données.

        Param:
        ------
        trajet: Trajet
            l'objet Trajet à enregistrer (son id_trajet est None avant l'insertion)

        Return:
        ------
        Trajet
            l'objet Trajet créé, avec son id_trajet renseigné
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trajets(id_ligne, id_train, heure_depart, heure_arrivee, tarif_base)       "
                "VALUES (%(id_ligne)s, %(id_train)s, %(heure_depart)s, %(heure_arrivee)s, %(tarif_base)s) "
                "RETURNING id_trajet                                                                    ",
                {
                    "id_ligne": trajet.ligne.id_ligne,
                    "id_train": trajet.train.id_train,
                    "heure_depart": trajet.heure_depart,
                    "heure_arrivee": trajet.heure_arrivee,
                    "tarif_base": trajet.tarif_base,
                },
            )
            trajet.id_trajet = cursor.fetchone()["id_trajet"]

        return trajet

    def modifier(self, trajet: Trajet) -> bool:
        """
        Met à jour les informations d'un trajet existant.

        Param:
        ------
        trajet: Trajet
            l'objet contenant les nouvelles données (identifié par son id_trajet)

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trajets                                    "
                "   SET id_ligne      = %(id_ligne)s,              "
                "       id_train      = %(id_train)s,              "
                "       heure_depart  = %(heure_depart)s,          "
                "       heure_arrivee = %(heure_arrivee)s,         "
                "       tarif_base    = %(tarif_base)s             "
                " WHERE id_trajet = %(id_trajet)s                  ",
                {
                    "id_ligne": trajet.ligne.id_ligne,
                    "id_train": trajet.train.id_train,
                    "heure_depart": trajet.heure_depart,
                    "heure_arrivee": trajet.heure_arrivee,
                    "tarif_base": trajet.tarif_base,
                    "id_trajet": trajet.id_trajet,
                },
            )
            nb_lignes_modifiees = cursor.rowcount

        return nb_lignes_modifiees > 0

    def supprimer(self, id_trajet: int) -> bool:
        """
        Supprime un trajet de la base de données.

        Param:
        ------
        id_trajet: int
            l'identifiant du trajet à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False sinon
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM trajets                               "
                " WHERE id_trajet = %(id_trajet)s                  ",
                {"id_trajet": id_trajet},
            )
            nb_lignes_supprimees = cursor.rowcount

        return nb_lignes_supprimees > 0

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare, date: datetime) -> list[Trajet]:
        """
        Recherche des trajets selon les critères de lieu et de date.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée
        date: datetime
            la date recherchée (seul le jour est pris en compte)

        Return:
        ------
        list[Trajet]
            la liste des trajets correspondants, triés par heure de départ
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                SELECT_TRAJET +
                " WHERE l.id_gare_depart  = %(id_gare_depart)s             "
                "   AND l.id_gare_arrivee = %(id_gare_arrivee)s            "
                "   AND t.heure_depart::date = %(date)s::date              "
                " ORDER BY t.heure_depart                                  ",
                {
                    "id_gare_depart": gare_depart.id_gare,
                    "id_gare_arrivee": gare_arrivee.id_gare,
                    "date": date,
                },
            )
            trajets_bdd = cursor.fetchall()

        return [self._construire_trajet(trajet_bdd) for trajet_bdd in trajets_bdd]

    def trouver_par_id(self, id_trajet: int) -> Trajet:
        """
        Récupère un trajet spécifique par son identifiant.

        Param:
        ------
        id_trajet: int
            l'identifiant unique du trajet

        Return:
        ------
        Trajet
            l'objet Trajet trouvé, ou None s'il n'existe pas
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                SELECT_TRAJET +
                " WHERE t.id_trajet = %(id_trajet)s                ",
                {"id_trajet": id_trajet},
            )
            trajet_bdd = cursor.fetchone()

        return self._construire_trajet(trajet_bdd) if trajet_bdd else None
