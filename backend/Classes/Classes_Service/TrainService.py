from Classes_Objets import Train
from Classes_Service import TrajetService


def creer(type_train: str, places_initiales: int):
    """
    Méthode servant à créer un nouveau train.

    Param:
    ------
    type_train: str
        le type de train (ex: TGV, TER)
    places_initiales: int
        le nombre de places disponibles au départ

    Return:
    ------
    int
        l'id du nouveau train créé
    """
    pass

def modifier_capacite(id_train: int, capacite: int):
    """
    Méthode servant à modifier la capacité d'un train existant.

    Param:
    ------
    id_train: int
        l'identifiant du train à modifier
    capacite: int
        la nouvelle capacité du train

    Return:
    ------
    bool
        True si la modification a réussi, False sinon
    """
    pass

