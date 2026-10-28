from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne


class LigneService:
    """Classe qui gère les opérations métier sur les lignes"""

    def creer(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne:
        """
        Méthode servant à créer une ligne.

        Param:
        ------
        gare_depart: Gare
            la gare de départ de la ligne
        gare_arrivee: Gare
            la gare d'arrivée de la ligne

        Return:
        ------
        Ligne
            la ligne créée, avec son id_ligne renseigné

        Raises:
        ------
        ValueError
            si une gare est manquante, si les deux gares sont identiques
            ou si la ligne existe déjà
        """
        if gare_depart is None or gare_arrivee is None:
            raise ValueError("La gare de départ et la gare d'arrivée sont obligatoires.")
        if gare_depart.id_gare == gare_arrivee.id_gare:
            raise ValueError("La gare de départ et la gare d'arrivée doivent être différentes.")
        if self.rechercher(gare_depart, gare_arrivee) is not None:
            raise ValueError("Une ligne existe déjà entre ces deux gares.")

        return LigneDAO().creer(gare_depart, gare_arrivee)

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne | None:
        """
        Méthode servant à rechercher la ligne reliant deux gares.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée

        Return:
        ------
        Ligne | None
            la ligne trouvée, ou None si aucune ligne ne relie ces deux gares
        """
        if gare_depart is None or gare_arrivee is None:
            return None
        return LigneDAO().rechercher(gare_depart=gare_depart, gare_arrivee=gare_arrivee)
