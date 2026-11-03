from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur


class Administrateur(Utilisateur):
    """Classe administrateur, héritée de la classe Utilisateur qui modélise les fonctionnalités de l'administrateur"""

    def __init__(self, mdp: str, nom_utilisateur: str, id: int | None = None):
        super().__init__(mdp, nom_utilisateur, id, role="ADMIN")

    def __str__(self):
        return f"Administrateur : {self.nom_utilisateur} (#{self.id})"
