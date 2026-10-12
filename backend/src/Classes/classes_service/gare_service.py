from src.Classes.classes_DAO.gare_DAO import GareDAO
from src.Classes.classes_objets.gare import Gare


class GareService:
    """Classe qui gère les opérations métier sur les gares"""

    def rechercher(self, nom: str | None, ville: str | None) -> list[Gare]:
        """
        Recherche des gares par nom et/ou par ville.
        Si aucun critère n'est renseigné, toutes les gares sont renvoyées.

        Param:
        ------
        nom: str | None
            le début du nom de la gare (optionnel)
        ville: str | None
            le début du nom de la ville (optionnel)

        Return:
        ------
        list[Gare]
            la liste des gares correspondantes (vide si aucune)
        """
        nom = nom.strip() if nom else None
        ville = ville.strip() if ville else None
        return GareDAO().rechercher(nom=nom or None, ville=ville or None)
