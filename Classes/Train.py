


class Train():
    "Modélise la classe Train, qui permet de gérer les différentes caracteristiques des trains comme le nombre de place ou l'identifiant du train "
    def __init__(self, id_train: int, type_train: str, places_initiales: list[int]):
        self.id_train: 