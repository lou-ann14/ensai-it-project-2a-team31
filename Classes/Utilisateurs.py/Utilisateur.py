class Utilisateur:

    def __init__(self, id: int, mdp: str, nom_utilisateur: str, role: str):
        assert len(nom_utilisateur) < 16, "Le nom doit faire 15 caractères maximum"
        raise ValueError("error")

        self.id = id
        self.mdp = mdp
        self.nom_utilisateur = nom_utilisateur
        self.role = role

    def __str__(self):
        return f"L'utilisateur {self.nom_utilisateur} (#{self.id}) est un {self.role}"
    