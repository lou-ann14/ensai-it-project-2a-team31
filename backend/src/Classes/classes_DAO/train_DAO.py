from src.Classes.classes_objets.train import Train
from src.utils.db_connexion import DBConnexion


class TrainDAO:
    """Classe qui interagit avec la base de données pour les objets de type Train"""

    def creer(self, train: Train) -> Train:
        """
        Enregistre un nouveau train dans la base de données.

        Param:
        ------
        train: Train
            le train à enregistrer (son id_train est None avant l'insertion)

        Return:
        ------
        Train
            l'objet Train créé, avec son id_train renseigné
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO trains(type_train, places_premiere, places_seconde)   "
                    "VALUES (%(type_train)s, %(places_premiere)s, %(places_seconde)s)  "
                    "RETURNING id_train                                                ",
                    {
                        "type_train": train.type_train,
                        "places_premiere": train.places_initiales[0],
                        "places_seconde": train.places_initiales[1],
                    },
                )
                train.id_train = cursor.fetchone()["id_train"]

        return train

    def trouver_par_id(self, id_train: int) -> Train | None:
        """
        Récupère un train par son identifiant.

        Param:
        ------
        id_train: int
            l'identifiant du train

        Return:
        ------
        Train | None
            l'objet Train trouvé, ou None s'il n'existe pas
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_train, type_train, places_premiere, places_seconde  "
                    "  FROM trains                                                 "
                    " WHERE id_train = %(id_train)s                                ",
                    {"id_train": id_train},
                )
                train_bdd = cursor.fetchone()

        train = None
        if train_bdd:
            train = Train(
                id_train=train_bdd["id_train"],
                type_train=train_bdd["type_train"],
                places_initiales=[train_bdd["places_premiere"], train_bdd["places_seconde"]],
            )
        return train