class Gare:

    def __init__(self, id_gare: int, nom: str, ville: str):
        self.id_gare = id_gare
        self.nom = nom
        self.ville = ville

    def __str__(self):
        return f"La gare {self.nom} ({self.id_gare}) se situe à {self.ville}"
