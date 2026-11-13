from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train
from src.utils.log_utils import log


class TrainService:

    @staticmethod
    def _verifier_capacite(places_premieres: int, places_secondes: int) -> None:
        """Vérifie que les nombres de places sont positifs ou nuls (lève ValueError sinon)."""
        if places_premieres < 0 or places_secondes < 0:
            raise ValueError("capacité incorrecte, le nombre de places doit être positif ou nul")

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
            Le Train créé, avec son id_train renseigné

        Raises:
        ------
        ValueError
            si la capacité est incorrecte ou si ce numéro de train existe déjà
        """
        self._verifier_capacite(places_premieres, places_secondes)
        train = Train(type_train, places_premieres, places_secondes, num_train)

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

        Raises:
        ------
        ValueError
            si la capacité est incorrecte, ou si elle est trop petite pour les réservations
            des trajets à venir de ce train (nombre de réservations ou numéro de place réservé)
        HTTPException 404
            si le train n'existe pas
        """
        self._verifier_capacite(capacite_premiere, capacite_seconde)

        train = TrainDAO().trouver_train_par_num(num_train)

        if not train:
            raise HTTPException(status_code=404, detail="Train pas trouvé")

        # On ne peut pas descendre sous ce qui est déjà réservé sur les trajets à venir
        minimum = ReservationDAO().capacite_minimale_par_train(train.id_train)
        for classe, nouvelle_capacite, libelle in (
            (1, capacite_premiere, "première classe"),
            (2, capacite_seconde, "seconde classe"),
        ):
            requis = minimum.get(classe, 0)
            if nouvelle_capacite < requis:
                raise ValueError(
                    f"Impossible de passer à {nouvelle_capacite} places en {libelle} : "
                    f"les réservations des trajets à venir de ce train en demandent au moins {requis}."
                )

        return TrainDAO().modifier_capacite(num_train, capacite_premiere=capacite_premiere, capacite_seconde=capacite_seconde)

    @log
    def supprimer(self, num_train: int) -> bool:
        """
        Méthode servant à supprimer un train.

        Param:
        ------
        num_train: int
            le numéro du train à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False sinon (train inexistant)

        Raises:
        ------
        ValueError
            si des trajets utilisent encore ce train
        """
        id_train = TrainDAO().trouver_id_par_num(num_train)
        if id_train is None:
            return False

        try:
            return TrainDAO().supprimer(id_train)
        except ForeignKeyViolation:
            raise ValueError(f"Impossible de supprimer le train numéro {num_train} : des trajets l'utilisent.")
