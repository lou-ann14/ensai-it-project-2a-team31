from classes_objets import Train


class TrainDAO:

    def creer(self, id_train: int, type_train: str, places_initiales: str) -> Train:
        return Train(id_train, type_train, places_initiales)

    def modifier_capacite(self, id_train: int, capacite: int) -> Train:
        pass

    def trouver_par_id(self, id_train: int) -> Train:
        pass
