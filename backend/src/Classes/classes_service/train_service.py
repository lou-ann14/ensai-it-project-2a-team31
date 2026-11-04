from fastapi import HTTPException
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train
from src.utils.log_utils import log


class TrainService:

    @log
    def creer(self, type_train: str, places_premieres: int, places_secondes: int, num_train: int):
        """
        Méthode servant à créer un nouveau train.

        Param:
        ------
        type_train: str
            le type de train (ex: TGV, TER)
        places_premieres: int
            le nombre de places en première classe disponibles au départ
        places_secondes: int
            le nombre de places en seconde classe disponibles au départ
        num_train
            le numéro du train

        Return:
        ------
        Train
            Le Train créé ou None si la création a échoué
        """
        train = Train(type_train, places_premieres, places_secondes, num_train)

        return train if TrainDAO().creer(train) else None

    @log
    def trouver_train_par_num(self, num_train: int):
        """
        Méthode servant à trouver un train avec son numéro.

        Param:
        ------
        num_train: int
            le numéro du train recherché

        Return:
        ------
        Train
            Le train trouvé

        Raises:
        ------
        HTTPException 404
            Erreur 404 si le train n'est pas trouvé
        """
        train = TrainDAO().trouver_train_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        return train

    @log
    def modifier_capacite(self, num_train: int, capacite_premiere: int, capacite_seconde: int):
        """
        Méthode servant à modifier la capacité d'un train existant.

        Param:
        ------
        num_train: int
            le numéro du train à modifier
        capacite_premiere: int
            la nouvelle capacité du train en premiere classe
        capacite_seconde: int
            la nouvelle capacité du train en seconde classe

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """

        train = TrainDAO().trouver_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        return TrainDAO().modifier_capacite(num_train, capacite_premiere=capacite_premiere, capacite_seconde=capacite_seconde)
