class Train :
    """Modélise la classe Train, qui permet de gérer les différentes caracteristiques des trains
    comme le nombre de place ou l'identifiant du train """
    def __init__(self, id_train: int, type_train: str, places_initiales: list[int]):
        self.id_train=id_train
        self.type_train=type_train
        self.places_initiales=places_initiales

    def __str__(self):
        return f"Le train numéro,{self.id_train}, dispose de {self.places_initiales[0]},places en première classe et , {self.places_initiales[1]}, en seconde classe, c'est un tgv,{self.type_train}"


