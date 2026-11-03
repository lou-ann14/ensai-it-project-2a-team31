class Gare:
    """Classe Gare : gère les différentes caractéristiques des trains (id, nom, ville)

    Params
    ------
    nom: str
        Nom de la gare
    ville: str
        Nom de la ville où se trouve la gare
    id_sncf: int
        id donné sur l'API SNCF
    id_gare: int | None = None
        Identifiant de la gare dans la BDD
    """
    def __init__(self, nom: str, ville: str, id_sncf: int, id_gare: int | None = None):
        self.id_gare = id_gare
        self.nom = nom
        self.ville = ville
        self.id_sncf = id_sncf

    def __str__(self):
        return f"La gare {self.nom} ({self.id_gare}) se situe à {self.ville}"
