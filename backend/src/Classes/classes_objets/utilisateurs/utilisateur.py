class Utilisateur:
    """Modélise une personne utilisant l'application.

    Param:
    ------
    mdp: str
        mot de passe de l'utilisateur
    nom_utilisateur: str
        nom de l'utilisateur (15 caractères maximum)
    grade: str
        niveau d'habilitation de l'utilisateur ("CLIENT", COLLABORATEUR", "ADMIN")
    token_acces: str | None = None
        token de connexion de l'utilisateur (None s'il ne s'est jamais connecté)
    id: int | None = None
        identifiant de l'utilisateur (None tant qu'il n'est pas enregistré en base)
    """

    def __init__(self, mdp: str, nom_utilisateur: str, grade: str, token_acces=None,  id: int | None = None):
        """
        Crée un utilisateur après avoir vérifié les paramètres.

        Raises:
        ------
        TypeError
            si un paramètre n'a pas le bon type
        ValueError
            si le nom d'utilisateur dépasse 15 caractères
        """
        if id is not None and not isinstance(id, int):
            raise TypeError("L'identifiant doit être un entier.")
        if not isinstance(mdp, str):
            raise TypeError("Le mot de passe doit être une chaîne de caractères.")
        if not isinstance(nom_utilisateur, str):
            raise TypeError("Le nom d'utilisateur doit être une chaîne de caractères.")
        if not isinstance(grade, str):
            raise TypeError("Le grade doit être une chaîne de caractères")
        if len(nom_utilisateur) > 15:
            raise ValueError("Le nom doit faire 15 caractères maximum")

        self.id = id
        self.mdp = mdp
        self.nom_utilisateur = nom_utilisateur
        self.grade = grade
        self.token = token_acces

    def __str__(self):
        """
        Représentation string d'un utilisateur.

        Return:
        ------
        str
            la description affichée
        """
        return f"L'utilisateur {self.nom_utilisateur} (#{self.id}) est un {self.grade}"
