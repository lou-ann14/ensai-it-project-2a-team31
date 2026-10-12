from utilisateur import Utilisateur

class Administrateur(Utilisateur):
    """Classe administrateur, héritée de la classe Utilisateur qui modélise les fonctionnalités de l'administrateur"""

    def __init__(self, id: int, mdp: str, nom_utilisateur: str):
        super().__init__(id, mdp, nom_utilisateur, role="ADMIN")

    def __str__(self):
        return f"Administrateur : {self.nom_utilisateur} (#{self.id})"