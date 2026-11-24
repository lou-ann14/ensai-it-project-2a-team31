class Gare:
    """Classe Gare : gère les différentes caractéristiques des gares

    Param:
    ------
    nom: str
        Nom de la gare
    ville: str
        Nom de la ville où se trouve la gare
    id_sncf: str | None = None
        Identifiant de la gare à la SNCF, par exemple "stop_area:SNCF:87471003"
    id_gare: int | None = None
        Identifiant de la gare (None tant qu'elle n'est pas enregistrée en base)
    """

    def __init__(self, nom: str, ville: str, id_sncf: str | None = None, id_gare: int | None = None):
        """
        Crée une gare après avoir vérifié le type des paramètres.

        Raises:
        ------
        TypeError
            si un paramètre n'a pas le bon type
        """
        if not isinstance(nom, str):
            raise TypeError("Le nom doit être une chaîne de caractères.")
        if not isinstance(ville, str):
            raise TypeError("La ville doit être une chaîne de caractères.")
        if id_sncf is not None and not isinstance(id_sncf, str):
            raise TypeError("L'identifiant SNCF doit être une chaîne de caractères.")
        if id_gare is not None and not isinstance(id_gare, int):
            raise TypeError("L'identifiant de la gare doit être un entier.")

        self.id_gare = id_gare
        self.nom = nom
        self.ville = ville
        self.id_sncf = id_sncf

    def __str__(self):
        """
        Représentation string d'une gare.

        Return:
        ------
        str
            la description affichée
        """
        return f"La gare {self.nom} ({self.id_gare}) se situe à {self.ville}"
