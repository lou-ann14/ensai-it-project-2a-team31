from Classes_Objets import Train


class TrainDAO:

    def creer(self, id_train: int, type_train: str, places_initiales: str) -> Train:
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
        Train
            l'objet Train créé
        """
        pass

    def modifier_capacite(self, id_train: int, capacite: int) -> Train:
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
        Train
            l'objet Train mis à jour
        """
        
        pass

    def trouver_par_id(self, id_train: int) -> Train:
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
        
        pass
