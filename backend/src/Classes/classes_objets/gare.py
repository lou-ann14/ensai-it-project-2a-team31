class Gare:
    """Classe Gare : gère les différentes caractéristiques des trains (id, nom, ville)

    Params
    ------
    nom: str
        Nom de la gare
    ville: str
        Nom de la ville où se trouve la gare"""
    def __init__(self, nom: str, ville: str, id_sncf: int, id_gare: int | None = None):
        if not isinstance(nom, str):
            raise TypeError("Le nom du client doit être une chaîne de caractères.")
        if not isinstance(ville, str):
            raise TypeError("La ville doit être une chaîne de caractères.")
        if not isinstance(id_sncf, int):
            raise TypeError("L'id sncf doit être un entier.")
        if not isinstance(id_gare, int):
            raise TypeError("L'id gare doit être un entier.")

        self.id_gare = id_gare
        self.nom = nom
        self.ville = ville
        self.id_sncf = id_sncf

    def __str__(self):
        return f"La gare {self.nom} ({self.id_gare}) se situe à {self.ville}"
