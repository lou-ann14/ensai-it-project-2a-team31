from utilisateur import Utilisateur

class Collaborateur(Utilisateur):
    """Classe qui modélise un collaborateur (rôle qui peut créer de
    nouveaux trajets ou lignes sur l'application).
    Hérite de la classe Utilisateur.
    """

    def __init__(self, id: int, mdp: str, nom_utilisateur: str):
        super().__init__(id, mdp, nom_utilisateur, role="COLLABORATEUR")

    def __str__(self):
        return f"Collaborateur : {self.nom_utilisateur} (#{self.id})"