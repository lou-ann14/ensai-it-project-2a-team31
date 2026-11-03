from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur


class Collaborateur(Utilisateur):
    """Classe qui modélise un collaborateur (rôle qui peut créer de
    nouveaux trajets ou lignes sur l'application).
    Hérite de la classe Utilisateur.
    """

    def __init__(self, mdp: str, nom_utilisateur: str, id: int | None = None):
        super().__init__(mdp, nom_utilisateur, id, grade="COLLABORATEUR")

    def __str__(self):
        return f"Collaborateur : {self.nom_utilisateur} (#{self.id})"