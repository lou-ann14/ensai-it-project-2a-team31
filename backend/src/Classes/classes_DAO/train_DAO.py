from src.Classes.classes_objets.train import Train
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import log


class TrainDAO:

    @log
    def creer(self, train: Train) -> Train:
        """
        Enregistre un nouveau train dans la base de données.

        Param:
        ------
        train: Train
            le train à enregistrer dans la base de données

        Return:
        ------
        Train
            le train créé, avec son id_train renseigné
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                    "INSERT INTO trains(type_train, places_premieres, places_secondes, num_train)   "
                    "VALUES (%(type_train)s, %(places_premieres)s, %(places_secondes)s, %(num_train)s) "
                    "RETURNING id_train                                                             ",
                    {
                        "type_train": train.type_train,
                        "places_premieres": train.places_initiales[0],
                        "places_secondes": train.places_initiales[1],
                        "num_train": train.num_train,
                    },
                )
            train.id_train = cursor.fetchone()["id_train"]

        return train

    @log
    def modifier_capacite(self, num_train: int, capacite: list[int, int]) -> bool:
        """
        Met à jour la capacité d'un train existant.

        Param:
        ------
        num_train: int
            le numéro du train
        capacite: list[int, int]
            la nouvelle capacité [première classe, seconde classe]

        Return:
        ------
        Bool
            Réussite ou échec de la modification
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trains                               "
                "   SET places_premieres = %(places_premieres)s, "
                "       places_secondes  = %(places_secondes)s   "
                " WHERE num_train = %(num_train)s            ",
                {
                    "places_premieres": capacite[0],
                    "places_secondes": capacite[1],
                    "num_train": num_train,
                }
            )
            nb_lignes_modifiees = cursor.rowcount

        return nb_lignes_modifiees > 0

    @log
    def trouver_train_par_num(self, num_train: int) -> Train:
        """
        Récupère un train par son numéro.

        Param:
        ------
        num_train: int
            le numéro du train

        Return:
        ------
        Train
            l'objet Train trouvé
        """

        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT *                          "
                "  FROM trains                     "
                " WHERE num_train = %(num_train)s",
                {
                    "num_train": num_train
                })
            train_bdd = cursor.fetchone()

        if train_bdd is None:
            return None

        train = Train(
                type_train=train_bdd["type_train"],
                places_initiales=[train_bdd["places_premieres"], train_bdd["places_secondes"]],
                num_train=train_bdd["num_train"],
                id_train=train_bdd["id_train"],
            )

        return train

    @log
    def trouver_id_par_num(self, num_train: int) -> int:
        """
        Récupère l'id d'un train par son numéro.

        Param:
        ------
        num_train: int
            le numéro du train

        Return:
        ------
        int
            l'identifiant trouvé
        """

        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_train                          "
                "  FROM trains                     "
                " WHERE num_train = %(num_train)s",
                {
                    "num_train": num_train
                })
            id_bdd = cursor.fetchone()

        if id_bdd is None:
            return None

        return id_bdd["id_train"]
