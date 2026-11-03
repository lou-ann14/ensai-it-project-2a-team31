class Train:
    """Modélise la classe Train, qui permet de gérer les différentes caracteristiques des trains
    comme le nombre de place ou l'identifiant du train.

    Params
    ------
    type_train: str
        Chaîne de caractère décrivant le type du train
    places_initiales: list[int]
        Nombre de places en première classe et en deuxième classe
    num_train: int
        Numéro du train sur l'API SNCF
    id_train: int | None = None
        id du train dans la BDD
    """
    def __init__(self, type_train: str, places_initiales: list[int, int], num_train: int, id_train: int | None = None):
        self.type_train = type_train
        self.places_initiales = places_initiales
        self.num_train = num_train

    def __str__(self):
        return f"Le train numéro {self.num_train} dispose de {self.places_initiales[0]} places en première classe et {self.places_initiales[1]} en seconde classe, c'est un train {self.type_train}"
