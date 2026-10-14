from utilisateur import Utilisateur


class Client(Utilisateur):
    """Implémentation de la classe Client, hérité de la classe Utilisateur"""

    def __init__(self, id: int, mdp: str, nom_utilisateur: str):
        super().__init__(id, mdp, nom_utilisateur, role="CLIENT")

    def __str__(self):
        return f"Client : {self.nom_utilisateur} (#{self.id})"
