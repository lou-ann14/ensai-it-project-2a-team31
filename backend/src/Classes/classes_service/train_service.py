from fastapi import HTTPException
from psycopg2.errors import UniqueViolation
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train
from src.utils.log_utils import log


class TrainService:

    @staticmethod
    def _verifier_capacite(capacite: list[int, int]) -> None:
        """Vérifie qu'il y a deux nombres de places positifs ou nuls (lève ValueError sinon)."""
        if len(capacite) != 2:
            raise ValueError("capacité incorrecte, la longueur de la liste doit être de 2")
        if capacite[0] < 0 or capacite[1] < 0:
            raise ValueError("capacité incorrecte, le nombre de places doit être positif ou nul")

    @log
    def creer(self, type_train: str, places_initiales: list[int, int], num_train: int):
        """
        Méthode servant à créer un nouveau train.

        Param:
        ------
        type_train: str
            le type de train (ex: TGV, TER)
        places_initiales: list[int]
            le nombre de places disponibles au départ
        num_train
            le numéro du train

        Return:
        ------
        Train
            Le Train créé, avec son id_train renseigné

        Raises:
        ------
        ValueError
            si la capacité est incorrecte ou si ce numéro de train existe déjà
        """
        self._verifier_capacite(places_initiales)
        train = Train(type_train, places_initiales, num_train)

        try:
            return TrainDAO().creer(train)
        except UniqueViolation:
            raise ValueError(f"Le train numéro {num_train} existe déjà.")

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
    def modifier_capacite(self, num_train: int, capacite: list[int, int]):
        """
        Méthode servant à modifier la capacité d'un train existant.

        Param:
        ------
        num_train: int
            le numéro du train à modifier
        capacite: list[int, int]
            la nouvelle capacité du train

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """
        self._verifier_capacite(capacite)

        train = TrainDAO().trouver_train_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        return TrainDAO().modifier_capacite(num_train, capacite=capacite)
