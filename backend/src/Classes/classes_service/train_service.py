from fastapi import HTTPException
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train
from src.utils.log_utils import log


class TrainService:

    @log
    def creer(self, type_train: str, places_initiales: list[int, int], num_train : int):
        """
        Méthode servant à créer un nouveau train.

        Param:
        ------
        type_train: str
            le type de train (ex: TGV, TER)
        places_initiales: list[int]
            le nombre de places disponibles au départ

        Return:
        ------
        Train
            Le Train créer ou None si la création a échoué
        """
        train = Train(type_train, places_initiales, num_train)

        return train if TrainDAO().creer(train) else None

    @log
    def trouver_par_num(self, num_train: int):
        """
        Méthode servant à trouver un train avec son id.

        Param:
        ------
        id_train: int
            l'identifiant du train à modifier

        Return:
        ------
        Train
            Le train trouvé
        
        Raises:
        ------
        HTTPException 404
            Erreur 404 si le train n'est pas trouvé
        """
        train = TrainDAO().trouver_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        return train 

    @log
    def modifier_capacite(self, num_train: int, capacite: list[int, int]):
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

        train = TrainDAO().trouver_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        return TrainDAO().modifier_capacite(num_train, capacite = capacite)

