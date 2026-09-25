from classes_objets import Train


class TrainDAO:

    def creer(self, id_train: int, type_train: str, places_initiales: str) -> train:
        return train(id_train, type_train, places_initiales)

    def modifier_capacite(self, id_train: int, capacite: int) -> train:
        pass

    def trouver_par_id(self, id_train: int) -> train:
        pass
