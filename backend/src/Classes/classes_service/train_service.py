from src.Classes.classes_DAO import TrainDAO
from src.Classes.classes_objets import Train
from src.utils.log_utils import log


class TrainService:

    @log
    def creer(self, type_train: str, places_initiales: int):
        """
        Méthode servant à créer un nouveau train.

        Param:
        ------
        type_train: str
            le type de train (ex: TGV, TER)
        places_initiales: int
            le nombre de places disponibles au départ

        Return:
        ------
        Train
            Le Train créer ou None si la création a échoué
        """
        train = Train(type_train, places_initiales)

        return train if TrainDAO().creer(train) else None

    @log
    def modifier_capacite(self, id_train: int, capacite: list[int]):
        """
        Méthode servant à modifier la capacité d'un train existant.

        Param:
        ------
        id_train: int
            l'identifiant du train à modifier
        capacite: list[int]
            la nouvelle capacité du train

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """
        if len(capacite) != 2:
            raise ValueError("capacité incorrecte, la longueur de la liste doit être de 2")

        return TrainDAO().modifier_capacite(id_train, capacite = capacite)

