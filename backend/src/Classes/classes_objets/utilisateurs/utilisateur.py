class Utilisateur:
    """Modélise une personne utilisant l'application.

    Param:
    ------
    id: int | None
        identifiant de l'utilisateur (None tant qu'il n'est pas enregistré en base)
    mdp: str
        mot de passe de l'utilisateur
    nom_utilisateur: str
        nom de l'utilisateur (15 caractères maximum)
    role: str
        niveau d'habilitation de l'utilisateur
    """

    def __init__(self, id: int | None, mdp: str, nom_utilisateur: str, role: str):
        if id is not None and not isinstance(id, int):
            raise TypeError("L'identifiant doit être un entier.")
        if not isinstance(mdp, str):
            raise TypeError("Le mot de passe doit être une chaîne de caractères.")
        if not isinstance(nom_utilisateur, str):
            raise TypeError("Le nom d'utilisateur doit être une chaîne de caractères.")
        if not isinstance(role, str):
            raise TypeError("Le role doit être une chaîne de caractères")
        if len(nom_utilisateur) > 15:
            raise ValueError("Le nom doit faire 15 caractères maximum")

        self.id = id
        self.mdp = mdp
        self.nom_utilisateur = nom_utilisateur
        self.role = role

    def __str__(self):
        return f"L'utilisateur {self.nom_utilisateur} (#{self.id}) est un {self.role}"
