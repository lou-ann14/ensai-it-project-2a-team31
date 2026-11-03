class Gare:
    """Classe Gare : gère les différentes caractéristiques des trains (id, nom, ville)

    Params
    ------
    id_gare: int
        Identifiant de la gare
    nom: str
        Nom de la gare
    ville: str
        Nom de la ville où se trouve la gare"""
    def __init__(self, id_gare: int, nom: str, ville: str, id_sncf: str | None = None):
        self.id_gare = id_gare
        self.nom = nom
        self.ville = ville
        self.id_sncf = id_sncf

    def __str__(self):
        return f"La gare {self.nom} ({self.id_gare}) se situe à {self.ville}"
