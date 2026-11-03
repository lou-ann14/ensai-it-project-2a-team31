from src.Classes.classes_objets.train import Train
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import log


class TrainDAO:

    @log
    def creer(self, train : Train) -> bool:
        """
        Enregistre un nouveau train dans la base de données.

        Param:
        ------
        id_train: int
            l'identifiant du train
        type_train: str
            le type de train (ex: TGV)
        places_initiales: str
            le nombre de places au départ

        Return:
        ------
        Bool
            Réussite ou échec de la création de l'objet train dans la table trains
        """
        type_train = train.type_train
        places_initiales = str(train.places_initiales)
        num_train = train.num_train

        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                    "INSERT INTO trains(type_train, places_restantes, num_train)   "
                    "VALUES (%(type_train)s, %(places_restantes)s, %(num_train)s)      "
                    "RETURNING id_train                                    ",
                    {
                        "type_train": type_train,
                        "places_restantes": places_initiales,
                        "num_train": num_train
                    },
                )
            id_train = cursor.fetchone()["id_train"]

        return id_train is not None
        

    @log
    def modifier_capacite(self, num_train: int, capacite: list[int, int]) -> bool:
        """
        Met à jour la capacité d'un train existant.

        Param:
        ------
        id_train: int
            l'identifiant du train
        capacite: int
            la nouvelle capacité

        Return:
        ------
        Bool
            Réussite ou échec de la modification
        """
        capa = str(capacite)

        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trains"
                "SET places_restantes = %(places_restantes)s"
                "WHERE num_train = %(num_train)s",
                {
                    "places_restantes": capa,
                    "num_train": num_train
                }
            )
            res = cursor.fetchone()["places_restantes"]

        return res == capa
        

    def trouver_par_num(self, num_train: int) -> Train:
        """
        Récupère un train par son identifiant.

        Param:
        ------
        id_train: int
            l'identifiant du train

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

        train = Train(
                type_train=train_bdd["type_train"],
                places_initiales=train_bdd["places_restantes"],
                num_train=train_bdd["num_train"]
            )

        return train