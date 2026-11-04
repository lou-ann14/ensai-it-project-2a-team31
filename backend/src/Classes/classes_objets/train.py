class Train:
    """Modélise la classe Train, qui permet de gérer les différentes caracteristiques des trains
    comme le nombre de place ou l'identifiant du train.

    Params
    ------
    type_train: str
        Chaîne de caractère décrivant le type du train
    places_premieres: int
        Nombre de places en première classe
    places_secondes: int
        Nombre de places en seconde classe
    num_train: int
        Numéro du train sur l'API SNCF
    id_train: int | None = None
        id du train dans la BDD
    """
    def __init__(self, type_train: str, places_premieres: int, places_secondes: int, num_train: int, id_train: int | None = None):
        self.type_train = type_train
        self.places_premieres = places_premieres
        self.places_secondes = places_secondes
        self.num_train = num_train
        self.id_train = id_train

    def __str__(self):
        return f"Le train numéro {self.num_train} dispose de {self.places_premieres} places en première classe et {self.places_secondes} en seconde classe, c'est un train {self.type_train}"
