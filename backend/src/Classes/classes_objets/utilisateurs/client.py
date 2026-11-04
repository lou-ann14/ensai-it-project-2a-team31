from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur


class Client(Utilisateur):
    """Implémentation de la classe Client, hérité de la classe Utilisateur"""

    def __init__(self, mdp: str, nom_utilisateur: str,  id: int | None = None):
        super().__init__(mdp, nom_utilisateur, id, grade="CLIENT")

    def __str__(self):
        return f"Client : {self.nom_utilisateur} (#{self.id})"
